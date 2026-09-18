---
id: self-docs/files/rbac-phase1-improvement-teststrategy
canonical_question: 'Technical guide and specification: Core System — RBAC Improvement
  & Test Strategy'
aliases:
- Core System — RBAC Improvement & Test Strategy
- RBAC Phase1 Improvement TestStrategy
entity_type: how_to
domain: self-docs > files
last_verified: 2026-07-20
---

# Core System — RBAC Improvement & Test Strategy (Phase 1: Dev/Internal)

**Status**: Giai đoạn 1 — Phát triển nội bộ  
**Priority**: Stability + Test Coverage + Ops/Configuration  
**Focus**: Core Permission Logic + Multi-role Scenarios + FE-BE Sync  
**Date**: 2026-07-20 onwards

---

## I. HIỆN TRẠNG & RỦI RO

### 1.1 Những gì VỪA ĐƯỢC SỬA (2026-07-20)
| Lĩnh vực | Bug cũ | Cách sửa | Rủi ro còn lại |
|---------|--------|---------|----------------|
| **FE Fallback** | `roleMatrixChecked` mặc định true chỉ cho `hr_admin`, false cho role khác → Lưu Ma trận Role ghi đè hàng loạt ô chưa dùng | Mặc định cho phép chung (opt-out) | Tái diễn nếu thêm role mới mà quên update fallback logic |
| **BE Permission Merge** | Gộp ALL role permission rồi mới xét mặc định 1 lần → 1 role deny + role khác chưa có dòng = vẫn deny | Per-role calculation + priority tier + OR result trong tier cao nhất | Nếu priority chưa được set đúng trên role, thuật toán vẫn có thể out of control |
| **Seed & Auth** | N/A (đã hoạt động) | N/A | `super_admins` table hardcode `user@company.test` + env var → dễ miss khi setup UAT/golive |

### 1.2 Những gì CÒN OPEN / CHƯA TEST
- ❌ **BE Integration Test**: Chưa chạy với Postgres thật, thiếu `TEST_DATABASE_URL`
- ❌ **FE-BE Sync**: Fallback logic FE + backend priority algorithm → chưa test cùng nhau
- ❌ **Multi-role Edge Cases**: 
  - User giữ 5 role, 3 role có priority 0, 2 role có priority 10 → cấp phát quyền đúng không?
  - Role cha (parent_role_id) ✗ dùng, nhưng có code xử lý → gây confusion khi override?
  - Scope company/department + priority → tổng hợp lại như nào?
- ❌ **Permission Matrix CRUD**: Ghi vào DB (SET granted=false/true) có đảm bảo consistent không?
- ❌ **Permission Matrix Restore**: Ma trận `cb_staff` bị ghi sai cần khôi phục tay → chưa có UI/tool
- ❌ **Migration & Atlas**: `atlas.sum` chưa regenerate, khiến CI có thể gate
- ❌ **Role Priority Configuration**: Chưa có UI, chỉ set qua SQL tay → dễ sai/quên

### 1.3 Những gì CÓ THỂ GÂY HIỂU LẦM / KHÓ DEBUG
| Vấn đề | Tác động | Mức độ |
|--------|----------|-------|
| 2 lớp gate (thô + mịn) không rõ ranh giới → dev thêm feature quên gate thô | Bảo mật lơ lỏng hoặc quyền không được apply | 🔴 Cao |
| `super_admins` logic auto-override `employee_roles` → test role trên dev/admin không có tác dụng | Đổi role test nhưng không thấy kết quả, nghĩ là bug | 🟡 Trung |
| Permission matrix 2 màn (Per User / Per Role) độc lập, chưa có validation → data inconsistency | Ma trận rối, quyền không match kỳ vọng | 🟡 Trung |
| `roles.parent_role_id` tồn tại nhưng NULL mọi nơi + `expandRoleHierarchy` dormant | Code rác, confusion, khó bảo trì | 🟠 Thấp |

---

## II. IMPROVEMENT ROADMAP (3 PHASE)

### **PHASE 1A: Foundation & Safety (Ngay — ~1 tuần)**
🎯 Làm chắc những gì vừa sửa, tránh tái diễn bug, setup test infrastructure

