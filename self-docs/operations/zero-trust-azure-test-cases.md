---
id: self-docs/operations/zero-trust-azure-test-cases
canonical_question: 'Technical guide and specification: Zero Trust — bộ test case
  chạy khi có tài khoản Azure'
aliases:
- Zero Trust — bộ test case chạy khi có tài khoản Azure
- Zero Trust Azure Test Cases 160926
entity_type: how_to
domain: self-docs > operations
last_verified: 2026-09-17
---

# Zero Trust — bộ test case chạy khi có tài khoản Azure (160926)

> Artefact của `self-docs/Zero-Trust-Prod-Review-160926.md` (file canonical — thắng nếu mâu thuẫn).
> Nhánh code: `review/zero-trust-160926` (backend `de7d882`, frontend `7d9da87`, devops `ac89c42` + 170926 review độc
> lập, chưa commit — xem canonical mục 13).
> **170926**: thêm P0-5/6/7, TASK-REF, TASK-REF, TASK-REF; sửa TASK-REF (GUID giả) — theo review độc lập mục 13.
> Bối cảnh: môi trường Azure **là prd, hiện trống, được phép dùng để test**. Mọi thứ tạo ra lúc test phải ghi vào
> sổ tài nguyên (mục 2) và dọn theo checklist reset (mục 11) trước go-live.

## 0. Cách dùng

- Mỗi case có **ID**, **Công cụ** (`unit` = go test/vitest không cần Azure · `az` = az CLI + curl/script · `pw` =
  Playwright đăng nhập Entra thật · `bin` = chạy binary backend thật), **Tiền điều kiện**, **Bước**, **Kỳ vọng**.
- Chạy theo thứ tự nhóm: **P0 → AZ → AR → KV → LA → OBO → CI → RESET**. Nhóm sau dựa vào nhóm trước.
- Kết quả ghi vào bảng mục 12 (ngày, người chạy, PASS/FAIL, bằng chứng). Không ghi token, secret, giá trị ID vào file
  này — chỉ ghi "khớp/không khớp" hoặc 8 ký tự đầu TASK-REF.
- **Không dùng tài khoản thật của nhân viên, không thêm ai vào nhóm thật** (`Core System-PRD-SalaryRead`, nhóm công ty
  thật) trong lúc test. Dùng nhóm/tài khoản `-test`.

### Nguyên tắc an toàn khi test trên prd trống

| Luật | Lý do |
|------|-------|
| Tên tài nguyên test có hậu tố `-test`, tag `purpose=zt-test` | Có danh sách chính xác để dọn |
| KEK/khoá ký dùng lúc test **không bao giờ** dùng cho lương thật | Key đã bị thử quyền/tải về; purge protection khiến không xoá hẳn được |
| Log test đi vào bảng/DCR riêng (`PayrollSalaryAccessTest_CL`) | Log Analytics không xoá được như DB |
| DB prd drop/tạo lại trước go-live | Dữ liệu test bọc bằng KEK test |
| Không để client secret trên app registration | Thiết kế là OBO bằng federated credential từ MI — secret là lối tắt tồn tại mãi |

## 1. Quyền cần xin

| Quyền | Phạm vi | Dùng cho nhóm |
|-------|---------|---------------|
| Owner app registration Core System prd (hoặc Application Administrator giới hạn trên app đó) | App registration | AZ, AR, OBO |
| Tạo nhóm bảo mật + quản lý thành viên nhóm test | Entra | AR |
| 2–3 tài khoản test (không phải tài khoản cá nhân) | Entra | AR, OBO |
| Key Vault Administrator (hoặc RBAC Administrator giới hạn) | Resource group prd | KV, OBO |
| Log Analytics Contributor + Monitoring Contributor | Resource group prd | LA |
| Contributor trên VM/Container App prd + gán Managed Identity | Resource group prd | OBO |
| Maintainer trên 3 repo GitLab (biến CI/CD, protected env) | GitLab | CI |

## 2. Sổ tài nguyên test (điền khi tạo — dùng cho checklist reset)

