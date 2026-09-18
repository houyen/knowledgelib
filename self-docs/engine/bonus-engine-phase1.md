---
id: self-docs/engine/bonus-engine-phase1
canonical_question: 'Technical guide and specification: Bonus Engine Phase 1 — 070926'
aliases:
- Bonus Engine Phase 1 — 070926
- Bonus Engine Phase1 070926
entity_type: architecture_explainer
domain: self-docs > engine
last_verified: 2026-09-17
---

# Bonus Engine Phase 1 — 070926

**Canonical doc** cho công việc "Bonus Engine Phase 1" (TASK-REF,22,23,24,28). Bắt đầu từ yêu cầu user:
đọc 2 file tracker BRD (`Payroll_BRD_Tracker_Item.xlsx`, `checklist.xlsx`) liệt kê 9 task TASK-REF +
TASK-REF..29 về "Công cụ tính Thưởng", phân loại BRD nào đủ dữ liệu để tự động code trước.

## Phạm vi

Sau khảo sát 2 file tracker, 5 BRD có công thức cụ thể + đủ dữ liệu — **Phase 1**:
- **TASK-REF**: Công thức Quỹ thưởng cơ sở (Tết/KPI/Tháng 13)
- **TASK-REF**: Quy tắc tự động loại trừ (thai sản/ốm đau/không lương)
- **TASK-REF**: Tính Lương tháng 13
- **TASK-REF**: Tính Thưởng Tết Âm lịch
- **TASK-REF**: Tính Thưởng đột xuất

**Ngoài phạm vi** (để chờ HR chốt): TASK-REF (KPI %, thiếu tỷ trọng), TASK-REF (tách điều động, cần
align One-Time Payment WD), TASK-REF/TASK-REF (Công trình/VLN, rule linh động không có công thức cứng).
TASK-REF (tổng) chỉ hoàn tất một phần.

## Quyết định đã chốt qua `AskUserQuestion` (070926)

1. **Phạm vi Phase 1** = 5 BRD trên (không thêm TASK-REF dù cơ chế tính khả thi).
2. **Quy tắc loại trừ (TASK-REF): LIÊN TỤC**, không phải "lũy kế" như PRD2 §4.4 gốc ghi — theo ghi
   chú làm rõ thực địa trong TASK-REF tracker. Chỉ loại trừ chuỗi ngày nghỉ liền nhau ≥10 ngày, không
   cộng dồn các chuỗi rời rạc.
3. **Migration DB dev**: xác nhận trước khi apply (đã làm, thêm bảng mới, không sửa bảng cũ).

## Kiến trúc đã chọn (SPEC `## Approaches`, phương án C)

Bảng mới `bonus_periods` + `bonus_calculations` — **độc lập hoàn toàn với `payroll_periods`**
(không bị ảnh hưởng lock kỳ 21-20, chỉ đọc `payroll_records`/`hris_attendance_daily`/`employees`).
Không dùng `FormulaEngine`/`salary_components` (gắn chặt vòng đời với payroll_period, không khớp
"kỳ xét thưởng" tuỳ ý HR chọn). Tái dùng `approval_requests` (entity_type mới `bonus_period`) cho
luồng duyệt — không sửa `ApprovalService.Act`, chỉ thêm 1 case trong `applyFinal` + setter 2 chiều.

## Công thức đã cài (Go, `internal/service/bonus_calc.go`)

- `ratio = (review_days_total - exclusion_days) / review_days_total`
- Lương tháng 13 = `ratio × avg_salary_12_months` (mẫu số động: N=12 nếu đủ, N=số kỳ thực có nếu <12)
- Tết Âm lịch = `ratio × MIN(avg_salary, cap_amount)` — cap cấu hình được theo từng đợt, không hardcode
- Thưởng đột xuất = `ratio × selected_month_salary` (KHÔNG dùng bình quân)
- Loại trừ: dò chuỗi ngày liên tục ≥10 ngày qua `hris_attendance_daily`, lọc `leave_type_ref_1/2/3`
  ∈ {`TS`,`TSN`,`ON`,`OD`,`Ro`} (statistic_code seed `internal/database/database.go`)

