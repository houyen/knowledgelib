---
id: self-docs/engine/zero-trust-prod-review
canonical_question: 'Technical guide and specification: Zero Trust — cổng vào production'
aliases:
- Zero Trust — cổng vào production
- Zero Trust Prod Review 160926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Zero Trust — cổng vào production (160926)

**File canonical** cho hạng mục "Zero Trust / OBO / mã hoá lương". Phạm vi: chỉ những gì phải đúng **trước khi lên
production** (staging ngoài phạm vi — chốt 16/09).

- Tài liệu gốc: `zero-trust/Core System-ZeroTrust-PheDuyetKyThuat-140926.docx` (Đào Duy Thoại, 14/09/2026).
- Nhánh: `review/zero-trust-160926` — **đã push** cả 3 repo: backend `f8e6ad7` (160926: `de7d882`, sau + G1 170926:
  `f8e6ad7`), frontend `59e49cd` (160926: `7d9da87`, sau + G4/G5 170926: `d01aea3` → `59e49cd`) (nền `origin/develop`),
  devops `ac89c42` (nền `origin/main@7f3e6e2`, chưa đổi 170926). Upstream local vẫn trỏ `develop`/`main` → push sau
  này phải ghi rõ tên nhánh.
- Bộ test case chạy khi có tài khoản Azure: `self-docs/Zero-Trust-Azure-Test-Cases-160926.md`.
- Bản đầy đủ trước khi rút gọn (có các PLAN đã thi hành) chỉ còn bản sao tạm trong scratchpad phiên 160926 — thư mục tạm, có thể mất.

---

## 0. Trạng thái và việc còn lại

**Code: xong** (Nhóm 1, C4(b), Nhóm 3, A1–A3, B4–B7, B5). Mọi thay đổi hành vi mới đều sau cờ mặc định tắt hoặc chỉ
chặn ở `APP_ENV=prd`. Suite backend có DB dev: 1297 pass / 8 fail (8 fail có sẵn trên `origin/develop`, 0 fail mới);
FE vitest 324/0, tsc 0, eslint 0.

**Việc còn lại — không nằm ở code:**

| # | Việc | Ai | Mục |
|---|------|----|-----|
| 1 | 🔴 Xoay mật khẩu 2 tài khoản Workday (G1, G4); thu hồi khoá Power Automate HRIS (G2); xoay `WD_ADAPTER_SECRET` ↔ `SYNC_API_TOKEN` (N1) | Người có quyền Workday/HRIS/adapter | 11.9 |
| 2 | 🔴 Dữ liệu thật trong lịch sử git: A9 (dump backend 51MB), G3 (dump adapter 397MB, `Get_Worker` 75MB) | User — **đang giữ nguyên, phương án sau** | A9, 11.9 |
| 3 | Azure (Nhóm 2): token config "Groups assigned to the application"; khai app role + gán nhóm; AKV prd + MI + federated credential; Log Analytics DCE/DCR/bảng; xoá `DEV_USER_EMAIL` khỏi kho bí mật; đổi tên nhóm `Core System-SalaryRead` → `Core System-PRD-SalaryRead` | IT / người có quyền Azure | 12.6, file test case |
| 4 | GitLab: CI Lint thật, biến CI/CD, protected branch/environment, runner prd | Maintainer GitLab | 10.6, 10.7 |
| 5 | Kiểm đầu-cuối trên Azure theo bộ test case (môi trường prd còn trống, dùng tạm để test rồi reset) | Tôi + user khi có tài khoản | file test case |
| 6 | Bật dần: 3 cờ app role → đo một kỳ lương → tắt nguồn DB | Vận hành | 12.6 |
| 7 | Cutover prd (B1–B6) | Vận hành | 3, Nhóm B |
| 8 | Sửa tờ trình trình CTO — **làm cuối cùng** | Tôi | 4.6, 5.1 |

---

## 2. Đọc hiểu logic — commit Zero Trust của `thoaidd`

### 2.1 Ba mốc

**M1 — danh tính & phân quyền từ Entra (26/08 → 12/09)**

| Commit | Nội dung |
|--------|----------|
| `aad8cc5` | Đóng cửa hậu `Authorization: Bearer dev`. Đường tắt dev chỉ sống khi `APP_ENV=dev`; `DEV_AUTH_TOKEN` là khoá riêng từng instance. |
| `df8128a`, `03b2a52` | Gỡ hai đường tự cấp super-admin; `EnsureSuperAdmins` chỉ tạo bảng, không seed ai. |
| `a273976` | Hai cổng đọc lương chạy song song (`salary_auth.go`). |
| `358e0c3` | Claim `groups` → role code qua bảng `role_entra_groups` (migration `v100`). |
| `1caf2d2` | Hợp nhất role hai nguồn Entra + `employee_roles` (`rbac_source.go`). |
| `8058e7f` | Sàn `employee` tách khỏi công tắc nguồn. |

**M3 — mã hoá kết quả lương (14/09 → 15/09)**

| Commit | Nội dung |
|--------|----------|
| `ac48a04` | Phong bì v2 (`envelope_v2.go`): DEK theo lô, TASK-REF-GCM, AAD ràng vị trí, digest lô, máy chủ chỉ `wrap`. |
| `725932f` | Migration `v101`: `payroll_batch_keys`, cột bản mã, `payroll_batch_seen` append-only (chống rollback). |
| `7a6ce0e` | Nối vào đường ghi/đọc thật: `salaryenc/codec.go`, `azure_signer.go`, `cmd/encrypt-backfill`. |
| `a822b1e` | Chia lô khi vượt trần DEK (`MaxSealsPerDEK = 2^20`). |

**M4 — On-Behalf-Of (12/09 → 14/09)**

| Commit | Nội dung |
|--------|----------|
| `623a6f7` | Danh tính vault thôi đọc `AZURE_CLIENT_ID` (nó là app SSO, khiến MI nhắm nhầm). Chain tự dựng: MI (khi có IMDS) → Azure CLI. `AKV_MI_CLIENT_ID` cho user-assigned MI. |
| `017670a` | Mở bọc DEK dưới danh tính người xem: OBO với assertion từ MI (federated credential — **không client secret**), cache client theo `sha256(userToken)` đến `exp`. |
| `0e21e22`, `1db4d84` | `POST /api/v1/Core System/crypto-probe/unwrap` — trả TASK-REF của DEK, không trả DEK. |
| FE `3bfc024` | Scope `api://<client>/access_as_user`, gửi access token (ID token không dùng được cho OBO). |

### 2.2 Năm điểm cốt lõi

1. **Xác thực** (`auth.go`): `WithIssuer` + `WithAudience(cfg.ClientID)`, JWKS theo tenant, không phiên phía máy chủ.
2. **Nguồn role, ngữ nghĩa HOẶC** (`rbac_source.go`): `RBAC_SOURCE_ENTRA` ∨ `RBAC_SOURCE_DB` (∨ `RBAC_SOURCE_APP_ROLE`
   từ B5) — "nguồn yếu nhất thắng", trạng thái TẠM.
3. **Cổng đọc lương, cũng HOẶC** (`salary_auth.go`): nhóm AAD ∨ role DB (∨ app role `salary_read` từ B5). Mỗi lượt ghi
   cổng nào cho qua — thước đo để tắt cổng cũ.