| # | Loại | Tên | Tạo bởi | Ngày | Giữ lại sau go-live? | Đã dọn |
|---|------|-----|---------|------|----------------------|--------|
| 1 | Nhóm Entra | `Core System-PRD-Test-HrAdmin` | | | Không | ☐ |
| 2 | Nhóm Entra | `Core System-PRD-Test-CompanyCTD` | | | Không | ☐ |
| 3 | Nhóm Entra | `Core System-PRD-Test-CompanyAll` | | | Không | ☐ |
| 4 | Nhóm Entra | `Core System-PRD-Test-SalaryRead` | | | Không | ☐ |
| 5 | Tài khoản | `zt-test-1@…`, `zt-test-2@…` | | | Không | ☐ |
| 6 | Key | `Core System-kek-test` | | | Không (disable) | ☐ |
| 7 | Key | `Core System-batch-sign-test` | | | Không (disable) | ☐ |
| 8 | Bảng LA | `PayrollSalaryAccessTest_CL` + DCR test | | | Không | ☐ |
| 9 | Redirect URI | `http://localhost:3000` trên app registration | | | **Không** | ☐ |
| 10 | Role assignment | (ghi từng cái: principal → role → scope) | | | Theo tờ trình | ☐ |
| 11 | Secret vault | (ghi từng secret test) | | | | ☐ |

## 3. Cấu hình local mẫu (KHÔNG commit, không ghi giá trị vào đây)

Backend (`Core System-backend/.env.zt-test`, nằm ngoài git — `.env*` bị cấm stage):

```bash
APP_ENV=dev                # KV/LA chạy local; nhóm OBO dùng APP_ENV=prd trên máy Azure
AZURE_TENANT_ID=
AZURE_CLIENT_ID=           # app registration prd
AKV_VAULT_URL=             # vault prd — ở APP_ENV=dev không bị chốt "-prd"; ở prd bắt buộc có "-prd"
AKV_KEY_NAME=Core System-kek-test
AKV_SIGN_KEY_NAME=Core System-batch-sign-test
AKV_OBO=off                # chỉ hợp lệ APP_ENV=dev
OBO_CACHE_MAX_TTL_SECONDS=  # để trống = mặc định 300s (review 170926, G1) — hạ xuống 30-60s khi chạy TASK-REF để không phải chờ 5 phút
AKV_SECRETS=               # để trống = nạp từ vault
PAYROLL_ENC=
PAYROLL_ENC_REQUIRE_SIGN=1
RBAC_SOURCE_DB=true
RBAC_SOURCE_ENTRA=
RBAC_SOURCE_APP_ROLE=      # bật theo từng case
SCOPE_SOURCE_APP_ROLE=
SALARY_AUTH_AAD_GROUP=
SALARY_AUTH_DB_ROLE=false
SALARY_AUTH_APP_ROLE=
SALARY_READ_GROUP_ID=
AUDIT_SINK=azure_monitor
AUDIT_DCE_ENDPOINT=
AUDIT_DCR_RULE_ID=
AUDIT_STREAM_NAME=Custom-PayrollSalaryAccessTest_CL
AUDIT_FAIL_CLOSED=1
AUDIT_EMP_LIST_MAX=500
AUTO_MIGRATE=false
WD_ADAPTER_URL=
DEV_USER_EMAIL=            # PHẢI trống: test đi qua token Entra thật
```

Frontend: không cần `NEXT_PUBLIC_AZURE_*` — lấy từ `GET /api/v1/public-config` của backend local.

---

## 4. P0 — cổng hồi quy không cần Azure (chạy trước MỖI nhóm)

