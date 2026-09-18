---
id: self-docs/files/rbac-test-templates-and-samples
canonical_question: 'Technical guide and specification: RBAC Test Code Templates &
  Samples'
aliases:
- RBAC Test Code Templates & Samples
- RBAC Test Templates and Samples
entity_type: how_to
domain: self-docs > files
last_verified: 2026-07-20
---

# RBAC Test Code Templates & Samples

**Purpose**: Provide copy-paste templates for implementing Phase 1A tests  
**Language**: Go (Backend) + TypeScript/React (Frontend)  
**Status**: Template examples (adjust to your actual code style)

---

## 1. BACKEND TEST SETUP (Go)

### 1.1 Test Database Setup (`tests/integration/db_setup.go`)

```go
package integration

import (
	"context"
	"fmt"
	"testing"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/require"
)

var testDB *pgxpool.Pool

// SetupTestDB initializes test database connection
// Expects TEST_DATABASE_URL env var, e.g.:
// TEST_DATABASE_URL=postgres://user:password@localhost:5432/payroll_test
func SetupTestDB(t *testing.T) {
	if testDB != nil {
		return // Already initialized
	}

	dbURL := os.Getenv("TEST_DATABASE_URL")
	if dbURL == "" {
		t.Skip("TEST_DATABASE_URL not set, skipping integration tests")
	}

	ctx := context.Background()
	pool, err := pgxpool.New(ctx, dbURL)
	require.NoError(t, err, "failed to connect to test DB")

	// Run migrations
	err = runMigrations(ctx, pool)
	require.NoError(t, err, "failed to run migrations")

	testDB = pool
}

// TeardownTestDB cleans up connections
func TeardownTestDB(t *testing.T) {
	if testDB != nil {
		testDB.Close()
		testDB = nil
	}
}

// ClearTestData removes all test data (use before each test)
func ClearTestData(t *testing.T, ctx context.Context) {
	require.NotNil(t, testDB, "test DB not initialized")

	// Clear in dependency order (foreign keys first)
	tables := []string{
		"permissions",
		"employee_roles",
		"roles",
		"employees",
		"users",
	}

	for _, table := range tables {
		_, err := testDB.Exec(ctx, fmt.Sprintf("DELETE FROM %s CASCADE", table))
		require.NoError(t, err, "failed to clear %s", table)
	}
}

// LoadFixture loads seed data from JSON fixtures
func LoadFixture(t *testing.T, ctx context.Context, fixtureFile string) {
	data, err := ioutil.ReadFile(fixtureFile)
	require.NoError(t, err, "failed to read fixture %s", fixtureFile)

	// Parse and insert (implementation depends on your data structure)
	// Example: unmarshal JSON → iterate → insert rows
	var fixtures map[string]interface{}
	json.Unmarshal(data, &fixtures)
	
	// Insert roles from fixture
	roles := fixtures["roles"].([]interface{})
	for _, r := range roles {
		role := r.(map[string]interface{})
		_, err := testDB.Exec(ctx,
			`INSERT INTO roles (id, name, description, priority) 
			 VALUES ($1, $2, $3, $4)`,
			role["id"], role["name"], role["description"], role["priority"],
		)
		require.NoError(t, err)
	}
}

// Helper: Create test user with role
func CreateTestUserWithRole(t *testing.T, ctx context.Context,
	userID string, roleID int, companyID, deptID interface{}) {

	_, err := testDB.Exec(ctx,
		`INSERT INTO employee_roles (user_id, role_id, scope_company_id, scope_department_id)
		 VALUES ($1, $2, $3, $4)`,
		userID, roleID, companyID, deptID,
	)
	require.NoError(t, err)
}

// Helper: Create test permission entry
func CreateTestPermission(t *testing.T, ctx context.Context,
	module string, action string, roleID int, granted bool) {

	_, err := testDB.Exec(ctx,
		`INSERT INTO permissions (module, action, role_id, granted)
		 VALUES ($1, $2, $3, $4)`,
		module, action, roleID, granted,
	)
	require.NoError(t, err)
}
```

---