4. **Mã hoá**: AAD = `schema|tenant|company|employee|period|field`; tráo bản mã giữa NV/kỳ/trường bị GCM bác. Chỉ ô
   tiền mã hoá; ô khác giữ bản rõ nhưng vẫn nằm trong băm bản ghi. Cột lạ/chưa khai `format` → coi là tiền.
5. **Fail-closed lúc khởi động**: unwrapper hỏng → `log.Fatalf`; `AKV_OBO=off` ngoài dev → từ chối; `PAYROLL_ENC=on`
   mà chưa gắn codec → từ chối ghi bản rõ.

---

## 3. Cổng vào production

### Nhóm A — chặn (phát hiện 16/09)

| # | Vấn đề | Trạng thái |
|---|--------|------------|
| **A1** | Group claim overage: Entra bỏ claim `groups` → mất sạch role Entra + `SalaryRead`, im lặng | Code: B6 báo ERROR nêu `oid` (`8dd053b`). Đóng hẳn: token config "Groups assigned to the application" (Azure) hoặc app roles (B5) |
| **A2** | `RBAC_SOURCE_DB` còn bật → ai `UPDATE` được DB tự cấp `hr_admin`; trái §3.2 | Chưa tắt được: cần B5 bật + đo (12.6). **Tắt trước B5 là mọi người mất dữ liệu (F-B5-1)** |
| **A3** | Không có chốt "vault khớp môi trường" | ✅ `config/required.go` (`1631f43`) |
| **A4** | Định danh literal trong CI và bundle FE | ✅ cổng `no-hardcoded-ids` (`6371bb8`, `970bc8b`), `public-config` (`f765741`, `6e2e5a4`), CI (`ac89c42`) |
| **A5** | Bí mật qua `docker run -e` → phép `docker inspect` của tờ trình trượt | ✅ code `internal/vaultenv` (`dcce461`) + pipeline prd 0 bí mật S0. Cần AKV prd + MI |
| **A6** | Lô không chữ ký vẫn đọc được | ✅ prd bắt buộc `PAYROLL_ENC_REQUIRE_SIGN` + `AKV_SIGN_KEY_NAME` (`1631f43`) |
| **A7** | Kho bí mật hiện là HashiCorp Vault trên runner, không phải AKV như §3.5 | Chốt: prd dùng AKV. Sửa tờ trình (5.1) |
| **A8** | `DEV_USER_EMAIL` còn trong kho bí mật | Việc tay (Azure/Vault). Backend đã từ chối khởi động nếu có ngoài dev |
| **A9** | 🔴 `Core System-backend/database_dev/payroll_prod_20260519_160301.sql` 51MB **track trong git**: 11.951 NV có `basic_salary` thật, 11.925 CCCD, MST, ngày sinh, điện thoại, địa chỉ. Vào từ commit `5b877db`. `git clone` là có bản rõ → vô hiệu M3. Viết lại lịch sử không hoàn tác được, và bản clone đã phát tán vẫn còn → coi là **đã lộ** | **User giữ nguyên, phương án sau.** Ghi nợ công khai ở `scripts/zt-allowlist.txt` |

### Nhóm B — cutover prd, đúng thứ tự

| # | Việc | Ghi chú |
|---|------|---------|
| **B1** | Hạ tầng prd riêng: vault `Core System-kv-prd` (purge protection), KEK + khoá ký, nhóm PRD, MI, pipeline | KEK/khoá ký dùng lúc test **không** dùng cho lương thật |
| **B2** | Gán app role cho nhóm PRD | Quên = mọi người vào prd 0 role |
| **B3** | `cmd/encrypt-backfill` (`-dry-run` trước) trên dữ liệu prd | Bản ghi `employee_id` mồ côi không dựng được AAD → để nguyên **và đếm**; phải = 0 hoặc giải trình |
| **B4** | Xoá sao lưu bản rõ sau khi khôi phục từ sao lưu **mới** đạt; ghi biên bản | §3.3 |
| **B5** | Diễn tập khôi phục có biên bản | §5 |
| **B6** | Chạy lại toàn bộ ma trận kiểm chứng mục 4 tờ trình trên prd; đánh dấu N/A phép "MI backend `getSecret` WD → Forbidden" (theo C1) | §5 M8 |

### Nhóm C — quyết định đã chốt 16/09

| # | Chốt | Rủi ro còn lại phải ghi vào tờ trình |
|---|------|--------------------------------------|
| **C1** | Hợp nhất compute, không tách | Một MI mang `Secrets User` + `wrap` + `sign`; §3.5 "quyền secret theo thành phần" không áp dụng. User-assigned MI không cứu được (mọi tiến trình trên máy xin được token qua IMDS) |
| **C2** | Giữ access token ở `localStorage` | XSS một lần = đọc được lương trong thời hạn token (sau M4 token là chìa mở DEK qua OBO). Bù: CSP, rà `dangerouslySetInnerHTML`, token ngắn hạn, Conditional Access |
| **C3** | App roles (token mang thẳng role code) | Giá trị app role là hợp đồng Entra ↔ code (`app_roles.go`); lệch một ký tự = mất quyền |
| **C4** | **(b)** nhật ký đúng §3.7: Log Analytics, 12 trường, đệm + fail-closed | Đã làm (mục 9). Key Vault gián đoạn vốn đã fail-closed |
| **C5** | KEK chung; phạm vi công ty lấy từ Entra | Key Vault **không** thực thi phạm vi công ty — người trong `SalaryRead` vượt được app là mở được DEK mọi công ty |

### 3.1 Vì sao C3 chọn app roles

| | A1 overage | A2 bỏ nguồn DB | A4 hết GUID | C5 phạm vi từ Entra | Quyền Azure thêm |
|---|---|---|---|---|---|
| Cách 1 — backend gọi Graph, suy từ tên nhóm | Vẫn dính | Có | Có | Có | `Group.Read.All` toàn tenant; tên nhóm thành ranh giới bảo mật |
| **Cách 2 — app roles** | **Hết** | Có | **Hết** | Có | Không |
| Cách 3 — giữ `groups`, bảng ánh xạ vào vault | Hết (nhờ token config) | Có | Không | Phải tự thêm | Không |

Hai điều bắt buộc giữ đúng:

1. Nhóm `Core System-PRD-SalaryRead` **vẫn tồn tại** và là **đúng một nhóm** vừa được gán app role `salary_read`, vừa
   được gán custom role `Core System-KEK-Unwrap` tại phạm vi khoá — hai lớp (app, Key Vault) không bao giờ lệch nhau.
2. Giá trị app role khai trong **một file** (`internal/middleware/app_roles.go`), không rải chuỗi.

### Đã đúng, không cần đụng

`AKV_OBO=off` bị chặn ngoài dev; OBO fail-closed khi thiếu MI; AAD ràng vị trí; digest lô luôn kiểm; `payroll_batch_seen`
append-only; máy chủ chỉ `wrap`+`sign`; bypass `super_admins` đã gỡ.

---

## 4. Giải pháp: không lưu key / server / id trong code

Tờ trình mục 9 liệt kê subscription/tenant/app id, tên vault/khoá/nhóm/MI, resource group, máy chủ. Không cái nào là
bí mật mật mã, nhưng gộp lại là **bản đồ tấn công**, và nằm cứng trong YAML là một lần sửa nhầm prd trỏ sai vault.