| ID | Công cụ | Bước | Kỳ vọng |
|----|---------|------|---------|
| P0-1 | unit | `cd Core System-backend && TEST_DATABASE_URL=… go test -p 1 ./...` | pass ≥ 1299, fail = đúng 8 test tiền tồn tại (danh sách ở canonical 12.7), 0 fail mới |
| P0-2 | unit | `cd Core System-frontend && npx vitest run && npx tsc --noEmit && npx eslint .` | vitest ≥ 330/0, tsc 0, eslint 0 lỗi (warning `react-hooks/exhaustive-deps` tiền tồn tại được phép) |
| P0-3 | unit | `scripts/no-hardcoded-ids.sh` + `gitleaks dir` + `gitleaks git` ở cả 3 repo | 0 phát hiện mới ngoài allowlist. **Chạy `gitleaks dir` trên checkout SẠCH** (không có `node_modules`/`.next`/`.env` cục bộ) — quét trên máy dev có 2 thứ đó sẽ ra hàng nghìn báo giả không liên quan tới CI |
| P0-4 | bin | Lặp phép A1 (canonical 11.7) với 3 cờ app role TẮT | GET không role 403+1 sự kiện · POST hỏng 403+0 · GET hr_admin tạm 200+1 · `/me` 4 công ty |
| P0-5 | unit | `npx vitest run lib/__tests__/middleware-csp-nonce.test.ts` (G4, review 170926) | nonce khác nhau mỗi request; `Content-Security-Policy-Report-Only` chứa `'nonce-x' 'strict-dynamic'`; `Content-Security-Policy` (enforced) KHÔNG chứa `script-src` (vẫn report-only theo 13.2) |
| P0-6 | unit | `npx vitest run lib/__tests__/poll-fail-count.test.ts` (G5, review 170926) | 2 poller (`useAttendanceDaily.ts`, `employees/page.tsx`) có `POLL_MAX_CONSECUTIVE_FAILS`, tăng đếm lỗi trong catch, reset về 0 khi thành công |
| P0-7 | unit | `go test ./internal/crypto/... -run 'TestClientForCacheBiChanTranTTL|TestAzureConfigFromEnv_OBOCacheMaxTTLMacDinh'` (G1, review 170926) | entry cache OBO bị chặn trần theo `OBO_CACHE_MAX_TTL_SECONDS` (mặc định 300s), không sống tới hết `exp` thật của token |

## 5. AZ — xác minh cấu hình Azure bằng `az login` (chỉ đọc)

Tiền điều kiện: `az login --tenant <tenant>`; `az account show` đúng tenant.

| ID | Bước | Kỳ vọng |
|----|------|---------|
| TASK-REF | So tenant/client/group ID trong docx với `az ad app show --id <clientId>`, `az ad group show --group …` | Mọi ID trong tài liệu khớp tài nguyên thật; ID nào không khớp → ghi vào canonical, không sửa tay tài liệu |
| TASK-REF | `az ad group list --display-name Core System-` | Có `Core System-PRD-SalaryRead` (đã đổi từ `Core System-SalaryRead`); không có nhóm prd sai chuẩn tên |
| TASK-REF | `az ad app show --id <clientId> --query "{g:groupMembershipClaims, roles:appRoles[].value, scopes:api.oauth2PermissionScopes[].value, redirects:spa.redirectUris}"` | `g = ApplicationGroup` (nhóm gán cho app — chống overage); `scopes` chứa `access_as_user`; redirect prd đúng domain |
| TASK-REF | Sau khi khai app role: `appRoles[].value` | Trùng **từng ký tự** với hợp đồng `internal/middleware/app_roles.go`: `hr_admin cb_staff cb_lead cb_director config_admin salary_read company.all company.Enterprise company.UNI company.CVT company.CTC` (mã công ty = `companies.code` đang hoạt động, chữ HOA). Viết script so tự động: lấy danh sách từ az, so với hằng số grep từ mã |
| TASK-REF | `az ad app federated-credential list --id <appObjectId>` | Đúng 1 credential, issuer/subject trỏ MI prd; không có credential lạ |
| TASK-REF | `az ad app credential list --id <appObjectId>` | **Rỗng** — không client secret/cert |
| TASK-REF | `az role assignment list --scope <vault-id> --include-inherited -o table` | Unwrap trên KEK: chỉ nhóm SalaryRead (người dùng qua OBO), MI **không** có; quyền của MI (ký lô, đọc secret) đúng mức tờ trình; không Contributor/Administrator thừa |
| TASK-REF | `az keyvault show --name … --query "properties.{purge:enablePurgeProtection, rbac:enableRbacAuthorization, soft:softDeleteRetentionInDays}"` | `purge=true`, `rbac=true` |
| TASK-REF | `az keyvault secret list --vault-name …` | Không có `dev-user-email` / secret dev nào (A8) |
| TASK-REF | `az keyvault show --name <vault-stg> --query id` và `az keyvault show --name <vault-prd> --query id` (review 170926, G2 — 4.3a) | Hai resource ID **khác nhau hoàn toàn** (khác subscription/resource-group/tên) — xác nhận vault prd không phải alias/rename của vault stg. Đây là điều kiện bắt buộc để an toàn "chữ ký lô không replay được chéo môi trường" đứng vững, vì `BatchDigest` không tự ràng tenant/env (xem canonical 4.3a) |

