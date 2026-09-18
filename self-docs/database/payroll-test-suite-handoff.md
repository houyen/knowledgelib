---
id: self-docs/database/payroll-test-suite-handoff
canonical_question: 'Technical guide and specification: Bàn giao: Bộ test 7 phân hệ
  Core System'
aliases:
- 'Bàn giao: Bộ test 7 phân hệ Core System'
- Core System Test Suite Handoff 100826
entity_type: specification
domain: self-docs > database
last_verified: 2026-09-17
---

# Bàn giao: Bộ test 7 phân hệ Core System (100826)

**Mục đích tài liệu:** người đọc tài liệu này có thể không có context gì từ phiên làm việc trước — tài liệu viết đủ để tiếp tục công việc mà không cần hỏi lại người đã làm. Đây là file canonical duy nhất cho hạng mục "bộ test 7 phân hệ Core System" bắt đầu 100826 — cập nhật tiếp vào đây, không tạo file mới cho cùng hạng mục.

**Bối cảnh:**  Tài liệu này bàn giao lại toàn bộ: đã làm gì, ở đâu, cách chạy lại, cái gì cần test tay, cái gì còn thiếu/chờ quyết định.

---

## 1. Tóm tắt 1 phút

Đã thiết kế **74 kịch bản test** cho 7 phân hệ nghiệp vụ của Core System, xuất mỗi phân hệ thành 2 file Excel (Blind che đáp án / Answer có đáp án) để test tay, và tự động hoá được **33 test** trong số đó bằng Playwright (chạy PASS ổn định). Trong lúc làm phát hiện **4 lỗi/lệch hành vi thật** so với tài liệu/giả định cũ (chi tiết ở mục 6).

Không có migration DB, không sửa code nghiệp vụ của `Core System-backend`/`Core System-frontend` (trừ các file test `e2e/*.spec.ts` + `playwright.config.ts`). Toàn bộ thay đổi còn **chưa commit**.

---

## 2. Vị trí file — tra cứu nhanh

| Loại                            | Đường dẫn                               | Số lượng                     |
| ------------------------------- | --------------------------------------- | ---------------------------- |
| Excel test tay (Blind + Answer) | `*-TestCase-{Blind,Answer}-100826.xlsx` | 7 phân hệ × 2 file = 14 file |
| Playwright spec                 | `Core System-frontend/e2e/*.spec.ts`        | 7 file (5 mới + 2 sửa)       |
| Config Playwright               | `Core System-frontend/playwright.config.ts` | 1 file (đã sửa)              |
| Trang tổng kết (HTML)           | `100826-Core System-test-summary.html`      | 1 file                       |
| Wiki draft                      | `100826-Core System-test-summary.md`        | 1 file                       |
| Tài liệu này                    | `Core System-Test-Suite-Handoff-100826.md`  | —                            |

---

## 3. Cách chạy lại từ đầu (máy local, giống máy đã dùng để làm việc này)

### 3.1. Điều kiện cần

- Postgres local đang chạy trên `localhost:5432`, database `payroll_engine`, role `payroll_app_role` (KHÔNG phải Docker — DB đã chuyển sang chạy trực tiếp từ 060826, xem nhật ký `CLAUDE.md`).
- `Core System-backend/.env` đã có `DEV_USER_EMAIL=<email admin thật>` và `PAYROLL_TEMPLATE_ENFORCE=on` (dev local only).

### 3.2. Khởi động backend + frontend

```bash
cd "Core System-backend" && go run ./cmd/Core System          # cổng :8080
cd "Core System-frontend" && npm run dev                    # cổng :3000
```

Đợi cả 2 lên hẳn (backend in ra `Server starting on :8080`, frontend in ra `Ready in Xs`).

### 3.3. Chạy toàn bộ test tự động (trừ RBAC)

```bash
cd Core System-frontend
npx playwright test e2e/Core System-formula.spec.ts e2e/Core System-template.spec.ts \
  e2e/Core System-override.spec.ts e2e/Core System-period-flow.spec.ts \
  e2e/report-template-config.spec.ts e2e/smoke.spec.ts
```

Kỳ vọng: **30/30 PASS** (10+3+5+5+6+1). Mỗi file tự dọn dữ liệu test của nó (xem mục 5), an toàn chạy lại nhiều lần trên DB dev thật.