### 4.1 Phân ba lớp, mỗi lớp một luật

| Lớp | Là gì | Ví dụ | Luật |
|-----|-------|-------|------|
| **S0 — bí mật** | Lộ là mất | `DB_PASSWORD`, `WD_PASSWORD`, `PAYSLIP_SFTP_PASSWORD`, `INTERNAL_API_TOKEN`, `DEV_AUTH_TOKEN` | Không bao giờ ở git, YAML, image, `.md`, log. Chỉ ở vault; app tự đọc lúc khởi động |
| **S1 — định danh môi trường** | Không bí mật, khác nhau theo môi trường | `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AKV_VAULT_URL`, `AKV_KEY_NAME`, `AKV_SIGN_KEY_NAME`, `SALARY_READ_GROUP_ID`, `BACKEND_URL` | Không hardcode. Biến CI theo environment hoặc vault |
| **S2 — hằng số giao thức** | Giống nhau mọi tenant | `api://AzureADTokenExchange/.default`, URL issuer Entra, `SchemaV2`, `MaxSealsPerDEK` | **Được phép** cứng trong code |

### 4.2 Container prd chỉ nhận định danh + cờ, không bí mật

Container prd nhận S1 + cờ hành vi từ GitLab CI/CD variable (protected, scope `production`); **không một bí mật S0 nào**.
App tự đọc S0 từ đúng vault đó bằng **Managed Identity** (`internal/vaultenv`, "env thắng vault" để gỡ dần). MI là danh
tính của compute, không phải giá trị lưu được — runner bị chiếm cũng không lấy được gì. Đây là cách duy nhất để phép
"`docker inspect` → không có secret" đạt.

Tên secret theo `internal/vaultenv.DefaultMapping`: `db-password`, `db-user`, `db-host`, `db-name`, `wd-adapter-secret`,
`internal-api-token`, `payslip-sftp-host`, `payslip-sftp-user`, `payslip-sftp-password`, `salary-read-group-id`.

### 4.3a Ràng buộc bắt buộc cho B1 (hạ tầng prd) — vault phải tách vật lý

Chữ ký lô (`BatchDigest`, `internal/crypto/envelope_v2.go`) băm `schema|periodID|company|version|kid|...` —
**không có tenant/environment trong nội dung ký**. An toàn "chữ ký stg không verify được ở prd" hoàn toàn dựa vào
việc **vault stg và vault prd là hai tài nguyên Azure vật lý khác nhau** (khoá `Core System-batch-sign` dù trùng tên ở
hai vault là hai vật liệu khoá khác nhau) — chốt `checkVaultMatchesEnv` (`config/required.go`) chỉ kiểm TÊN vault có
đúng hậu tố `-stg`/`-prd`, không kiểm vault có bị tái sử dụng chéo môi trường hay không. **Khi B1 dựng vault prd:
phải là vault MỚI hoàn toàn, không phải đổi tên/alias vault stg cũ.** Không cần sửa code (`envelope_v2.go`/
`azure_signer.go`) — xác nhận lại 170926, xem 13.1.

### 4.3 Chốt fail-closed lúc khởi động — đã làm

`internal/config/required.go` (`ValidateStartup`), áp cho `cmd/Core System`, `cmd/Core System-recalc`, `cmd/encrypt-backfill`:

- `APP_ENV` chỉ nhận `dev|stg|prd`; ngoài dev bắt buộc `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AKV_VAULT_URL`, `AKV_KEY_NAME`.
- Vault phải khớp môi trường (`-stg` / `-prd` trong tên).
- prd: bắt buộc ký lô; `AUDIT_SINK=azure_monitor` + DCE/DCR/stream + `AUDIT_FAIL_CLOSED=1`; `SALARY_AUTH_DB_ROLE` tắt
  **tường minh** (B7 — `envBool` coi rỗng và gõ sai là BẬT).

### 4.4 Frontend — đã làm

Bỏ `NEXT_PUBLIC_AZURE_*`: FE gọi `GET /api/v1/public-config` (không auth) lấy `tenantId`/`clientId` rồi mới dựng MSAL;
lỗi thì lùi về biến build-time. Một image chạy được nhiều môi trường. CSP: 4 directive chặn thật (`base-uri`,
`form-action`, `object-src 'none'`, `frame-ancestors 'none'`) + chính sách đích ở report-only.

### 4.5 Cổng chặn tái phát — đã làm

- **Lớp 1 — `scripts/no-hardcoded-ids.sh`** (backend + frontend), 5 luật: R1 khoá riêng, R2 URL vault, R3 ID đã biết
  (so bằng TASK-REF), R4 GUID gán cho biến cấu hình, R5 file dump dữ liệu được track. Ngoại lệ ở
  `scripts/zt-allowlist.txt`. Hook pre-commit ở FE; **backend cố ý gitignore `.pre-commit-config.yaml` → cổng thật ở
  backend chỉ có CI**.
- **Lớp 2 — gitleaks v8.30.1** trong CI: báo ở develop, **chặn** ở prd. Allowlist trong `.gitleaks.toml` theo đúng
  file + đúng luật (không dùng `.gitleaksignore` vì fingerprint gãy khi thêm dòng).
- **Lớp 3 — `Core System verify-config`** (B4): in **nguồn** từng biến (vault/env/thiếu) theo lớp S0/S1/cờ, chỉ in giá trị
  cờ, thoát 1 khi trượt cổng, cảnh báo khi prd mà S0 đến từ env. Chạy: `docker exec <container> ./Core System verify-config`.

Giới hạn: gitleaks tìm **bí mật**, không tìm **dữ liệu cá nhân**; R5 chỉ quét HEAD. Chặn dump dữ liệu ở lịch sử và
tương lai cần kiểm kích thước/kiểu tệp ở pre-receive phía GitLab.

### 4.6 Tài liệu trình CTO

- Bản trình thay giá trị bằng `<SUB>`, `<TENANT>`, `<APP_ID>`, `<VM_IP>`; sổ định danh để nơi có kiểm soát truy cập.
- Nếu môi trường prd được dùng tạm để test: ghi khoảng thời gian test + ngày tạo key thật + checklist reset đã chạy.

---

## 5.1 Việc sửa tờ trình — các quyết định làm lệch tài liệu

Làm **cuối cùng**, sau khi mọi mục code/hạ tầng xong.

**C1 (hợp nhất compute) — nghiêm trọng nhất.** Tờ trình viết đúng cho trạng thái *tạm* ("khi chưa tách compute"), nhưng
C1 biến tạm thành vĩnh viễn → chuỗi tự khoá: mục 4 "Quyền secret tối thiểu (sau khi tách compute)" không bao giờ đạt →
M2 không đóng → §5 "mục 4 đạt đầy đủ" → không bao giờ trình được prd. Sửa:

| Chỗ | Sửa thành |
|-----|-----------|
| Mục 4, dòng "Quyền secret tối thiểu" | N/A — quyết định 7.4 = không tách (hoặc gỡ dòng) |
| §3.6 "Thiết kế đích" | Kiến trúc thật: một MI mang `Secrets User` + `wrap` + `sign` |
| §5 M2 | Bỏ vế "Tách compute và danh tính" |
| §6 | Bỏ "(trước M2)" — rủi ro thường trực |
| §7.4 | Đã quyết: không tách |