## 6. AR — app roles + phạm vi công ty (token Entra thật)

Tiền điều kiện: TASK-REF/TASK-REF PASS. Nhóm test mục 2 gán app role tương ứng. Backend local `.env.zt-test`, frontend
`npm run dev`. Tài khoản test đăng nhập qua Playwright (headed lần đầu để qua MFA, lưu `storageState` vào thư mục
scratchpad — **không** vào repo).

Script lấy claim để ghi bằng chứng: trong Playwright, đọc access token từ `localStorage` (MSAL), decode phần payload,
chỉ in `roles`, `groups` (đếm), `hasgroups`, `aud`, `oid` 8 ký tự.

| ID | Công cụ | Tiền điều kiện | Bước | Kỳ vọng |
|----|---------|----------------|------|---------|
| TASK-REF | pw | `zt-test-1` ∈ Test-HrAdmin + Test-CompanyCTD | Đăng nhập, decode token | `roles` = `["company.Enterprise","hr_admin"]` (thứ tự bất kỳ); `aud` = client id |
| TASK-REF | pw+bin | TASK-REF; 3 cờ app role **tắt**; `zt-test-1` không có dòng `employee_roles` | Gọi `/api/v1/me`, mở `/Core System` | Không có role nghiệp vụ (sàn `employee`) — hành vi cũ, cờ tắt không đổi gì |
| TASK-REF | pw+bin | `RBAC_SOURCE_APP_ROLE=true`, `SCOPE_SOURCE_APP_ROLE=true` | `/api/v1/me` | roles có `hr_admin`; companies = `["Enterprise"]`; log `cấp role … source=approle` |
| TASK-REF | pw+bin | TASK-REF | Mở bảng lương Enterprise; đổi dropdown sang UNI (sửa request bằng tay nếu UI không cho) | Enterprise 200; UNI 403; dropdown chỉ có Enterprise (UI và server cùng nguồn — F-B5-1 đóng) |
| TASK-REF | pw+bin | TASK-REF | Chốt kỳ (route dùng `RequireUnrestrictedScope`) | 403 (không có `company.all`, QĐ2) |
| TASK-REF | pw+bin | Thêm `zt-test-1` vào Test-CompanyAll, đăng nhập lại | `/me`, chốt kỳ | companies = mọi công ty đang hoạt động; chốt kỳ 200 |
| TASK-REF | pw+bin | `zt-test-2` ∈ Test-HrAdmin, **không** nhóm công ty nào; `RBAC_SOURCE_DB=false` | `/me`, bảng lương Enterprise | companies rỗng; 403; log WARN "không mang company.* nào" |
| TASK-REF | pw+bin | TASK-REF nhưng `RBAC_SOURCE_DB=true` + dòng `employee_roles` không scope | bảng lương UNI | 200 — giai đoạn chuyển đổi DB vẫn thắng (có chủ ý); ghi nhận để nhắc bước contract |
| TASK-REF | pw+bin | `zt-test-1` ∈ Test-SalaryRead (gán `salary_read`), `SALARY_AUTH_APP_ROLE=true`, `SALARY_AUTH_AAD_GROUP` tắt | GET dữ liệu lương | 200, sự kiện `gate=approle`; bỏ khỏi nhóm + đăng nhập lại → 403 |
| TASK-REF | pw+bin | Luồng duyệt: `zt-test-1` giữ `cb_lead` + `company.Enterprise` | Duyệt bước cấp 1 bản ghi Enterprise; thử bản ghi UNI; thử bước cấp 2 | Enterprise OK; UNI 403; cấp 2 403 (bản vá 040926 giữ) |
| TASK-REF | pw+bin | Gán app role giá trị sai chuẩn tạm (`company.Enterprise`) | `/me` | Không cấp; log liệt kê trong `Unknown`. Xoá role sai ngay sau case |
| TASK-REF | az+bin | Tài khoản test trong >200 nhóm, app để `groupMembershipClaims=SecurityGroup` **tạm** (chỉ làm nếu TASK-REF cho phép đổi và đổi lại ngay) | Đăng nhập, gọi API | Log ERROR overage nêu `oid` + cách chữa (B6); không cấp quyền nhầm. Có thể **bỏ qua** nếu đã `ApplicationGroup` — test unit `auth_overage_test.go` đã phủ |
| TASK-REF | pw+bin | (review 170926) `zt-test-1` gán ĐỒNG THỜI `company.Enterprise` **và** `company.UNI` (2 role công ty cùng lúc, không phải `company.all`) | `/me`; bảng lương Enterprise; bảng lương UNI | Cả hai đều 200, `companies` trong `/me` = `["Enterprise","UNI"]` — đo đúng kịch bản QĐ1 "phẳng" ghi trong canonical 12.1 ("đo lại trên prd trước khi bật"), trước đó chưa có case nào gán >1 company role cùng lúc |

