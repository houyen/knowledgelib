---
id: self-docs/engine/payroll-architecture-roadmap
canonical_question: 'Technical guide and specification: PHÂN TÍCH KIẾN TRÚC BẢO MẬT
  Core System STANDALONE'
aliases:
- PHÂN TÍCH KIẾN TRÚC BẢO MẬT Core System STANDALONE
- Core System Architecture Roadmap
entity_type: architecture_explainer
domain: self-docs > engine
last_verified: 2026-07-09
---

# PHÂN TÍCH KIẾN TRÚC BẢO MẬT Core System STANDALONE
---

## 🔐 DANH MỤC I: KIỂM SOÁT TRUY CẬP (Access Control Layer)

### 1.1 RBAC (Role-Based Access Control)

#### ✅ Ưu Điểm

- **Đơn giản triển khai**: Thiết kế dựa trên vai trò doanh nghiệp hiện hành
- **Dễ hiểu quản trị**: Quản lý quyền trực tiếp qua giao diện quản lý vai trò
- **Chi phí thấp**: Không cần tích hợp hệ thống bên ngoài phức tạp
- **Dễ kiểm toán**: Audit log rõ ràng: User → Role → Permission
- **Phù hợp MVP**: Có thể triển khai nhanh trong 2-3 tuần

#### ❌ Nhược Điểm

- **Bùng nổ vai trò**: Khi doanh nghiệp mở rộng, số lượng vai trò tăng theo cấp số nhân
  - 50 nhân viên → ~8 vai trò
  - 500 nhân viên → ~40+ vai trò
- **Không linh hoạt**: Không thể áp dụng quy tắc động dựa trên ngữ cảnh
  - Ví dụ: Không thể chặn phê duyệt bảng lương vào chiều thứ 6 mặc dù người dùng có vai trò approver
- **Độc quyền cao**: Một vai trò phê duyệt có quyền phê duyệt **mọi** bảng lương
  - Không có ràng buộc theo phòng ban, chi nhánh, hoặc mức tiền
- **Gian lận khó kiểm soát**: Phải dựa hoàn toàn vào quy tắc phân tách nhiệm vụ (SoD) cơ bản

#### 🛠️ Chi Tiết Triển Khai

| Yếu Tố                            | Ghi Chú                        |
| --------------------------------- | ------------------------------ |
| **Backend (Role Service)**        | CRUD vai trò, gán quyền        |
| **Database Schema**               | Bảng users, roles, permissions |
| **Frontend (Role Management UI)** | Giao diện quản lý vai trò      |
| **Documentation &amp; Testing**   | Hướng dẫn sử dụng, test cases  |

#### 📊 Mô Hình Cấu Trúc Vai Trò

```
Tổng giám đốc
├── Giám đốc Tài chính
│   ├── Kế toán trưởng (Core System Approver)
│   ├── Kế toán nhân sự (Core System Processor)
│   └── Kế toán cấp dưới (Assistant)
├── Giám đốc Nhân sự
│   ├── Trưởng phòng HR
│   ├── Chuyên viên Chế độ (Benefits Specialist)
│   └── Chuyên viên Tuyển dụng
└── Giám đốc Vận Hành
    ├── Quản lý Chi nhánh
    └── Chuyên viên Dữ liệu
```

---

### 1.2 ABAC (Attribute-Based Access Control)

#### ✅ Ưu Điểm

- **Linh hoạt tối đa**: Quy tắc phân quyền động dựa trên 4 nhóm thuộc tính:
  - **Subject** (Chủ thể): Vai trò, phòng ban, chứng chỉ, trạng thái onboarding
  - **Resource** (Tài nguyên): Loại dữ liệu, mức độ nhạy cảm, chi nhánh
  - **Action** (Hành động): Read, Write, Approve, Export
  - **Environment** (Môi trường): Giờ, IP, thiết bị, VPN
- **Skalable**: Không bùng nổ vai trò; số quy tắc tăng tuyến tính chứ không exponential
- **Tuân thủ tốt**: Dễ thực hiện Policy-as-Code cho kiểm toán định kỳ
- **Chặn Insider Threat**: Ví dụ chặn Kế toán trưởng phê duyệt bảng lương ngoài giờ hành chính từ IP công cộng
- **Tinh chỉnh mịn**: Ví dụ chỉ cho phép xem lương nhân viên &gt; 10,000 USD nếu người dùng có chứng chỉ tài chính

#### ❌ Nhược Điểm

- **Phức tạp triển khai**: Yêu cầu thiết kế hệ thống Policy Engine phức tạp
- **Chi phí cao**: Cần tích hợp Open Policy Agent (OPA) hoặc Styra
- **Đòi hỏi expertise**: Đội ngũ cần có kinh nghiệm với Policy-as-Code
- **Hiệu năng**: Mỗi request phải query OPA (latency +5-10ms nếu không optimize)
- **Khó kiểm soát**: Khi quy tắc quá phức tạp, khó debug và maintain
- **Yêu cầu quản lý dữ liệu**:
  - Phải tồn tại database lưu trữ IP ranges, danh sách certificates
  - Phải tích hợp LDAP/AD để lấy phòng ban, chứng chỉ người dùng

#### 🎯 Ví Dụ ABAC Policy (Rego Language)