### 3.4. Chạy test RBAC (khác biệt — đọc kỹ mục 5.5 trước khi chạy)

`Core System-rbac.spec.ts` **không chạy được cùng lúc** với các spec khác — cần backend đang chạy dưới 1 identity KHÔNG phải super-admin. Toàn bộ quy trình bật/tắt đã viết chi tiết trong comment đầu file đó, và lặp lại đầy đủ ở mục 5.5 dưới đây.

---

## 4. Bảng tổng hợp theo phân hệ

| #   | Phân hệ                                                      | Kịch bản Excel | Test Playwright                  | File spec                        | Trạng thái                 |
| --- | ------------------------------------------------------------ | -------------- | -------------------------------- | -------------------------------- | -------------------------- |
| 1   | Formula Engine (tab Công thức)                               | 16             | 10                               | `Core System-formula.spec.ts`        | PASS                       |
| 2   | Core System Template (cấu trúc lương theo cấp bậc)               | 12             | 3                                | `Core System-template.spec.ts`       | PASS                       |
| 3   | Salary Override (phòng ban/nhân viên)                        | 10             | 5                                | `Core System-override.spec.ts`       | PASS                       |
| 4   | Core System Period Flow (Calculate/Finalize/Approve/Reject/Lock) | 8              | 5                                | `Core System-period-flow.spec.ts`    | PASS                       |
| 5   | RBAC                                                         | 10             | 3                                | `Core System-rbac.spec.ts`           | PASS* (quy trình đặc biệt) |
| 6   | Bảng chấm công (Core System-adapter)                             | 10             | 0 (dùng Go test có sẵn, 58 case) | —                                | 58/58 PASS                 |
| 7   | Report Template Config                                       | 8              | 6                                | `report-template-config.spec.ts` | PASS                       |
|     | **Tổng**                                                     | **74**         | **32 + smoke**                   |                                  |                            |

`smoke.spec.ts` (1 test, kiểm tra `/Core System` load được) không thuộc phân hệ nào cụ thể — chạy cùng lô, tính riêng.

---

## 5. Chi tiết từng phân hệ

### 5.1. Formula Engine (`Core System-formula.spec.ts`)

**Đã có từ trước, sửa lại trong phiên này** (không phải viết mới). 3 lỗi hạ tầng đã sửa:

1. **Bỏ phụ thuộc Docker.** Helper `psql()` cũ gọi `docker exec payroll_db psql -U postgres -d Core System` — container `payroll_db` không còn tồn tại (DB đã chuyển local từ 060826). Đã sửa gọi `psql` trực tiếp, đọc `DB_HOST/DB_PORT/DB_USER/DB_NAME` từ biến env giống `Core System-backend/.env`.
2. **Fixture thiếu.** Period "Tháng 06/2026" (`PERIOD_ID = eb960286-...`, hardcode trong file) không tồn tại trên DB local hiện tại (chỉ có tới Tháng 05/2026). Đã tạo lại period này + 3 dòng `attendance_summary` FAKE (copy từ Tháng 03/2026, note `"FAKE — seed test data..."`) cho 3 mã NV mượn (`000061`, `000023`, `000025`) mà file test dùng.
3. **Bug thật, không phải hạ tầng:** từ thay đổi 040826 trong `Core System-backend`, cột `employees.contract_type`/`employees.is_foreigner` được **ưu tiên hơn** `emp_status`/`nationality` khi engine tính lương (`payroll_service.go` hàm `buildInputValues`). Test cũ chỉnh `emp_status='probation'` để giả lập nhánh "Thử việc" — **vô tác dụng** vì NV mượn (`000023`) đã có `contract_type='Chính thức'` thật từ HRIS, cột đó thắng. Đã sửa `beforeAll`/`afterAll` ghi/khôi phục đúng `contract_type`/`is_foreigner`.