## 7. KV — Key Vault từ máy local (`AKV_OBO=off`, `az login`)

Tiền điều kiện: KEK `Core System-kek-test`, khoá ký `Core System-batch-sign-test`; tài khoản `az login` có Crypto User trên 2
key và Secrets User trên vault; DB local/dev (không phải DB prd).

| ID | Công cụ | Bước | Kỳ vọng |
|----|---------|------|---------|
| TASK-REF | bin | `go run ./cmd/Core System verify-config` | Mỗi biến S0 báo nguồn `vault`, không in giá trị; cờ in giá trị; không cảnh báo thiếu |
| TASK-REF | bin | Đặt `DB_PASSWORD` trong env **và** trong vault khác nhau | verify-config báo nguồn `env` (env thắng vault — đúng thiết kế gỡ dần) |
| TASK-REF | bin | `go run ./cmd/encrypt-backfill -dry-run -period <kỳ test> -max-groups 1` | Niêm phong + ký thành công, rollback; không lỗi quyền |
| TASK-REF | bin | Chạy thật trên 1 kỳ test, rồi GET dữ liệu lương kỳ đó | Đọc ra đúng bản rõ; sự kiện audit có `BatchIds` + `Kids` |
| TASK-REF | az | Gỡ quyền unwrap của tài khoản (`az role assignment delete`), chờ ~5 phút, GET lại | Lỗi mở bọc → 5xx/403, **không** trả dữ liệu, không lùi về bản rõ. Gán lại quyền sau case |
| TASK-REF | bin | Sửa 1 byte chữ ký lô trong DB test | Từ chối đọc lô (`PAYROLL_ENC_REQUIRE_SIGN=1`) |
| TASK-REF | bin | `APP_ENV=prd` + `AKV_VAULT_URL` không chứa `-prd` | Binary từ chối khởi động (chốt vault khớp môi trường) |
| TASK-REF | bin | `APP_ENV=prd AKV_OBO=off` | Từ chối khởi động: "AKV_OBO=off chỉ được phép khi APP_ENV=dev" |
| TASK-REF | az | Diagnostic setting của vault → workspace; KQL `AzureDiagnostics \| where OperationName == "KeyUnwrap"` | Thấy các lần unwrap của TASK-REF; caller = tài khoản `az login` (đường OBO tắt — mong đợi, OBO kiểm ở mục 8) |

## 8. LA — nhật ký đọc lương lên Log Analytics (C4b)

Tiền điều kiện: bảng `PayrollSalaryAccessTest_CL` (schema 12+ trường theo `internal/auditsink/event.go`), DCE, DCR
stream `Custom-PayrollSalaryAccessTest_CL`; tài khoản `az login` có **Monitoring Metrics Publisher** trên DCR.