## Fact-check quan trọng phát hiện lúc code (khác với báo cáo khảo sát ban đầu)

1. **Mã cột lương thật trong `computed_values` là `GROSS`**, không phải `TONG_THU_NHAP_TRONG_THANG`
   như agent khảo sát ban đầu ghi (paraphrase sai một chữ khoá quan trọng) — xác nhận bằng
   `SELECT jsonb_object_keys(computed_values)` trên DB dev thật trước khi tin. Đã sửa cả code lẫn
   PLAN doc.
2. **`leave_type_ref_1/2/3` có thể NULL dù `leave_day_count>=1`** (dữ liệu cũ chỉ có
   `leave_type_id`/`leave_type_name`, chưa migrate sang cột ref mới) → biểu thức SQL boolean ra
   `NULL` → lỗi Scan "couldn't convert &lt;nil&gt; into type bool". Sửa bằng `COALESCE(...,false)`.
3. **`employees` struct Go không map hết cột bảng thật** (thiếu field so với `employee_type_id` và
   một số cột khác) → `SELECT *` phải dùng `db.Unsafe()`, không thể dùng `GetContext`/`SelectContext`
   trần như các bảng khác.
4. **Chưa có rule duyệt cho entity_type mới** — `ApprovalService.Submit` trả lỗi "no approval rules
   configured for this scope" nếu không seed. Thêm `migrationSeedBonusApprovalRules` (boot-time,
   khuôn giống `migrationSeedInsuranceApprovalRules`): 2 cấp `cb_lead`→`cb_director`, global
   (company/site NULL).
5. **`POST .../calculate` trả `BonusCalculation[]` thô, không join `employee_code`/`employee_name`**
   — chỉ `GET .../calculations` (`ListCalculationsWithEmployee`) mới join. Phát hiện qua Playwright
   click-through thật: FE ban đầu hiển thị UUID thay vì mã NV. Sửa: FE gọi thêm
   `listBonusCalculations` sau `calculateBonusPeriod`.
6. **ag-grid không xoá sạch 1 dòng dữ liệu mock cũ** khi `rowData` chuyển từ dataset giả lập sang
   dataset thật (dòng "006351/Trần Thị B" — xác nhận KHÔNG tồn tại trong DB thật lẫn response API,
   thuần là rendering artifact). Sửa bằng `key={mock|real}` ép `DataGrid` remount khi đổi nguồn.

## Bằng chứng test

- **Unit (không DB)**: `internal/service/bonus_calc_test.go` — 16 case, gồm biên 9/10/11 ngày liên
  tục, 2 chuỗi rời rạc không cộng dồn, cap Tết âm 2 nhánh (kể cả biên `==cap`), đột xuất dùng đúng
  lương tháng chọn không phải bình quân.
- **Integration (DB dev thật, `TEST_DATABASE_URL`)**: `bonus_repo_integration_test.go` (4 test),
  `bonus_service_integration_test.go` (4 test, gồm submit→approve 2 cấp qua approval engine thật)
  — tất cả PASS.
- **Handler**: `bonus_handler_test.go` (3 test, validate input).
- **`go test ./internal/...`**: baseline đo bằng `git stash -u` = 1205 passed/15 failed → sau khi
  code xong = 1213-1214 passed/15 failed (đúng cùng 15 tên test tiền tồn tại, không hồi quy). 1 lần
  đo lệch số fail phụ (16) do flaky sẵn có của `TestReplayCapsAndPITTrenDuLieuThat` (nhiều
  sub-assertion, không phải test mới hỏng).
- **Kiểm tay dev server thật (curl)**: tạo đợt Tết âm cho toàn bộ NV, tính ra số tiền đúng công
  thức với dữ liệu lương thật; **TASK-REF**: khoá 1 `payroll_period` thật rồi vẫn `calculate` bonus
  period thành công (200, không 423) — xác nhận bonus engine độc lập hoàn toàn khỏi lock kỳ 21-20.