### 1.2 Unit Test: Permission Logic (`tests/unit/permission_logic_test.go`)

```go
package unit

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"Core System-backend/internal/models"
	"Core System-backend/internal/middleware"
)

// Mock database for unit tests (no real DB)
type MockPermissionStore struct {
	permissions map[string]map[string]bool // [moduleAction][roleID] = granted
}

// UT-TASK-REF: Single Role, Default Permit (Opt-Out)
func TestPermissionLogic_SingleRole_DefaultPermit(t *testing.T) {
	store := &MockPermissionStore{
		permissions: map[string]map[string]bool{}, // Empty = no explicit rows
	}

	user := &models.User{
		ID:    "user1",
		Roles: []int{4}, // Single role "employee"
	}

	granted := middleware.ResolveModuleActionPermission(
		user, "reports", "view", store, []int{0}, // priority 0
	)

	assert.True(t, granted, "should default permit when no permission row exists")
}

// UT-TASK-REF: Single Role, Explicit Deny
func TestPermissionLogic_SingleRole_ExplicitDeny(t *testing.T) {
	store := &MockPermissionStore{
		permissions: map[string]map[string]bool{
			"config_edit": {
				"2": false, // cb_staff (role_id=2) explicitly denied
			},
		},
	}

	user := &models.User{
		ID:    "user2",
		Roles: []int{2}, // cb_staff
	}

	granted := middleware.ResolveModuleActionPermission(
		user, "config", "edit", store, []int{0},
	)

	assert.False(t, granted, "should deny when permission row exists with granted=false")
}

// UT-TASK-REF: Multi-Role, Same Priority, OR Logic
func TestPermissionLogic_MultiRole_SamePriority_ORLogic(t *testing.T) {
	// role_a (id=1): no row for "export" = default allow
	// role_b (id=2): explicit grant for "export"
	store := &MockPermissionStore{
		permissions: map[string]map[string]bool{
			"export_run": {
				"2": true, // role_b grants
				// role_a has no entry = default
			},
		},
	}

	user := &models.User{
		ID:    "user3",
		Roles: []int{1, 2}, // Both roles at priority 0
	}

	granted := middleware.ResolveModuleActionPermission(
		user, "export", "run", store, []int{0, 0}, // Both priority 0
	)

	assert.True(t, granted, "should grant when at least one role in same priority tier grants")
}

// UT-TASK-REF: Multi-Role, Different Priority, Ignore Lower Tier
func TestPermissionLogic_MultiRole_DifferentPriority_IgnoreLowerTier(t *testing.T) {
	// role_a (id=10, priority=10): no row = default allow
	// role_b (id=30, priority=0): explicit deny
	store := &MockPermissionStore{
		permissions: map[string]map[string]bool{
			"reports_view": {
				"30": false, // role_b denies (but ignored due to lower priority)
			},
		},
	}

	user := &models.User{
		ID:    "user4",
		Roles: []int{10, 30},
	}

	// Simulate priority: [10, 0] for roles [10, 30]
	// Algorithm should only evaluate priority 10 tier
	granted := middleware.ResolveModuleActionPermissionWithPriority(
		user, "reports", "view", store,
		map[int]int{10: 10, 30: 0}, // role_id -> priority
	)

	assert.True(t, granted, "should only evaluate highest priority tier, ignore lower")
}

// UT-TASK-REF: Multi-Role, Same Priority, All Deny
func TestPermissionLogic_MultiRole_SamePriority_AllDeny(t *testing.T) {
	store := &MockPermissionStore{
		permissions: map[string]map[string]bool{
			"delete_employee": {
				"1": false, // role_a denies
				"2": false, // role_b denies
			},
		},
	}

	user := &models.User{
		ID:    "user5",
		Roles: []int{1, 2},
	}

	granted := middleware.ResolveModuleActionPermission(
		user, "delete", "employee", store, []int{0, 0},
	)

	assert.False(t, granted, "should deny when all roles in tier deny")
}

// UT-TASK-REF: Role Hierarchy Dormant (No Inheritance)
func TestRoleHierarchy_Dormant_NoInheritance(t *testing.T) {
	roleWithParent := &models.Role{
		ID:           10,
		Name:         "manager",
		ParentRoleID: 5, // Has parent set, but feature not active
	}

	// expandRoleHierarchy should return only the role itself
	expanded := middleware.ExpandRoleHierarchy(roleWithParent)

	assert.Len(t, expanded, 1, "should only return the role itself")
	assert.Equal(t, 10, expanded[0].ID)
}

// UT-TASK-REF: Super Admin Override
func TestAuth_SuperAdminOverride_IgnoreEmployeeRoles(t *testing.T) {
	store := &MockAuthStore{
		superAdmins: []string{"user@company.test"},
	}

	user := &models.User{
		ID:    "admin1",
		Email: "user@company.test",
	}

	isSuperAdmin := middleware.IsSuperAdmin(user.Email, store)
	assert.True(t, isSuperAdmin, "email in super_admins should be identified as super admin")

	// When getting roles, should return ALL roles in system
	allRoles := middleware.GetAppRoles(user, store)
	assert.Greater(t, len(allRoles), 1, "super admin should have all roles in system")
}
```