```rego
package Core System.authorization

import rego.v1

default allow := false

# Quy tắc: Kế toán viên chỉ được phê duyệt bảng lương trong giờ hành chính từ VPN
allow if {
    # Subject attributes
    input.user.role == "payroll_approver"
    
    # Resource attributes
    input.resource.type == "Core System"
    
    # Action attributes
    input.action == "approve"
    
    # Environment constraints
    is_business_hours(input.context.timestamp)
    is_internal_network(input.context.ip)
    
    # Monetary constraint: chỉ phê duyệt <= $100K
    input.data.total_amount <= 100000
}

is_business_hours if {
    hour := time.now_ns() | time.hour
    hour >= 8
    hour < 18
}

is_internal_network if {
    # Danh sách IP VPN/nội bộ
    ip := input.context.ip
    ip_prefix := split(ip, ".")[0:3] | join(".")
    
    allowed_prefixes := ["192.168.1", "10.0.1", "203.0.113"]
    ip_prefix in allowed_prefixes
}
```

---

### 1.3 Hybrid: RBAC + ABAC (Recommended for MVP → Scale)

#### ✅ Cách Kết Hợp Tối Ưu

- **Tầng 1 (Coarse-Grained)**: RBAC tại API Gateway
  - Kiểm tra nhanh: User có vai trò "payroll_approver" không?
  - Latency &lt; 1ms (chỉ query in-memory cache)
- **Tầng 2 (Fine-Grained)**: ABAC tại Business Logic hoặc OPA
  - Kiểm tra chi tiết: Người dùng có thể phê duyệt **bảng lương này** không?
  - Latency ~ 5-10ms (có cache tại API Gateway)

#### 📊 So Sánh Chi Phí &amp; Kiểm Soát

| Tiêu Chí                  | RBAC Thuần            | ABAC Thuần | RBAC+ABAC (Hybrid) |
| ------------------------- | --------------------- | ---------- | ------------------ |
| **Chi phí Initial**       | $?                    | $?         | $?                 |
| **Chi phí Bảo trì/năm**   | $?                    | $?         | $?                 |
| **Thời gian triển khai**  | 2-3 tuần              | 6-8 tuần   | 4-5 tuần           |
| **Mức độ kiểm soát**      | 60%                   | 98%        | 85%                |
| **Skalability**           | Kém (vai trò bùng nổ) | Tốt        | Rất tốt            |
| **Dễ implement**          | Rất dễ                | Khó        | Vừa phải           |
| **Insight Threat Detect** | Kém                   | Tuyệt      | Tốt                |

---

## 🌉 DANH MỤC II: API GATEWAY &amp; AUTHORIZATION (Tầng Biên)

### 2.1 API Gateway + Simple Token (JWT)

#### ✅ Ưu Điểm

- **Nhanh**: Xác thực token chỉ cần verify signature (&lt; 1ms)
- **Stateless**: Không cần query database, mỗi request độc lập
- **Dễ scale**: Có thể chạy multiple gateway instances
- **Tiêu chuẩn**: JWT là chuẩn công nghiệp, hầu hết framework đều support

#### ❌ Nhược Điểm

- **Không thể revoke nhanh**: Token tồn tại đến khi hết hạn (thường 1 giờ)
  - Nếu nhân viên bị sa thải, phải đợi token hết hạn, không revoke tức thì
- **Bùng nổ scope**: Khi thêm quyền, JWT payload tăng kích thước (vì mã hóa chứa tất cả quyền)
- **Không hỗ trợ ABAC**: Token chỉ chứa vai trò cơ bản, không có attribute động

---

### 2.2 API Gateway + OPA (Open Policy Agent)

#### ✅ Ưu Điểm

- **Fine-grained**: Hỗ trợ ABAC policy evaluation tại gateway
- **Revoke tức thì**: Có thể push policy updates mà không cần restart
- **Audit trail**: Tất cả quyết định phân quyền được log lại

#### ❌ Nhược Điểm

- **Latency tăng**: Mỗi request phải call OPA (~5-10ms)
- **Operational complexity**: Phải maintain OPA cluster riêng
- **Licensing**: Styra DAS (commercial) ~ $5-15K/năm

---

### 2.3 Kong vs APISIX vs AWS API Gateway

| Tiêu Chí              | Kong          | APISIX               | AWS API Gateway                   |
| --------------------- | ------------- | -------------------- | --------------------------------- |
| **Open Source**       | ✅ (Community) | ✅ (Apache)           | ❌ (Managed)                       |
| **OPA Integration**   | ✅ Plugin      | ✅ Plugin             | ⚠️ Lambda custom                  |
| **Chi phí License**   | $?            | Free                 | Pay-as-you-go (~$0.35/M requests) |
| **Độ phức tạp Setup** | Trung bình    | Trung bình           | Thấp (Managed)                    |
| **Scaling**           | Manual (K8s)  | Manual (K8s)         | Auto (Serverless)                 |
| **Phù hợp**           | Enterprise    | Startup → Enterprise | Startup (AWS-first)               |

**Khuyến nghị**: APISIX cho Core System Standalone (mã nguồn mở, cost-effective, hỗ trợ OPA)

---

## 🗄️ DANH MỤC III: DATABASE SECURITY (Tầng Lưu Trữ)

### 3.1 Row-Level Security (RLS)

#### ✅ Ưu Điểm

- **Phòng thủ chiều sâu**: Ngay cả nếu app logic bị bypass, RLS vẫn bảo vệ
- **Tự động cô lập**: Không cần app layer phải ghi đúng WHERE clause
- **Hiệu năng**: RLS được apply bởi query optimizer, không overhead
- **Tiêu chuẩn**: PostgreSQL, SQL Server, Oracle đều hỗ trợ

#### ❌ Nhược Điểm

- **Chỉ bảo vệ horizontal**: Bảo vệ hàng (row), không bảo vệ cột (column)
  - Không thể che giấu cột lương trong SELECT *