- **Kiểm tay Playwright thật (click-through UI)**: script tạm (xoá sau khi kiểm) qua dev-bypass
  (`payroll_authed` cookie + `payroll_user`/`idToken` localStorage, khớp `devLogin()` thật của app) —
  xác nhận nút "Tiếp theo" gọi đúng 3 API thật, bảng kết quả hiện đúng tên/mã NV + số tiền thật,
  không còn dòng mock lẫn vào. Đã dọn 7 `bonus_periods` rác tạo ra lúc kiểm khỏi DB dev sau khi xong.

## Đợt bổ sung 070926-3 — Sửa tay số tiền + "Xóa" = reset về 0

User yêu cầu sau khi Phase 1 đã chạy thật: cho HR **sửa tay** `bonusAmount` 1 dòng, và nút "Xóa"
**KHÔNG xóa dòng** — chỉ đặt số tiền về 0 (giữ nguyên dữ liệu tính toán khác của dòng).

**Quyết định chốt qua `AskUserQuestion`:** khi "Tính lại" (`Calculate`) chạy lại cho cả đợt, dòng đã
sửa tay/xóa **PHẢI giữ nguyên giá trị đã sửa**, không bị công thức ghi đè — chọn "Giữ giá trị đã
sửa tay (Recommended)" thay vì để công thức tính đè lên.

**Cơ chế:** thêm cột `bonus_calculations.is_manual_override` (bool) + `manual_override_by`/`_at`
(migration `v97`, `IF NOT EXISTS`, idempotent). `BonusService.Calculate()` trước khi tính lại,
đọc các dòng cũ có `is_manual_override=true` theo `employee_id`, "đóng băng" (giữ nguyên, bỏ qua
tính toán) — không sửa `computeEmployee`/công thức gốc. API mới `PUT
/bonus-periods/{id}/calculations/{calcId}` (`{bonusAmount: number}`) — dùng chung 1 API cho cả
"Sửa" (amount tùy ý) và "Xóa" (amount=0 cố định); chặn nếu `bonus_period.status` không còn
draft/calculated (không sửa được sau khi đã duyệt). Ghi audit `manual_override`.

**FE:** grid "Kết quả thưởng (dữ liệu thật)" thêm 2 cột icon cuối (`_edit`/`_reset`,
`actionKind`/`actionKind2` = "edit"/"delete"), dùng `window.prompt` (sửa) + `window.confirm` (xóa),
gọi API rồi tải lại `listBonusCalculations` để cập nhật cờ `isManualOverride` (không tự suy đoán ở
FE). Trạng thái hiện thêm `" · Đã sửa tay"` khi cờ bật.

**Test:** `TestIntegrationBonusService_UpdateCalculationAmount_PreservedOnRecalculate` (BE) — sửa
tay → tính lại → vẫn giữ giá trị đã sửa + cờ đúng; set period `approved` → sửa bị chặn lỗi đúng.
Verify tay bằng `curl` trên DB dev thật: sửa lưu đúng, sống sót qua tính lại, reset về 0 đúng, bị
chặn khi đợt đã duyệt. FE `tsc`/`eslint` sạch (3 lỗi tiền tồn tại không liên quan, `payslip-lib.test.ts`).

## Đợt bổ sung 070926-4 — Sửa/Xóa không bấm được, thiết kế lại theo phản hồi user

User báo (kèm ảnh) cả 2 icon "Sửa"/"Xóa" ở đợt 070926-3 không bấm được, và yêu cầu thiết kế lại
thay vì chỉ vá: (1) giữ nguyên vị trí nút Xóa, bấm reset về 0, hỗ trợ chọn nhiều dòng để xóa theo
lô; (2) bỏ hẳn nút Sửa — double-click thẳng vào ô "Số tiền thưởng" để sửa tại chỗ.