---

### 1.3 Integration Test: Multi-Role Scenarios (`tests/integration/permission_test.go`)

```go
package integration

import (
	"context"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"Core System-backend/internal/models"
	"Core System-backend/internal/service"
)

// IT-TASK-REF: User Assigned 3 Roles (Mixed Priority)
func TestMultiRole_MixedPriority_CorrectEvaluation(t *testing.T) {
	ctx := context.Background()
	SetupTestDB(t)
	defer TeardownTestDB(t)
	ClearTestData(t, ctx)

	// Setup: Create 3 roles with different priorities
	// Role A (id=10, priority=10)
	_, err := testDB.Exec(ctx,
		`INSERT INTO roles (id, name, priority) VALUES ($1, $2, $3)`,
		10, "role_a", 10,
	)
	require.NoError(t, err)

	// Role B (id=20, priority=10)
	_, err = testDB.Exec(ctx,
		`INSERT INTO roles (id, name, priority) VALUES ($1, $2, $3)`,
		20, "role_b", 10,
	)
	require.NoError(t, err)

	// Role C (id=30, priority=0)
	_, err = testDB.Exec(ctx,
		`INSERT INTO roles (id, name, priority) VALUES ($1, $2, $3)`,
		30, "role_c", 0,
	)
	require.NoError(t, err)

	// Setup: Assign all 3 roles to user 100
	CreateTestUserWithRole(t, ctx, "user100", 10, nil, nil)
	CreateTestUserWithRole(t, ctx, "user100", 20, nil, nil)
	CreateTestUserWithRole(t, ctx, "user100", 30, nil, nil)

	// Setup: Permission rows
	// Role A: ["reports/view: allow" (default), "export/run: deny"]
	CreateTestPermission(t, ctx, "export", "run", 10, false)

	// Role B: ["export/run: allow"]
	CreateTestPermission(t, ctx, "export", "run", 20, true)

	// Role C: ["reports/view: deny"]
	CreateTestPermission(t, ctx, "reports", "view", 30, false)

	// Create mock service
	svc := service.NewPermissionService(testDB)
	user := &models.User{ID: "user100"}

	// TEST 1: reports/view
	// Priority 10 tier: A=no row (default allow), B=no row (default allow)
	// Priority 0 tier: C=deny (but ignored)
	// Result: ALLOWED
	granted, err := svc.ResolvePermission(ctx, user, "reports", "view")
	require.NoError(t, err)
	assert.True(t, granted, "reports/view should be allowed (priority 10 tier defaults)")

	// TEST 2: export/run
	// Priority 10 tier: A=deny, B=allow → OR = allow
	// Result: ALLOWED
	granted, err = svc.ResolvePermission(ctx, user, "export", "run")
	require.NoError(t, err)
	assert.True(t, granted, "export/run should be allowed (B grants in high priority tier)")

	// TEST 3: config/edit (no rows at all)
	// All roles default → ALLOWED
	granted, err = svc.ResolvePermission(ctx, user, "config", "edit")
	require.NoError(t, err)
	assert.True(t, granted, "config/edit should be allowed (opt-out default)")
}

// IT-TASK-REF: Scope Company/Department + Multi-Role
func TestMultiRole_WithScope_ScopeMatchingWorks(t *testing.T) {
	ctx := context.Background()
	SetupTestDB(t)
	defer TeardownTestDB(t)
	ClearTestData(t, ctx)

	// Setup: Companies and departments
	companyA := "comp_a"
	companyB := "comp_b"
	deptD1 := "dept_d1"
	deptD2 := "dept_d2"

	// Setup: Role
	_, err := testDB.Exec(ctx,
		`INSERT INTO roles (id, name, priority) VALUES ($1, $2, $3)`,
		11, "dept_manager", 0,
	)
	require.NoError(t, err)

	// Setup: Assign role with scope
	// (user_id=101, role_id=11, scope_company_id=comp_a, scope_department_id=dept_d1)
	_, err = testDB.Exec(ctx,
		`INSERT INTO employee_roles (user_id, role_id, scope_company_id, scope_department_id) 
		 VALUES ($1, $2, $3, $4)`,
		"user101", 11, companyA, deptD1,
	)
	require.NoError(t, err)

	// Also assign to company B (department = NULL = any dept in company B)
	_, err = testDB.Exec(ctx,
		`INSERT INTO employee_roles (user_id, role_id, scope_company_id, scope_department_id) 
		 VALUES ($1, $2, $3, $4)`,
		"user101", 11, companyB, nil, // NULL dept = any dept
	)
	require.NoError(t, err)

	// Create permission row (role has specific permission)
	CreateTestPermission(t, ctx, "Core System", "view", 11, true)

	// Create service
	svc := service.NewPermissionService(testDB)
	user := &models.User{ID: "user101"}

	// TEST 1: Check permission in context (comp_a, dept_d1) - SHOULD MATCH first assignment
	context1 := &models.PermissionContext{CompanyID: companyA, DepartmentID: deptD1}
	granted, err := svc.ResolvePermissionWithContext(ctx, user, "Core System", "view", context1)
	require.NoError(t, err)
	assert.True(t, granted, "should have permission in matching scope (comp_a, dept_d1)")

	// TEST 2: Check permission in context (comp_a, dept_d2) - SHOULD NOT MATCH
	context2 := &models.PermissionContext{CompanyID: companyA, DepartmentID: deptD2}
	granted, err = svc.ResolvePermissionWithContext(ctx, user, "Core System", "view", context2)
	require.NoError(t, err)
	assert.False(t, granted, "should NOT have permission in non-matching dept")

	// TEST 3: Check permission in context (comp_b, dept_d3) - SHOULD MATCH second assignment (NULL dept)
	context3 := &models.PermissionContext{CompanyID: companyB, DepartmentID: "dept_d3"}
	granted, err = svc.ResolvePermissionWithContext(ctx, user, "Core System", "view", context3)
	require.NoError(t, err)
	assert.True(t, granted, "should have permission in comp_b (dept NULL = any dept)")
}

// IT-TASK-REF: Bug Regression — FE Fallback (Old Bug #1)
func TestRegression_FEFallback_DoesNotCreateFalseRows(t *testing.T) {
	ctx := context.Background()
	SetupTestDB(t)
	defer TeardownTestDB(t)
	ClearTestData(t, ctx)

	// Setup: Role without any permission rows
	_, err := testDB.Exec(ctx,
		`INSERT INTO roles (id, name, priority) VALUES ($1, $2, $3)`,
		50, "cb_staff", 0,
	)
	require.NoError(t, err)

	// OLD BUG: If FE fallback was `false` for this role,
	// saving the matrix without changes would create many `granted=false` rows.
	// NEW FIX: FE fallback should be `true` (allow by default), so saving
	// without changes creates NO rows.

	// Simulate: Admin opens matrix for role 50, doesn't change anything, clicks Save
	// FE sends empty list of changes
	svc := service.NewPermissionService(testDB)
	err = svc.SavePermissionMatrix(ctx, 50, []models.PermissionChange{})
	require.NoError(t, err)

	// Verify: No permission rows were created
	var count int
	err = testDB.QueryRow(ctx,
		`SELECT COUNT(*) FROM permissions WHERE role_id = $1`,
		50,
	).Scan(&count)
	require.NoError(t, err)
	assert.Equal(t, 0, count, "should not create any permission rows when saving without changes")
}

// IT-TASK-REF: Bug Regression — BE Permission Merge (Old Bug #2)
func TestRegression_BEPermissionMerge_ORLogicWorks(t *testing.T) {
	ctx := context.Background()
	SetupTestDB(t)
	defer TeardownTestDB(t)
	ClearTestData(t, ctx)

	// Setup: Two roles
	_, err := testDB.Exec(ctx,
		`INSERT INTO roles (id, name, priority) VALUES ($1, $2, $3)`,
		60, "role_x", 0,
	)
	require.NoError(t, err)

	_, err = testDB.Exec(ctx,
		`INSERT INTO roles (id, name, priority) VALUES ($1, $2, $3)`,
		61, "role_y", 0,
	)
	require.NoError(t, err)

	// OLD BUG: If role_x explicitly denied "delete/user",
	// but role_y had no row (default allow),
	// old algorithm would merge into single result = deny.
	// NEW FIX: Per-role evaluation with OR = should grant if any role grants.

	CreateTestPermission(t, ctx, "delete", "user", 60, false) // role_x denies
	// role_y has no row = defaults to allow

	CreateTestUserWithRole(t, ctx, "user102", 60, nil, nil)
	CreateTestUserWithRole(t, ctx, "user102", 61, nil, nil)

	svc := service.NewPermissionService(testDB)
	user := &models.User{ID: "user102"}

	granted, err := svc.ResolvePermission(ctx, user, "delete", "user")
	require.NoError(t, err)

	assert.True(t, granted, "should grant when one role denies + other defaults allow (OR logic)")
}
```

