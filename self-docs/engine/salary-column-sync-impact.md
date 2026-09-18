---
type: draft
title: Đồng bộ cột lương giữa 2 sheet + kiểm tra tác động khi sửa rule
status: proposed
timestamp: 2026-07-28
task: null
id: self-docs/engine/salary-column-sync-impact
canonical_question: 'Technical guide and specification: 280726 — Đồng bộ cột lương
  giữa 2 sheet + kiểm tra tác động khi sửa rule'
aliases:
- 280726 — Đồng bộ cột lương giữa 2 sheet + kiểm tra tác động khi sửa rule
- Salary Column Sync Impact 280726
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# 280726 — Đồng bộ cột lương giữa 2 sheet + kiểm tra tác động khi sửa rule

**Status:** đã thi hành xong 9/9 task (2026-07-28). Chi tiết ở mục "Kết quả thi hành" cuối file — gồm bảng commit thật, kết quả test, và danh sách chỗ PLAN ghi sai so với code thật đã phải sửa khi làm. Phần SPEC bên dưới giữ nguyên như lúc duyệt để đối chiếu.

## Yêu cầu (một câu)

Làm cho quan hệ giữa sheet "Danh sách cột lương" và sheet "Bảng lương tháng" trở nên đáng tin ở cả ba chiều — thêm rule thì cột mới nói thật về trạng thái số liệu của nó, xoá rule thì người dùng thấy trước mọi thứ sẽ mất theo, thứ tự cột là một thứ tự duy nhất lưu được — và bổ sung khả năng xem trước tác động trước khi sửa một công thức lương.

## Context

Wiki `concepts/`, `entities/` và `sources/adr/` hiện chưa có nội dung nào cho phạm vi này, nên phần nền được lấy từ các SPEC/PLAN đã duyệt trong `sources/draft/` và tài liệu canonical trong `self-docs/`:

- `sources/draft/240726-formulas-tab-fe.md` — SPEC đã thi hành xong của tab "Công thức". **TASK-REF** ở đó đặt ra quy tắc: xoá cột mà bị cột khác phụ thuộc thì phải hiện rõ danh sách phụ thuộc, không được báo lỗi chung chung. **TASK-REF** đặt ra quy tắc: sau khi tạo/sửa/xoá cột, danh sách cột trên sheet chính phải cập nhật ngay, không cần tải lại trang. SPEC này mở rộng đúng hai quy tắc đó — TASK-REF sang các nhóm phụ thuộc chưa ai kiểm (override, template, dữ liệu nhập tay), TASK-REF sang phần "cập nhật rồi, nhưng số liệu nói gì".
- `sources/draft/240726-salary-component-db-hardening.md` — đợt gia cố schema `salary_components`, nơi `salary_component_overrides` được nối UI lần đầu. Đây là nhóm dữ liệu mà thao tác xoá cột hiện đang CASCADE mất mà không cảnh báo.
- `sources/draft/260726-salary-structure-usage-and-grading.md` và `-PLAN.md` — cấu trúc lương theo cấp bậc, cơ chế mask theo template, kill-switch `PAYROLL_TEMPLATE_ENFORCE`, và endpoint shadow-mode `GET /Core System/template-impact/{periodId}`. Endpoint đó là khuôn mẫu kỹ thuật được tái dùng cho phần dry-run của SPEC này. Nhóm tính năng template **đang được hold** theo yêu cầu người dùng ngày 28/07.
- `sources/draft/270726-Core System-template-audit-and-preview-ui-PLAN.md` — PLAN mà Task A/B/D/E đã thi hành, Task C (UI xem trước tác động của template) đã bị **xoá khỏi FE** theo yêu cầu (`Core System-frontend@e066f7a`), endpoint backend vẫn còn sống.
- `self-docs/Salary-Structure-Template-Analysis-260726.md` — tài liệu canonical của nhóm template, mục 7 ghi ba vòng thiết kế quy tắc mask và khái niệm `maskableUniverse` (union mọi cột xuất hiện trong bất kỳ template nào). Đây là lý do việc xoá một cột ra khỏi `template_components` không phải thao tác vô hại.
- `self-docs/PIT-Formula-Fix-270726.md` — tiền lệ gần nhất về việc một trường point-in-time không được gán làm cả một cột tiền im lặng về 0 trên toàn hệ thống. Bài học đó áp dụng trực tiếp cho quyết định chặn dry-run khi thiếu danh sách lương ở SPEC này.
- `Core System-backend/docs/routes-permissions.md` — bảng gate theo route, là nơi phải cập nhật khi thêm route mới.

## Sự thật kỹ thuật đã xác minh trực tiếp (nền của mọi quyết định dưới đây)

Toàn bộ mục này đọc từ code thật, không suy từ tài liệu:

1. **Hai sheet vốn đã dùng chung một nguồn.** Sheet "Bảng lương tháng" dựng cột từ `data.cols` → `buildLiveCols(components)` (`Core System-frontend/components-page/tinh-luong/data.ts:248` và `:130`); sheet "Danh sách cột lương" đọc `data.allComponents` (`TinhLuongExcel.tsx:2355`). Cả hai đến từ **một** lần gọi `getSalaryComponents()` (`data.ts:209`, `data.ts:302`), và mọi thao tác Thêm/Sửa/Xoá đều gọi `data.refetchComponents()` (`TinhLuongExcel.tsx:3538/3551/3564/3577`). Backend `Create` luôn đặt `IsVisible = true` (`internal/service/salary_component_service.go:110`). **Kết luận: phần "thêm/xoá rule thì cột bên kia theo" đã chạy sẵn ở mức hiển thị.** Việc thật còn lại là ba hệ quả dữ liệu ở dưới.
2. **Cột mới hiện toàn số 0 và không có gì nói ra điều đó.** `mapRow` gán `emp[code] = vals[code] ?? 0` (`data.ts:247`), nên "chưa có key trong `computed_values`" và "đã tính, ra đúng 0" trông giống nhau tuyệt đối.
3. **Kỳ đã finalize thì cột mới vĩnh viễn không có số.** `UpsertBatchComputed` có `WHERE payroll_records.status != 'finalized'` (`internal/repository/payroll_record_repo.go`) — bảo vệ số đã chốt là đúng, nhưng hệ quả chưa được nói với người dùng ở bất cứ đâu.
4. **Xoá một cột lương CASCADE xoá sạch dữ liệu thật, im lặng.** `atlas/migrations/20260612000000_baseline.sql:2490` đặt `salary_component_overrides_component_id_fkey ... ON DELETE CASCADE`; `:2498` đặt `template_components_component_id_fkey ... ON DELETE CASCADE`. Nghĩa là xoá cột sẽ xoá mọi override theo phòng ban/nhân viên của cột đó và gỡ nó khỏi mọi salary template — mà kiểm tra trước khi xoá ở `salary_component_service.go:168-176` **chỉ** quét `strings.Contains(c.Formula, "[CODE]")` trên các `salary_components` khác. Override của cột khác có tham chiếu `[CODE]` cũng không được kiểm.
5. **Năm bảng khoá theo `component_code` dạng text, không có FK** — nên xoá cột để lại dữ liệu mồ côi, và tạo lại cùng mã code sẽ làm dữ liệu cũ "sống lại": `payroll_manual_inputs` (số HR nhập tay, `baseline.sql:1353`), `payroll_cell_snapshots`, `payroll_formula_snapshots`, `payroll_cell_edits`, `salary_formula_configs`.
6. **Thứ tự cột hiện là bất biến theo lịch sử tạo, không sửa được ở đâu.** Cả hai sheet cùng `ORDER BY seq ASC, code ASC` (`internal/repository/salary_component_repo.go:23` và `:30`); cột mới nhận `seq = MAX(seq)+1` (`:42`); SQL `Update` **không** có `seq` trong danh sách SET (`:70-85`); không có endpoint reorder nào.
7. **Kéo-thả cột chỉ sống trong phiên.** `moveColumn` (`TinhLuongExcel.tsx:931`) ghi vào `state.colOrder`, có comment ghi rõ là bộ nhớ phiên, không localStorage (`:518`). `reorderCols` (`:264`) đã xử lý đúng cột mới (nối cuối, sort ổn định). Sheet rule không đi theo `colOrder` → lệch ngay sau cú kéo đầu tiên.
8. **Sửa công thức hiện không có kiểm tra tác động nào.** `Update` (`salary_component_service.go:115`) chỉ ghi history khi `Formula` hoặc `Name` đổi; không quét tham chiếu, không tính tác động. `Validate` (`:198`) chỉ kiểm cú pháp và mã lạ theo whitelist.
9. **`BASIC_SAL` chỉ đến từ danh sách lương HR upload, không bao giờ đọc từ `employees`** (`internal/service/payroll_service.go:1021` ghi rõ, `:443` thi hành). Danh sách đó sống ở `sessionStorage` (`components-page/Core System/PayrollPage/PayrollPage.helpers.ts:238`, `SALARY_SESSION_KEY`) — per-tab, mất khi đóng tab.
10. **UI Excel đang dùng không có hành động tính lương nào.** `calculatePayroll` chỉ được gọi từ `components-page/Core System/PayrollPage/PayrollPage.tsx` (3 call site); grep toàn repo không có call site nào trong `components-page/tinh-luong/`.
11. **`ComputeTemplateImpact` đang có một bug làm báo cáo tác động nói sai.** Nó truyền `salaryOverrides: map[string]float64{}` cho cả hai lần mô phỏng (`payroll_service.go:713` và `:720`) → `BASIC_SAL` rỗng → phần lớn cột ra 0 ở **cả hai** lần → delta ≈ 0 → báo cáo kết luận "không có tác động" trong khi thực tế có. Đây là lỗi tiền tồn tại của nhóm template đang hold; SPEC này **không sửa nó**, nhưng endpoint mới **không được lặp lại** nó.
12. **Route mẫu để bám gate.** `GET /Core System/template-impact/{periodId}` gắn `requirePayrollCalculate, companyReadScope, requireView` (`internal/app/router.go:443`); nhóm `/config/salary-components` dùng `requireSalaryComponentsView/Create/Edit/Delete` (`router.go:286-299`).

