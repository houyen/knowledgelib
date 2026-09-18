---
id: self-docs/engine/formula-force-override-flag
canonical_question: 'Technical guide and specification: Formula Force-Override Flag
  — 030926'
aliases:
- Formula Force-Override Flag — 030926
- Formula Force Override Flag 030926
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Formula Force-Override Flag — 030926

**Canonical duy nhất cho hạng mục này.**

## Bối cảnh

Phát hiện khi test import Excel NV `004335` (`self-docs/Core System-Import-Template-Toolbar-Export-030926.md` + kiểm chứng engine, cùng ngày): file có `PROB_EARNED=150000` nhưng hệ thống từ chối ghi vì `PROB_EARNED` là cột `component_type='formula'` (tự tính từ `[PROB_DAYS]*[BASIC_SAL]*0.85/[STD_DAYS]`), không phải cột nhập liệu. User yêu cầu: (1) coi đây là case đặc biệt — giá trị import phải THẮNG công thức, và (2) đề xuất cơ chế tổng quát cho các trường hợp tương tự trong tương lai.

## Quyết định (chốt qua `AskUserQuestion`, 2026-09-03)

1. **Allowlist theo từng cột** — thêm cột mới `salary_components.allow_force_override` (mặc định `false`), không hardcode 1 mã trong code.
2. **Áp dụng cho CẢ Nhập Excel lẫn sửa 1 ô trên lưới** — đồng thời vá lỗ hổng phát hiện: `writeOverrideCell` (dùng chung `SetCell`+`BulkSetCells`) trước đây KHÔNG kiểm `component_type` ở backend, chỉ frontend chặn không cho mở ô sửa.
3. **4 cột thống kê pháp định** (`PIT`, `SI_EMP`, `HI_EMP`, `UI_EMP`) luôn loại trừ — blocklist thắng allowlist tuyệt đối.
4. **UI bật/tắt** — checkbox trong modal sửa cột lương (Cấu hình > Danh sách cột lương), không cần dev can thiệp mỗi case mới.

## Phát hiện kiến trúc quan trọng (khảo sát trước khi viết SPEC)

Cơ chế override đã có sẵn và **type-agnostic từ trước**: `applyResolvedFormulas` (`payroll_scoped_resolver.go`) thay thế `Formula` của BẤT KỲ `component_type` nào bằng 1 chuỗi số cố định — engine coi đó là 1 công thức bình thường và evaluate. `writeOverrideCell` đã tự động hoá bước tạo formula-từ-số. → **Không cần sửa `engine.go`/`computeEmployee` gì cả** — chỉ cần relax đúng 1 điểm gate ghi.

## Thi hành

`/propose` → SPEC `030926-formula-force-override-flag.md` → `/plan` → PLAN cùng tên `-PLAN.md`, 2 task, nhánh `feat/formula-force-override-flag` (cả 2 repo, từ `develop_v1`).

**Task 1 (BE, `Core System-backend@78f9155`):**
- Migration `v92_salary_components_allow_force_override.sql` — thêm cột `allow_force_override boolean DEFAULT false`, seed `true` cho `PROB_EARNED`.
- `models.SalaryComponent` thêm field `AllowForceOverride`.
- `salary_component_repo.go` (`Create`/`Update`) thêm cột vào SQL.
- `writeOverrideCell` (`payroll_service.go`) — thêm gate hợp nhất ngay sau khi lấy `comp`: cho ghi nếu `input`/`manual` HOẶC (`formula` AND `AllowForceOverride`). Blocklist pháp định (`statutoryOverrideBlocklist`, chạy TRƯỚC, không đổi) vẫn luôn thắng.
- `BulkSetCells` (`payroll_bulk_cell_set.go`) — xoá hẳn gate trùng lặp (tự fetch `comp` + kiểm `ComponentType` riêng), để rơi thẳng vào `writeOverrideCell` — cùng thông báo lỗi, không đổi hành vi cũ ngoài việc thêm allowlist.
- Test mới `formula_force_override_integration_test.go` (4 test, DB thật): cột formula bật cờ ghi được và thắng công thức; cột formula chưa bật cờ vẫn bị từ chối; `PIT` luôn bị chặn dù giả lập bật cờ; `SetCell` (đường trước đây không có gate) nay cũng từ chối đúng — xác nhận vá lỗ hổng.