- **Limitation với JOIN**: RLS có thể làm chậm query với JOIN phức tạp
- **Limited để debug**: Khó kiểm tra policy khi develop/testing

#### 📝 Ví Dụ RLS Setup PostgreSQL

```sql
-- 1. Kích hoạt RLS trên bảng employees
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees FORCE ROW LEVEL SECURITY;

-- 2. Tạo policy: Mỗi người dùng chỉ nhìn thấy nhân viên của chi nhánh mình
CREATE POLICY employee_branch_isolation ON employees
FOR ALL
USING (branch_id = current_setting('app.current_branch_id')::uuid);

-- 3. Khi connection từ app, set context
-- SELECT set_config('app.current_branch_id', 'branch-001', false);
-- SELECT * FROM employees; -- Chỉ lấy nhân viên của branch-001
```

---

### 3.2 Client-Side Field-Level Encryption (CSFLE)

#### ✅ Ưu Điểm

- **Bảo vệ tối đa**: DBA không thể xem dữ liệu lương ngay cả khi trực tiếp access database
- **Compliance**: Đáp ứng các yêu cầu GDPR, PCI DSS về mã hóa end-to-end
- **Khóa độc lập**: Khóa mã hóa nằm ngoài database server

#### ❌ Nhược Điểm

- **Hiệu năng**: Mã hóa/giải mã tạo overhead 10-30% (tùy thuộc data size)
- **Truy vấn giới hạn**: Không thể search/sort trực tiếp trên encrypted fields
  - Ví dụ: SELECT * FROM Core System WHERE salary &gt; 50000 không thể thực hiện trên encrypted salary
- **Phức tạp**: Yêu cầu Key Management Service (KMS) tích hợp

---

### 3.3 Envelope Encryption (DEK + KEK)

#### ✅ Ưu Điểm

- **Hiệu năng tối ưu**: 
  - Dữ liệu được mã hóa bằng DEK (Data Encryption Key) cơ bản nhanh
  - DEK được mã hóa bằng KEK (Key Encryption Key) từ HSM/KMS
- **Quay vòng khóa dễ**: Có thể thay KEK mà không cần giải mã lại toàn bộ dữ liệu
- **Compliance**: Hỗ trợ audit, tách biệt quyền giữa app và key operator

#### ❌ Nhược Điểm

- **Phức tạp**: Yêu cầu quản lý 2 loại khóa
- **Cost cao**: Phải trả phí cho HSM hoặc KMS service

---

### 3.4 So Sánh Database Security Approaches

| Tiêu Chí          | RLS  | CSFLE      | Envelope   | RLS + Envelope |
| ----------------- | ---- | ---------- | ---------- | -------------- |
| **Bảo vệ Row**    | ✅    | ✅          | ✅          | ✅✅             |
| **Bảo vệ Column** | ❌    | ✅          | ✅          | ✅              |
| **Hiệu năng**     | Tốt  | Trung bình | Tốt        | Trung bình     |
| **Chi phí**       | Thấp | Cao        | Trung bình | Cao            |
| **Dễ implement**  | Dễ   | Khó        | Vừa phải   | Khó            |
| **Mức kiểm soát** | 70%  | 90%        | 85%        | 98%            |
| **Khuyến nghị**   | MVP  | Enterprise | Scale      | Enterprise     |

---

## 🎭 DANH MỤC IV: DYNAMIC DATA MASKING (Che Giấu Dữ Liệu)

### 4.1 Server-Side DDM (Database Level)

#### ✅ Ưu Điểm

- **Transparency**: Transparent với application layer
- **Consistent**: Đảm bảo tất cả người dùng nhìn thấy dữ liệu đã masked

#### ❌ Nhược Điểm

- **Performance**: Tạo overhead đáng kể (20-40% latency tăng)
- **Limited**: Không thể áp dụng quy tắc phức tạp dựa trên ngữ cảnh
- **Maintenance**: Khó update masking rules mà không reset connection

---

### 4.2 Application-Level DDM (API Gateway)

#### ✅ Ưu Điểm

- **Linh hoạt**: Dễ dàng custom logic tùy theo vai trò/context
- **Hiệu năng**: Không ảnh hưởng đến database query
- **Versioning**: Có thể version masking rules cùng với API

#### ❌ Nhược Điểm

- **Dễ bypass**: Nếu không implement đúng, có thể bỏ sót trường
- **Phức tạp**: Phải maintain masking logic song song với business logic
- **Tính toàn vẹn**: Khó đảm bảo dữ liệu đã masked là nhất quán

---

### 4.3 Ví Dụ DDM Implementation

```javascript
// Application-level masking middleware
const maskPayrollData = (role, data) => {
  const masked = { ...data };
  
  if (role === 'hr_support') {
    // Che giấu tiền lương, số tài khoản
    masked.salary = '****REDACTED****';
    masked.bank_account = data.bank_account.slice(-4).padStart(10, '*');
    masked.ssn = data.ssn.slice(-4).padStart(9, '*');
  }
  
  if (role === 'payroll_processor') {
    // Chỉ che giấu số tài khoản
    masked.bank_account = data.bank_account.slice(-4).padStart(10, '*');
  }
  
  if (role === 'payroll_approver') {
    // Không che giấu gì
    return data;
  }
  
  return masked;
};
```

---

## 🛣️ ROADMAP PHÁT TRIỂN: PHASE 1 → PHASE 3

### PHASE 1: MVP

**Mục tiêu**: Core System system chạy được với bảo mật cơ bản

#### Kiến Trúc