## Rủi ro đã biết, ngoài phạm vi thi hành: chủ trương "không lưu lương" mới thi hành được một nửa

Mục này ghi lại một phát hiện phát sinh khi người dùng đi hỏi lại lý do thiết kế của `BASIC_SAL` và nhận được câu trả lời là "vì lý do bảo mật". Nó **không** nằm trong phạm vi thi hành của SPEC này, nhưng nó là gốc của cả ba hạn chế mà SPEC này phải đi vòng, nên phải được ghi ra để người đọc sau không phải điều tra lại từ đầu. Toàn bộ dưới đây đối chiếu trực tiếp với code và với DB dev `payroll_engine`.

### Lời giải thích nhận được

Đại ý: số lương vẫn phải đi qua hệ thống, vì không có nó thì không tính được gì; điều hệ thống bảo đảm là **không ghi số thực ở lại**; và nếu ai đó muốn suy ngược ra thì vẫn suy được.

### Nửa chủ trương ĐƯỢC code thi hành: chặn đầu vào

Cơ chế thật gói trong đúng một dòng cấu hình:

- Hàng `BASIC_SAL` trong `salary_components` có `component_type = 'input'`, `source_field = ''`, `formula = ''` (xác nhận bằng truy vấn DB dev, không phải suy từ seed). `source_field` trống nghĩa là vòng nạp `source_field` ở `payroll_service.go:447-454` không có đường nào lấy `employees.basic_salary`.
- Chủ ý được viết ra tường minh ở `internal/database/database.go:2271-2277`: `BASIC_SAL: source_field='' (chỉ từ Excel upload, không đọc employees.basic_salary)`, và `UPDATE salary_components SET source_field = '' WHERE code = 'BASIC_SAL';`.
- Hai comment cùng ý ở `payroll_service.go:442` ("không lưu DB") và `:546` ("BASIC_SAL không lưu DB").

Nên vế "số lương phải xuống backend mới tính được" là đúng và có chủ ý: nó xuống theo request, dùng trong bộ nhớ, không đi vào master data nhân viên.

### Nửa chủ trương KHÔNG được thi hành: số vẫn ghi lại nguyên văn

Không có dòng code nào cố gắng loại `BASIC_SAL` ra trước khi lưu:

1. `engine.Calculate` (`internal/service/engine.go`) mở đầu bằng việc copy **toàn bộ** `inputs.Values` vào map kết quả rồi trả về chính map đó. `BASIC_SAL` là input, nên nó có mặt trong output.
2. `computeEmployee` trả thẳng map đó lên (`payroll_service.go`, nhánh `return models.ComputedValues(computed), baseValues, nil`), và `UpsertBatchComputed` ghi cả map vào `payroll_records.computed_values` (JSONB).
3. Trong toàn bộ service chỉ có **một** lệnh `delete` trên tập giá trị (`payroll_service.go:520`), và nó phục vụ việc bỏ cột bị override để engine tính lại theo công thức override — không phải để xoá lương.

Bằng chứng trên DB dev `payroll_engine`:

```
SELECT count(*) AS tong,
       count(*) FILTER (WHERE computed_values ? 'BASIC_SAL')            AS co_key,
       count(*) FILTER (WHERE (computed_values->>'BASIC_SAL')::numeric > 0) AS duong
FROM payroll_records;
--  tong: 6435 | co_key: 6435 | duong: 0
```

**6435/6435 record đều có key `BASIC_SAL` được ghi trong `computed_values`.** Giá trị hiện đều bằng 0, nhưng đó là vì các lần tính sinh ra dữ liệu này chưa bao giờ kèm danh sách lương — **không phải vì code chặn**. Ngay lần đầu có ai bấm tính lương kèm file lương thật, số đó được serialize thành JSON và nằm lại trong `payroll_records`. Điểm ghi thứ hai: `Finalize` gọi `SnapshotCellsForPeriod` (`payroll_service.go`, nhánh Finalize) đóng băng giá trị gốc và giá trị cuối của từng ô HR ghi đè vào `payroll_cell_snapshots`.

### Vế "đảo ngược vẫn ra được" — đúng, và thực ra không cần đảo ngược

- `BASIC_SAL` có `is_visible = true` trong DB, nên nó là một **cột hiện thẳng trên sheet Bảng lương tháng**. Ai xem được bảng lương là đọc được số, không cần suy luận.
- Giả sử có ai xoá key đó trước khi lưu thì công thức vẫn là dữ liệu công khai, hiện ngay ở sheet "Danh sách cột lương": `CONTRACT_TOTAL = [BASIC_SAL] + [RESPONSIBILITY_ALLOW]`, `OFFICIAL_SAL = [BASIC_SAL] * [PAID_DAYS] / [STD_DAYS]`, `BHXH_NV = MIN([BASIC_SAL], 46800000) * 0.08`. Trong khi `NET_PAY` và `GROSS` đã khác 0 ở 6400/6435 record. Một phép chia là ra.

### Điểm trái ngược nằm trong chính codebase

- Cột `employees.basic_salary` **vẫn tồn tại**, `NOT NULL DEFAULT 0` (`database.go:344`), và có một seeder tự điền: `database.go:1166` ghi `SEED: Fake basic_salary by job_title (level) — DEMO DATA ONLY`, chạy với điều kiện `WHERE basic_salary = 0` (`:1417`).
- Trên DB dev: 12044/12044 nhân viên có `basic_salary > 0` và `insurance_salary > 0`. Nhưng chỉ có **10 giá trị khác nhau** (5tr, 9tr, 10tr, 12tr, 14tr, 18tr, 32tr, 60tr, 70tr, 75tr — riêng mức 12tr chiếm 10.539 người), tức đúng là dữ liệu giả của seeder chứ không phải lương thật. **Chỉ đọc được DB dev, không kết luận gì về production.**
- `EmployeeRepo.UpdateSalary()` (`internal/repository/employee_repo.go:469`) là **code chết** — grep toàn repo không có call site nào ngoài chính định nghĩa. `Core System-adapter` không gửi trường này (grep 0 kết quả).
- Còn một cấu hình cũ nói ngược hẳn chủ trương hiện tại: seed `salary_formula_configs` có hàng `SAL_BASE` với note "Lấy từ trường basic_salary của nhân viên (HR xác nhận Q1)" (`database.go:1262`).