**Nguyên nhân flakiness thật (áp dụng cho MỌI spec, không riêng file này):** ban đầu nghi là "dev-mode Next.js nguội" gây timeout 15-30s khi mở `/Core System`. **SAI** — đã đo lại bằng script chẩn đoán riêng: cùng luồng, chờ đủ lâu thì render trong &lt;1s. Nguyên nhân thật là `trace: "retain-on-failure"` trong `playwright.config.ts` — tự nó tạo overhead đủ lớn để chạm timeout trên máy này. Đã đổi `trace: "off"` — kết quả: cùng kịch bản, từ 30s+ timeout xuống 1.7s.

### 5.2. Core System Template (`Core System-template.spec.ts`) — mới viết

3 test, qua UI thật (ribbon tab Công thức → nút "Cấu trúc lương theo cấp bậc"/"Gán cấu trúc cho nhân viên"):

1. Tạo cấu trúc (chỉ 2 cột PHONE_ALLOW+TRANSPORT_ALLOW) + gán cho NV `000025` → cột trong cấu trúc giữ nguyên, cột ngoài (FUEL_ALLOW) về 0, PIT/bảo hiểm bắt buộc KHÔNG bị mask.
2. Gán hàng loạt theo cấp bậc (`level_code` chỉ có đúng 1 NV để giảm rủi ro) → đúng `created`/`updated` khi gán lần 1 và gán đè lần 2.
3. **Universe theo UNION mọi cấu trúc** — điểm dễ hiểu nhầm nhất của tính năng này: 1 NV có thể bị mask cả cột KHÔNG nằm trong cấu trúc của chính NV đó, nếu cột đó xuất hiện ở BẤT KỲ cấu trúc khác đang tồn tại (dù cấu trúc đó không gán cho ai). Test tạo 1 "cấu trúc rỗng" chỉ để mở rộng universe rồi xác nhận đúng hành vi.

Cách ly dữ liệu: mọi cấu trúc test đặt tên tiền tố `E2E_`, xoá theo tiền tố ở `beforeEach`/`afterEach` (không dựa vào biến nhớ trong bộ nhớ — an toàn cả khi 1 lần chạy trước bị crash giữa chừng).

### 5.3. Salary Override (`Core System-override.spec.ts`) — mới viết, API-only

5 test, gọi trực tiếp API (không qua UI) — lý do xem mục 6.1 (UI panel hiện không mở được).

1. Override theo phòng ban áp dụng đúng cho NV thuộc phòng, không rò sang phòng khác.
2. Override theo NHÂN VIÊN thắng override theo phòng ban (cùng priority).
3. Priority cao hơn thắng khi 2 override cùng phạm vi.
4. Xoá override → NV quay lại giá trị mặc định.
5. Sửa ô trực tiếp trên lưới (cell-pin, priority 1000) thắng mọi override khác.

Cách ly: override đánh dấu `note='E2E_TEST_100826'`, dọn theo note ở `beforeEach`/`afterEach`.

### 5.4. Core System Period Flow (`Core System-period-flow.spec.ts`) — mới viết

5 test, chia 2 nhóm:

- **Approve/Reject** (3 test) — dùng CHUNG kỳ Tháng 06/2026 với `Core System-formula.spec.ts` (an toàn vì chỉ đổi `status` của 1 bản ghi, không đổi số liệu); `afterEach` reset status về `draft`.
- **Finalize/Lock** (2 test) — dùng kỳ **cách ly riêng** 2099-01 (tự tạo trong `beforeEach`, tự xoá trong `afterEach` theo tiền tố tên `E2E_`) vì Finalize/Lock chặn sửa CẢ KỲ, không được chạm kỳ dùng chung.

Phát hiện trong lúc viết: `CalculateOne` trả **500** (không phải 400) khi bị chặn vì bản ghi đã Finalize — xem mục 6.2.

### 5.5. RBAC (`Core System-rbac.spec.ts`) — mới viết, quy trình đặc biệt

**Vấn đề kiến trúc phải hiểu trước khi chạy lại file này:** dev-bypass (header `Authorization: Bearer dev`) luôn gắn với **1 email cố định** đọc từ `DEV_USER_EMAIL` trong `.env` lúc backend khởi động — không đổi được theo từng request HTTP. Muốn test "quyền bị chặn thật" cần 1 identity KHÔNG phải super-admin, nên phải đổi `.env` + restart backend.