```
┌─────────────────────────────────────────┐
│        Frontend (React / Vue)            │
│   (Username/Password + 2FA via TOTP)    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   API Gateway (Kong / APISIX)            │
│   - JWT Token Verification              │
│   - RBAC Check (Coarse-Grained)         │
│   - Rate Limiting                       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   Backend Services (Node / Python)       │
│   - Core System Logic                       │
│   - RBAC-based Permission Check         │
│   - Basic Input Validation              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   PostgreSQL Database                    │
│   - Plain text sensitive data (TMP)     │
│   - Basic indexes                       │
│   - No RLS yet                          │
└─────────────────────────────────────────┘
```

#### Checklist Triển Khai

- [ ] User authentication (Email + Password + TOTP 2FA)
- [ ] JWT token generation &amp; validation
- [ ] RBAC module (5-8 vai trò cơ bản)
- [ ] API Gateway setup (Kong)
- [ ] Logging &amp; Monitoring (ELK / Datadog)
- [ ] Basic audit trail (bảng logs)

#### Timeline

- **Tuần 1-2**: Setup infra, auth system
- **Tuần 3-4**: Core Core System logic
- **Tuần 5-6**: Testing, deployment, documentation
- **Tuần 7-8**: Bug fixes, UAT (optional)

---

### PHASE 2: SCALE

**Mục tiêu**: Tối ưu hóa bảo mật, hỗ trợ multi-tenant, ABAC basics

#### Bổ sung Kiến Trúc

```
┌──────────────────────────────────────────┐
│        Existing from Phase 1              │
└──────────────────────┬───────────────────┘
                       │
      ┌────────────────┼────────────────┐
      │                │                │
┌─────▼─────┐ ┌───────▼──────┐ ┌──────▼──────┐
│   OPA     │ │ LDAP/Active  │ │   KMS      │
│  Engine   │ │   Directory  │ │ (AWS/Vault)│
└───────────┘ └──────────────┘ └────────────┘
      │                │                │
      └────────────────┼────────────────┘
                       │
┌──────────────────────▼───────────────────┐
│   API Gateway (Enhanced)                  │
│   - OPA Policy Evaluation                │
│   - Token Refresh Logic                  │
│   - LDAP Attribute Caching              │
└──────────────────────┬───────────────────┘
                       │
┌──────────────────────▼───────────────────┐
│   Backend Services (Enhanced)             │
│   - RBAC + ABAC hybrid                   │
│   - OPA Policy Enforcement               │
│   - Sensitive Data Encryption            │
│   - Audit Logging v2                     │
└──────────────────────┬───────────────────┘
                       │
┌──────────────────────▼───────────────────┐
│   PostgreSQL (Enhanced)                   │
│   - RLS Policies                         │
│   - Encrypted columns (salary, bank_acc) │
│   - Composite indexes                    │
│   - Connection pooling                   │
└──────────────────────────────────────────┘
```

#### Bổ sung Tính Năng

- [ ] LDAP/AD integration (đồng bộ users, departments, roles)
- [ ] OPA policies (ABAC evaluation)
- [ ] Row-Level Security (multi-tenant isolation)
- [ ] Envelope Encryption (Salary, Bank Account, SSN)
- [ ] Dynamic Data Masking (cho HR support, IT support)
- [ ] API versioning (v1, v2)
- [ ] Advance audit logging (who, what, when, why)

#### Timeline

- **Tuần 1-2**: OPA setup, LDAP integration
- **Tuần 3-4**: RLS policies, encryption
- **Tuần 5-6**: DDM, audit logging
- **Tuần 7-8**: Testing, deployment

---

### PHASE 3: ENTERPRISE

**Mục tiêu**: Compliance (ISO 27001, GDPR), High Availability, Advanced Threat Detection

#### Bổ sung Kiến Trúc

```
┌────────────────────────────────────────────┐
│   Existing from Phase 1 + 2                 │
└────────────────────┬───────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼───┐ ┌──────────▼──────┐ ┌──────▼───┐
│ SIEM  │ │ Compliance Mgmt │ │  HSM    │
│(Splunk│ │   (GRC Tool)    │ │ (Hardware│
│/ELK)  │ │                 │ │ Security) │
└───────┘ └─────────────────┘ └─────────┘
    │                │                │
    └────────────────┼────────────────┘
                     │
┌────────────────────▼────────────────────┐
│   API Gateway Cluster (HA)               │
│   - Threat Detection Rules               │
│   - Rate Limiting per user               │
│   - IP Whitelisting                      │
│   - Device Trust Score                   │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│   Microservices (Event-Driven)           │
│   - Core System Service                      │
│   - Audit Service                        │
│   - Notification Service                 │
│   - Compliance Service                   │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│   PostgreSQL Cluster (HA + Backup)       │
│   - Multi-region replication             │
│   - Encrypted backups (HSM)              │
│   - Version-based key management         │
│   - Compliance audit logs                │
└────────────────────────────────────────┘
```

#### Bổ sung Tính Năng

- [ ] SIEM Integration (Splunk / ELK)
  - Real-time threat detection
  - Anomaly detection (unusual Core System approvals)
  - Security incidents correlation
- [ ] Compliance Management
  - ISO 27001 controls mapping
  - GDPR compliance dashboard
  - Automated compliance reports
- [ ] High Availability
  - Database replication (active-active)
  - Multi-region failover
  - API Gateway load balancing
- [ ] Advanced Encryption
  - HSM integration (CloudHSM / Thales)
  - Key escrow management
- [ ] Threat Detection
  - Impossible Travel detection (user login from 2 countries simultaneously)
  - Brute force detection
  - Privilege escalation detection
  - Unusual data export detection

#### Chi Phí Chi Tiết