| ID | Công cụ | Bước | Kỳ vọng |
|----|---------|------|---------|
| TASK-REF | bin+az | GET dữ liệu lương 1 lần; chờ 5–10 phút; KQL `PayrollSalaryAccessTest_CL \| where TimeGenerated > ago(30m)` | Đúng 1 dòng; `ObjectId`, `TenantId`, `Roles`, `Scope`, `Path`, `Companies`, `Periods`, `EmpCount`, `BatchIds`, `Kids` có giá trị |
| TASK-REF | bin+az | POST/PUT vào route lương | 0 dòng (chỉ ghi GET/HEAD) |
| TASK-REF | bin+az | GET trả > 500 nhân viên | `EmpCodes` rỗng, `EmpCount` đúng, `EmpCodesSha256` có giá trị |
| TASK-REF | bin+az | GET với người bị che (masked) | Có dòng, không bị chặn |
| TASK-REF | bin | Gỡ quyền Publisher trên DCR, `AUDIT_FAIL_CLOSED=1`, GET lương nhiều lần tới khi vượt ngưỡng đệm | 503; GET người bị che vẫn 200; POST vẫn chạy. Gán lại quyền → tự hồi phục, sự kiện đệm được gửi |
| TASK-REF | bin | Như TASK-REF nhưng `AUDIT_FAIL_CLOSED` trống, `APP_ENV=prd` | Từ chối khởi động (`checkAuditInProd`) |
| TASK-REF | bin | GET lương rồi SIGTERM ngay | Sự kiện vẫn lên LA; tắt trong ≤ 10 giây kể cả khi LA không tới được |
| TASK-REF | az | Join `PayrollSalaryAccessTest_CL.BatchIds` với `AzureDiagnostics` KeyUnwrap theo thời gian | Mỗi lần mở lô có cặp tương ứng — chứng minh đối chiếu được §3.7 |

## 9. OBO — trên máy Azure có Managed Identity (`APP_ENV=prd`)

Tiền điều kiện: VM/Container App prd gắn **user-assigned MI** (`AKV_MI_CLIENT_ID`); federated credential của app
registration tin MI đó (TASK-REF); MI **không** có quyền crypto trên KEK (chỉ người dùng qua OBO có); nhóm
Test-SalaryRead có Crypto User trên `Core System-kek-test`. Frontend trỏ backend này.

| ID | Công cụ | Bước | Kỳ vọng |
|----|---------|------|---------|
| TASK-REF | bin | Chạy binary `APP_ENV=prd AKV_OBO=` trên máy **local** | Từ chối khởi động: "OBO cần Managed Identity nhưng không thấy IMDS" |
| TASK-REF | bin | Khởi động trên máy Azure với đủ biến prd | Khởi động thành công; mọi chốt `ValidateStartup` qua; `verify-config` không cảnh báo S0 từ env |
| TASK-REF | pw | `zt-test-1` ∈ Test-SalaryRead đọc lương | 200, dữ liệu đúng |
| TASK-REF | az | KQL vault KeyUnwrap của TASK-REF | Caller = **UPN/oid của `zt-test-1`**, không phải MI — mục tiêu chính của OBO |
| TASK-REF | pw | `zt-test-2` có role đọc ở app nhưng **không** ∈ Test-SalaryRead | App cho qua cổng nhưng Key Vault từ chối unwrap → không trả lương; log rõ lỗi quyền vault |
| TASK-REF | pw | Đăng xuất, dùng lại access token cũ sau khi hết hạn | 401; không unwrap |
| TASK-REF | az | Tạm xoá federated credential | Unwrap lỗi, không lùi về danh tính MI. Khôi phục ngay |
| TASK-REF | bin | `docker inspect` container | `Env` chỉ có biến bootstrap + cờ; **0 bí mật S0** (A5) |
| TASK-REF | pw | Build frontend prd (không `NEXT_PUBLIC_AZURE_*`), đăng nhập | Đăng nhập được (hồi quy 2 lỗi A2: `f36023b`, `e517d28`); bundle không chứa tenant/client id |
| TASK-REF | pw+az | (review 170926, G1) `zt-test-1` ∈ Test-SalaryRead, đọc lương thành công (như TASK-REF) lấy OBO client vào cache; **ngay sau đó** `az ad user update --id <zt-test-1> --account-enabled false` (vô hiệu hoá tài khoản, KHÔNG đợi access token hết hạn); đợi hết `OBO_CACHE_MAX_TTL_SECONDS` (mặc định 300s) rồi GET lương lần nữa bằng CÙNG access token cũ | Lần GET đầu (ngay sau khi vô hiệu hoá, trước khi trần cache hết) vẫn 200 (giới hạn đã biết, chấp nhận — xem 13.1 G1); lần GET sau khi qua trần 300s phải lỗi (401/403 hoặc lỗi OBO), KHÔNG được 200 — xác nhận trần cache buộc xin lại OBO credential và Entra từ chối tài khoản đã tắt. Bật lại tài khoản sau case |