**Bẫy đã gặp:** `EnsureSuperAdmins` (`Core System-backend/internal/database/database.go`) tự động thêm bất kỳ giá trị `DEV_USER_EMAIL` vào bảng `super_admins` **mỗi lần khởi động** (tính năng tiện cho dev thật — ai đặt email mình vào đó tự thành admin). Nghĩa là chỉ đổi `.env` + restart là KHÔNG ĐỦ — vẫn ra super-admin, phải xoá tay dòng đó sau khi backend đã lên.

**Quy trình đầy đủ** (đã viết trong comment đầu file `Core System-rbac.spec.ts`, chép lại đây cho đủ ý):

```bash
# 1. Backup .env
cd Core System-backend && cp .env .env.e2e-backup

# 2. Đổi DEV_USER_EMAIL
sed -i '' 's/^DEV_USER_EMAIL=.*/DEV_USER_EMAIL=user@company.test/' .env

# 3. Restart backend (tìm PID cũ, kill, chạy lại)
lsof -i :8080 -sTCP:LISTEN -t | xargs kill
go run ./cmd/Core System &

# 4. BẮT BUỘC — xoá dòng auto-seed (thiếu bước này test sẽ xanh giả vì vẫn super-admin)
psql -h localhost -U payroll_app_role -d payroll_engine \
  -c "DELETE FROM super_admins WHERE email='user@company.test'"

# 5. Xác nhận đúng trạng thái trước khi chạy test
curl -s http://localhost:8080/api/v1/me -H "Authorization: Bearer dev"
# phải trả về roles rỗng/ít, KHÔNG phải danh sách 6 role

# 6. Chạy test
cd Core System-frontend && npx playwright test e2e/Core System-rbac.spec.ts

# 7. Dọn + khôi phục
cp Core System-backend/.env.e2e-backup Core System-backend/.env
rm Core System-backend/.env.e2e-backup
lsof -i :8080 -sTCP:LISTEN -t | xargs kill
cd Core System-backend && go run ./cmd/Core System &
psql -h localhost -U payroll_app_role -d payroll_engine <<'SQL'
DELETE FROM employee_roles WHERE employee_id IN (SELECT id FROM employees WHERE employee_code='E2E_RBAC_01' OR email='user@company.test');
DELETE FROM employee_dependents WHERE employee_id IN (SELECT id FROM employees WHERE employee_code='E2E_RBAC_01' OR email='user@company.test');
DELETE FROM employees WHERE employee_code='E2E_RBAC_01' OR email='user@company.test';
DELETE FROM super_admins WHERE email='user@company.test';
SQL
```

`Core System-rbac.spec.ts` có `test.beforeAll` tự kiểm tra `/me` đúng trạng thái trước khi chạy — nếu chưa làm đúng bước 1-4, test sẽ throw lỗi rõ ràng ngay từ đầu (không chạy mù, không xanh giả).

**3 test đã xác nhận PASS trong phiên này** (dùng role thật `employee`/`cb_staff` đã có sẵn cấu hình permission, không cần tạo role mới):

1. Role `employee` đơn thuần bị chặn ở role-gate (403).
2. Thêm role `cb_staff` → view cho phép, delete vẫn bị chặn (permission theo action, không theo cả module).
3. Gỡ role `cb_staff` → quay lại bị chặn ngay (roles đọc live theo request, không cần restart lại).

### 5.6. Bảng chấm công (Core System-adapter) — KHÔNG viết Playwright

Kiểm tra trước khi viết: `Core System-adapter` ở nhánh code hiện tại **không có UI, không có HTTP endpoint** cho báo cáo Bảng chấm công — chỉ có CLI (`adapter report --period --out bangcong.xlsx`, xem `cmd/adapter/main.go`). Ép viết Playwright (công cụ test trình duyệt) cho thứ không có trình duyệt nào chạm tới sẽ không có giá trị thật.

Đã chạy lại bộ Go test có sẵn của package đó thay thế: `cd Core System-adapter && go test ./internal/report/bangcong/...` → **58/58 PASS**. Đây là bài test tự động chính thức cho phân hệ này. 10 kịch bản Excel vẫn hữu ích cho test tay khi có người xuất báo cáo qua CLI thật.

### 5.7. Report Template Config (`report-template-config.spec.ts`) — mới viết, API-only