#### Tasks:
1. **Test Suite Scaffolding** ✅
   - BE: Setup integration test với test DB (Postgres Docker)
   - FE: Setup test framework (Jest + React Testing Library nếu chưa có)
   - CI: Thêm test gate trước merge (chặn nếu test fail)

2. **Unit Test Coverage: Permission Logic**
   - BE: `resolveModuleActionPermission` (core algorithm)
   - FE: `roleMatrixChecked` (fallback logic)
   - Target: 90%+ coverage trên permission + role resolution

3. **Integration Test: Multi-role Scenarios**
   - 3-5 real-world scenarios (user + 2-3 role + permission matrix)
   - Verify permission calculation từ DB → BE response → FE UI

4. **Seed & Migration Verification**
   - Script check atlas.sum consistency
   - Seed script tự động populate `super_admins`, `roles`, sample `employee_roles`
   - Doc: Cách setup DB từ 0 cho người mới

5. **Bug Regression Tests**
   - Test case cho 2 bug vừa sửa (FE fallback + BE merge)
   - Chạy lại → pass → lock for future

#### Deliverable:
- `/Core System-backend/tests/integration/permission_test.go` (multi-role scenarios)
- `/Core System-backend/tests/unit/permission_logic_test.go` (core algorithm)
- `/Core System-frontend/__tests__/role-matrix.test.tsx` (FE fallback)
- `/Core System-backend/scripts/seed-rbac.sql` (seeding)
- `/Core System-backend/scripts/verify-migration.sh` (atlas.sum check)
- `/docs/RBAC-Testing-Guide.md` (how to run tests, interpret results)

---

### **PHASE 1B: Ops Automation & Configuration (Tuần 2-3)**
🎯 Giảm thủ công SQL, làm rõ config flow, xây dựng admin tools

#### Tasks:
1. **Role Priority Configuration UI** (nếu feasible trong Phase 1)
   - Form: Select Role → Input Priority → Save
   - Backend endpoint: `PUT /api/roles/{id}/priority`
   - Test case: Priority thay đổi → permission recalculate đúng

2. **Permission Matrix Backup/Restore Tool**
   - Export matrix từ DB thành JSON (version + timestamp)
   - Import/restore từ JSON
   - Use case: Khôi phục `cb_staff` matrix đã bị ghi sai

3. **Seeding Script Enhancement**
   - Interactive CLI: `./seed-rbac.sh --role=cb_staff --company=Enterprise --generate-permissions`
   - Output: SQL + verification report
   - Reduce: Setup từ 30 phút SQL tay → 5 phút CLI

4. **Role Audit Log** (BE middleware)
   - Log mọi thay đổi: role assign, permission matrix CRUD, priority update
   - Table: `rbac_audit_log` (user, action, role_id, change_json, timestamp)
   - Use case: Trace ai sửa ma trận → fix sai lầm dễ hơn

#### Deliverable:
- `Core System-backend/internal/handlers/role_priority_handler.go` + endpoint test
- `Core System-backend/scripts/export-import-matrix.sh` (backup/restore)
- `Core System-backend/scripts/seed-rbac-interactive.sh` (guided seeding)
- `Core System-backend/internal/models/rbac_audit_log.go` (schema + middleware)

---

### **PHASE 1C: Documentation & Developer Experience (Tuần 3-4)**
🎯 Rõ ràng design, giảm confusion, hướng dẫn dev khi thêm feature mới

#### Tasks:
1. **Architecture Decision Record (ADR)**
   - `docs/ADR-RBAC-Permission-Model.md`: Tại sao opt-out + 2-layer gate?
   - `docs/ADR-Role-Priority-Tier.md`: Tại sao priority dùng để break tie?
   - `docs/ADR-Scope-Company-Department.md`: Scope logic ở layer nào, edge case?

2. **Developer Guide: Adding New Feature**
   - Checklist: Gate thô (router) → Gate mịn (permission matrix) → Test
   - Real example: Thêm module mới `reports` → làm theo step
   - Common mistakes + fixes

3. **Runbook: Permission Troubleshooting**
   - User: "Sao tôi không vào được X?"
   - Runbook: Check super_admin → role assign → permission matrix → gate thô/mịn → kết luận
   - With SQL query + log pattern để trace