---

## 2. FRONTEND TEST TEMPLATES (React/TypeScript)

### 2.1 Test Setup (`__tests__/setup.ts`)

```typescript
import '@testing-library/jest-dom';

// Mock localStorage (artifacts don't support it)
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Mock API calls
export const mockFetchPermission = jest.fn();
export const mockSaveMatrix = jest.fn();
```

---

### 2.2 Unit Test: FE Fallback (`__tests__/role-matrix.test.tsx`)

```typescript
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TinhLuongExcel from '../components-page/tinh-luong/TinhLuongExcel';
import { roleMatrixChecked } from '../components-page/tinh-luong/TinhLuongExcel';

// UT-TASK-REF: Fallback When Cell Has No Data
describe('roleMatrixChecked - Fallback Logic', () => {
  it('should return true (ALLOW) when no permission data exists for any role', () => {
    // Simulate: No DB row for (role="employee", module="reports", action="view")
    const dbPermissions = {}; // Empty

    const result = roleMatrixChecked(
      'employee',
      'reports',
      'view',
      dbPermissions
    );

    expect(result).toBe(true); // Default allow
  });

  it('should return true for hr_admin when no data (same as other roles)', () => {
    // FIX for old bug: hr_admin should NOT be special case in fallback
    const dbPermissions = {};

    const resultHrAdmin = roleMatrixChecked(
      'hr_admin',
      'reports',
      'view',
      dbPermissions
    );
    const resultEmployee = roleMatrixChecked(
      'employee',
      'reports',
      'view',
      dbPermissions
    );

    expect(resultHrAdmin).toBe(true);
    expect(resultEmployee).toBe(true);
    expect(resultHrAdmin).toBe(resultEmployee); // Should be consistent
  });

  it('should return false when permission explicitly set to false', () => {
    const dbPermissions = {
      'employee-reports-view': false,
    };

    const result = roleMatrixChecked(
      'employee',
      'reports',
      'view',
      dbPermissions
    );

    expect(result).toBe(false);
  });

  it('should return true when permission explicitly set to true', () => {
    const dbPermissions = {
      'cb_staff-export-run': true,
    };

    const result = roleMatrixChecked(
      'cb_staff',
      'export',
      'run',
      dbPermissions
    );

    expect(result).toBe(true);
  });
});

// UT-TASK-REF: Fallback Consistency Across Roles
describe('Fallback Consistency Across All Roles', () => {
  const roles = ['hr_admin', 'employee', 'cb_staff', 'search_profile', 'site_admin'];
  const module = 'reports';
  const action = 'view';

  it('all roles should have same fallback when no permission data', () => {
    const dbPermissions = {}; // No data

    const results = roles.map(role =>
      roleMatrixChecked(role, module, action, dbPermissions)
    );

    // All should be true (default allow)
    results.forEach(result => {
      expect(result).toBe(true);
    });

    // All should be the same
    const firstResult = results[0];
    results.forEach(result => {
      expect(result).toBe(firstResult);
    });
  });
});

// UT-TASK-REF: Matrix Toggle → Save → Verify
describe('Matrix CRUD Workflow', () => {
  it('should toggle cell state and persist to DB', async () => {
    const user = userEvent.setup();
    const mockSave = jest.fn().mockResolvedValue({});

    render(
      <TinhLuongExcel
        role="employee"
        dbPermissions={{}}
        onSavePermissions={mockSave}
      />
    );

    // Find the cell for (module="export", action="run")
    const cell = screen.getByRole('button', { name: /export.*run/i });

    // Initially should be ALLOWED (fallback true)
    expect(cell).toHaveClass('allowed');

    // Click to toggle OFF (deny)
    await user.click(cell);

    // Now should show DENIED
    expect(cell).toHaveClass('denied');

    // Click Save button
    const saveBtn = screen.getByRole('button', { name: /save|lưu/i });
    await user.click(saveBtn);

    // Verify API was called with correct payload
    expect(mockSave).toHaveBeenCalledWith({
      role_id: 'employee',
      changes: [
        { module: 'export', action: 'run', granted: false },
      ],
    });
  });

  it('should reflect permission changes immediately in UI after save', async () => {
    const user = userEvent.setup();
    const mockSave = jest.fn().mockResolvedValue({
      success: true,
      updatedPermissions: {
        'employee-export-run': false,
      },
    });

    const { rerender } = render(
      <TinhLuongExcel
        role="employee"
        dbPermissions={{}}
        onSavePermissions={mockSave}
      />
    );

    const cell = screen.getByRole('button', { name: /export.*run/i });

    // Toggle and save
    await user.click(cell);
    const saveBtn = screen.getByRole('button', { name: /save|lưu/i });
    await user.click(saveBtn);

    // Wait for async save
    await screen.findByText(/saved successfully/i);

    // After save completes, re-render with new permissions
    rerender(
      <TinhLuongExcel
        role="employee"
        dbPermissions={{
          'employee-export-run': false,
        }}
        onSavePermissions={mockSave}
      />
    );

    // Verify cell state persisted
    expect(cell).toHaveClass('denied');
  });

  it('should not create permission rows for unchanged cells', async () => {
    const user = userEvent.setup();
    const mockSave = jest.fn().mockResolvedValue({});

    render(
      <TinhLuongExcel
        role="cb_staff"
        dbPermissions={{}} // No prior changes
        onSavePermissions={mockSave}
      />
    );

    // Don't toggle anything, just click Save
    const saveBtn = screen.getByRole('button', { name: /save|lưu/i });
    await user.click(saveBtn);

    // Verify API was called with empty changes (no false entries)
    expect(mockSave).toHaveBeenCalledWith({
      role_id: 'cb_staff',
      changes: [], // EMPTY — fix for old bug
    });
  });
});
```