### Kết luận và cái giá phải trả

Đây không phải một cơ chế bảo mật mà là một **quy ước vận hành** — đừng lưu lương vào master data nhân viên — được thi hành đúng một nửa. Nửa chặt: engine không đọc `employees.basic_salary`. Nửa hở: số lương vẫn được ghi vào `payroll_records.computed_values` mỗi lần tính, vẫn hiện như một cột bình thường trên bảng lương, và vẫn suy ra được từ các cột khác. Nói cách khác, chi phí thì trả đủ mà lợi ích bảo mật thì gần như không có.

Chi phí đó chính là ba hạn chế mà SPEC này phải thiết kế quanh, không phải né:

1. **Không có nút tính lương nào an toàn ở UI Excel** — gọi `Calculate` với body rỗng sẽ làm `BASIC_SAL` không được set, kéo mọi cột dẫn xuất lương về 0 và ghi đè `computed_values` của toàn bộ record chưa finalize trong kỳ. Đây là lý do Task 4 chỉ hiện nhãn chứ không hiện nút, và là lý do người dùng chọn phương án không thêm hành động ghi tiền vào UI này.
2. **Báo cáo tác động không tự ước tính được tiền** — phải nhận danh sách lương từ FE qua POST body (Task 6), và phải từ chối chạy khi thiếu (TASK-REF) thay vì trả về một báo cáo delta bằng 0 trông như "không có tác động".
3. **`ComputeTemplateImpact` đang báo sai** vì đúng lý do đó (Sự thật kỹ thuật #11) — không sửa trong SPEC này vì nhóm template đang hold, nhưng endpoint mới không được lặp lại.

Hướng xử lý gốc, nếu sau này muốn làm, là lưu danh sách lương theo kỳ xuống DB để `Calculate` trở nên idempotent và không còn phụ thuộc trạng thái trình duyệt. Đó là một quyết định riêng, chạm đường đi của tiền, cần migration, và đã được người dùng cân nhắc rồi chủ động để lại — không phải điều bị bỏ sót.

## Global constraints

Mọi task dưới đây đều mang theo nguyên văn các ràng buộc sau.

- **Nhánh làm việc: `feature_1` ở cả `Core System-backend` và `Core System-frontend`.** Không phải `sec_dev` — nhánh đó không tồn tại kể cả trên remote (ghi nhận từ 250726). Kiểm trước khi sửa: `cd "<repo>" && git branch --show-current`.
- **Không tạo file HTML trong `llmwiki/html/`** — quy ước máy local (`CLAUDE.md`, mục "Quy ước máy local này"). SPEC này cố ý không có companion `.html`; sequence diagram không cần thiết cho phạm vi này.
- **Backend verify:** `go vet ./...` sạch; `go test ./...` chỉ được có **đúng 4 fail baseline cũ** (2 report route + 2 pipeline route). Nhiều hơn 4 hoặc khác 4 cái đó = hồi quy, phải sửa trước khi coi task xong.
- **Frontend verify:** `npx tsc --noEmit` sạch, `npx eslint` sạch, **và `npm run build` (next build sản xuất thật)** — không được chỉ chạy `tsc`. Bài học 270726: `tsc` xanh mà `next build` đỏ đã từng xảy ra.
- **Không sửa `Core System-frontend/components-page/tinh-luong/ribbon-static.ts`** — file này là bản auto-extract, sửa sẽ bị ghi đè.
- **Hợp đồng API client:** `request<T>()` trong `lib/api/client.ts` trả **thẳng** `Promise<T>`, KHÔNG bọc `{data}`. Chỉ `requestWithTotal` (dùng bởi `getEmployees`) mới có `.data`. Bài học 270726: giả định sai chỗ này gây crash runtime.
- **Gate route mới phải khớp mẫu đang có, không tự phát minh:** route dưới `/config/salary-components` dùng `requireSalaryComponentsView` cho đọc và `requireSalaryComponentsEdit` cho ghi; route dry-run dưới `/Core System` dùng `requirePayrollCalculate, companyReadScope, requireView` đúng như `router.go:443`.
- **Không migration DB trong SPEC này.** Nếu thi hành phát sinh nhu cầu migration thì phải theo đúng quy ước: chỉ additive, dry-run `BEGIN; \i <file>; ROLLBACK;` trước, xác nhận với người dùng trước khi áp vào DB `payroll_engine`, rồi re-hash `atlas.sum`.
- **Mọi endpoint mô phỏng phải không ghi một dòng nào vào `payroll_records`** — khoá bằng test đếm số dòng trước/sau, không chỉ bằng review mắt.
- **Cập nhật tài liệu route:** thêm route mới vào `Core System-backend/docs/routes-permissions.md` và `Core System-frontend/docs/routes-permissions.md` (hai file trỏ chéo nhau).

## Non-goals

Những thứ cố ý KHÔNG làm trong SPEC này:

- **Không thêm nút tính lương hay upload danh sách lương vào UI Excel.** Quyết định của người dùng: tránh đưa một hành động ghi tiền mới vào UI này khi `BASIC_SAL` còn phụ thuộc sessionStorage — gọi `Calculate` với body rỗng sẽ zero-out toàn bộ cột dẫn xuất lương của mọi record chưa finalize trong kỳ.
- **Không đổi kiến trúc `BASIC_SAL`.** Không thêm bảng lưu danh sách lương theo kỳ, không cho `Calculate` đọc lương từ `employees`. Rủi ro đã ghi nhận ở mục Sự thật kỹ thuật #9, để dành cho một quyết định riêng.
- **Không hồi sinh UI xem trước tác động của template** (Task C, đã xoá ở `Core System-frontend@e066f7a`) và **không sửa bug `salaryOverrides` rỗng của `ComputeTemplateImpact`** — nhóm tính năng structure salary rule đang hold theo yêu cầu người dùng ngày 28/07. Chỉ ghi nhận để endpoint mới không lặp lại lỗi.
- **Không dọn dữ liệu mồ côi.** Cảnh báo và đếm, không xoá `payroll_manual_inputs` / snapshot / cell edit của cột đã xoá. Xoá dữ liệu lịch sử là quyết định riêng, có hệ quả đối chiếu.
- **Không chặn `Calculate` trên kỳ đã lock/finalize ở tầng handler.** Hiện chỉ chặn ở tầng SQL theo từng record; rủi ro đã ghi nhận, ngoài phạm vi.
- **Không đổi cơ chế xoá thành soft-delete.** Người dùng chọn hướng "cảnh báo rồi vẫn cho xoá", không chọn hướng đổi nút Xoá thành ẩn cột.
- **Không đưa cột `is_visible = false` vào sheet Bảng lương tháng.** Sheet rule tiếp tục hiện cả cột ẩn, sheet bảng lương tiếp tục lọc — đây là chủ đích, không phải lệch.

## Approaches

Ba phương án khác nhau về bản chất cho cả gói bốn yêu cầu, không chỉ khác chi tiết.

### Phương án A — Đồng bộ ở tầng đọc, cảnh báo dạng advisory (CHỌN)

Giữ nguyên nguồn dữ liệu và đường tính tiền. Bổ sung ba loại metadata mà UI hiện thiếu: trạng thái "cột này đã có số cho kỳ này chưa", "xoá cột này thì những gì mất theo", "sửa công thức này thì ai bị ảnh hưởng và lệch bao nhiêu tiền". Thứ tự cột trở thành thứ tự lưu được bằng cách persist `seq` — vốn đã là nguồn thứ tự chung của hai sheet.

- **Được:** không chạm `Calculate`, không chạm `payroll_records`, không migration. Mọi thứ thêm vào đều là đọc hoặc mô phỏng. Rủi ro tiền gần bằng không, và đúng ba việc người dùng yêu cầu.
- **Mất:** không "tự động đồng bộ" theo nghĩa hệ thống tự tính lại; người dùng vẫn phải chủ động chạy tính lương ở luồng hiện có để cột mới có số. Dữ liệu mồ côi vẫn còn đó, chỉ được nhìn thấy chứ không được dọn.

### Phương án B — Đồng bộ ở tầng ghi, event-driven

Mỗi thay đổi `salary_components` phát một event; backend tự tính lại kỳ đang mở, tự dọn dữ liệu mồ côi, tự đồng bộ template. Đây là nghĩa mạnh nhất của chữ "đồng bộ".

- **Được:** cột mới có số ngay, không ai phải nhớ chạy tính lại; không tồn tại trạng thái nửa vời.
- **Mất:** **bất khả thi ở trạng thái hiện tại** — `BASIC_SAL` chỉ có trong sessionStorage của trình duyệt (Sự thật #9), nên một job backend tự tính lại sẽ tính với `BASIC_SAL` rỗng và zero-out cả kỳ. Muốn làm được B thì phải làm xong việc lưu danh sách lương xuống DB trước, tức là chạm trực tiếp đường đi của tiền. Ngoài ra tự-tính-lại là hành động ghi tiền không do người dùng bấm — trái nguyên tắc vận hành hiện tại của dự án.

### Phương án C — Hợp nhất hai sheet thành một

Bỏ sheet "Danh sách cột lương" riêng, đưa việc xem/sửa rule vào chính header của sheet bảng lương. Không còn hai danh sách thì không còn bài toán đồng bộ.

- **Được:** diệt tận gốc cả ba câu hỏi về đồng bộ (thêm, xoá, thứ tự) vì chỉ còn một nơi.
- **Mất:** đập đi luồng UX vừa ship và vừa được người dùng phản hồi tinh chỉnh nhiều đợt (240726 tạo sheet, 250727 thêm sửa-tại-chỗ ô Công thức và cột Trạng thái duyệt). Mất khả năng thấy cột `is_visible = false` — bảng lương không hiện cột ẩn, nên hợp nhất đồng nghĩa không còn chỗ nào quản lý cột ẩn. Khối lượng lớn nhất trong ba phương án mà giá trị thêm cho người dùng nhỏ nhất.

**Chọn A.** B bị chặn bởi một điều kiện tiên quyết nằm ngoài phạm vi (kiến trúc `BASIC_SAL`) và trái nguyên tắc "không tự động ghi tiền"; C phá đi thứ đã ổn để giải một bài toán mà A giải được với chi phí thấp hơn nhiều.

## Requirements (FR)

- **TASK-REF**: Với một cột lương chưa có số liệu ở kỳ đang xem, sheet "Bảng lương tháng" PHẢI hiển thị rõ dấu hiệu "chưa tính cho kỳ này" ở header cột, phân biệt được với trường hợp "đã tính và giá trị đúng bằng 0".
- **TASK-REF**: Dấu hiệu ở TASK-REF PHẢI kèm giải thích cho người dùng nghiệp vụ biết phải làm gì tiếp: kỳ chưa chốt thì chỉ rõ cần chạy tính lương ở luồng hiện có; kỳ đã finalize thì nói thẳng rằng record đã chốt không bị ghi đè nên cột này sẽ không có số cho kỳ đó.
- **TASK-REF**: Hệ thống PHẢI có một endpoint trả về toàn bộ mức độ liên quan của một cột lương, gồm: các cột khác tham chiếu `[CODE]` trong công thức gốc; các override (theo phòng ban/nhân viên) tham chiếu `[CODE]` trong công thức của chúng; số override thuộc chính cột đó sẽ bị xoá theo; các salary template đang chứa cột đó; số dòng dữ liệu nhập tay, cell pin và số kỳ có giá trị đã tính của cột đó.
- **TASK-REF**: Dialog xoá cột PHẢI hiển thị đầy đủ thông tin ở TASK-REF trước khi người dùng xác nhận, nêu rõ nhóm nào sẽ **bị xoá theo** (override của cột) và nhóm nào sẽ **bị gỡ tham chiếu** (template), và PHẢI bắt một bước xác nhận riêng khi có dữ liệu thật sẽ mất.
- **TASK-REF**: Hành vi chặn xoá hiện có PHẢI giữ nguyên — cột đang bị công thức của cột khác tham chiếu thì vẫn không xoá được (409, `usedBy`), đúng như TASK-REF của `240726-formulas-tab-fe.md`. Các nhóm phụ thuộc mới ở TASK-REF chỉ cảnh báo, không chặn.
- **TASK-REF**: Hệ thống PHẢI có endpoint cho phép ghi lại thứ tự hiển thị của các cột lương (`salary_components.seq`) theo một danh sách mã cột, trong một transaction, có ghi audit log.
- **TASK-REF**: Kéo-thả đổi thứ tự cột trên sheet "Bảng lương tháng" PHẢI lưu được, và sau khi lưu thì sheet "Danh sách cột lương" PHẢI hiển thị đúng thứ tự đó — hai sheet dùng chung một thứ tự duy nhất.
- **TASK-REF**: Người dùng không có quyền sửa cột lương PHẢI vẫn kéo-thả được để xem tạm (không lưu), và không được nhận lỗi quyền dội lên mặt khi kéo.
- **TASK-REF**: Khi sửa công thức một cột lương, hệ thống PHẢI hiển thị ngay phần tác động tĩnh: những cột nào phụ thuộc vào cột này (cả trực tiếp và gián tiếp qua nhiều tầng), bao nhiêu override và bao nhiêu template liên quan.
- **TASK-REF**: Hệ thống PHẢI có endpoint mô phỏng tác động số học của một công thức ứng viên trên một kỳ: chạy hai lần tính (công thức hiện tại và công thức ứng viên) trên **cùng** toàn bộ dữ liệu point-in-time, chỉ khác duy nhất công thức của cột đang sửa, rồi trả về số nhân viên có số đổi, tổng lệch theo từng cột bị ảnh hưởng, và danh sách nhân viên lệch nhiều nhất.
- **TASK-REF**: Endpoint ở TASK-REF PHẢI KHÔNG ghi bất kỳ dòng nào vào `payroll_records` hay bảng dữ liệu lương nào khác.
- **TASK-REF**: Endpoint ở TASK-REF PHẢI từ chối chạy phần số học khi không nhận được danh sách lương (`salaries` rỗng), kèm thông báo nêu rõ lý do — vì thiếu `BASIC_SAL` sẽ làm cả hai lần mô phỏng ra ~0 và báo cáo kết luận sai rằng "không có tác động".
- **TASK-REF**: Báo cáo tác động PHẢI là advisory — hiển thị cảnh báo nhưng KHÔNG chặn người dùng lưu công thức.

## Success criteria (SC)

- **TASK-REF**: Một người làm C&B thêm một cột lương mới rồi mở sheet Bảng lương tháng, và **không** kết luận sai rằng công thức bị lỗi — họ đọc được ngay từ giao diện rằng cột chưa được tính cho kỳ này và biết bước tiếp theo phải làm gì. (Bằng chứng: thử nghiệm với người dùng nghiệp vụ trên kỳ chưa chốt và kỳ đã chốt; ở tầng máy có unit test phân biệt "key vắng trong `computed_values`" với "giá trị đúng bằng 0".)
- **TASK-REF**: Không còn trường hợp người dùng xoá một cột lương rồi phát hiện sau đó là các override theo phòng ban/nhân viên của cột đó đã mất hoặc cột đã bị gỡ khỏi salary template — mọi thứ mất theo đều đã được liệt kê trên màn hình trước khi họ bấm xác nhận. (Bằng chứng: test tích hợp dựng cột có override + template + dữ liệu nhập tay, xác nhận endpoint đếm đúng cả bốn nhóm; kiểm tay trên UI.)
- **TASK-REF**: Người dùng sắp xếp thứ tự cột theo ý mình một lần, và thứ tự đó vẫn còn sau khi đóng trình duyệt mở lại, và giống nhau ở cả hai sheet. (Bằng chứng: test tích hợp cho endpoint reorder xác nhận `seq` đổi đúng và `ListActive` trả về đúng thứ tự mới; kiểm tay hai sheet.)
- **TASK-REF**: Trước khi sửa một công thức lương ảnh hưởng tới tiền, người làm C&B trả lời được hai câu hỏi ngay trên màn hình mà không cần hỏi ai: "còn cột nào bị kéo theo" và "tổng số tiền lệch bao nhiêu trên kỳ này". (Bằng chứng: test tích hợp đối chiếu delta đúng dấu và đúng độ lớn trên một kỳ cách ly; kiểm tay.)
- **TASK-REF**: Báo cáo tác động không bao giờ nói "không có tác động" trong khi thực tế có. (Bằng chứng: test khoá bất biến — gọi endpoint không kèm danh sách lương phải bị từ chối, không được trả về báo cáo delta bằng 0.)
- **TASK-REF**: Không có dòng nào của `payroll_records` bị thay đổi bởi bất kỳ thao tác xem-trước nào. (Bằng chứng: test đếm số dòng và checksum giá trị trước/sau khi gọi endpoint mô phỏng.)

## Plan

- [ ] **Task 1 — Backend: endpoint "mức độ liên quan" của một cột lương.** Thêm `GET /config/salary-components/{id}/usage` (gate `requireSalaryComponentsView`) trả về đúng sáu nhóm ở TASK-REF. Tái dùng vòng quét token `"[" + code + "]"` đang có ở `Delete` (`salary_component_service.go:168`), mở rộng sang closure nhiều tầng cho phần phụ thuộc cột, và quét thêm `salary_component_overrides.formula`, `template_components`, `payroll_manual_inputs`, cell pin, cùng số kỳ có giá trị đã tính. Phục vụ cả Task 3 (xoá) và Task 5 (sửa) — một endpoint, hai chỗ dùng.
- [ ] **Task 2 — Backend: endpoint lưu thứ tự cột.** Thêm `PUT /config/salary-components/reorder` (gate `requireSalaryComponentsEdit`) nhận danh sách mã cột và ghi lại `seq` theo thứ tự đó trong một transaction, có audit log. Cho phép đổi thứ tự cả cột `is_system` (đây chỉ là thứ tự hiển thị, không phải ngữ nghĩa tính toán — khác hẳn `Update` vốn chặn `is_system`).
- [ ] **Task 3 — Frontend: dialog xoá cột nói hết sự thật.** `DeleteColumnDialog.tsx` gọi endpoint Task 1 khi mở, hiển thị bảng phân nhóm rõ "bị xoá theo" / "bị gỡ tham chiếu" / "để lại mồ côi", bắt một bước tick xác nhận riêng khi có dữ liệu thật sẽ mất, giữ nguyên ô lý do bắt buộc và giữ nguyên nhánh 409 hiện có.
- [ ] **Task 4 — Frontend: nhãn "chưa tính cho kỳ này".** `data.ts` tính tập mã cột vắng mặt trong `computed_values` của mọi dòng đã nạp (không kết luận khi kỳ có 0 dòng), gắn cờ lên `Col` trong `buildLiveCols`; `TinhLuongExcel.tsx` hiển thị dấu hiệu ở header cột kèm tooltip, và thông điệp khác nhau cho kỳ chưa chốt so với kỳ đã finalize. Giữ nguyên định dạng số trong ô (không đổi 0 thành dấu gạch) để không ảnh hưởng xuất Excel và copy vùng.
- [ ] **Task 5 — Frontend: kéo-thả lưu thật.** Sau `moveColumn`, nếu người dùng có quyền quản lý cột lương thì gọi endpoint Task 2 (debounce, gộp nhiều cú kéo liên tiếp thành một lần lưu) rồi `refetchComponents()`; giữ `colOrder` làm state optimistic để không nhảy cột trong lúc chờ. Chỉ persist thứ tự tương đối của các cột thuộc `salary_components`; các cột đầu (Mã NV, Họ tên, Phòng ban, Chức danh, Loại HĐ) và cột cuối (Trạng thái duyệt) không nằm trong bảng đó nên tiếp tục là thứ tự phiên. Người không có quyền vẫn kéo được để xem, không gọi API, không hiện lỗi quyền.
- [ ] **Task 6 — Backend: endpoint mô phỏng tác động của công thức ứng viên.** Thêm `POST /Core System/formula-impact/{periodId}` (gate `requirePayrollCalculate, companyReadScope, requireView` — khớp `router.go:443`) nhận `componentId`, `candidateFormula` và `salaries`. Dựng hai `calcShared` dùng chung mọi dữ liệu point-in-time theo đúng khuôn `ComputeTemplateImpact` (`payroll_service.go:664`), biến duy nhất khác nhau là công thức của một cột. **Truyền `salaries` vào cả hai lần mô phỏng** — đây chính là chỗ `ComputeTemplateImpact` đang sai. `salaries` rỗng thì từ chối với thông báo rõ (TASK-REF). Không ghi `payroll_records` (TASK-REF).
- [ ] **Task 7 — Frontend: panel tác động khi sửa công thức.** Trong `SalaryComponentModal.tsx` (mode edit) và luồng sửa-tại-chỗ `UpdateFormulaDialog.tsx`: phần tĩnh (Task 1) hiện ngay khi mở; nút "Ước tính tác động lên kỳ …" gọi Task 6 với danh sách lương đọc từ `SALARY_SESSION_KEY`; rỗng thì hiện thông báo giải thích vì sao không ước tính được số tiền thay vì hiện một báo cáo delta bằng 0. Advisory, không chặn nút Lưu (TASK-REF).
- [ ] **Task 8 — Test khoá bất biến.** Backend: endpoint usage đếm đúng bốn nhóm trên dữ liệu dựng thật; reorder đổi `seq` đúng và `ListActive` trả thứ tự mới; formula-impact ra delta đúng dấu và đúng độ lớn trên một kỳ cách li, bị từ chối khi thiếu danh sách lương, và không ghi một dòng nào vào `payroll_records` (đếm trước/sau). Frontend: unit test phân biệt "key vắng" với "giá trị 0" trong mapping.
- [ ] **Task 9 — Tài liệu.** Cập nhật `Core System-backend/docs/routes-permissions.md` và `Core System-frontend/docs/routes-permissions.md` cho ba route mới; viết `self-docs/Salary-Column-Sync-Impact-280726.md` (file canonical của hạng mục này, cập nhật liên tục trong ngày, không tách file rời); thêm một dòng vào mục "Nhật ký công việc theo ngày" của `CLAUDE.md`; cập nhật `self-docs/document-map.md`.

## Assumptions

Những điểm người dùng không nói và model tự điền — liếc qua đây là biết đâu là quyết định của máy:

- **(default)** Ô của cột "chưa tính" vẫn hiển thị `0` theo đúng định dạng số hiện tại, không đổi thành dấu gạch hay để trống. Lý do: đổi nội dung ô sẽ chạm luồng xuất Excel, copy vùng và các công thức tham chiếu ô; dấu hiệu đặt ở header là đủ để nói ra sự thật mà không chạm dữ liệu hiển thị.
- **(default)** Kết luận "cột này chưa có số" chỉ được đưa ra khi kỳ đang xem có ít nhất một dòng dữ liệu. Kỳ 0 dòng thì không hiện nhãn gì — không có cơ sở để phân biệt "chưa tính" với "chưa có nhân viên nào".
- **(default)** Endpoint reorder cho phép đổi thứ tự của cả cột `is_system`. Đây chỉ là thứ tự hiển thị, không phải ngữ nghĩa tính toán (thứ tự tính là topological sort theo phụ thuộc trong `engine.go:buildOrder`, hoàn toàn độc lập với `seq`). Nếu chặn `is_system` thì người dùng không sắp được cột `NET_PAY`/`PIT` về đúng chỗ họ muốn, mà đó lại là các cột họ hay muốn kéo nhất.
- **(default)** Kéo-thả lưu bằng debounce khoảng 800ms và gộp nhiều cú kéo liên tiếp thành một lần gọi API, thay vì gọi ngay mỗi cú kéo. Tránh spam endpoint khi người dùng sắp xếp liên tục nhiều cột.
- **(default)** Phần số học của báo cáo tác động chạy trên **kỳ đang được chọn** ở giao diện, không phải mọi kỳ. Chạy nhiều kỳ nhân chi phí mô phỏng lên nhiều lần mà không thêm thông tin quyết định.
- **(default)** Thiếu danh sách lương thì phần tĩnh vẫn hiện bình thường, chỉ phần số học bị chặn. Người dùng vẫn nhận được nửa giá trị thay vì không nhận được gì.
- **(default)** `topEmployees` trong báo cáo giới hạn ở 20 dòng lệch lớn nhất và số này được nói rõ trên giao diện (không cắt im lặng).
- **(default)** Phần tĩnh của tác động tính closure phụ thuộc **nhiều tầng** (cột A dùng B, B dùng cột đang sửa → A cũng được liệt kê, có ghi rõ là gián tiếp), không chỉ một tầng trực tiếp. Một tầng sẽ bỏ sót đúng các cột tổng (`GROSS`, `TAXABLE_INC`, `NET_PAY`) — vốn là các cột người dùng quan tâm nhất.

## Agent Task Assignment

| Task | Agent (CLI) | Lý do chọn | Status |
|---|---|---|---|
| Task 1 — endpoint usage | claude-cli | Đụng logic phụ thuộc công thức và bốn bảng không có FK; đếm sai một nhóm là cảnh báo sai cho người dùng trước khi họ xoá dữ liệu thật. Không giao CLI rẻ. | pending |
| Task 2 — endpoint reorder | claude-cli | Ghi `seq` trong transaction, có audit; nhỏ nhưng chạm bảng cấu hình dùng chung cả hai sheet. | pending |
| Task 3 — dialog xoá | claude-cli | Phải giữ nguyên nhánh 409 cũ trong khi thêm nhánh cảnh báo mới; hồi quy ở đây làm mất khả năng chặn xoá đang có. | pending |
| Task 4 — nhãn chưa tính | claude-cli | Sửa `mapRow`/`buildLiveCols` — đường dữ liệu dùng chung cho mọi sheet lương; sai ở đây ảnh hưởng toàn bộ lưới. | pending |
| Task 5 — kéo-thả lưu thật | claude-cli | `moveColumn` có bẫy closure/ref đã ghi trong code (`TinhLuongExcel.tsx:954-958`) và bug remap vùng chọn đã từng xảy ra; cần người hiểu ngữ cảnh. | pending |
| Task 6 — endpoint formula-impact | claude-cli | Rủi ro cao nhất cả gói: mô phỏng trên đường tính tiền, và phải cố ý không lặp lại bug `salaryOverrides` rỗng của endpoint tiền lệ. | pending |
| Task 7 — panel tác động FE | claude-cli | Nối hai luồng sửa công thức khác nhau (modal và sửa-tại-chỗ) vào cùng một panel, phải khớp hợp đồng API client thật. | pending |
| Task 8 — test khoá bất biến | claude-cli | Test là thứ duy nhất chứng minh TASK-REF và TASK-REF; viết hộ bằng CLI rẻ thì mất chính giá trị của nó. | pending |
| Task 9 — tài liệu | claude-cli | Tài liệu người đọc, theo quy ước file canonical theo ngày của dự án. | pending |

Toàn bộ dồn về `claude-cli` một cách có chủ ý: mọi task đều đụng hoặc đường tính tiền, hoặc cơ chế chặn xoá đang bảo vệ dữ liệu, hoặc dữ liệu dùng chung của cả hai sheet. Không có task nào thuộc loại boilerplate độc lập — vốn là điều kiện để giao cho CLI rẻ theo bảng chi phí của `orca-workflow`.

**Về sequence diagram và vị trí file:** cố ý không có diagram, và file này nằm ở `self-docs/` chứ không ở `llmwiki/wiki/sources/draft/`. Quy ước máy local (`CLAUDE.md`, mục "Quy ước máy local này") cấm tạo file HTML trong `llmwiki/html/`, nêu đích danh cả `/propose`; trong khi rule R7 của harness lại chặn mọi draft trong `sources/draft/` không có companion `.html`. Hai luật đụng nhau, và quy ước của người dùng thắng: không tạo HTML, và tài liệu về nằm đúng chỗ mà `CLAUDE.md` chỉ định cho mọi tài liệu mô tả công việc. Đây cũng là file canonical của hạng mục theo quy ước "một file theo ngày, cập nhật liên tục" — Task 9 sẽ cập nhật tiếp vào chính file này khi thi hành, không tạo file mới. Về nội dung, phạm vi này cũng không có luồng nhiều bên cần vẽ: ba endpoint đọc/mô phỏng và bốn điểm sửa UI đã được mô tả đủ ở `## Plan`.

## Self-review

Ba mắt lưới theo yêu cầu của skill, đã soi lại và sửa tại chỗ trước khi trình:

1. **Phủ yêu cầu.** Bốn yêu cầu gốc của người dùng ánh xạ hết và không trùng: "thêm rule thì bảng lương thêm cột" → đã chạy sẵn (Sự thật #1), phần còn thiếu là Task 4 (TASK-REF, TASK-REF); "xoá cột ở salary rule thì bên kia xoá" → đã chạy sẵn ở mức hiển thị, phần còn thiếu là Task 1 + Task 3 (TASK-REF đến TASK-REF); "kiểm tra thứ tự hai sheet có đồng bộ" → đã trả lời trong Sự thật #6, #7 và xử lý ở Task 2 + Task 5 (TASK-REF đến TASK-REF); "thêm tính năng kiểm tra impact nếu edit rule" → Task 1 (phần tĩnh) + Task 6 + Task 7 (TASK-REF đến TASK-REF). Mỗi FR có ít nhất một task, mỗi task neo vào ít nhất một FR.
2. **Quét placeholder.** Không còn chỗ nào để trống dạng chờ-điền-sau, không còn câu mô tả chung chung kiểu "làm cho hợp lý" hay "giống task phía trên". Một chỗ ở bản nháp đầu chỉ ghi là sẽ cảnh báo mà không nói cảnh báo cái gì, đã được thay bằng nội dung cụ thể ở TASK-REF (phân nhóm bị-xoá-theo / bị-gỡ-tham-chiếu / để-lại-mồ-côi, cộng bước tick xác nhận riêng).
3. **Nhất quán tên-kiểu.** Ba route mới được gọi đúng một tên xuyên suốt: `GET /config/salary-components/{id}/usage`, `PUT /config/salary-components/reorder`, `POST /Core System/formula-impact/{periodId}`. Bản nháp đầu có lúc gọi endpoint thứ nhất là `/dependents` ở mục Plan và `/usage` ở mục FR — đã thống nhất thành `/usage` vì nó phục vụ cả hai chỗ dùng (xoá và sửa), không chỉ phần phụ thuộc.

Một điểm tự phản biện còn để mở, có ý thức: phần số học của báo cáo tác động phụ thuộc vào việc người dùng đã nạp danh sách lương ở cùng phiên trình duyệt. Với quyết định "không thêm upload vào UI Excel", điều này nghĩa là trong nhiều trường hợp thực tế người dùng sẽ chỉ thấy phần tĩnh. Đó là đánh đổi đã được người dùng chọn tường minh sau khi được trình bày cả bốn phương án; SPEC này không cố lách nó bằng cách âm thầm chạy mô phỏng với `BASIC_SAL` rỗng — chính vì làm vậy sẽ tái tạo đúng lỗi đang có ở `ComputeTemplateImpact`.

## Origin

- **Draft:** `self-docs/Salary-Column-Sync-Impact-280726.md` (file canonical của hạng mục, xem ghi chú vị trí file ở mục Agent Task Assignment)
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_

---

# Kết quả thi hành (2026-07-28)

Thi hành theo `llmwiki/wiki/sources/draft/280726-salary-column-sync-and-edit-impact-PLAN.md`, đúng thứ tự lát cắt A → C → B → D rồi Task 8 + 9. Không migration DB (đúng ràng buộc PLAN — không phát sinh nhu cầu nào).

## Bảng 9 task

| Task | Nội dung | Repo / commit |
|---|---|---|
| 1 | `GET /config/salary-components/{id}/usage` + closure phụ thuộc nhiều tầng | `Core System-backend@93303ad` |
| 3 | Dialog xoá cột hiện đủ 3 nhóm hệ quả + tick xác nhận | `Core System-frontend@56ddded` |
| 4 | Nhãn "chưa tính cho kỳ này" ở header + tooltip 2 kịch bản | `Core System-frontend@560868a` |
| 2 | `PUT /config/salary-components/reorder` (ghi `seq`, transaction, audit) | `Core System-backend@5fa961f` |
| 5 | Kéo-thả lưu thật xuống `seq`, debounce 800ms | `Core System-frontend@34e105c` |
| 6 | `POST /Core System/formula-impact/{periodId}` (mô phỏng, 422 khi thiếu lương) | `Core System-backend@1bc278f` |
| 7 | `FormulaImpactPanel` dùng chung 2 luồng sửa công thức | `Core System-frontend@e81bb22` |
| 8 | Kiểm chứng tổng hợp (không sửa code, không phát sinh commit) | — |
| 9 | Tài liệu (file này + 2 `routes-permissions.md` + `document-map.md` + `CLAUDE.md`) | `Core System-backend@63dff55`, `Core System-frontend@6adf6fc` |

Cả 2 repo trên nhánh `feature_1` (đã kiểm bằng `git branch --show-current` trước khi sửa). **Chưa push** — chỉ commit theo yêu cầu.

## Bằng chứng test

**Backend** — baseline đo TRƯỚC khi sửa gì: đúng 4 fail (`TestReportPayrollSummaryRouteRequiresPeriodID`, `TestReportBankTransferRouteRequiresPeriodID`, `TestPipelineProtectedRunRouteWithDevAuthReachesHandler`, `TestPipelineProtectedLogsRouteWithDevAuthReachesHandler`). Sau mỗi task và ở Task 8: vẫn **đúng 4 fail đó**, không thêm, không đổi. `go vet ./...` sạch mọi lần.

Test mới:
- `internal/repository/salary_component_usage_integration_test.go` — 2 test (đếm đủ 4 nhóm liên quan; reorder ghi `seq` đúng thứ tự kể cả cột `is_system`).
- `internal/service/payroll_formula_impact_integration_test.go` — 2 test (từ chối khi `salaries` rỗng; delta đúng độ lớn + `payroll_records` không đổi số dòng).

**Frontend** — `npx tsc --noEmit` sạch; `npx eslint .` 0 error / 13 warning (toàn bộ ở file không đụng tới: `PayrollPage.tsx`, `data-grid-excel.tsx`, `useHeadDescription.ts`, `useHeadTitle.ts`); `npx vitest run` 20/20 pass (5 file — 17 test có sẵn + 3 test mới); `npm run build` (next build sản xuất thật) `✓ Compiled successfully` sau **mỗi** task FE, không chỉ chạy `tsc`.

Test mới: `components-page/tinh-luong/data.notcomputed.test.ts` — 3 test phân biệt "key vắng" / "giá trị 0" / "kỳ 0 dòng".

## TASK-REF — `payroll_records` không bị chạm

Đo trên `payroll_engine` trước và sau khi chạy TOÀN BỘ `go test ./...`:

```
truoc:  6435 | 2026-07-24 14:16:11.817263+07 | 46716902711
sau:    6435 | 2026-07-24 14:16:11.817263+07 | 46716902711
```

Giống nhau cả 3 chỉ số (số dòng, `max(updated_at)`, tổng `NET_PAY`). Ngoài ra 5 truy vấn dọn dẹp đều trả 0: không sót `salary_components` mã `ZZ_*`, không sót kỳ `year = 2099`, không sót `employees` mã `ZZ*`, không sót `attendance_summary`, không sót `payroll_templates` thử nghiệm.

**Chưa làm:** bước gọi endpoint `formula-impact` qua HTTP bằng token thật (PLAN Task 8 Step 3). Cần tài khoản đăng nhập, phiên này không có. Bất biến "không ghi DB" đã được khoá ở tầng service bằng test đếm dòng trước/sau, và đối chiếu lại ở mức toàn bộ DB như trên — nhưng đường HTTP thì chưa có ai bấm thật.

## Ba ràng buộc tuyệt đối — cách đã kiểm, không chỉ tuyên bố

1. **Không thêm hành động tính lương vào UI Excel.** `grep -rn "calculatePayroll\|calculateOne" components-page/tinh-luong/` → **0 kết quả**. Call site duy nhất vẫn là `PayrollPage.tsx` + định nghĩa ở `lib/api/Core System.ts`.
2. **`formula-impact` truyền `salaries` vào cả hai lần mô phỏng.** Trong thân `ComputeFormulaImpact`, số lần xuất hiện `salaryOverrides: map[string]float64{}` = **0**; cả `shBefore` lẫn `shAfter` dựng từ **cùng một** closure `mkShared` mang `salaryOverrides: in.Salaries`, nên không tồn tại đường nào để một nhánh mất danh sách lương. Test khoá thêm bằng cách neo công thức ứng viên vào `[BASIC_SAL]`: nếu ai đó bỏ `salaries` đi thì `BASIC_SAL = 0`, delta = 0, và test fail ngay.
3. **Không sửa `ComputeTemplateImpact`, không hồi sinh UI template.** `git diff` của `internal/service/payroll_service.go` là **+208 / −0** — thuần thêm mới, không xoá/sửa dòng nào của hàm cũ. Không đụng file FE nào thuộc nhóm template.

## Những chỗ PLAN ghi sai so với code thật (phần giá trị nhất cho người đọc sau)

PLAN chủ động đánh dấu 3 chỗ "phải grep xác minh, đừng đoán" — cả 3 đều **đúng là sai nếu đoán bừa**:

| PLAN viết | Code thật | Hệ quả nếu tin PLAN |
|---|---|---|
| `toFloat(...)` trong package `service` | **`asFloat`** (`internal/service/engine.go:644`) | không biên dịch được |
| `uuidParse(body.ComponentID)` trong package `handler` | không tồn tại; chỉ có `parseUUID(w, r, param)` (đọc từ URL, không nhận string) | không biên dịch được → đã dùng `uuid.Parse` + import `github.com/google/uuid` |
| `PayrollPeriod` có thể không có field `status` | **có** (`lib/api/types.ts:854`) | nhánh phân biệt kỳ đã chốt vẫn dùng được, không phải bỏ như PLAN dự phòng |

Bốn chỗ PLAN sai mà PLAN **không** lường trước, phát hiện khi thi hành:

1. **Fixture `payroll_periods` thiếu 3 cột NOT NULL.** PLAN insert `(id, month, year, status)`; thực tế `name`, `start_date`, `end_date` đều `NOT NULL` không default → test sẽ vỡ ngay. Đã bổ sung.
2. **`dbtest` không có helper `QueryRow`.** PLAN dùng `dbtest.QueryRow(...)`; package chỉ có `Open` và `Exec`. Đã dùng `db.Get(...)` của sqlx.
3. **Fixture Task 6 của PLAN làm test xanh giả.** PLAN cho công thức ứng viên là `[ZZ_IMPACT_BASE] * 2` với `ZZ_IMPACT_BASE` là cột `input` không có nguồn giá trị nào → luôn bằng 0, nhân 2 vẫn 0, delta = 0 và `EmployeesAffected = 0` → test fail (hoặc tệ hơn: nếu ai nới điều kiện, test xanh mà không chứng minh gì). Đã đổi cột thử nghiệm thành `formula` neo vào `[BASIC_SAL]`, ứng viên `[BASIC_SAL] * 2`, khẳng định delta đúng bằng `+10.000.000` với `BASIC_SAL = 10tr`. Đây mới là test thật sự khoá được ràng buộc #2.
4. **`loadSalarySession()` gọi thẳng trong thân render.** PLAN đặt ở thân component; `sessionStorage` không tồn tại lúc Next prerender nên giá trị server luôn là `[]` còn client có thể khác → lệch hydration. Đã chuyển vào `useEffect` + state.

Một cái bẫy tiền tồn tại đã tránh: `gofmt -l` báo `internal/service/salary_component_service.go` chưa format, nhưng diff cho thấy nó muốn đổi `''` thành smart-quote `”` ở **dòng 32 — comment có sẵn, không phải code mới**, và bản `HEAD` cũng bị báo y hệt. Đúng sự cố đã ghi ở nhật ký 270726 (`gofmt -w` blanket làm hỏng chính file này). **Không** chạy `gofmt -w` lên file đó; các file còn lại đều đã sạch.

## Vòng kiểm chứng độc lập ở tầng HTTP thật (cùng ngày, sau khi thi hành) — tìm ra 2 lỗi mà không lớp gate nào bắt được

Phiên thi hành để lại hai món nợ: chưa kiểm tay trình duyệt, và chưa gọi `formula-impact` qua HTTP bằng token thật (Task 8 Step 3). Món thứ hai **đóng được không cần trình duyệt**: `internal/middleware/auth.go:205` có sẵn cơ chế bypass `Authorization: Bearer dev` khi `DEV_USER_EMAIL` được set, và `.env` local đã set (`database.go:51` còn tự cấp super-admin cho email đó). Chạy server bằng `AUTO_MIGRATE=false go run ./cmd/Core System` để không ghi gì vào schema/seed, rồi gọi thật.

Việc gọi thật lộ ra hai lỗi mà **`go test`, `go vet`, `tsc --noEmit`, `eslint` và `next build` đều xanh** — tức là không có lớp gate nào của quy trình bắt được:

### Lỗi 1 (nặng): `usage` trả `null` thay vì `[]` → crash render ở trường hợp phổ biến nhất

`GET /config/salary-components/{id}/usage` trên một cột thật trả về:

```json
{ "dependentComponents": [], "overrideRefs": null, "templates": null, ... }
```

Go marshal slice `nil` thành `null`. Frontend gọi thẳng `.length`/`.map` lên đúng hai field đó ở **6 chỗ** (`DeleteColumnDialog.tsx:86,88,98,100,101` và `FormulaImpactPanel.tsx:71,74`) → `TypeError` trong thân render → trắng màn hình. Và đây không phải trường hợp hiếm mà là **trường hợp phổ biến nhất**: hầu hết cột không có override nào, còn template thì hiện chưa có dòng nào tồn tại trong DB. Nghĩa là dialog xoá cột và panel tác động **hầu như luôn** vỡ khi mở.

Vì sao mọi gate đều xanh: kiểu TypeScript khai `overrideRefs: OverrideRef[]` — không-nullable. Type **nói dối** về thứ API thật trả về, nên `tsc` không có gì để phàn nàn; `next build` chỉ biên dịch, không gọi API; test Go chỉ kiểm struct, không kiểm JSON. Lớp duy nhất bắt được là gọi thật hoặc mở trình duyệt.

Đã sửa hai lớp: `GetUsage` luôn coerce `nil → []` trước khi trả (`salary_component_repo.go`), và `getSalaryComponentUsage` ở API client chuẩn hoá `?? []` (`lib/api/config.ts`) làm chốt thứ hai cho mọi consumer sau này. Test mới `TestIntegrationSalaryComponentGetUsageNeverMarshalsNullSlices` khoá bất biến **ở tầng JSON thật** (`json.Marshal` rồi tìm chuỗi `null`), không chỉ ở tầng struct. Xác nhận lại bằng chính request đã crash: giờ trả `[]`.

### Lỗi 2: `ComputeFormulaImpact` spam log và vu oan cho PIT

Chạy test Task 6 in ra `[PIT] TAXABLE_INC non-numeric string: "ZZIMP1"` — `ZZIMP1` là **mã nhân viên**, không phải thu nhập chịu thuế. Truy ra: vòng diff của `ComputeFormulaImpact` (do PLAN viết) quét **mù mọi key** của bản đồ giá trị bằng `asFloat()`, mà bản đồ đó chứa cả field chuỗi (`EMPLOYEE_CODE`, `PERSONAL_TAX_CODE`, `PERSONAL_SOCIAL_INS_NUMBER`) và uuid (`EMPLOYEE_ID`) — xem `initValues`. `asFloat()` ở `engine.go:681` log một dòng cho **mọi** chuỗi không phải số, với nội dung hardcode chữ `[PIT] TAXABLE_INC` từ thời nó còn là hàm riêng của PIT.

Hai hệ quả thật: (a) ~4 dòng log mỗi nhân viên mỗi lần mô phỏng — kỳ 12.000 người là khoảng **100.000 dòng log cho MỘT lần bấm nút**, mà đây là nút người dùng bấm được nhiều lần, đủ để chôn log lỗi thật; (b) ai đọc log sẽ đi truy một bug PIT không tồn tại. Độ chính xác của báo cáo thì không bị ảnh hưởng (chuỗi giống nhau ở hai lần đều quy về 0 nên không sinh delta giả).

Đã thêm `numericValue()` — như `asFloat()` nhưng **trả cờ** thay vì im lặng quy về 0, và không log gì — rồi cho vòng diff bỏ qua key không phải số. Test `TestIntegrationComputeFormulaImpactDoesNotSpamAsFloatLog` khoá bất biến bằng cách capture `log.Writer()` và đếm số dòng, cộng unit test `TestNumericValueRejectsNonNumericWithoutCoercing` cho hàm thuần.

### Task 8 Step 3 — đã đóng, bằng chứng cụ thể

Ảnh chụp `payroll_records` trước và sau khi gọi `POST /Core System/formula-impact/{periodId}` thật (299 dòng lương, kỳ 05/2026, công thức ứng viên `[BASIC_SAL] + [RESPONSIBILITY_ALLOW] + 1000`), so cả ba đại lượng gồm md5 của toàn bộ `computed_values`:

```
trước: 6435 | 2026-07-24 14:16:11.817263+07 | 202a20ec949db110efa1d304b456f6b7
sau  : 6435 | 2026-07-24 14:16:11.817263+07 | 202a20ec949db110efa1d304b456f6b7
```

Kết quả trả về đúng số học kiểm được bằng tay: `employeesAffected` 3273/3273, `byComponent` đúng một dòng `CONTRACT_TOTAL` với delta `3.273.000` = 3273 × 1000. Nhánh 422 khi thiếu `salaries` trả đúng thông báo tiếng Việt. Route `reorder` kiểm được nhánh xác thực mà **không** ghi vào `seq` thật: danh sách thiếu → 400 kèm `"danh sách phải gồm đủ 110 mã cột, nhận được 1"`, mã không tồn tại → 400, không token → 401.

### Một quan sát UX, chưa sửa

Trong lần gọi thật ở trên, `totalNetDelta = 0` trong khi `CONTRACT_TOTAL` lệch 3,27 triệu — vì `CONTRACT_TOTAL` không nằm trên đường dẫn tới `NET_PAY`. Panel FE hiện số nhân viên bị ảnh hưởng trước (3273) nên người dùng vẫn thấy có tác động, nhưng câu "Tổng thực lãnh lệch 0 đ" đứng ngay cạnh đó dễ đọc thành "không ảnh hưởng gì". Đáng chỉnh câu chữ khi có dịp — cùng họ với chính rủi ro mà TASK-REF sinh ra để chống.

### Bằng chứng sau vòng sửa

`go vet ./...` sạch; `go test ./...` đúng 4 fail baseline cũ (2 report route + 2 pipeline route), không hồi quy. `tsc --noEmit` sạch, `eslint` sạch, `vitest run` 20/20 PASS, `next build` `✓ Compiled successfully` (41/41 trang). Commit: `Core System-backend@9fe9147`, `Core System-frontend@f8b9bb0`.

## Còn nợ

- **Chưa kiểm tay trên trình duyệt** bất kỳ màn hình nào trong 4 điểm sửa FE (dialog xoá, nhãn ⚠ + tooltip, kéo-thả 2 sheet, panel tác động 2 kịch bản). PLAN có các bước này (Task 3 Step 5, Task 4 Step 6, Task 5 Step 4, Task 7 Step 5) — vẫn là việc còn lại. **Lỗi 1 ở mục trên là bằng chứng trực tiếp rằng bước này không thay thế được bằng test và build**: một lỗi làm trắng màn hình ở trường hợp phổ biến nhất đã sống qua toàn bộ `go test` + `tsc` + `eslint` + `next build` mà không ai thấy.
- **Chưa push** cả 2 repo.
- Bug `ComputeTemplateImpact` vẫn còn nguyên, có chủ ý (nhóm template đang hold). Comment trong `ComputeFormulaImpact` trỏ thẳng vào `payroll_service.go:713`/`:720` để ai gỡ hold sau này tìm được ngay.
- Câu chữ `totalNetDelta` ở panel tác động (quan sát UX ở mục trên) — chưa sửa.