**C4 = (b) — đã làm cho đúng tài liệu.** §3.7 và 7.8 giữ nguyên nội dung; bổ sung: sự kiện `salary_access` chỉ ghi
GET/HEAD; fail-closed chỉ chặn **đọc** lương và không chặn người bị che; >500 mã NV thì ghi số lượng + TASK-REF; bảng
`audit_logs` trong DB vẫn giữ làm bản tra cứu, bản chính thức là Log Analytics.

**C5 (KEK chung).** §3.4 đã ghi đúng "Key Vault không kiểm bản ghi thuộc ai". Việc thật: (1) §7.7 đánh dấu đã quyết KEK
chung, bỏ "chưa cam kết"; (2) **thêm tiểu mục §3.2 nói phạm vi công ty lấy từ đâu**: app role `company.<MÃ>` /
`company.all` trên Entra; không có `company.*` = không thấy công ty nào; mạnh hơn DB ở lớp ứng dụng, **không** thêm lớp
nào ở Key Vault.

**C2 (`localStorage`).** Thêm vào bảng §6:

| Rủi ro | Giảm thiểu | Còn lại |
|--------|-----------|---------|
| Access token ở `localStorage`, XSS đọc được | CSP, rà `dangerouslySetInnerHTML`, token ngắn hạn, Conditional Access theo thiết bị | Một lỗ XSS = đọc được lương trong thời hạn token, qua đường OBO hợp lệ nên nhật ký Key Vault ghi tên nạn nhân |

**A7.** §3.5 thêm một câu: hiện trạng là HashiCorp Vault trên runner; prd dùng AKV + MI.

---

## 9. C4(b) — nhật ký đọc lương đúng §3.7

**Thiết kế đã chốt:** sự kiện riêng `salary_access` (không nâng `logAuthzAllowed` lên Info — nó chạy cho mọi quyết định
phân quyền, nhân log mà thiếu trường); ≤500 mã NV ghi đủ, vượt thì số lượng + TASK-REF danh sách đã sắp xếp; giữ
`audit_logs` DB; fail-closed chỉ chặn đọc. Đệm nằm trong tiến trình (Logs Ingestion API) chứ không dựa agent — vì
fail-closed đòi ứng dụng **biết** log có đi được không.

### 9.5 Cấu hình

| Biến | Mặc định | Ghi chú |
|------|----------|---------|
| `AUDIT_SINK` | `stdout` | `stdout` \| `azure_monitor` (prd bắt buộc `azure_monitor`) |
| `AUDIT_DCE_ENDPOINT` | — | Data Collection Endpoint |
| `AUDIT_DCR_RULE_ID` | — | immutable id của DCR |
| `AUDIT_STREAM_NAME` | — | vd `Custom-PayrollAccessAudit_CL` |
| `AUDIT_BUFFER_MAX` | `10000` | trần đệm; vượt → không khoẻ |
| `AUDIT_FAIL_CLOSED` | tắt | prd bắt buộc `1` |
| `AUDIT_EMP_LIST_MAX` | `500` | ngưỡng ghi đủ danh sách mã NV |

Hạ tầng cần (Azure): DCE + DCR + bảng custom + `Monitoring Metrics Publisher` cho MI.

### 9.9 Kết quả (16/09, commit `f4d34c0`)

| Phần | File |
|------|------|
| Sự kiện 12 trường, ngưỡng mã NV | `internal/auditsink/event.go`; `auth.go` thêm `TenantIDKey`/`GetTenantID` |
| Gom batch ID/kid theo request | `auditsink/collector.go`; `salaryenc/codec.go` ghi lô **sau** khi mở bọc thành công; `scope.go` ghi phạm vi |
| Phát sự kiện + fail-closed | `middleware/salary_auth.go` — `serveWithSalaryAudit` |
| Đệm có trần, flusher nền, backoff, cảnh báo 80% | `auditsink/sink.go` — `Buffered` (test chạy `-race`) |
| Gửi Log Analytics | `auditsink/azure.go` — azlogs v1.1.0 + MI |
| Chốt prd | `config/required.go` — `checkAuditInProd` |
| Nối vào main | `Setup` trước khi nhận request, `Close` sau `srv.Shutdown` |

Chi tiết hành vi phát sinh khi đọc mã thật:
1. `EvaluateSalaryRead` gắn cho cả nhóm `/Core System` (gồm route ghi) → chỉ GET/HEAD ghi sự kiện và bị fail-closed; WebSocket đi thẳng.
2. Fail-closed không chặn người bị che (họ vốn không thấy số nào).
3. Phân biệt `not_in_salary_read` (app che) và `key_vault_forbidden` (vượt app nhưng Key Vault từ chối — dấu hiệu hai lớp lệch nhau).

Bug thật tìm ra khi viết test: `Buffered.Close` với backend lỗi vĩnh viễn thử lại **mãi mãi** → Log Analytics sập đúng
lúc deploy là tiến trình cũ không tắt được. Sửa: `Close` luôn có hạn chót (10s); test `TestBuffered_CloseKhongHanVanPhaiTraVe`.

Giới hạn: `PAYROLL_ENC=off` (dev) không mở lô nào nên sự kiện không có batch ID / mã NV — kiểm đủ 12 trường phải chạy
trên môi trường bật mã hoá (test case TASK-REF, TASK-REF).

---

## 10. Nhóm 3 — repo `devops`

### 10.1 Phát hiện (`devops@origin/main`, `7f3e6e2`)

| # | Phát hiện | Xử lý |
|---|-----------|-------|
| N1 | 🔴 `WD_ADAPTER_SECRET` thật literal trong `Core System-backend/.gitlab-ci.yml` (64 hex, commit `da14c78`, 07/08). Cổng 5 luật không bắt được → lý do cần gitleaks | Gỡ khỏi YAML. **Phải xoay** cả hai đầu (với `SYNC_API_TOKEN` của adapter) |
| N2 | Không tồn tại pipeline production (chỉ `*-dev` → máy staging tingting) | Dựng pipeline prd mới |
| N3 | 24 `HRIS_*` + `SYNC_SERVICE_URL` là cấu hình chết nhưng vẫn bơm `HRIS_PASSWORD`/`HRIS_KEY_*` vào container | Gỡ |
| N4 | Literal `AZURE_CLIENT_ID` (hardcode đè), `SALARY_READ_GROUP_ID`, `AKV_VAULT_URL`; FE 3 literal + 4 dòng `echo` | → biến CI/CD |
| N5 | `APP_ENV=prod` trên máy staging (vault `kv-stg`) → sau Nhóm 1 sẽ từ chối khởi động | → `stg` (không code nào so chuỗi `"prod"`) |
| N6 | Không có bước quét bảo mật | Thêm |
| — | `PAYSLIP_SFTP_DIR` mặc định trong mã là thư mục **UAT** | prd bắt buộc khai tường minh |

### 10.5 Kết quả (commit `ac89c42`)