**Task 2 (FE, `Core System-frontend@70be103`):**
- `lib/api/types.ts` — thêm `allowForceOverride: boolean` vào `SalaryComponent`.
- `data.ts` (`buildLiveCols`) — `editable` tính thêm `(componentType==="formula" && allowForceOverride)`.
- `SalaryComponentModal.tsx` — thêm state + checkbox "Cho phép ghi đè giá trị công thức (Nhập Excel/sửa ô)", chỉ hiện khi `componentType==="formula"`, truyền vào `createSalaryComponent`/`updateSalaryComponent`.
- Sửa kèm 1 fixture test có sẵn (`lib/template-picker.test.ts`) do thêm field bắt buộc mới vào type `SalaryComponent`.

## Kết quả kiểm

- **BE:** `go build`/`go vet` sạch. 4 test mới pass. 2 test tích hợp cũ của `BulkSetCells` + 2 test `CalculateBatch` (đợt trước cùng ngày) pass, không hồi quy. `go test ./internal/...` toàn bộ: 1115 pass/7 fail — 7 fail khớp tuyệt đối danh sách tiền tồn tại (đối chiếu bằng `git stash`, chạy 2 lần để loại trừ 1 flake tạm thời `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` xác nhận không liên quan tới thay đổi — pass khi chạy riêng lẻ và không tái hiện ở cả baseline lẫn lần chạy lại).
- **FE:** `tsc`/`eslint` sạch (3 lỗi tsc còn lại tiền tồn tại, không liên quan). `vitest` 194 pass/0 fail.
- **Kiểm chứng thật trên dev server** (đúng case gốc user đưa ra): `GET /config/salary-components` xác nhận `PROB_EARNED.allowForceOverride=true` (FE sẽ mở khoá ô sửa). Gọi `POST /Core System/cell-set` ghi `PROB_EARNED=150000` cho NV `004335` (kỳ 08/2026, `BASIC_SAL=120000`) — **ghi thành công**, `PROB_EARNED` trả về đúng `150000` (trước đây bị từ chối/luôn tính ra 0), và chuỗi phụ thuộc tính lại đúng: `EARNED_SAL=308400` (=150000+120000+0+38400), `GROSS=708400` (=308400+400000 PHONE_NONTAX). Sau đó dọn: gọi `cell-set` với `value=null` để xoá override — `PROB_EARNED` trở lại đúng `0` (giá trị tự tính từ `PROB_DAYS=0`); xác nhận `DeleteByCoord` là soft-delete (`is_active=false`, giữ lịch sử) — hành vi bình thường của hệ thống, không phải rác cần dọn thêm.

## Trạng thái git

- `Core System-backend@feat/formula-force-override-flag` (từ `develop_v1`), 1 commit (`78f9155`).
- `Core System-frontend@feat/formula-force-override-flag` (từ `develop_v1`), 1 commit (`70be103`).
- **Chưa push, chưa merge** cả 2 repo.

## Lưu ý vận hành (đã ghi trong SPEC, nhắc lại ở đây)

Nếu admin cần bật `allow_force_override` cho 1 cột formula khác trong tương lai — **bật RIÊNG 1 lượt lưu**, không gộp chung với sửa công thức/tên cột cùng lúc. Lý do: luồng duyệt hiện có (`salary_component_pending_changes`) chỉ lưu `OldFormula/NewFormula/OldName/NewName` — nếu cờ mới đi kèm 1 thay đổi formula/tên phải qua duyệt, cờ đó có thể bị rơi mất khi request được duyệt (giới hạn có sẵn từ trước cho MỌI field khác ngoài formula/tên, không riêng cờ này — không thuộc phạm vi sửa của đợt này).