4. **FE-BE Contract Specification**
   - Permission response format: `{ module, action, granted, reason? }`
   - Fallback behavior: Khi API chậm/lỗi → default deny hay default allow?
   - Test: FE handle các trường hợp API response

#### Deliverable:
- `docs/ADR-RBAC-*.md` (3-4 file)
- `docs/RBAC-Developer-Guide.md` (feature checklist + examples)
- `docs/RBAC-Troubleshooting-Runbook.md` (debug steps + SQL)
- `docs/FE-BE-Contract-Specification.md` (API & fallback)

---

## III. TEST SUITE ARCHITECTURE

```
Core System-backend/
├── tests/
│   ├── integration/
│   │   ├── permission_test.go          (Multi-role + permission matrix)
│   │   ├── permission_scope_test.go    (Company/department scope)
│   │   ├── rbac_audit_test.go          (Audit log)
│   │   └── db_setup.go                 (Test DB fixtures)
│   ├── unit/
│   │   ├── permission_logic_test.go    (resolveModuleActionPermission core)
│   │   ├── role_priority_test.go       (Priority tier algorithm)
│   │   ├── super_admin_test.go         (Super admin override logic)
│   │   └── role_hierarchy_test.go      (expandRoleHierarchy — even if dormant)
│   └── fixtures/
│       ├── roles.json                  (Seed data)
│       ├── permissions.json
│       └── employee_roles.json
│
Core System-frontend/__tests__/
├── role-matrix.test.tsx
│   ├── roleMatrixChecked fallback logic
│   ├── FE-BE permission format sync
│   └── Matrix CRUD validation
├── permission-gate.test.tsx
│   ├── Component render when denied
│   └── Loading state during API call
└── integration/
    └── full-flow.test.tsx              (User login → see role → matrix → save)
```

---

## IV. TEST CASES CHI TIẾT

### **IV.1 UNIT TEST: Permission Logic (BE)**

#### UT-TASK-REF: Single Role, Default Permit (Opt-Out)
```
Given: User has role "employee" (role_id=4)
       No row in permissions table for (module="reports", action="view", role_id=4)
When:  resolveModuleActionPermission(user_id, "reports", "view")
Then:  Result = GRANTED (mặc định opt-out)
```

#### UT-TASK-REF: Single Role, Explicit Deny
```
Given: User has role "cb_staff" (role_id=2)
       permissions table has row (module="config", action="edit", role_id=2, granted=false)
When:  resolveModuleActionPermission(user_id, "config", "edit")
Then:  Result = DENIED
```

#### UT-TASK-REF: Multi-Role, Same Priority, OR Logic
```
Given: User has 2 roles at priority 0:
       - role_a (id=1): [no row for "export"] → mặc định grant
       - role_b (id=2): (module="export", action="run", role_id=2, granted=true)
When:  resolveModuleActionPermission(user_id, "export", "run")
Then:  Result = GRANTED (role_a default + role_b explicit = OR = grant)
```

#### UT-TASK-REF: Multi-Role, Different Priority, Ignore Lower Tier
```
Given: User has:
       - role_a at priority 10 (high): [no row for "reports/view"]
       - role_b at priority 0 (low): (module="reports", action="view", role_id=b, granted=false)
When:  resolveModuleActionPermission(user_id, "reports", "view")
Then:  Result = GRANTED (only priority 10 tier evaluated, role_b ignored)
```

#### UT-TASK-REF: Multi-Role, Same Priority, All Deny
```
Given: User has 2 roles at priority 0:
       - role_a: (module="delete", action="employee", granted=false)
       - role_b: (module="delete", action="employee", granted=false)
When:  resolveModuleActionPermission(user_id, "delete", "employee")
Then:  Result = DENIED (both deny = OR = deny)
```

#### UT-TASK-REF: Role Hierarchy Dormant (Should NOT Expand)
```
Given: role_parent has parent_role_id = NULL (or parent exists but not used)
When:  expandRoleHierarchy(role_parent) is called
Then:  Returns only [role_parent] (no inherited roles, as parent_role_id logic is not active)
       NOTE: This test documents current behavior; if hierarchy is later enabled, update.
```

#### UT-TASK-REF: Super Admin Override
```
Given: User email in super_admins table
When:  getAppRoles(user_id) is called
Then:  Returns ALL roles in system regardless of employee_roles table
       AND isSuperAdmin(user_id) returns true
```