---

### 2.3 Integration Test: Full Workflow (`__tests__/integration/full-flow.test.tsx`)

```typescript
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TinhLuongExcel from '../../components-page/tinh-luong/TinhLuongExcel';

// Mock API
global.fetch = jest.fn();

// IT-TASK-REF: FE Matrix Save + BE Permission Update (E2E)
describe('Matrix Save → BE Permission Update → User Test Flow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should save matrix changes and reflect user permission updates', async () => {
    const user = userEvent.setup();

    // Mock: Admin saves 3 cells OFF
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        changes: [
          { module: 'export', action: 'excel', granted: false },
          { module: 'reports', action: 'monthly', granted: false },
          { module: 'config', action: 'edit', granted: false },
        ],
      }),
    });

    render(
      <TinhLuongExcel
        role="analyst"
        dbPermissions={{}} // Initially no restrictions
        onSavePermissions={jest.fn()}
      />
    );

    // Admin toggles 3 cells OFF
    const exportCell = screen.getByRole('button', { name: /export.*excel/i });
    const reportsCell = screen.getByRole('button', { name: /reports.*monthly/i });
    const configCell = screen.getByRole('button', { name: /config.*edit/i });

    await user.click(exportCell);
    await user.click(reportsCell);
    await user.click(configCell);

    // Admin clicks Save
    const saveBtn = screen.getByRole('button', { name: /save|lưu/i });
    await user.click(saveBtn);

    // Verify API called
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/permissions'),
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    // Verify UI shows success message
    await screen.findByText(/saved successfully|lưu thành công/i);

    // Verify cells show as DENIED
    expect(exportCell).toHaveClass('denied');
    expect(reportsCell).toHaveClass('denied');
    expect(configCell).toHaveClass('denied');

    // Now test: User with "analyst" role tries to use those features
    // This part would be tested separately (user permission test)
    // but contract is: if permission row exists with granted=false,
    // BE returns false → FE hides feature
  });
});
```