## 10. CI — GitLab

| ID | Bước | Kỳ vọng |
|----|------|---------|
| TASK-REF | MR devops → CI Lint | YAML hợp lệ |
| TASK-REF | Pipeline develop | `security-scan-dev` chạy, `allow_failure`; không echo ID |
| TASK-REF | Tạo biến theo canonical 10.6 (protected, environment-scoped) | `require_vars` qua; thiếu 1 biến → job dừng tên biến đó |
| TASK-REF | Đẩy commit chứa chuỗi giống GUID gán cho biến cấu hình vào nhánh thử — **dùng GUID GIẢ tự sinh** (vd `uuidgen`), KHÔNG dùng ID thật của tenant/app/nhóm/vault để tránh tự kích hoạt báo động sai vào chính hệ thống theo dõi bảo mật thật | `security-scan-prd` **chặn** |
| TASK-REF | Pipeline prd khi chưa đặt `PRD_BRANCH`/`PRD_RUNNER_TAG` | Không tạo job prd nào |
| TASK-REF | Deploy prd | Manual, `resource_group` tuần tự, healthcheck qua; FE `build-prd` nhận `BACKEND_URL` prd |

## 11. RESET — checklist trước go-live (người KHÁC người test kiểm)

| # | Việc | Lệnh kiểm | Xong |
|---|------|-----------|------|
| 1 | Tạo KEK + khoá ký **mới**; disable `-test` | `az keyvault key list` | ☐ |
| 2 | Gỡ mọi role assignment của tài khoản/nhóm test | `az role assignment list --all --query "[?contains(principalName,'test')]"` | ☐ |
| 3 | Gỡ assignment app role của nhóm/tài khoản test; xoá nhóm test | `az rest` GET `servicePrincipals/{id}/appRoleAssignedTo` | ☐ |
| 4 | Gỡ redirect `localhost` | TASK-REF | ☐ |
| 5 | 0 client secret, đúng 1 federated credential | TASK-REF, TASK-REF | ☐ |
| 6 | Xoá secret test trong vault, không `dev-user-email` | TASK-REF | ☐ |
| 7 | DCR/bảng log prd sạch (`PayrollSalaryAccessTest_CL` tách khỏi bảng thật) | `az monitor data-collection rule list` | ☐ |
| 8 | DB prd drop/tạo lại, migration từ đầu | `\dt` + đếm bản ghi lương = 0 | ☐ |
| 9 | Máy prd: không `.env`, không `DEV_USER_EMAIL`, `APP_ENV=prd` | TASK-REF + `verify-config` | ☐ |
| 10 | Vô hiệu tài khoản test | `az ad user update --account-enabled false` | ☐ |
| 11 | Sổ tài nguyên mục 2 mọi dòng "Đã dọn" | — | ☐ |
| 12 | Ghi vào tờ trình: khoảng thời gian dùng prd để test + ngày tạo key thật | — | ☐ |

## 12. Nhật ký chạy

| Ngày | ID | Người chạy | Kết quả | Bằng chứng (không token/secret) | Ghi chú |
|------|----|-----------|---------|---------------------------------|---------|
| | | | | | |