---

### **IV.2 UNIT TEST: Permission Matrix Fallback (FE)**

#### UT-TASK-REF: Fallback When Cell Has No Data
```
Given: roleMatrixChecked(role="employee", module="reports", action="view")
       No row in DB for this (role, module, action)
When:  Component renders matrix
Then:  Cell displays as "ALLOWED" (default = opt-out allow)
       Clicking toggle → sets granted=false → saves to DB
```

#### UT-TASK-REF: Fallback Consistency Across Roles
```
Given: 2 roles without explicit permission data
When:  roleMatrixChecked called for both
Then:  Both return true (allow) — consistent fallback, not role-dependent
       (Fix for old bug where only hr_admin got true)
```

#### UT-TASK-REF: Matrix Toggle → DB Save → Immediate UI Update
```
Given: User on "Ma trận theo Role" for role="cb_staff"
       Cell (module="export", action="run") currently = ALLOWED
When:  User clicks cell → toggle OFF → "Lưu"
Then:  API call: PUT /api/permissions { role_id, module, action, granted: false }
       Response confirms save
       UI cell immediately shows "DENIED"
       Reload page → still shows "DENIED" (DB persistent)
```

---

### **IV.3 INTEGRATION TEST: Multi-Role Scenarios**

#### IT-TASK-REF: User Assigned 3 Roles (Mixed Priority)
```
Setup:
  - User id=100
  - Role A (id=10, priority=10): permissions = ["reports/view: allow", "export/run: deny"]
  - Role B (id=20, priority=10): permissions = ["export/run: allow"]
  - Role C (id=30, priority=0): permissions = ["reports/view: deny"]

Test:
  1. Assign: employee_roles INSERT (user_id=100, role_id=10, scope_company_id=NULL)
                              INSERT (user_id=100, role_id=20, scope_company_id=NULL)
                              INSERT (user_id=100, role_id=30, scope_company_id=NULL)
  
  2. Query: resolveMultiRolePermissions(user_id=100)
  
  3. Verify:
     - "reports/view" → GRANTED (priority 10 tier: A=allow [default] + B=no row [default] = grant; C ignored)
     - "export/run" → GRANTED (priority 10 tier: A=deny + B=allow = OR = grant)
     - "config/edit" → GRANTED (priority 10 tier: both default = grant)
```

#### IT-TASK-REF: Scope Company/Department + Multi-Role
```
Setup:
  - User id=101
  - Company A, Company B, Department D1, D2
  - Role "department_manager" (id=11)
  - Assign: employee_roles (user_id=101, role_id=11, scope_company_id=A, scope_department_id=D1)
  - Assign: employee_roles (user_id=101, role_id=11, scope_company_id=B, scope_department_id=NULL)

Test:
  1. When checking permission for action="view_payroll" in context (company_id=A, department_id=D1):
     → Should include role assignment (scope match)
  2. When checking in context (company_id=A, department_id=D2):
     → Should EXCLUDE role assignment (department doesn't match)
  3. When checking in context (company_id=B, department_id=D3):
     → Should include role assignment (company match, department NULL = any)

Expected: resolvePermissionWithScope returns correct role set based on scope matching
```

#### IT-TASK-REF: FE Matrix Save + BE Permission Update (End-to-End)
```
Setup:
  - Role "analyst" (id=50)
  - Current permissions: [no rows = default allow]
  
Flow:
  1. Admin opens FE "Ma trận theo Role" → Select "analyst"
     → All cells show "ALLOWED" (fallback true)
  
  2. Admin toggles 3 cells OFF: "export/excel", "reports/monthly", "config/edit"
     Clicks "Lưu"
  
  3. FE calls: POST /api/permissions
     { role_id: 50, module: "export", action: "excel", granted: false }
     ... (3 POST calls total)
  
  4. BE inserts 3 rows into permissions table
  
  5. Admin refreshes page → Matrix shows "DENIED" for those 3 cells
  
  6. Test user with role "analyst" tries to access those features:
     → BE resolveModuleActionPermission returns DENIED
     → FE gate component hides feature
  
  7. Admin toggles one back ON → Save → Test user can access again
  
Assert: CRUD cycle consistent FE ↔ BE ↔ DB
```