- `security-scan-dev` (báo, `allow_failure`) + `security-scan-prd` (chặn) ở cả 2 project; chạy cả `no-hardcoded-ids` lẫn gitleaks rồi mới quyết.
- Develop: `APP_ENV=stg`; literal → biến CI có `require_vars` nêu tên biến thiếu; gỡ HRIS; FE gỡ `echo`.
- Pipeline prd: `security → build (tag CI_COMMIT_SHA) → deploy (manual, resource_group) → healthcheck`; container nhận 0 bí mật S0; `-e TEN` không `=giá trị` để không lọt job log; `DB_SSLMODE=verify-full`; `PAYSLIP_SFTP_DIR(_PRD)` và `RBAC_SOURCE_DB` bắt buộc khai; FE `build-prd` không `NEXT_PUBLIC_AZURE_*` và có `environment: {name: production, action: prepare}` (thiếu cái này thì `BACKEND_URL` staging bị nướng vào ảnh prd).
- Tự kiểm: YAML parse; 16/16 khối script qua `bash -n`; `require_vars` đúng ở bash và sh; anchor quét giả lập 4 tình huống đúng exit.
- **Chưa CI Lint thật trên GitLab.**

### 10.6 Biến CI/CD cần tạo TRƯỚC khi chạy

**Pipeline develop (máy staging tingting)**

| Project | Biến | Scope | Protected | Masked | Ghi chú |
|---------|------|-------|-----------|--------|---------|
| backend | `AZURE_CLIENT_ID` | `*` | không | không | app registration Core System SSO (không phải app HRIS trong Vault) |
| backend | `SALARY_READ_GROUP_ID` | `*` | không | không | object id nhóm SalaryRead staging |
| backend | `AKV_VAULT_URL` | `*` | không | không | vault staging |
| backend | `WD_ADAPTER_SECRET` | `*` | theo nhánh `develop` | **có** | **GIÁ TRỊ MỚI**, trùng `SYNC_API_TOKEN` adapter — xoay cả hai cùng lúc |
| frontend | `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `BACKEND_URL` | `*` | **không** | không | `build-dev` FE chạy trên mọi nhánh — Protected là build feature đỏ |

**Pipeline production**

| Project | Biến | Scope | Protected | Masked | Ghi chú |
|---------|------|-------|-----------|--------|---------|
| cả hai | `PRD_BRANCH`, `PRD_RUNNER_TAG` | **`*`** (không scope `production`) | **có** | không | Nằm trong `rules:`, được đánh giá trước khi biết environment. Chưa đặt → không có job prd nào |
| backend | `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AKV_VAULT_URL` | `production` | có | không | vault phải chứa `-prd` |
| backend | `AUDIT_DCE_ENDPOINT`, `AUDIT_DCR_RULE_ID`, `AUDIT_STREAM_NAME` | `production` | có | không | cần Log Analytics |
| backend | `WD_ADAPTER_URL`, `CORS_ORIGINS`, `DB_PORT` | `production` | có | không | |
| backend | `PAYSLIP_SFTP_DIR`, `PAYSLIP_SFTP_DIR_PRD` | `production` | có | không | ⚠️ mặc định trong mã là UAT |
| backend | `RBAC_SOURCE_DB` | `production` | có | không | `true` tới khi xong 12.6 bước 5 |
| frontend | `PRD_API_URL`, `BACKEND_URL` | `production` | có | không | |

Bí mật prd **không** tạo ở GitLab — tạo trong AKV prd theo tên ở 4.2; MI prd cần `Key Vault Secrets User`.

### 10.7 Việc tay trên GitLab/Azure — checklist

- [ ] Xoay `WD_ADAPTER_SECRET` ↔ `SYNC_API_TOKEN` cùng lúc; tạo biến masked mới.
- [ ] Tạo biến ở 10.6.
- [ ] CI Lint hai file (mở MR devops).
- [ ] Protected branch cho `PRD_BRANCH` + bắt buộc review MR.
- [ ] Protected environment `production` + approver khác người viết (§3.11 — `when: manual` chỉ là nút bấm).
- [ ] Runner prd với tag `PRD_RUNNER_TAG`, chạy trên máy có MI prd.
- [ ] Secret trong AKV prd + role cho MI.
- [ ] Log Analytics: DCE + DCR + bảng + `Monitoring Metrics Publisher` cho MI.
- [ ] Merge 2 repo ứng dụng **cùng đợt** với devops — lệch nhau thì deploy develop từ chối khởi động hoặc bước quét thiếu script.
- [ ] Ký ảnh + pinned digest (§3.11) — chưa có hạ tầng registry/cosign; YAML dừng ở tag SHA.

---

## 11. Kiểm chứng thật và commit

### 11.5 Commit (backend 15, frontend 7, devops 1)

| Repo | Commit |
|------|--------|
| backend | `6371bb8` cổng no-hardcoded-ids · `1631f43` cổng khởi động · `dcce461` vaultenv · `f4d34c0` auditsink · `f765741` public-config + nối `cmd/Core System` · `5c1d1c5` `.gitleaks.toml` · `771ba61` B7 · `8dd053b` B6 · `6a00b94` B4 · `7be856a` `89509bf` `010a06e` `5f0678b` `6b2b1c2` `de7d882` B5 |
| frontend | `970bc8b` cổng + hook · `3b341df` CSP · `6e2e5a4` public-config · `f36023b` `e517d28` sửa 2 lỗi đăng nhập (11.8) · `9ed56e3` `.gitleaks.toml` · `7d9da87` B5 T8 |
| devops | `ac89c42` quét bảo mật + gỡ literal + pipeline prd |

Ràng buộc khi commit (cần biết nếu sửa tiếp):
- Gói nạp vault tên `internal/vaultenv` (không phải `internal/secrets`) vì gitignore toàn cục `*secret*`.
- `loginRequest.scopes` là getter trong `lib/login-request.ts` để không phải sửa `token-manager.ts` (luật không stage `*token*`).
- FE có 3 file `skip-worktree` cố ý (`.claude/settings.json`, `.pre-commit-config.yaml`, `lib/msal.tsx`); commit hook
  pre-commit được dựng từ bản HEAD + 1 hook, không đụng cấu hình cục bộ.
- `scripts/zt-allowlist.txt` so khớp theo trường đầu tiên; `# lý do` tuỳ chọn.

### 11.7 Kết quả A1 — binary backend thật

**Cổng khởi động 6/6 đúng:** `dev` qua; `uat` từ chối; `prod` + vault `kv-stg` (**đúng cấu hình đang chạy trên
tingting**) từ chối; prd thiếu `AKV_SIGN_KEY_NAME` từ chối; prd `AUDIT_SINK=stdout` từ chối; `stg` + vault stg qua.

**Chạy thật trên DB dev** (email tổng hợp `user@company.test`, `AUTO_MIGRATE=false`, không adapter):

| Bước | Kết quả |
|------|---------|
| `/health` | 200 |
| `/api/v1/public-config` | 200, 2 trường; `AZURE_CLIENT_ID` rỗng → 503 |
| GET `/Core System/rows/{kỳ}` không role | 403 + đúng 1 sự kiện |
| POST `/Core System/cell-set` thân hỏng | 403 + 0 sự kiện |
| GET cùng route, role tạm `hr_admin` | 200 + đúng 1 sự kiện, `Scope=unlimited` |
| `SIGTERM` | `Server exited cleanly` ngay |
| Dọn | `employee_roles`=0, `audit_logs`=0 |