| Thành phần                  | Ghi chú                   |
| --------------------------- |-------------------------- |
| SIEM Integration            |Splunk / ELK setup         |
| Compliance Framework        |ISO 27001, GDPR automation |
| HA Database Setup           |Replication, backup        |
| HSM Integration             |CloudHSM or Thales         |
| Threat Detection            |ML-based anomaly           |
| Microservices Refactor      |Event-driven architecture  |
| Testing &amp; Certification |Penetration testing        |
|                             |                           |

---

## 🎯 RECOMMENDATIONS &amp; BEST PRACTICES

### Phương Pháp Triển Khai Được Khuyến Nghị

#### MVP (Phase 1)

```
RBAC (Backend) 
  + JWT (Gateway) 
  + Basic Logging
  = Nhanh, chi phí thấp, phù hợp startup
```

**Tại sao?**

- Thiết kế đơn giản, dễ triển khai
- Không cần external service phức tạp
- Có thể mở rộng sang ABAC sau

---

#### Scale (Phase 2)

```
RBAC (Gateway) 
  + ABAC via OPA (Business Logic) 
  + RLS (Database) 
  + Envelope Encryption
  = Cân bằng bảo mật & hiệu năng
```

**Tại sao?**

- RBAC fast-track người dùng không có quyền
- OPA giải quyết bùng nổ vai trò
- RLS bảo vệ nếu app logic bị bypass
- Encryption bảo vệ DBA lạm dụng

---

#### Enterprise (Phase 3)

```
RBAC + ABAC 
  + RLS + CSFLE + Envelope Encryption
  + SIEM + HSM
  = Bảo vệ tối đa, compliance 99%+
```

**Tại sao?**

- Layers phòng thủ chiều sâu (Defense-in-Depth)
- Compliance automatized
- Threat detection real-time
- Key management enterprise-grade

---

## 🛠️ TECHNOLOGY STACK RECOMMENDATION

### Phase 1 (MVP)

| Component      | Technology                 | Reason                           |
| -------------- | -------------------------- | -------------------------------- |
| Backend        | Node.js / Python (FastAPI) | Nhanh phát triển, eco-system tốt |
| API Gateway    | APISIX                     | Open source, OPA-ready           |
| Database       | PostgreSQL 14+             | RLS native, mã nguồn mở          |
| Authentication | Passport.js + TOTP         | Standard, support TOTP           |
| Logging        | Winston / Structlog        | Simple, JSON structured          |
| Deployment     | Docker + Docker Compose    | Single server first              |

### Phase 2 (Scale)

| Component  | Technology                   | Reason                      |
| ---------- | ---------------------------- | --------------------------- |
| OPA Engine | Open Policy Agent + Styra    | Industry standard           |
| Directory  | OpenLDAP hoặc Okta           | Centralized identity        |
| KMS        | AWS KMS hoặc Hashicorp Vault | Secure key storage          |
| Cache      | Redis                        | Policy cache, session cache |
| Monitoring | Prometheus + Grafana         | Open source, scalable       |
| Deployment | Kubernetes (k3s)             | Microservices ready         |

### Phase 3 (Enterprise)

| Component  | Technology                | Reason                       |
| ---------- | ------------------------- | ---------------------------- |
| SIEM       | Splunk / ELK Stack        | Threat detection, compliance |
| HSM        | AWS CloudHSM / Thales     | Hardware security            |
| Event Bus  | Apache Kafka              | Async event processing       |
| IDP        | Okta / Azure AD           | Enterprise-grade IAM         |
| GRC        | ServiceNow / AuditBoard   | Compliance management        |
| Deployment | Kubernetes (Multi-region) | HA, multi-region             |

---

## 🎬 ACTION ITEMS

### Session 1

- [ ] Xác định target users (max bao nhiêu người sử dụng năm 1)
- [ ] Liệt kê các loại vai trò hiện tại trong doanh nghiệp
- [ ] Định nghĩa use cases chính (Tính lương, Phê duyệt, Xuất report)
- [ ] Setup dev environment (Docker, PostgreSQL local)

### Session 2

- [ ] Thiết kế Database Schema (users, roles, permissions, Core System)
- [ ] Implement authentication (JWT + TOTP)
- [ ] Setup APISIX gateway
- [ ] Implement basic RBAC

### Session 3

- [ ] Core Core System logic (salary calculation, deductions)
- [ ] Basic audit logging

### Session 4

- [ ] Integration testing
- [ ] Performance testing
- [ ] Security audit (manual)
- [ ] Documentation

---

## 🔗 REFERENCES &amp; RESOURCES

### 1. Kiểm Soát Truy Cập &amp; Mô Hình Ủy Quyền (RBAC &amp; ABAC)