---

## 3. SEED DATA FIXTURE EXAMPLE

### 3.1 Fixture File (`tests/fixtures/roles.json`)

```json
{
  "roles": [
    {
      "id": 1,
      "name": "hr_admin",
      "description": "HR Department Admin",
      "priority": 0
    },
    {
      "id": 2,
      "name": "cb_staff",
      "description": "Construction/Business Staff",
      "priority": 0
    },
    {
      "id": 4,
      "name": "employee",
      "description": "Regular Employee",
      "priority": 0
    },
    {
      "id": 10,
      "name": "site_admin",
      "description": "Site Administrator",
      "priority": 0
    }
  ],
  "permissions": [
    {
      "module": "config",
      "action": "edit",
      "role_id": 2,
      "granted": false,
      "description": "cb_staff cannot edit config"
    },
    {
      "module": "audit-logs",
      "action": "view",
      "role_id": 2,
      "granted": false,
      "description": "cb_staff cannot view audit logs"
    }
  ],
  "employee_roles": [
    {
      "user_id": "user_100",
      "role_id": 1,
      "scope_company_id": null,
      "scope_department_id": null
    },
    {
      "user_id": "user_200",
      "role_id": 2,
      "scope_company_id": "comp_a",
      "scope_department_id": null
    }
  ]
}
```