Lặp lại sau B5 với 3 cờ app role tắt: **y hệt**.

Phát hiện dẫn tới B7: `SALARY_AUTH_DB_ROLE` mặc định `true` khi không đặt → xoá một dòng cấu hình prd là âm thầm bật lại
cổng đọc lương theo role DB. Đã chặn ở prd (`771ba61`).

Lưu ý khi lặp phép thử trên macOS: không có `timeout` (dùng `perl alarm`); Bash tool chạy zsh không tách từ (chạy trong
`bash` với mảng); sự kiện audit xả mỗi 1 giây (chờ trước khi đếm).

### 11.8 Kết quả A2 — frontend trên trình duyệt thật

Phép thử: backend trả `clientId` app Core System SSO, biến build-time FE để **rỗng** (đúng điều kiện ảnh prd), bấm "Sign in
with Microsoft", đọc `client_id` trên URL `oauth2/v2.0/authorize`.

#### 🔴 Hai lỗi chặn đăng nhập production — do chính Nhóm 1 gây ra, unit test không bắt được

**Lỗi #1 — `lib/auth.tsx` ném lỗi khi thiếu `NEXT_PUBLIC_AZURE_CLIENT_ID`.** Pipeline prd cố ý không truyền biến đó →
mọi lần bấm Đăng nhập ném lỗi. Cùng gốc: `app/(app)/v1/ess/profile/page.tsx`. Sửa: `assertLoginConfigured()` /
`isAzureConfigured()` trong `lib/login-request.ts` đọc cấu hình đang dùng (public-config, lùi build-time). Commit `f36023b`.

**Lỗi #2 — `PublicClientApplication` bị dựng trước khi public-config về → `client_id` rỗng.** Bằng chứng stack:
`react-refresh-runtime … Proxy.get → initInstance(clientId="")`, trước response public-config — Fast Refresh duyệt export,
Proxy `msalInstance` cũ dựng PCA ở lần chạm đầu. Sửa tận gốc: Proxy không bao giờ tự dựng PCA, chỉ `msalReady` dựng;
tách `lib/msal-instance.ts` để test. Commit `e517d28`.

| Lần | Điều kiện | Chuyển hướng Entra | Kết luận |
|-----|-----------|--------------------|----------|
| R1 | `auth.tsx` cũ | không có | ĐỎ — lỗi #1 |
| R2 | sửa #1, Proxy cũ | `client_id` rỗng | ĐỎ — lỗi #2 |
| R2' | sửa cả hai | `client_id` đúng | XANH |
| PROD | `next build` standalone | `client_id` đúng | XANH |

Test hồi quy `lib/login-request.test.ts`, `lib/msal-instance.test.ts` — đưa Proxy về hành vi cũ thì ĐỎ. Bundle prd:
**0 file** chứa tenant id, client id, email dev.

#### CSP trên bản build production

0 vi phạm directive đang chặn. Vi phạm report-only — điều kiện trước khi siết:

| Directive | Nguồn | Cần làm |
|-----------|-------|---------|
| `script-src-elem` (29, mọi trang) | inline của Next.js hydrate | **Nonce qua `middleware.ts`** — bật `script-src 'self'` là trắng trang |
| `style-src-elem`, `font-src` | Google Fonts | Thêm 2 origin hoặc tự host font |
| `connect-src` | `ws://…/payslip-sftp/ws` | Thêm `wss:` của origin API; nếu prd tách origin API thì khai origin đó |

Phát hiện phụ (ngoài Zero Trust): khi backend không chạy, client gọi lại liên tục **không backoff** (~100 nghìn lượt/4
phút) — API sập thật thì mỗi tab dội liên tục. Chưa xử lý.

### 11.9 Kết quả A3 — gitleaks v8.30.1

HEAD: backend 1 báo giả (`auth_test.go`), frontend 68 báo giả (tên cột template) → allowlist `.gitleaks.toml` đúng
file + luật, đã đối chứng không thành lỗ (khoá AWS cài vào file được miễn vẫn bị bắt). devops 0.

**Phải xử lý (ngoài code, cần người có quyền):**

| # | Phát hiện | Việc | Mức |
|---|-----------|------|-----|
| G1 | Credential Workday `user:mật-khẩu` trong `Core System-adapter/reference/workday/ctd_project_distance_api.md` (HEAD) và lịch sử **từ 14/07** — tenant `impl-services1.wd102.myworkday.com` | Xoay mật khẩu; gỡ khỏi file | 🔴 Cao |
| G4 | Credential Workday **thứ hai** trong lịch sử adapter (`scripts/curl-workday-api.txt`, `llmwiki/html/140726-…`, từ 15/07) | Xoay mật khẩu | 🔴 Cao |
| G2 | Khoá Power Automate HRIS literal: lịch sử `devops` (`c05a0b2`, `653e98c`, `d955009`, 20–22/05) và `Core System-backend` `internal/database/database.go` (`eb53934`, 17/08) | Thu hồi / cấp lại | 🔴 Cao |
| N1 | `WD_ADAPTER_SECRET` trong lịch sử `devops` | Xoay (10.7) | 🔴 Cao |
| G3 | Dump dữ liệu thật trong lịch sử adapter: `payroll_adapter.sql` 397MB (`e46de7e`, 16/07), `reference/workday/Get_Worker` 75MB, báo cáo bảng công/phụ cấp trong `llmwiki/raw/` | Cùng quyết định với A9 — **giữ nguyên, phương án sau** | 🔴 Cao |

### 11.10 Kết quả B4, B6, B7 — `Core System-backend`

| Mục | Commit | Việc | Bằng chứng |
|-----|--------|------|------------|
| **B7** | `771ba61` | prd bắt buộc `SALARY_AUTH_DB_ROLE` ∈ `0\|false\|no\|off`; rỗng hoặc gõ sai (`fasle`) bị từ chối | Test 12 giá trị; bỏ lời gọi → đỏ; binary thật đúng 3 trường hợp |
| **B6** | `8dd053b` | Token có `hasgroups=true` hoặc `_claim_names.groups` → `slog.Error` nêu `oid` + cách chữa. Không đổi quyết định phân quyền | Test qua middleware xác thực thật (JWKS giả + JWT ký RSA); tắt nhánh → đỏ |
| **B4** | `6a00b94` | `Core System verify-config` (4.5 lớp 3) | Giá trị S0/S1 không xuất hiện trong output; binary thật 0 dòng lộ giá trị |

---

## 12. B5 — app roles + phạm vi công ty từ token

### 12.1 Quyết định (chốt 16/09)

| # | Chốt |
|---|------|
| QĐ1 | **Phẳng**: `roles: [hr_admin, cb_staff, company.Enterprise, company.UNI]` → mọi role áp cho mọi công ty được liệt kê. Dữ liệu dev: 0 người có các role với phạm vi công ty khác nhau — **đo lại trên prd trước khi bật** |
| QĐ2 | Không có `company.*` → **không thấy công ty nào**; "tất cả" = `company.all` tường minh; `RequireUnrestrictedScope` (chốt kỳ, tính lương toàn kỳ) đòi `company.all` |
| QĐ3 | Người mang phạm vi công ty từ token **không giới hạn phòng ban** (dev: 0/32 dòng dùng `scope_department_id` — đo lại trên prd) |
| QĐ4 | Giữ trang cấu hình quyền, gắn nhãn "chỉ áp cho nguồn DB — đang chuyển đổi"; gỡ khi tắt nguồn DB |