---

### **IV.4 EDGE CASES & REGRESSION**

#### IT-TASK-REF: Empty Role (No Permissions, No Assignments)
```
Given: Role "viewer" (id=99) exists, has 0 rows in permissions table
       User has only this role
When:  User tries any module/action
Then:  All granted (opt-out default)
```

#### IT-TASK-REF: Bug Regression — FE Fallback (Old Bug #1)
```
Given: Old code had fallback = true only for hr_admin, false for others
When:  Role "cb_staff" opens Matrix, no permission data exists
       Clicks "Lưu" without changing anything
Then:  Should NOT create `granted=false` rows (fix: default allow)
       Verify: permissions table still empty for cb_staff
```

#### IT-TASK-REF: Bug Regression — BE Permission Merge (Old Bug #2)
```
Given: User has roles with conflicting permissions at SAME priority:
       - role_a: (module="delete", action="user", granted=false)
       - role_b: (module="delete", action="user", granted=true)
When:  resolveModuleActionPermission for "delete/user"
Then:  Result = GRANTED (OR logic within priority tier)
       (Fix: not gated by single deny from role_a)
```

#### IT-TASK-REF: Concurrent Matrix Updates
```
Given: 2 admins simultaneously open Matrix for same role
       Admin1 toggles cell A → saves
       Admin2 toggles cell B → saves
When:  Both operations complete
Then:  DB has both changes (no lost updates)
       Subsequent query sees both A and B toggled
```

#### IT-TASK-REF: Permission Matrix Post-Restore
```
Given: Matrix was corrupted/wrong
       Admin runs restore from backup JSON
When:  All permission rows are reset to backup state
Then:  FE Matrix shows restored state
       User permission re-evaluates based on restored matrix
```

---

## V. IMPLEMENTATION CHECKLIST

### **Phase 1A: Foundation & Safety**

#### Test Infrastructure Setup
- [ ] Create `/Core System-backend/tests/` directory structure
- [ ] Add `docker-compose.test.yml` for Postgres test DB
- [ ] Create `tests/integration/db_setup.go` with fixture loader
- [ ] Add `go test ./tests/...` to CI pipeline (gate on failure)
- [ ] Create `/Core System-frontend/__tests__/` structure + jest.config.js
- [ ] Add `npm test` + coverage report to CI

#### Unit Tests Implementation
- [ ] Implement `permission_logic_test.go` — UT-TASK-REF through 007
  - **Acceptance**: 90%+ coverage on `resolveModuleActionPermission`
- [ ] Implement `role_matrix.test.tsx` — UT-TASK-REF through 003
  - **Acceptance**: All tests pass, no regression in old bug

#### Integration Tests Implementation
- [ ] Implement `permission_test.go` — IT-TASK-REF through 003
- [ ] Implement `permission_scope_test.go` — scope matching
- [ ] Implement `full-flow.test.tsx` (FE) — end-to-end matrix CRUD
- [ ] All edge cases (IT-TASK-REF through 005)
  - **Acceptance**: 100% pass, 2 bug regressions locked

#### Seeding & Verification
- [ ] Create `scripts/seed-rbac.sql` (base roles + sample permissions + super_admin)
- [ ] Create `scripts/verify-migration.sh` (check atlas.sum consistency)
- [ ] Test: Run seed on clean DB → Run all tests → All pass
  - **Acceptance**: New dev can set up DB in 5 min + run tests in 2 min

#### Documentation
- [ ] Write `docs/RBAC-Testing-Guide.md` (how to run, interpret, add new tests)
- [ ] Update `docs/document-map.md` with test files
  - **Acceptance**: A person unfamiliar with codebase can run tests via guide

---

### **Phase 1B: Ops Automation & Configuration**

#### Role Priority Configuration UI (Optional if time)
- [ ] Add `PUT /api/roles/{id}/priority` endpoint (with auth gate)
- [ ] FE form: Role selector + Priority input + Save button
- [ ] Test: Change priority → query user → permission recalculates
  - **Acceptance**: Priority change takes effect immediately

#### Permission Matrix Backup/Restore
- [ ] Create `scripts/export-matrix.sh` → output JSON with timestamp
- [ ] Create `scripts/import-matrix.sh` ← load JSON → update DB
- [ ] Test: Export → Corrupt → Import → Verify restored
  - **Acceptance**: `cb_staff` matrix can be restored via this flow