6 test, qua API (UI có sheet Tạo/Sửa riêng nhưng là lưới bespoke, không phải form chuẩn — API cho kết quả xác thực chắc hơn):

1. Tạo template chọn cột lương thật → chạy ra đúng số khớp `payroll_records` gốc.
2. Mã cột không tồn tại → chạy báo cáo trả 422 (không phải 0 im lặng).
3. Dòng Tổng nhiều mã (`sum`) → ra đúng tổng.
4. Alias trùng mã cột thật — **LƯU vẫn thành công**, chỉ **CHẠY báo cáo mới bị chặn (422)**. Xem mục 6.3 — phát hiện này khác với mô tả ban đầu trong file Excel, đã tự sửa lại Excel cho đúng.
5. Xoá template → không còn trong danh sách, chạy lại bằng id cũ bị từ chối.
6. Chạy báo cáo nhiều lần không đổi dữ liệu `payroll_records` gốc (read-only thật).

---

## 6. Phát hiện quan trọng — cần ai đó quyết định hoặc theo dõi

### 6.1. `SalaryComponentOverridesPanel` không có đường vào từ UI chính (mức độ: nên xử lý)

`Core System-frontend/components-page/tinh-luong/SalaryComponentOverridesPanel.tsx` là UI CRUD cho override phòng ban/nhân viên, chỉ render bên trong `SalaryComponentModal` khi `mode === "edit"`. Đã grep toàn bộ `TinhLuongExcel.tsx`: `state.salaryComponentModal = {mode: "edit", ...}` **không còn được gọi ở đâu cả** — chỉ có `{mode: "add"}` (tạo cột mới). Có thể do 1 lần refactor trước đây (250727, chuyển sang "sửa inline trong panel bên cạnh" cho phần công thức) đã vô tình bỏ luôn đường mở modal edit đầy đủ, kéo theo panel Override "mồ côi".

**Cần quyết định:** khôi phục đường vào (thêm nút "Sửa chi tiết"/"Quản lý override" mở lại `SalaryComponentModal` mode edit), hay chính thức bỏ UI này (tính năng override chỉ dùng qua API/curl từ giờ)? Hiện tại backend + component React đều hoạt động tốt (đã test qua API), chỉ thiếu lối vào từ UI.

### 6.2. Lệch mã lỗi HTTP 400 vs 500 cho cùng loại lỗi nghiệp vụ (mức độ: nhẹ, nên dọn)

Khi 1 bản ghi lương đã `Finalize`:

- `POST /Core System/cell-set/{periodId}` → **400** (`payroll_handler.go`, `writeError(w, http.StatusBadRequest, err.Error())`)
- `POST /Core System/calculate-one/{periodId}` → **500** (cùng file, `CalculateOne` bọc MỌI lỗi service thành `StatusInternalServerError`, không phân loại lỗi nghiệp vụ vs lỗi hạ tầng thật)

Không gây sai số liệu, nhưng nếu FE nào đó xử lý lỗi theo status code (vd "400 = báo user, 500 = báo lỗi hệ thống") sẽ hiển thị sai loại thông báo cho đúng 1 tình huống ("bản ghi đã chốt"). Sửa: đổi `CalculateOne` handler nhận diện lỗi nghiệp vụ và trả 400 giống `CellSet`.

### 6.3. `ReportTemplateConfig` — alias trùng mã thật chặn ở bước CHẠY, không phải bước LƯU (mức độ: đã tự sửa tài liệu, không cần hành động thêm)

File Excel Answer ban đầu tôi viết mô tả "Lưu bị chặn" — SAI so với code thật. Đọc `report_template_service.go`/`report_run_service.go`: `validateReportTemplate` (chạy lúc Lưu) chỉ kiểm cú pháp alias + trùng lặp NỘI BỘ trong chính template, KHÔNG tra cứu component thật (cần dữ liệu DB, để dành cho lúc Chạy). `ReportRunService.Run` mới thực sự chặn (422) khi phát hiện alias trùng `component_code` thật. Đã sửa lại file Excel Answer + Blind cho đúng — không cần làm gì thêm, chỉ nêu ở đây để người kiểm thử tay không bối rối khi thấy Lưu vẫn thành công.