### 12.2 Hai phát hiện khi khảo sát

**F-B5-1 — Đường role từ Entra đang HỎNG với mọi dữ liệu có phạm vi.** Người có role nhưng không có dòng
`employee_roles` nhận `ResolveCompanyScope` → `unlimited=false, allowed={}` (server không trả công ty nào,
`RequireUnrestrictedScope` 403), trong khi `/me` trả 4 công ty → giao diện cho chọn, server trả rỗng. Không ai thấy vì
nguồn DB đang bật. **Hệ quả: tắt `RBAC_SOURCE_DB` khi chưa bật B5 là mọi người mất dữ liệu.** Đã sửa bởi B5.

**F-B5-2 — Có hai cơ chế phạm vi công ty:** theo người (`employee_roles.scope_company_id`, chặn ở server) và theo role
(`roles.sees_all_companies` + `role_companies`, dropdown qua `/me`). Với token cả hai đọc chung `company.*`.

### 12.4 Thiết kế

**Hợp đồng với Entra — một file `internal/middleware/app_roles.go`:**

| App role value | Ý nghĩa |
|----------------|---------|
| `hr_admin`, `cb_staff`, `cb_lead`, `cb_director`, `config_admin` | role nghiệp vụ, trùng mã role DB. Mã khác (vd `site_admin`) **không** nhận qua token |
| `salary_read` | cổng đọc lương — gán cho đúng nhóm `Core System-<ENV>-SalaryRead` đang được gán quyền unwrap trên Key Vault |
| `company.<MÃ>` | mã chữ HOA 2–10 ký tự, phải là công ty đang hoạt động; lạ → bỏ qua + WARN |
| `company.all` | mọi công ty đang hoạt động, kể cả công ty thêm sau |

Giá trị lạ → bỏ qua, không đoán (`company.Enterprise` sai hợp đồng). Token quyết định **ai giữ role nào ở công ty nào**; **role
được làm gì** (bảng quyền module/action) vẫn ở DB — §3.2 cấm DB làm nguồn *gán* role, không cấm DB chứa *định nghĩa* role.

**Ba cờ, mặc định TẮT:**

| Cờ | Bật thì |
|----|---------|
| `RBAC_SOURCE_APP_ROLE` | role từ claim `roles` là nguồn thứ ba, `bySource="approle"` |
| `SCOPE_SOURCE_APP_ROLE` | phạm vi công ty/phòng ban đọc thêm từ `company.*` |
| `SALARY_AUTH_APP_ROLE` | cổng đọc lương thứ ba `salary_read`, `gate=approle` |

**Ngữ nghĩa trong giai đoạn chuyển đổi (nguồn DB còn bật):** `unlimited = unlimited_DB || company.all`;
`allowed = allowed_DB ∪ company.*`. Mặc định "không có scope = không giới hạn" của DB vẫn thắng — **có chủ ý**, để không
ai mất quyền trước khi đo; chỉ an toàn thật sau bước contract (`RBAC_SOURCE_DB=false`).

Phạm vi token chỉ áp khi email trong context **trùng** người đang xét (luồng duyệt không mượn token người gọi cho actor
khác) và người gọi giữ ít nhất một role được hỏi.

### 12.6 Trình tự bật

1. Merge với 3 cờ **tắt** → không đổi hành vi.
2. Azure: khai app role, gán nhóm — gồm nhóm công ty, `company.all`, `salary_read`.
3. Bật 3 cờ, **nguồn DB vẫn bật** → hợp nhất, không ai mất quyền; log `bySource`/`gate` cho thấy độ phủ. Theo dõi WARN
   "có role nhưng token không mang company.* nào" — mỗi dòng là một người sẽ mất quyền sau contract.
4. Đo: một kỳ lương đầy đủ không còn role/phạm vi/cổng lương nào **chỉ** đến từ DB; đo lại QĐ1/QĐ3 trên dữ liệu prd.
5. Contract: `RBAC_SOURCE_DB=false` → QĐ2 có hiệu lực. Rồi mới thêm chốt prd (ghi chú ở `config/required.go`): bắt buộc
   `RBAC_SOURCE_DB=false` + 3 cờ bật.
6. Gỡ `role_entra_groups` và trang cấu hình quyền (QĐ4).

### 12.5a Lưu ý vận hành — đổi `company.*` không có hiệu lực tức thời

Access token là claim tĩnh, cache phía MSAL client. Đổi/thu hồi app role `company.<MÃ>` ở Entra **không** tự áp
dụng cho phiên đang mở của người dùng — chỉ có hiệu lực từ lần lấy token mới (đăng nhập lại, hoặc token tự nhiên hết
hạn rồi silent-refresh). Khác hành vi cũ của `RBAC_SOURCE_DB` (sửa DB có hiệu lực ngay request kế tiếp — xem case 12
110826). Ops cần biết: thu hồi quyền công ty gấp qua Entra phải đi kèm vô hiệu hoá phiên (revoke refresh token /
Conditional Access sign-out) nếu cần tức thời, không chỉ gỡ app role. Xác nhận lại 170926, xem 13.1.

### 12.7 Kết quả B5

| Repo | Commit | Việc |
|------|--------|------|
| backend | `7be856a` | `app_roles.go` + nguồn role thứ ba `RBAC_SOURCE_APP_ROLE` |
| backend | `89509bf` | `scope_token.go`: `ResolveCompanyScopeCtx`/`ResolveDepartmentScopeCtx`, thay 4 điểm gọi trong `scope.go` |
| backend | `010a06e` | `actorEligible` nhận ctx: giữ role qua DB chỉ khi `RBAC_SOURCE_DB`, qua token chỉ khi actor = người gọi; giữ bản vá 040926 (chỉ role gán trực tiếp) |
| backend | `5f0678b` | `/me` hợp công ty từ token (đóng lệch UI/server) |
| backend | `6b2b1c2` | cổng lương `SALARY_AUTH_APP_ROLE` |
| backend | `de7d882` | chỉ ghi điều kiện trong `required.go`, chưa ép prd |
| frontend | `7d9da87` | nhãn QĐ4 (`lib/rbac-source-notice.ts`) |

**Kiểm chứng:**
- Test đỏ→xanh: F-B5-1 tái hiện ĐỎ khi cờ tắt (token `company.Enterprise` → 403), XANH khi bật (Enterprise 200, UNI 403, chốt kỳ
  không `company.all` 403); luồng duyệt không mượn quyền; sau contract dòng `employee_roles` không còn cấp gì; app roles
  đi qua middleware JWT ký RSA thật.
- Suite backend có DB dev: `origin/develop` 1174/8/1 → sau B5 **1297/8/1**, 0 fail mới.
- Binary thật 3 cờ tắt: y hệt A1.

**Giới hạn:** chưa kiểm đầu-cuối với token Entra thật → test case TASK-REF…TASK-REF.

---

## 13. Review độc lập (170926) — góc nhìn phản biện, trước khi có tài khoản Azure