#### Seeding Enhancements
- [ ] Create `scripts/seed-rbac-interactive.sh` (menu-driven)
- [ ] Output: SQL preview + "Apply?" prompt
- [ ] Test: Follow wizard → generate correct SQL → apply to DB
  - **Acceptance**: Setup time reduced from 30 min to 5 min

#### RBAC Audit Log
- [ ] Add `rbac_audit_log` table schema migration
- [ ] Add middleware hook to log: role assign/unassign, permission CRUD, priority updates
- [ ] Add `GET /api/audit/rbac` endpoint (admin only, with pagination)
- [ ] Test: Make changes → Query audit log → See all actions
  - **Acceptance**: Audit trail complete for troubleshooting

---

### **Phase 1C: Documentation & Developer Experience**

#### ADR Documents
- [ ] `docs/ADR-RBAC-Permission-Model.md` — opt-out rationale, trade-offs
- [ ] `docs/ADR-Role-Priority-Tier.md` — priority algorithm, why not role hierarchy
- [ ] `docs/ADR-Scope-Company-Department.md` — scope logic placement
  - **Acceptance**: Each ADR has "Context", "Decision", "Consequences", "Alternatives"

#### Developer Guide
- [ ] `docs/RBAC-Developer-Guide.md` — feature addition checklist
- [ ] Real example: Walk through adding new module "reports"
  - Step 1: Add gate thô in router (which role can access?)
  - Step 2: Add permission matrix rows (which actions within module?)
  - Step 3: Verify with test
  - Step 4: Merge & deploy
- [ ] Common mistakes section with fixes

#### Troubleshooting Runbook
- [ ] `docs/RBAC-Troubleshooting-Runbook.md`
  - Q: "User can't access X"
  - Runbook: Check super_admin → employee_roles → permissions → gate thô/mịn → diagnosis
  - Include: SQL queries to inspect, log patterns to find, screenshots
- [ ] Interactive decision tree if possible (text-based flowchart)

#### FE-BE Contract Specification
- [ ] `docs/FE-BE-Contract-Specification.md`
  - Permission response: `{ module: string, action: string, granted: boolean, reason?: string }`
  - Fallback behavior: When API fails/timeout → DEFAULT DENY in UI (safety)
  - FE test: Verify fallback handling for latency/errors
  - **Acceptance**: FE & BE devs agree on spec, test covers all paths

---

## VI. RISK & MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Test data doesn't match prod schema** | Medium | High | Use same migration scripts for test DB; test DB created via `atlas migrate apply` with prod migration files |
| **Priority system misunderstood → wrong tier evaluated** | Medium | High | Unit test `role_priority_test.go` covers all priority combinations; ADR documents why tier-based not hierarchical |
| **FE fallback logic drifts again when adding new role** | Medium | Medium | Centralize fallback constant in shared utils; add test for every role in the system, not just hr_admin |
| **Permission matrix not synced after FE/BE separation** | Medium | High | E2E test `full-flow.test.tsx` saves matrix → verifies BE reads it; if test fails, merge blocked |
| **Scope matching bug (company/department)** | Low | Medium | `permission_scope_test.go` covers all combinations; scope logic concentrated in 1 function |
| **Seed data outdated → new roles not included** | Medium | Low | Seed script regenerated when new role added (manual step documented in dev guide); test failure if seed incomplete |
| **Atlas migration not regenerated → CI gate fails** | Low | High | Add CI step to check `atlas.sum`; doc: "Before merging, run `atlas migrate hash` and commit `atlas.sum`" |
| **audit_log table fills up → query slow** | Low | Medium | Add retention policy (keep 90 days); add index on (user_id, timestamp); test with 100k rows |
| **super_admins logic prevents testing on prod-like env** | Medium | Low | Doc clearly: For UAT/golive, set `DEV_USER_EMAIL=""` to disable auto-seed; use dedicated test account |

---

## VII. SUCCESS CRITERIA (Phase 1 Complete)

### Stability
- ✅ All regression tests for 2 old bugs pass
- ✅ No permission-related bugs filed in first 2 weeks after Phase 1A
- ✅ Permission logic unchanged during Phase 1B/1C (ops/docs, no algo changes)