**Nghi vấn root cause đã sửa luôn:** `buildPreviewView` tính `actionCol2` (vị trí cột icon thứ 2)
CỨNG bằng `pcols.length - 2`, giả định LUÔN đi kèm `actionCol` (2 cột hành động liền nhau, đúng cho
"Đồng bộ"/"Duyệt Của Tôi"). Khi bỏ nút Sửa (chỉ còn 1 cột hành động "Xóa" ở vị trí cuối), công thức
cũ trỏ NHẦM sang cột áp chót ("Trạng thái") — icon Xóa không render đúng chỗ, cột đúng ("Xóa") lại
render như ô text thường. Sửa: `actionCol2 = rowActions2 ? (rowActions ? pcols.length - 2 :
pcols.length - 1) : -1` — đúng cột cuối khi không có `actionCol` đi kèm.

**Sửa tại chỗ (double-click):** thêm `isBonusAmountEdit`/`bonusCalcId` vào `Cell`, cùng khuôn
`isNameEdit` đã có sẵn (sheet Danh sách cột lương, sửa "Tên") nhưng **commit thẳng** (không mở
dialog xin lý do — số tiền thưởng chưa duyệt, không giống đổi tên cột lương đã sống lâu dài).
`buildPreviewView` gán cờ này cho đúng cột "Số tiền thưởng" khi `scope === sheet:${BONUS_SHEET_ID}`,
dùng `rowIdsSrc` (đã có sẵn trong signature, trước chỉ Bảng công phụ cấp dùng cho diff) mang mảng
`calc.id` song song `bonusRealRows` — gọi `sheet.bonusRealRows?.map(c => c.id)` tại call site chung,
sheet khác không có field này nên vẫn `undefined`, không đổi hành vi. `commitInlineBonusAmountEdit`
parse số, so với giá trị cũ (bỏ qua nếu không đổi), gọi API, tải lại `listBonusCalculations`.

**Xóa theo lô:** cùng `rowIdsSrc` này cấp `view.rowIds` → `rowSelectionIds` → `state.selected` (cơ
chế chọn dòng CHUNG của lưới Excel-clone, Shift/Ctrl+click số dòng ở gutter — vốn đã tồn tại cho
lưới lương, chỉ chưa từng được "cấp nguồn" cho sheet cfgGrid nào trước đây). `resetBonusCalculationAmount`
kiểm nếu dòng đang bấm Xóa nằm trong `state.selected` VÀ tập đó >1 phần tử thì reset TẤT CẢ dòng đã
chọn (vòng lặp tuần tự gọi API, 1 confirm dialog duy nhất), ngược lại chỉ reset đúng dòng vừa bấm —
hành vi cũ (đợt 070926-3) vẫn nguyên vẹn khi không chọn nhiều dòng.

**Verify:** `tsc --noEmit` sạch (3 lỗi tiền tồn tại không liên quan), `eslint` sạch. Chưa kiểm bằng
Playwright/tay trên dev server trong phiên này (không khởi động được trình duyệt) — khuyến nghị
user tự kiểm double-click sửa số + Shift-click nhiều dòng + Xóa theo lô trước khi merge/deploy.
Commit `Core System-frontend@3c608ec`, đã push `feature/bonus-engine-phase1` (0 conflict với `develop_v1`).

## Trạng thái git

Nhánh `feature/bonus-engine-phase1` (cả `Core System-backend`, `Core System-frontend`, tách từ `develop_v1`).
Backend: đã merge `develop_v1` sạch (0 conflict thật), đã **push** (commit `64cb082`, merge
`ead768e..64cb082`). Frontend: commit FE wiring sửa/xóa (`64e0f9e`) + merge `develop_v1` (`8709c54`,
0 conflict), đã **push** (`245958d..8709c54`).

## SPEC/PLAN nguồn

- `llmwiki/wiki/sources/draft/070926-bonus-engine-phase1.md` (SPEC, đã duyệt 070926)
- `llmwiki/wiki/sources/draft/070926-bonus-engine-phase1-PLAN.md` (PLAN, 8 task)