### 6.4. Bảng chấm công không có UI/HTTP (mức độ: quyết định phạm vi sản phẩm)

Xem mục 5.6. Nếu về sau có yêu cầu cho HR tự xuất báo cáo Bảng chấm công qua web (không cần IT chạy CLI), đây là việc **xây mới** (thêm route HTTP + UI), không phải "bổ sung test còn thiếu".

### 6.5. Tháng 2 (28/29 ngày) — hạn chế thiết kế template Excel đã biết trước (mức độ: theo dõi)

Kịch bản TC04 trong file `BangChamCong-TestCase-*` ghi nhận: công thức ẩn/hiện cột ngày trong template gốc chỉ xử lý đúng chênh lệch 0-1 ngày (30 vs 31 ngày); tháng 2 chênh 2-3 ngày so với tháng dài nhất nên có thể lộ thêm 2-3 cột ngày ngoài kỳ ở cuối lưới. Đây là hạn chế đã biết từ trước (không phải phát sinh mới trong phiên này), chưa sửa — cần người phụ trách nghiệp vụ xác nhận có chấp nhận được hay cần chặn riêng cho tháng 2.

---

## 7. Cần test tay cái gì (ưu tiên theo rủi ro)

1. **Toàn bộ UI thật của 4 phân hệ mà test tự động chỉ chạy qua API** (Salary Override, Report Template Config, phần lớn RBAC, phần "Xem tất cả assignment" của Core System Template) — dùng đúng file Excel Blind tương ứng, tự chạy theo "Bước thực hiện", điền "Kết quả thực tế", rồi đối chiếu Answer.
2. **Bảng chấm công** — chưa ai test tay lần nào trong phiên này (không đụng được qua Playwright). Dùng `BangChamCong-TestCase-Blind-100826.xlsx`, chạy CLI thật `adapter report --period ... --out ...`, mở file bằng Excel/LibreOffice để soi công thức.
3. **Kịch bản cần mở Excel/LibreOffice thật để xem công thức bên trong ô** (TC02 Formula Engine — thứ tự tính topological sort; nhiều TC của Bảng chấm công) — Playwright không mở được Excel thật, chỉ gọi API.
4. **Banner/tooltip enforce của Core System Template** ("Cấu hình enforce ĐANG BẬT...") — test tự động không assert nội dung hiển thị, chỉ assert hành vi số liệu.

---

## 8. Còn thiếu / chưa làm (khác với "phát hiện" ở mục 6)

- **Chưa commit gì cả.** Toàn bộ file mới/sửa ở `Core System-frontend/e2e/` + `playroll-frontend/playwright.config.ts` đang ở trạng thái uncommitted trên nhánh `feature_v2` (cả `Core System-backend` và `Core System-frontend`). `git status` xác nhận `Core System-backend` sạch (không đổi code, chỉ đổi DB/config tạm thời và đã khôi phục).
- `**/wikieval**` — bổ sung lớp eval độc lập xác nhận lại các phát hiện ở mục 6, tôi không tự gọi được (skill chặn model-invocation), cần gõ lệnh trực tiếp nếu muốn.
- **Chưa tự động hoá:** các kịch bản đòi hỏi mở file Excel thật bằng ứng dụng desktop (không có headless-Excel trong Playwright), và toàn bộ phân hệ Bảng chấm công (do không có UI/HTTP, xem mục 6.4).
- **CI/CD:** chưa có pipeline nào tự chạy các spec này — hiện chỉ chạy tay qua `npx playwright test`.

---

## 9. Trạng thái môi trường tại thời điểm bàn giao

- `Core System-backend` đang chạy `:8080`, `DEV_USER_EMAIL=user@company.test` (bình thường, không phải trạng thái test RBAC), `PAYROLL_TEMPLATE_ENFORCE=on`.
- `Core System-frontend` đang chạy `:3000` (dev server).
- Postgres local `payroll_engine`: đã xác nhận sạch — 0 dòng còn sót tiền tố `E2E_`/note `E2E_TEST_100826` ở mọi bảng liên quan (`payroll_templates`, `salary_component_overrides`, `payroll_periods`, `report_templates`, `employees`, `super_admins`).
- Cả 2 repo đang ở nhánh `feature_v2`.