### Test Coverage
- ✅ 90%+ code coverage on `permission.go` + `role_matrix.tsx`
- ✅ 40+ test cases (unit + integration + edge) running in CI
- ✅ All tests pass on both `sec_dev` and clean DB startup

### Ops/Configuration
- ✅ New setup takes ≤10 min (was 30 min SQL tay)
- ✅ No hardcoded SQL needed for role assignment (use script or API)
- ✅ Permission matrix restore from backup in <5 min

### Developer Experience
- ✅ New dev can add a module + permissions + tests in <1 hour (following guide)
- ✅ Runbook resolves 90% of permission issues without escalation
- ✅ ADRs explain design trade-offs; no "why is this like this?" confusion

---

## VIII. FILES TO CREATE/MODIFY

### NEW FILES
```
/Core System-backend/
  tests/integration/
    ├── db_setup.go
    ├── permission_test.go
    ├── permission_scope_test.go
    ├── rbac_audit_test.go
    └── fixtures/
        ├── roles.json
        ├── permissions.json
        └── employee_roles.json
  tests/unit/
    ├── permission_logic_test.go
    ├── role_priority_test.go
    ├── super_admin_test.go
    └── role_hierarchy_test.go
  scripts/
    ├── seed-rbac.sql
    ├── seed-rbac-interactive.sh
    ├── export-matrix.sh
    ├── import-matrix.sh
    └── verify-migration.sh
  internal/models/
    └── rbac_audit_log.go

/Core System-frontend/
  __tests__/
    ├── role-matrix.test.tsx
    ├── permission-gate.test.tsx
    └── integration/
        └── full-flow.test.tsx

/docs/
  ├── RBAC-Testing-Guide.md
  ├── ADR-RBAC-Permission-Model.md
  ├── ADR-Role-Priority-Tier.md
  ├── ADR-Scope-Company-Department.md
  ├── RBAC-Developer-Guide.md
  ├── RBAC-Troubleshooting-Runbook.md
  └── FE-BE-Contract-Specification.md
```

### MODIFY
```
/Core System-backend/
  internal/middleware/
    ├── permission.go (already done, verify)
    ├── auth.go (add audit logging hook)
  internal/app/
    ├── router.go (add audit logging for role-related endpoints)
  
/Core System-frontend/
  components-page/tinh-luong/
    ├── TinhLuongExcel.tsx (add fallback consistency test)

/.github/workflows/
  ├── ci.yml (add `go test ./tests/...` + coverage gate)

/docker-compose.yml (or new docker-compose.test.yml)
  (add Postgres test service)
```

---

## IX. QUICK START FOR DEVELOPER

### Step 1: Set Up Test Environment
```bash
# Clone & setup
cd Core System-backend
docker-compose -f docker-compose.test.yml up -d  # Start test Postgres

# Run all tests
go test ./tests/... -v
```

### Step 2: Run Specific Test
```bash
# Permission logic tests
go test ./tests/unit -run TestPermissionLogic -v

# Multi-role integration
go test ./tests/integration -run TestMultiRole -v

# FE tests
cd ../Core System-frontend
npm test -- --testNamePattern="roleMatrix"
```

### Step 3: Seed Database
```bash
# Auto-seed with defaults
./Core System-backend/scripts/seed-rbac-interactive.sh

# Or raw SQL
psql -U postgres -d payroll_dev -f ./Core System-backend/scripts/seed-rbac.sql
```

### Step 4: Check Audit Log
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/audit/rbac?limit=10
```

---

## X. NEXT PHASE PREVIEW (Phase 2: UAT Readiness)

- [ ] Run smoke tests on UAT env (not just dev)
- [ ] Load test permission matrix with 10k+ users/roles
- [ ] Setup monitoring: Permission deny rate, audit log growth
- [ ] Train support team: Runbook, common issues
- [ ] Compliance check: Audit trail meets compliance requirements
- [ ] Cutover plan: v1 old RBAC → TinhLuongExcel new RBAC

---

**Drafted**: 2026-07-20  
**Status**: Ready for Phase 1A kickoff  
**Owner**: [ThaiDT & Team]  
**Review**: Recommend review & sign-off before coding starts