---

## 4. MANUAL TEST CHECKLIST (For Phase 1A Verification)

After implementing automated tests, run these manual checks:

### 4.1 Manual Test: Priority Tier Calculation
```
Setup:
  - User has: Role A (priority 10), Role B (priority 10), Role C (priority 0)
  - Permissions:
    * Role A: [export/run: DENY]
    * Role B: [export/run: ALLOW]
    * Role C: [export/run: DENY]

Expected: ALLOW (only priority 10 tier evaluated, both grant/deny, OR = allow)
Run: 
  1. Create user in DB with these roles
  2. Call /api/permissions?module=export&action=run
  3. Verify response = { granted: true }
```

### 4.2 Manual Test: Scope Matching
```
Setup:
  - User assigned to role "dept_manager" with:
    * scope_company_id = "comp_a", scope_department_id = "dept_1"

Expected: User only has permission in context of comp_a + dept_1
Run:
  1. Make request with header: X-Company-ID: comp_a, X-Dept-ID: dept_1
  2. Check permission → GRANTED
  3. Make request with header: X-Company-ID: comp_a, X-Dept-ID: dept_2
  4. Check permission → DENIED (scope mismatch)
```

### 4.3 Manual Test: FE Fallback Consistency
```
Setup:
  - Matrix for "new_role" (never had data before)

Expected: All cells show ALLOWED (not role-dependent)
Run:
  1. Admin opens Matrix for "new_role"
  2. Verify ALL cells show green/ALLOWED (not mixed)
  3. Close without saving
  4. Reopen → verify still all ALLOWED
  5. Save without changes → verify NO rows inserted in DB
```