- NIST RBAC Specification: [https://csrc.nist.gov/pubs/detail/sp/800-162/final](https://csrc.nist.gov/pubs/detail/sp/800-162/final)
- ABAC Primer (Proofpoint): [https://www.proofpoint.com/us/blog/security-awareness/what-attribute-based-access-control-abac](https://www.proofpoint.com/us/blog/security-awareness/what-attribute-based-access-control-abac)
- Strata — Access Control Fundamentals: [https://www.strata.io/glossary/access-control/](https://www.strata.io/glossary/access-control/)
- Oracle Fusion applications security architecture: [https://www.ateam-oracle.com/oracle-fusion-cloud-implementation-architecture-deep-dive-security-designing-identity-access-data-protection-and-evidence-for-scalable-secure-and-ai-ready-deployments](https://www.ateam-oracle.com/oracle-fusion-cloud-implementation-architecture-deep-dive-security-designing-identity-access-data-protection-and-evidence-for-scalable-secure-and-ai-ready-deployments)
- Rippling — Access Control &amp; Identity Verification: [https://www.rippling.com/glossary/access-control](https://www.rippling.com/glossary/access-control)
- LeiPay — Role-Based Access Control and Visibility: [https://www.leipay.co/features/access-control](https://www.leipay.co/features/access-control)
- SecurEnds — Deep Dive: RBAC vs ABAC: [https://www.securends.com/blog/rbac-vs-abac/](https://www.securends.com/blog/rbac-vs-abac/)
- Oloid — Understanding Access Control Models: [https://www.oloid.com/blog/rbac-vs-abac-the-difference-between-the-two-types-of-access-control](https://www.oloid.com/blog/rbac-vs-abac-the-difference-between-the-two-types-of-access-control)
- Okta — Granting Access: RBAC vs ABAC: [https://www.okta.com/identity-101/role-based-access-control-vs-attribute-based-access-control/](https://www.okta.com/identity-101/role-based-access-control-vs-attribute-based-access-control/)
- Netwrix — Access Control Policy Strategy: [https://netwrix.com/en/resources/blog/rbac-vs-abac-which-one-to-choose/](https://netwrix.com/en/resources/blog/rbac-vs-abac-which-one-to-choose/)
- Oso — Fine-Grained Authorization Trade-offs: [https://www.osohq.com/learn/rbac-vs-abac](https://www.osohq.com/learn/rbac-vs-abac)
- Imperva — Role-Based Access Control Implementation: [https://www.imperva.com/learn/data-security/role-based-access-control-rbac/](https://www.imperva.com/learn/data-security/role-based-access-control-rbac/)

### 2. Phân Quyền API &amp; Công Nghệ Policy-as-Code (OPA &amp; Gateway)

- Open Policy Agent Docs: [https://www.openpolicyagent.org/docs/latest/](https://www.openpolicyagent.org/docs/latest/)
- Kong — API Secure Access Control Integration with OPA: [https://konghq.com/blog/engineering/secure-access-control-with-opa-and-kong](https://konghq.com/blog/engineering/secure-access-control-with-opa-and-kong)
- OneUptime — OPA API Authorization with Rego: [https://oneuptime.com/blog/post/2026-01-28-opa-api-authorization/view](https://oneuptime.com/blog/post/2026-01-28-opa-api-authorization/view)
- Curity — API Authorization using OPA and Kong: [https://curity.io/resources/learn/curity-opa-kong-api/](https://curity.io/resources/learn/curity-opa-kong-api/)
- Auth0 — FGA and API Gateway Best Practices: [https://auth0.com/blog/using-api-gateway-fine-grained-authorization/](https://auth0.com/blog/using-api-gateway-fine-grained-authorization/)
- FusionAuth — Trends in Fine-Grained Authorization (FGA): [https://fusionauth.io/blog/fine-grained-authorization](https://fusionauth.io/blog/fine-grained-authorization)
- Zelarsoft — Envoy and OPA Integration for Microservices: [https://zelarsoft.com/styra-das-opa-and-envoy-integration-give-you-fine-grained-access-control-over-microservice-api-authorization/](https://zelarsoft.com/styra-das-opa-and-envoy-integration-give-you-fine-grained-access-control-over-microservice-api-authorization/)

### 3. Bảo Mật Cấp Cơ Sở Dữ Liệu (Row-Level Security)

- PostgreSQL RLS: [https://www.postgresql.org/docs/current/ddl-rowsecurity.html](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- YugabyteDB — Row-Level Security Concepts: [https://www.yugabyte.com/key-concepts/what-is-row-level-security/](https://www.yugabyte.com/key-concepts/what-is-row-level-security/)
- Propelius — SaaS Tenant Isolation: RLS vs App-Level: [https://propelius.ai/blogs/row-level-security-vs-application-level-multi-tenancy-saas/](https://propelius.ai/blogs/row-level-security-vs-application-level-multi-tenancy-saas/)
- Cockroach Labs — Postgres Row-Level Security Overview: [https://www.cockroachlabs.com/docs/stable/row-level-security](https://www.cockroachlabs.com/docs/stable/row-level-security)
- AWS Big Data — Redshift Dynamic RLS with Session Context: [https://aws.amazon.com/blogs/big-data/implement-row-level-access-control-in-a-multi-tenant-environment-with-amazon-redshift/](https://aws.amazon.com/blogs/big-data/implement-row-level-access-control-in-a-multi-tenant-environment-with-amazon-redshift/)
- Microsoft SQL Server — Best Practices for Row-Level Security: [https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security?view=sql-server-ver17](https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security?view=sql-server-ver17)
- DZone — PostgreSQL Multi-Tenant Isolation with RLS: [https://dzone.com/articles/multi-tenant-data-isolation-row-level-security](https://dzone.com/articles/multi-tenant-data-isolation-row-level-security)

### 4. Mã Hóa Dữ Liệu Tĩnh và Mã Hóa Phong Bì (Envelope Encryption)

- Medium — Data Encryption: In-Transit and At-Rest Controls: [https://medium.com/@cypanrisk/data-encryption-practical-controls-for-encryption-in-transit-and-at-rest-cb6a98a4c24e](https://medium.com/@cypanrisk/data-encryption-practical-controls-for-encryption-in-transit-and-at-rest-cb6a98a4c24e)
- CyberArk — Client-Side Field-Level Encryption (CSFLE): [https://www.cyberark.com/what-is/field-level-encryption/](https://www.cyberark.com/what-is/field-level-encryption/)
- Satori Cyber — Essentials of Field Level Encryption: [https://satoricyber.com/row-level-security/field-level-encryption-the-essentials/](https://satoricyber.com/row-level-security/field-level-encryption-the-essentials/)
- Hyperbots — Employee Data Encryption in HR Operations: [https://www.hyperbots.com/glossary/employee-data-encryption](https://www.hyperbots.com/glossary/employee-data-encryption)
- FileCloud — Protecting Data At Rest vs Data In Transit: [https://www.filecloud.com/blog/data-at-rest-vs-transit/](https://www.filecloud.com/blog/data-at-rest-vs-transit/)
- Alibaba Cloud — Envelope Encryption Flow and KMS: [https://www.alibabacloud.com/help/en/kms/key-management-service/use-cases/use-envelope-encryption](https://www.alibabacloud.com/help/en/kms/key-management-service/use-cases/use-envelope-encryption)
- Google Cloud KMS — Envelope Encryption with DEK &amp; KEK: [https://docs.cloud.google.com/kms/docs/envelope-encryption](https://docs.cloud.google.com/kms/docs/envelope-encryption)
- AWS KMS — Cryptographic Details and Internal Workings: [https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html](https://docs.aws.amazon.com/kms/latest/developerguide/kms-cryptography.html)
- Stack Overflow — Understanding AWS KMS Envelope Encryption: [https://stackoverflow.com/questions/75445235/how-does-envelope-encryption-work-in-aws-kms](https://stackoverflow.com/questions/75445235/how-does-envelope-encryption-work-in-aws-kms)
- Yandex Cloud — Client-Side Envelope Encryption Implementation: [https://yandex.cloud/en/docs/kms/concepts/envelope](https://yandex.cloud/en/docs/kms/concepts/envelope)
- Railway — Database Envelope Encryption Migration Guide: [https://blog.railway.com/p/envelope-encryption](https://blog.railway.com/p/envelope-encryption)
- PostgreSQL Official — The pgcrypto Module Documentation: [https://www.postgresql.org/docs/current/pgcrypto.html](https://www.postgresql.org/docs/current/pgcrypto.html)
- YugabyteDB — Implementing pg_sym_encrypt for Column Encryption: [https://docs.yugabyte.com/stable/secure/column-level-encryption/](https://docs.yugabyte.com/stable/secure/column-level-encryption/)
- Sahaj — Secure pgcrypto and Spring Hibernate Implementation: [https://www.sahaj.ai/a-practical-guide-to-implementing-sensitive-data-encryption-using-postgres-pgcrypto/](https://www.sahaj.ai/a-practical-guide-to-implementing-sensitive-data-encryption-using-postgres-pgcrypto/)
- Stack Overflow — Database Column-Level Encryption in PostgreSQL: [https://stackoverflow.com/questions/34658560/database-column-encryption-postgres](https://stackoverflow.com/questions/34658560/database-column-encryption-postgres)
- Vibhor Kumar — Modern PostgreSQL Column-Level Encryption Model: [https://vibhorkumar.wordpress.com/2026/04/12/column_encrypt-v4-0-a-simpler-safer-model-for-column-level-encryption-in-postgresql/](https://vibhorkumar.wordpress.com/2026/04/12/column_encrypt-v4-0-a-simpler-safer-model-for-column-level-encryption-in-postgresql/)
- AWS DMS — SQL Server to Aurora Postgres Column Encryption Migration: [https://docs.aws.amazon.com/dms/latest/sql-server-to-aurora-postgresql-migration-playbook/chap-sql-server-aurora-pg.security.columnencryption.html](https://docs.aws.amazon.com/dms/latest/sql-server-to-aurora-postgresql-migration-playbook/chap-sql-server-aurora-pg.security.columnencryption.html)

### 5. Che Giấu Dữ Liệu Động Trên Giao Diện (Data Masking)

- AWS — What is Data Masking? Techniques &amp; Approaches: [https://aws.amazon.com/what-is/data-masking/](https://aws.amazon.com/what-is/data-masking/)
- Rapid7 — Fundamentals of Dynamic Data Masking (DDM): [https://www.rapid7.com/fundamentals/data-masking/](https://www.rapid7.com/fundamentals/data-masking/)
- K2View — Challenges of Workday Data Masking: [https://www.k2view.com/blog/workday-data-masking/](https://www.k2view.com/blog/workday-data-masking/)
- Satori Cyber — Data Masking Techniques &amp; Implementation Guide: [https://satoricyber.com/data-masking/data-masking-8-techniques-and-how-to-implement-them-successfully/](https://satoricyber.com/data-masking/data-masking-8-techniques-and-how-to-implement-them-successfully/)
- Boomi Community — Implementing DDM for Sensitive Support Roles: [https://community.boomi.com/s/article/Implementing-Data-Masking](https://community.boomi.com/s/article/Implementing-Data-Masking)
- GoReplay — Data Masking Trends &amp; Substitution in 2025: [https://goreplay.org/blog/data-masking-techniques-20250808133113/](https://goreplay.org/blog/data-masking-techniques-20250808133113/)

### 6. Tuân Thủ Pháp Lý &amp; Tiêu Chuẩn Quốc Tế (GDPR, ISO 27001, Nghị định 13/2023/NĐ-CP)

- GDPR Checklist: [https://gdpr-info.eu/](https://gdpr-info.eu/)
- ISO 27001:2022: [https://www.iso.org/standard/27001](https://www.iso.org/standard/27001)
- BrightPay — GDPR Core System Software Requirements: [https://www.brightpay.ie/pages/gdpr-compliant-software/](https://www.brightpay.ie/pages/gdpr-compliant-software/)
- DD Core System — GDPR Legal Requirements and Secure Communication: [https://ddpayroll.co.uk/security/](https://ddpayroll.co.uk/security/)
- Net Defence — Managing HR and Core System Risks under GDPR: [https://net-defence.com/hr-gdpr-compliance-protecting-employee-data-and-reducing-organisational-risk/](https://net-defence.com/hr-gdpr-compliance-protecting-employee-data-and-reducing-organisational-risk/)
- Globalli — AI-Powered HR and Core System GDPR Checklist: [https://globalli.io/resources/blogs/ai-hr-Core System-compliance-checklist-for-gdpr-requirements](https://globalli.io/resources/blogs/ai-hr-Core System-compliance-checklist-for-gdpr-requirements)
- Littler — Navigating Global Core System Under EU GDPR Regulations: [https://www.littler.com/news-analysis/asap/navigating-global-Core System-under-impending-eu-general-data-protection-regulation](https://www.littler.com/news-analysis/asap/navigating-global-Core System-under-impending-eu-general-data-protection-regulation)
- Employment Hero — UK GDPR Compliance Principles for HR/Core System: [https://employmenthero.com/uk/blog/gdpr-Core System/](https://employmenthero.com/uk/blog/gdpr-Core System/)
- Globalli — ISO 27001 Compliance Guidelines for Core System Operations: [https://globalli.io/resources/blogs/ai-hr-Core System-compliance-checklist-for-iso-27001-requirements](https://globalli.io/resources/blogs/ai-hr-Core System-compliance-checklist-for-iso-27001-requirements)
- HighTable — ISO 27001 Annex A 8.26 Application Security Checklist: [https://hightable.io/iso27001-annex-a-8-26-application-security-requirements/](https://hightable.io/iso27001-annex-a-8-26-application-security-requirements/)
- DataGuard — ISO 27001 Annex A Security Controls: [https://www.dataguard.com/iso-27001/annex-a/](https://www.dataguard.com/iso-27001/annex-a/)
- ISMS.online — Understanding ISO 27001:2022 Control 8.26: [https://www.isms.online/iso-27001/annex-a-2022/8-26-application-security-requirements-2022/](https://www.isms.online/iso-27001/annex-a-2022/8-26-application-security-requirements-2022/)
- BDO — ISAE 3402 and ISO 27001 Control Assurance for Core System: [https://www.bdo.my/en-gb/insights/advisory/thought-leadership/leadership-reflections-on-isae-3402-and-iso-27001-the-Core System-service-provider-perspective](https://www.bdo.my/en-gb/insights/advisory/thought-leadership/leadership-reflections-on-isae-3402-and-iso-27001-the-Core System-service-provider-perspective)
- Konfirmity — Mapping ISO 27001 HR Security Controls: [https://www.konfirmity.com/blog/iso-27001-hr-security-controls](https://www.konfirmity.com/blog/iso-27001-hr-security-controls)
- Luật Việt An — Chi Tiết Nghị Định 13/2023/NĐ-CP Về Bảo Vệ Dữ Liệu Cá Nhân: [https://vietanlaw.com/decree-13-2023-nd-cp-on-protection-of-personal-data/](https://vietanlaw.com/decree-13-2023-nd-cp-on-protection-of-personal-data/)
- Helio Legal — Tóm tắt Nghị định 13/2023/NĐ-CP và Lưu ý Doanh nghiệp: [https://www.heliolegal.com/en/nghi-dinh-so-13-2023-nd-cp-ve-bao-ve-du-lieu-ca-nhan-2/](https://www.heliolegal.com/en/nghi-dinh-so-13-2023-nd-cp-ve-bao-ve-du-lieu-ca-nhan-2/)
- Vietnam Briefing — Vietnam's Personal Data Privacy Law and Compliance: [https://www.vietnam-briefing.com/doing-business-guide/vietnam/company-establishment/vietnam-personal-data-privacy-law](https://www.vietnam-briefing.com/doing-business-guide/vietnam/company-establishment/vietnam-personal-data-privacy-law)
- Cổng Thông tin Điện tử Chính phủ — Văn Bản Nghị Định 13/2023/NĐ-CP: [https://vanban.chinhphu.vn/?pageid=27160&docid=207759](https://vanban.chinhphu.vn/?pageid=27160&docid=207759)
- AusCham — Impact Assessment Requirements under Decree 13: [https://auschamvn.org/advocacy/decree-132023nd-cp-personal-data-protection](https://auschamvn.org/advocacy/decree-132023nd-cp-personal-data-protection)
- Tokio Marine — Decree 13/2023/ND-CP Personal Data Protection Overview: [https://tokiomarine.com.vn/en/decree-no.-13-2023-nd-cp-on-personal-data-protection.html](https://tokiomarine.com.vn/en/decree-no.-13-2023-nd-cp-on-personal-data-protection.html)
- Mercans — Global Core System Data Protection and Enterprise Trust: [https://mercans.com/resources/blogs/protecting-your-peoples-data-advanced-Core System-security-for-the-modern-workplace/](https://mercans.com/resources/blogs/protecting-your-peoples-data-advanced-Core System-security-for-the-modern-workplace/)
- Native Teams — Core Data Protection and Security Best Practices: [https://nativeteams.com/blog/Core System-data-protection-security-tips-2026](https://nativeteams.com/blog/Core System-data-protection-security-tips-2026)
- HR Certification — Best Practices for Securing Sensitive Core System: [https://hrcertification.com/blog/Core System-data-security-best-practices-biid1000300](https://hrcertification.com/blog/Core System-data-security-best-practices-biid1000300)

---

**Document Version**: 1.0 | Last Updated: 2026-07-09