Mục tiêu: đóng vai người đánh giá khác (không phải người code) soát lại thuật toán/code đã triển khai 160926, tìm gap
chưa được doc ghi, trước khi đi test thật trên Azure.

### 13.1 Phát hiện + xử lý

| # | Vấn đề | Kết luận | Xử lý |
|---|--------|----------|-------|
| **G1** | OBO client cache theo `sha256(userToken)` sống tới đúng `exp` token gốc, không có trần riêng — tài khoản bị vô hiệu hoá giữa phiên vẫn unwrap được tới hết `exp` | **Có thật.** Cửa sổ rủi ro = thời hạn access token (phụ thuộc cấu hình Entra, có thể 60-90 phút) | ✅ Sửa: thêm `OBO_CACHE_MAX_TTL_SECONDS` (mặc định 300s), cap entry cache độc lập với `exp` thật — `internal/crypto/azure_unwrapper.go` (`clientFor`, `AzureConfigFromEnv`). Test `TestClientForCacheBiChanTranTTL`, `TestAzureConfigFromEnv_OBOCacheMaxTTLMacDinh` (`azure_obo_test.go`). Commit backend `f8e6ad7` |
| **G2** | Chữ ký lô (`BatchDigest`) không ràng tenant/environment — nghi cross-env replay | **Không có thật** ở đường đi bình thường — verify luôn qua vault đúng `APP_ENV` đang chạy (`checkVaultMatchesEnv`), khoá vật lý stg/prd khác nhau dù trùng tên. Rủi ro chỉ còn nếu B1 dựng sai (dùng chung vault) | Không sửa code. Ghi ràng buộc vào 4.3a: vault prd phải là tài nguyên MỚI, không alias/đổi tên từ vault stg |
| **G3** | Đổi `company.*` trên Entra không tự có hiệu lực với phiên đang mở (token cache MSAL) | Đúng là hành vi hệ quả thiết kế (token tĩnh), không phải bug | Ghi chú vận hành vào 12.5a — thu hồi gấp cần kèm revoke session, không chỉ gỡ app role |
| **G4** | CSP: `script-src 'self'` chỉ ở report-only, chưa enforce được vì thiếu nonce (biết từ 11.8 nhưng chưa làm) | **Có thật**, đã có sẵn ghi chú trong code (`next.config.js`) tự nhận chưa làm | ✅ Sửa: `middleware.ts` (file có sẵn, dùng để redirect/auth — không tạo mới) sinh nonce per-request, gắn `'nonce-x' 'strict-dynamic'` vào `script-src`; bỏ header CSP tĩnh khỏi `next.config.js`. CSP vẫn để **report-only** thêm 1 đợt quan sát thực tế trước khi enforce (xem 13.2) — tránh lặp bẫy "trang trắng" đã tự ghi trong code cũ. Commit frontend `d01aea3` |
| **G5** | "API storm không backoff" (11.8, ~100k request/4 phút khi backend down) — nghi ngờ điểm cụ thể | Grep tĩnh **không xác định được thủ phạm chính** khớp đúng con số đó (WS reconnect và react-query đã có backoff sẵn). Tìm ra 2 job-poller thiếu backoff (`useAttendanceDaily.ts`, `employees/page.tsx`) — cùng lớp lỗi, không chắc là nguyên nhân chính | ✅ Sửa cả 2 poller: dừng sau 5 lỗi liên tiếp thay vì poll vô thời hạn. **Chưa đóng được nguyên nhân chính của 11.8** — cần đo lại bằng Network tab lúc tái hiện thật (nhiều tab, MSAL silent-renew iframe, hay dev-server HMR) khi có môi trường test. Commit frontend `59e49cd` |

### 13.2 CSP — kế hoạch bật enforce (chưa làm ở đợt này)

`middleware.ts` mới đưa nonce vào CSP nhưng **vẫn giữ report-only** cho `script-src` — chỉ enforce 4 directive cũ
(`base-uri`/`form-action`/`object-src`/`frame-ancestors`, không đổi). Trước khi chuyển `script-src` sang enforce:
quan sát report-only qua mọi route (kể cả `/app/(app)/...` nested layout) xác nhận 0 vi phạm còn lại, rồi mới bật.
Việc BẬT ENFORCE để ở đợt sau (đụng hành vi render mọi trang — rủi ro "trắng trang" nếu nonce sai một layout nào đó,
cần kiểm tay trên nhiều route trước khi chốt).

### 13.3 G5 — còn mở

Sửa 2 poller là vá đúng lớp lỗi đã thấy, nhưng KHÔNG khẳng định đã đóng hiện tượng 100k request/4 phút ở 11.8 —
mục đó cần đo lại bằng Network tab thật khi tái hiện (ứng viên nghi vấn thêm: nhiều tab cùng poll job cộng dồn, MSAL
silent-renew iframe, dev-server WebSocket riêng của Next.js — không phải code nghiệp vụ).

## Phụ lục — lịch sử tài liệu

- **160926**: rà soát (bản 1 cả staging → bản 2 chỉ prd); chốt C1–C5, A7, C3 = app roles; Nhóm 1, C4(b), Nhóm 3, A1–A3,
  B4–B7, B5 code xong; push 3 repo; soạn bộ test case Azure.
- **160926 (rút gọn)**: xoá các PLAN đã thi hành (thứ tự đợt, task list C4(b)/Nhóm 3/A/B/C/B5), mục trạng thái cũ, phân
  tích chi tiết Cách 1/3 của C3; gộp kết quả với phát hiện. Giữ nguyên số mục mà code trỏ tới (4.1, 4.5, 9, 11.7, 11.8,
  12, 12.6) và mã phát hiện (A1–A9, N1, G1–G4, F-B5-1).
- Đính chính giữ lại từ các bản trước: chữ ký lô **có** được verify khi lô có chữ ký, lỗ thật là lô *không* chữ ký vẫn
  được chấp nhận (A6); §3.4 tờ trình **đã** ghi đúng giới hạn Key Vault với KEK chung, mảnh thiếu là nguồn phạm vi công ty.
- **170926**: review độc lập (góc nhìn phản biện, trước khi có tài khoản Azure) — 5 phát hiện G1-G5 (mục 13); code xong
  G1 (trần cache OBO) + G4 (nonce CSP, vẫn report-only) + G5 (2 poller dừng sau lỗi liên tiếp); G2/G3 xác nhận không
  phải bug, chỉ bổ sung ghi chú (4.3a, 12.5a); cập nhật bộ test case Azure theo phát hiện mới. `go test` 1299/8 (0 hồi
  quy, +2 test mới), `vitest` 330/0 (+6 test mới), `tsc`/`eslint` sạch. Việc phụ phát hiện lúc gitleaks scan: fixture
  test `cmd/Core System/verify_config_test.go` (nợ cũ từ B4 160926, giá trị `-SENTINEL-Sx` giả) chưa vào `.gitleaks.toml`
  allowlist — đã thêm, đối chứng riêng (ngoài working tree) xác nhận allowlist chỉ khoanh đúng
  `targetRules=["generic-api-key"]` + đúng path, khoá AWS/API key khác giả lập vẫn bị bắt bình thường. Commit + **đã
  push** cùng nhánh `review/zero-trust-160926`: backend `f8e6ad7` + `7203579` (allowlist); frontend `d01aea3` (G4),
  `59e49cd` (G5).