---

## 5. CI/CD INTEGRATION EXAMPLES

### 5.1 GitHub Actions: Run Tests Before Merge (`.github/workflows/test.yml`)

```yaml
name: RBAC Tests

on:
  pull_request:
    branches: [sec_dev]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: payroll_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: 1.21

      - name: Setup Test DB
        env:
          TEST_DATABASE_URL: postgres://postgres:testpass@localhost:5432/payroll_test
        run: |
          cd Core System-backend
          go test ./tests/integration -v -run TestSetup

      - name: Run Backend Tests
        env:
          TEST_DATABASE_URL: postgres://postgres:testpass@localhost:5432/payroll_test
        run: |
          cd Core System-backend
          go test ./tests/... -v -race -coverprofile=coverage.out
          go tool cover -func=coverage.out

      - name: Check Coverage
        run: |
          cd Core System-backend
          coverage=$(go tool cover -func=coverage.out | tail -1 | awk '{print $NF}' | sed 's/%//')
          if (( $(echo "$coverage < 90" | bc -l) )); then
            echo "Coverage $coverage% is below 90%"
            exit 1
          fi

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: |
          cd Core System-frontend
          npm ci

      - name: Run Tests
        run: |
          cd Core System-frontend
          npm test -- --coverage --watchAll=false

  atlas-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Verify atlas.sum exists
        run: |
          if [ ! -f "Core System-backend/migrations/atlas.sum" ]; then
            echo "atlas.sum missing — run 'atlas migrate hash' and commit"
            exit 1
          fi
```

---

## 6. QUICK START FOR DEVELOPERS

### Step 1: Set Up Test Environment
```bash
# Backend
cd Core System-backend
export TEST_DATABASE_URL=postgres://postgres:testpass@localhost:5432/payroll_test
docker-compose -f docker-compose.test.yml up -d
go test ./tests/unit -v

# Frontend
cd Core System-frontend
npm test
```

### Step 2: Run Specific Test Category
```bash
# Permission logic only
go test ./tests/unit/permission_logic_test.go -v -run UT-PERM

# Multi-role only
go test ./tests/integration/permission_test.go -v -run IT-MULTI

# FE matrix only
npm test role-matrix.test.tsx
```

### Step 3: Add New Test
1. Create file in appropriate location (`tests/unit/`, `tests/integration/`, `__tests__/`)
2. Copy template from this guide
3. Run locally: `go test ./tests/... -v` or `npm test`
4. Commit + push → CI runs full suite before merge

---

## APPENDIX: Test Data SQL Scripts

### Quick Seed for Local Testing
```sql
-- Copy to: Core System-backend/scripts/seed-test-data.sql

-- Roles
INSERT INTO roles (id, name, priority) VALUES
  (1, 'hr_admin', 0),
  (2, 'cb_staff', 0),
  (4, 'employee', 0),
  (10, 'site_admin', 0),
  (11, 'dept_manager', 5),
  (50, 'analyst', 0);

-- Permissions (sample)
INSERT INTO permissions (module, action, role_id, granted) VALUES
  ('config', 'edit', 2, false),           -- cb_staff cannot edit config
  ('audit-logs', 'view', 2, false),       -- cb_staff cannot view audit
  ('export', 'run', 1, true),             -- hr_admin can export
  ('delete', 'user', 50, false);          -- analyst cannot delete users

-- Test users
INSERT INTO employee_roles (user_id, role_id, scope_company_id, scope_department_id) VALUES
  ('test_hr', 1, NULL, NULL),             -- hr_admin, no scope limit
  ('test_cb', 2, 'comp_a', NULL),         -- cb_staff, company A only
  ('test_analyst', 50, NULL, NULL);       -- analyst, no scope
```

---

**Updated**: 2026-07-20  
**Next**: Implement one test type at a time, run locally, then merge to sec_dev branch
