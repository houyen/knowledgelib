---
id: self-docs/engine/report-template-config-uiux-excel-style
canonical_question: 'Technical guide and specification: Report Template Config — Cải
  thiện UI/UX theo style Excel'
aliases:
- Report Template Config — Cải thiện UI/UX theo style Excel
- Report Template Config UIUX Excel Style 200826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Report Template Config — Cải thiện UI/UX theo style Excel (200826)

Canonical cho hạng mục UI/UX của màn "Cấu hình > Template báo cáo" (khác `Report-Template-Config-Analysis-040826.md` — file đó là phân tích chức năng/logic gốc). File này gộp cập nhật liên tục nếu còn việc UI/UX tiếp theo cho đúng màn này.

**Cập nhật đợt 2 (cùng ngày 200826):** sau đợt 1 (2 việc: dời nút "+ Thêm template báo cáo" + mockup xem trước — xem mục dưới), user yêu cầu lên plan và thi hành tiếp 8 ý tưởng UI/UX đã đề xuất trong hội thoại. Đã hỏi lại 3 điểm đánh đổi hành vi thật qua `AskUserQuestion` trước khi khoá phạm vi (user chọn phương án an toàn cho cả 3) — xem mục "Phase 2 (đợt thi hành thứ hai)" bên dưới.

## Bối cảnh

User gửi 2 screenshot (danh sách template + sheet Sửa) và nhận xét: cả app theo concept "Excel" nhưng 2 điểm lệch style:
1. Nút "+ Thêm template báo cáo" (màn danh sách) nằm lẫn trong formula bar (thanh `fx` cao 32px) — không đúng vị trí Excel, thanh đó không có chỗ cho action lớn.
2. Màn Sửa template (`Sửa: demo 01`) không cho biết báo cáo xuất ra sẽ có HÌNH DẠNG ra sao — user muốn ý tưởng "mockup".

Quyết định: làm thẳng trên FE, tại local, trên đúng 2 nhánh đang checkout sẵn (`Core System-frontend@feature_v2`, `Core System-backend@release/uat-180826` — không cần đụng BE cho việc này). User cho phép tự do sửa, xoá được nếu không ưng.

## Thay đổi

File duy nhất bị sửa: `Core System-frontend/components-page/tinh-luong/TinhLuongExcel.tsx` (không đụng BE — không cần API mới, dùng lại dữ liệu `data.emps`/`data.cols` đã tải sẵn ở client).

### 1. Dời nút "+ Thêm template báo cáo" ra khỏi formula bar

- Trước: nút nằm trong dải `fx` (dòng ~7355-7420 cũ), style outline (border, nền trong suốt) — khác hẳn nút cùng vị trí của các sheet khác ("+ Thêm vai trò" dùng nền đặc).
- Sau: 1 hàng toolbar riêng ngay trên lưới, đúng khuôn đã có sẵn cho sheet "Gán quyền NV" (đếm số dòng bên trái, nút nền đặc bên phải, `marginLeft: "auto"`). Chỉ hiện khi `sheet.id === REPORT_TEMPLATES_SHEET_ID`, giữ nguyên gate quyền `canManageSalaryComponents`.
- Kết quả: formula bar gọn lại đúng vai trò (tên ô + fx), nút thêm có hàng riêng đủ chỗ, đồng bộ với các sheet danh sách khác trong app.

### 2. Mockup "Xem trước hình dạng báo cáo" trong sheet Sửa/Tạo

Thêm 1 khối ngay dưới "+ Thêm dòng" (trước vùng lỗi), render bằng đúng khuôn lưới Excel thật (chữ cái cột A/B/C.., gutter số dòng, header nền accent) — tái dùng style `letterHead`/`fieldHead`/`gutterCell`/`dataCell` đã có ở `ApprovalRulesPanel` để nhất quán toàn app, và hàm `colLetter()` module-level đã có sẵn (không viết lại).

Logic hiển thị 1 dòng dữ liệu mẫu:
- Chỉ hiện cột KHÔNG bị tick "Ẩn khỏi báo cáo" (`form.lines.filter(l => !l.hidden)`), đúng thứ tự thật.
- `sourceKind = "identity"`: map sang field tương ứng trên `Emp` đã tải (`employee_code→id, full_name→name, department→dept, position→title, level_name→level`; `company_code` chưa có sẵn client-side → hiện placeholder `(mã CT)`).
- `sourceKind = "component"`: đọc trực tiếp `emp[sourceCode]` (giá trị THẬT đã tính sẵn cho kỳ đang xem, không gọi thêm API) + format qua `fmtValue` với `Col` tra từ `data.cols`.
- `sourceKind = "sum"`: cộng thật các mã trong `sumCodes` từ cùng 1 nhân viên mẫu.
- `sourceKind = "expr"`: hiện `"…"` in nghiêng màu nhạt + `title` giải thích — KHÔNG có evaluator công thức ở FE (logic `evalExpression`/alias chỉ có trong `report_run_service.go`, chạy lúc "Chạy template báo cáo" sau khi Lưu) → cố tình không giả lập số để tránh hiểu lầm là giá trị thật.
- Nhân viên mẫu: `data.emps[0]`, fallback `SAMPLE_EMPS[0]` (đã có sẵn trong `data.ts`, dùng khi kỳ/công ty đang chọn 0 dòng lương).
- Luôn có dòng chữ giải thích rõ đây là "1 dòng dữ liệu mẫu, KHÔNG phải kết quả cuối" — tránh nhầm với "Chạy template báo cáo" (kết quả thật, toàn công ty/kỳ, chỉ chạy được SAU khi Lưu).

**Không tự tạo endpoint preview/run ad-hoc mới ở BE** — đã khảo sát `ReportRunService.Run` (`report_run_service.go:61`) bắt buộc `templateID` đã lưu (gọi `templateRepo.GetByID` đầu tiên) + chạy trên toàn bộ `payroll_records` của kỳ, không có đường "chạy thử chưa lưu". Việc mockup client-side này cố ý CHỈ xấp xỉ hình dạng (đúng cột/nhãn/thứ tự + giá trị thật cho identity/component/sum), KHÔNG cố mô phỏng `expr` — nếu sau này cần preview thật cho `expr` trước khi lưu, sẽ cần 1 endpoint mới bên BE (chưa làm, ngoài phạm vi hôm nay).

## Kiểm chứng

- `npx tsc --noEmit`: không phát sinh lỗi nào ở `TinhLuongExcel.tsx` (3 lỗi hiện có trong `public/backup/payslip-lib.test.ts` là tiền tồn tại, không liên quan).
- `npx eslint components-page/tinh-luong/TinhLuongExcel.tsx`: sạch.
- Kiểm bằng trình duyệt thật (Playwright, dev server local đang chạy sẵn ở `:3000`/`:8080`, dev-bypass qua `devLogin`): script tạm mở sheet "Template báo cáo" → chụp xác nhận toolbar mới đúng vị trí (đếm "0 template báo cáo" + nút xanh đặc bên phải, formula bar gọn); mở sheet Sửa mới, điền 2 dòng ("Mã NV" = Thông tin NV, "Lương GROSS" = 1 cột lương chọn `DIFF_DAYS`) → mockup hiện đúng header A/B + nhãn + 1 dòng dữ liệu THẬT của nhân viên mẫu (`000023`, `0,00`). Đã xoá script tạm sau khi kiểm xong (`e2e/zz-visual-check.spec.ts`), không có test mới nào được thêm vào bộ suite chính thức.

## Trạng thái git (đợt 1)

`Core System-frontend@feature_v2`: 1 file sửa (`components-page/tinh-luong/TinhLuongExcel.tsx`), **chưa commit**. `Core System-backend@release/uat-180826`: không đụng, không có thay đổi.

---

## Phase 2 (đợt thi hành thứ hai) — 5/8 ý tưởng còn lại

Sau đợt 1, user yêu cầu lên plan cho 8 ý tưởng UI/UX đã đề xuất trước đó rồi thi hành. Trước khi khoá plan, hỏi lại 3 điểm có ảnh hưởng hành vi thật qua `AskUserQuestion` (không tự quyết vì đây là đánh đổi UX thật, không phải chỉ đổi giao diện):

| Ý tưởng | User chọn | Kết quả |
|---|---|---|
| #2 Dồn công thức tuỳ chỉnh vào 1 thanh `fx` chung | **Giữ ô công thức tại từng dòng** (an toàn) | Không làm — giữ nguyên overlay tô màu công thức tại mỗi dòng như cũ |
| #6 Gộp nút Lưu/Huỷ vào nút Lưu ribbon | **Giữ nút Lưu/Huỷ riêng cho sheet template** (an toàn) | Không làm — không đụng logic nút Lưu ribbon (đang phục vụ Ô LƯƠNG, nghiệp vụ khác) |
| #4 "+ Thêm dòng" → dòng trống tự thêm khi gõ | **Giữ nút "+ Thêm dòng"** (an toàn) | Không đổi nút; thay vào đó Enter ở dòng cuối (Phase 5) tự thêm dòng mới — đạt hiệu quả tương tự mà không có rủi ro nhầm dòng mẫu |

→ Phạm vi thi hành rút xuống 5 việc, làm tuần tự, mỗi phase build (`tsc`/`eslint`) + kiểm bằng Playwright thật trên dev server local trước khi qua phase sau:

### Phase 1 — Khung lưới Excel thật cho "Cột/dòng"
Đổi từ `<div style="display:grid">` sang `<table>` thật: header chữ cái A-E (tái dùng `colLetter()` module-level đã có), gutter số dòng, border kẻ đủ 4 cạnh mỗi ô — khuôn `letterHead`/`fieldHead`/`gutterCell`/`dataCell` y hệt `ApprovalRulesPanel` (đưa các style này lên khai 1 lần đầu IIFE, dùng chung cho cả bảng editor lẫn khối mockup preview, bỏ khai trùng).

### Phase 3 — Gộp "Tên template"/"Mô tả" vào chính lưới
2 input này giờ là 2 dòng số 1/2 của CHÍNH bảng (merge `colSpan={5}`), không còn tách riêng phía trên — làm cùng lúc với Phase 1 vì chung 1 table. Đánh số dòng liên tục cho cả sheet: 1=Tên template, 2=Mô tả, header field (Nhãn hiển thị/Vai trò/...) không đánh số (theo đúng quy ước đã có ở `ApprovalRulesPanel`/mockup preview — header luôn gutter trống), rồi dòng dữ liệu Cột/dòng đánh số tiếp 3,4,5...

### Phase 4 — Tô màu theo Vai trò
Thêm `ROLE_ROW_TINT` (màu nhạt riêng cho `earning`/`deduction`/`employer_cost`/`total`, `info` để trong suốt) — tô nền cả dòng dữ liệu (không chỉ ô Vai trò) để dễ quét mắt theo nhóm, có set khác nhau cho dark/light qua biến `dark` sẵn có trong closure.

### Phase 2 — Right-click context menu ở gutter số dòng
Thêm state UI cục bộ `reportLineMenu` (`useState`, không nhét vào state chính vì thuần UI tạm) + 2 hàm mới `insertReportTemplateEditLine(idx, before)` / `duplicateReportTemplateEditLine(idx)` (hàm xoá dòng tái dùng nguyên hàm cũ). Menu có 4 mục: Chèn dòng trên/dưới, Sao chép dòng, Xoá dòng.

**Bug tự phát hiện + tự sửa ngay trong lúc kiểm bằng Playwright (không có trong PLAN):** bản đầu dùng `createPortal(..., document.body)` giống `colFilterPanel` đã có sẵn trong file — nhưng chụp ảnh thật lộ ra nền menu TRONG SUỐT, chữ lưới bên dưới lộ xuyên qua. Nguyên nhân: biến CSS `--tl-bg`/`--tl-text`/... chỉ khai trong rule `.tl-root { ... }` (đọc đúng comment sẵn có trong file giải thích lý do đặt class này ở div ngoài cùng), mà `document.body` là SIBLING của `.tl-root`, không phải con — nên `var(--tl-bg)` không resolve được khi portal thẳng ra `document.body`. Có khả năng `colFilterPanel` cũ cũng mang cùng lỗi này nhưng chưa ai chụp ảnh bắt được (ngoài phạm vi sửa hôm nay, chỉ ghi nhận ở đây để dev sau biết mà kiểm nếu cần). Sửa bằng cách bỏ portal, render menu `position: fixed` ngay trong cây DOM hiện tại (vẫn nằm trong `.tl-root` nên biến CSS resolve đúng) — chụp lại xác nhận nền đặc, đọc rõ.

### Phase 5 — Enter di chuyển xuống dòng dưới (rút gọn theo quyết định ở AskUserQuestion đợt trước)
Chỉ làm cho ô "Nhãn hiển thị" (ô gõ nhiều nhất khi nhập liên tiếp nhiều dòng) — KHÔNG làm Tab-order đầy đủ giữa mọi input/select khác kích thước (rủi ro vỡ hành vi Tab mặc định của trình duyệt, đã quyết định hoãn từ lúc lên plan). Thêm `reportLabelInputRefs` (ref array theo index dòng). Enter ở dòng chưa cuối → focus dòng dưới; Enter ở dòng CUỐI → tự gọi `addReportTemplateEditLine()` rồi focus vào dòng mới tạo (`requestAnimationFrame` đợi React render xong).

## Kiểm chứng (đợt 2)

Sau mỗi phase: `npx tsc --noEmit` + `npx eslint components-page/tinh-luong/TinhLuongExcel.tsx` — sạch xuyên suốt cả 5 phase (0 lỗi mới, 3 lỗi tiền tồn tại ở `public/backup/payslip-lib.test.ts` không đổi). Playwright thật trên dev server local (`devLogin` dev-bypass, script tạm `e2e/zz-visual-check.spec.ts` — viết, chụp, xoá sau mỗi phase, không để lại trong bộ test chính thức):
- Phase 1+3+4: chụp thật cho thấy lưới liền mạch đúng số dòng 1→2→3,4,5, 2 dòng merge Tên/Mô tả, header accent, và dòng role "Thu nhập" tự tô nền xanh nhạt.
- Phase 2: chụp trước/sau khi sửa bug portal — xác nhận menu đọc được chữ, bấm "Sao chép dòng" nhân bản đúng dòng, mockup cập nhật đúng số cột.
- Phase 5: `expect()` đếm số input "Nhãn hiển thị" tăng đúng 1 sau Enter ở dòng cuối (2→3), chụp ảnh xác nhận nội dung gõ tiếp đúng vào dòng mới vừa tự thêm.

## Trạng thái git (sau đợt 2)

`Core System-frontend@feature_v2`: vẫn 1 file sửa (`components-page/tinh-luong/TinhLuongExcel.tsx`, gộp cả đợt 1+2), **chưa commit**. Không có file test tạm nào sót lại trong `e2e/`. `Core System-backend@release/uat-180826`: không đụng.

## Còn lại chưa làm (theo đúng quyết định ở AskUserQuestion, không phải bỏ quên)

Ý #2 (fx-bar chung) và #6 (gộp nút Lưu ribbon) — user chọn KHÔNG làm, giữ hành vi cũ. Ý #4 (dòng trống tự thêm) — user chọn giữ nút cũ, đã thay bằng giải pháp khác ít rủi ro hơn ở Phase 5.

---

## Phase 3 (đợt thi hành thứ ba) — 2 lỗi UI/UX phát hiện khi user tự dùng thật

User tự thao tác thật trên bản đã làm (thêm dòng công thức tuỳ chỉnh `[STD_REPORT] * 2` tham chiếu alias của 1 dòng ẨN) và báo 2 vấn đề bằng ảnh chụp:
1. Cột "Công thức tuỳ chỉnh" trong khối "Xem trước hình dạng báo cáo" không hiện giá trị demo (vẫn `…` từ đợt 1).
2. Template có nhiều dòng (= nhiều cột báo cáo) → cuộn xuống mất luôn hàng chữ cái/nhãn cột, khó biết đang ở cột nào.

### Việc 1 — Bộ tính công thức demo phía FE, khớp đúng ngữ pháp thật của backend

Trước khi viết, đã sai một agent con đọc kỹ `evalExpression` (`Core System-backend/internal/service/engine.go`) để LẤY ĐÚNG ngữ pháp thật, không đoán: hỗ trợ `+ - * /`, đơn nguyên `-`, so sánh `== != < > <= >=`, ngoặc, tham chiếu `[MÃ]`, và các hàm `MIN/MAX/ABS/ROUND/IF/AND/OR/SUM` (không có modulo/luỹ thừa/hàm tự định nghĩa). Biến thiếu trong map → 0 (khớp `fromInterfaceValue(nil)`); lỗi runtime (chia 0, cú pháp hỏng) → "fail-soft" về 0 (khớp `Run()` không chặn cả báo cáo).

Viết `evalReportExprDemo(formula, vals)` trong `ReportTemplateModal.tsx` (file thuần, test không cần jsdom) — tokenizer regex + recursive-descent parser (comparison→additive→multiplicative→unary→atom), **không dùng `eval()`/`new Function()`** (tránh thực thi mã tuỳ ý từ nội dung công thức, dù đây là màn admin-only). 24 test mới trong `ReportTemplateModal.test.ts` khớp từng nhóm cú pháp — pass hết.

Nối vào khối mockup preview (`TinhLuongExcel.tsx`): phải tính **TOÀN BỘ `form.lines` theo đúng thứ tự gốc** (không chỉ dòng đang hiện) để dựng map `vals` tăng dần đúng ngữ nghĩa alias-chỉ-nhìn-về-trước của backend — vì dòng ẨN (`hidden: true`, chỉ dùng làm biến trung gian) vẫn phải nạp alias vào map TRƯỚC khi dòng công thức SAU dùng lại; lọc dòng ẩn phải làm SAU khi tính xong hết, không phải trước (bug logic dễ mắc nếu filter trước). Kiểm bằng ảnh chụp thật: dòng ẩn "Trợ tính" = `[STD_DAYS-ish] - 1`... thực tế test dùng `5 - 1` → alias `STD_REPORT` = 4; dòng hiện "Gấp đôi trợ tính" = `[STD_REPORT] * 2` → mockup hiện đúng **8,00**.

### Việc 2 — Đóng băng hàng tiêu đề khi cuộn (Freeze panes)

Thêm `position: "sticky"` vào `letterHead` (top:0) và `fieldHead` (top:"22px", đúng bằng chiều cao hàng chữ cái) trong bảng "Cột/dòng" — **KHÔNG** thêm vào `gutterCell` gốc (nó bị `rowNumCell`/nhiều style khác spread lại, thêm sticky ở đó sẽ dính nhầm mọi ô số dòng dữ liệu). Thêm 1 style riêng `fieldHeadGutter` cho ô gutter trống đầu hàng nhãn cột, cùng top với `fieldHead` để cả hàng dính liền khối, không hở cột A.

**Bug tự phát hiện + tự sửa khi kiểm bằng Playwright (không có trong dự tính ban đầu):** thêm `position:sticky` xong vẫn KHÔNG đứng lại khi cuộn — chụp ảnh thật bắt lỗi rõ. Nguyên nhân: div bọc bảng có `overflowX: "auto"` riêng (để cuộn ngang khi bảng rộng); theo CSS spec, đặt `overflow-x` khác `visible` mà không đặt `overflow-y` sẽ tự ép `overflow-y` thành `auto` luôn — biến chính div đó thành 1 "scroll container" riêng. Vì div này cao bằng đúng nội dung (không giới hạn chiều cao), nó không bao giờ thực sự cuộn, nên `sticky` bên trong nó bám vào ĐÚNG NÓ (không cuộn = không cần đứng lại) chứ không bám vào div cuộn dọc thật ở ngoài (`flex:1, overflow:"auto"`). Sửa bằng cách bỏ hẳn `overflowX:"auto"` dư thừa ở div này — div cha ngoài đã tự cuộn cả 2 chiều nên không mất khả năng cuộn ngang khi bảng rộng. Sau khi sửa, chụp ảnh xác nhận: cuộn qua 14 dòng, hàng chữ cái A-E + hàng nhãn cột (Nhãn hiển thị/Vai trò/...) đứng cố định phía trên đúng hành vi Freeze panes của Excel.

## Kiểm chứng (đợt 3)

`npx tsc --noEmit` + `npx eslint` sạch (3 file: `TinhLuongExcel.tsx`, `ReportTemplateModal.tsx`, `ReportTemplateModal.test.ts`) — 0 lỗi mới. `npx vitest run ReportTemplateModal.test.ts`: **24/24 pass** (thêm 6 case mới cho `evalReportExprDemo`, giữ nguyên 18 case cũ). Playwright thật trên dev server local (script tạm, xoá sau khi xong): dựng 1 template 6 dòng (2 dòng thường + 1 dòng expr ẩn có alias + 1 dòng expr dùng alias đó) → mockup hiện đúng `8,00`; thêm 10 dòng nữa rồi cuộn tới dòng 14 → header vẫn đứng nguyên tại chỗ.

## Trạng thái git (sau đợt 3)

`Core System-frontend@feature_v2`: 3 file sửa (`TinhLuongExcel.tsx`, `ReportTemplateModal.tsx`, `ReportTemplateModal.test.ts`), **chưa commit** (gộp cả 3 đợt). Không có file test tạm sót lại. `Core System-backend@release/uat-180826`: không đụng (chỉ ĐỌC `engine.go` để lấy đúng ngữ pháp, không sửa BE).

---

## Phase 4 (đợt thi hành thứ tư) — dời nút "+ Thêm template báo cáo" lên ruy-băng (ribbon)

User tiếp tục phản hồi bằng ảnh: dù đã dời khỏi formula bar (đợt 1) ra 1 hàng toolbar riêng, nút vẫn "không giống style đặt nút của Excel" — yêu cầu đưa hẳn lên header/ribbon.

**Khảo sát trước khi sửa:** ruy-băng "Cấu hình" (`SettingsRibbon.tsx`) render từ 1 chuỗi HTML tĩnh `SETTINGS_STATIC` (`ribbon-static.ts`, ghi "AUTO-EXTRACTED... đừng sửa tay") qua `dangerouslySetInnerHTML`; click trên bất kỳ `.xbtn` nào bubble lên 1 handler chung `onSettingsClick` (`TinhLuongExcel.tsx`) so khớp action theo TEXT của nút (`label.includes("Tên nút")`) — không có prop/callback riêng cho từng nút. "Template báo cáo" đã có trong ribbon dưới dạng 1 dòng của sheet "Danh sách cấu hình" (catalog gộp tất cả mục cấu hình), nhưng KHÔNG có icon riêng trên chính dải ribbon — muốn có nút riêng phải thêm cả HTML (icon+nhãn) lẫn nhánh action.

**Thi hành:**
- `ribbon-static.ts`: thêm 1 group mới cuối `SETTINGS_STATIC` — nút "Thêm template báo cáo" (icon trang giấy + dấu cộng xanh, đúng khuôn "Chèn" ở `HOME_DATA`) — hand-edit có chủ đích đi ngược ghi chú auto-extract (cùng tiền lệ đã có ở `FORMULAS_STATIC`, vì nút này không có trong design gốc).
- `TinhLuongExcel.tsx`: thêm 1 nhánh vào `onSettingsClick` — `label.includes("Thêm template báo cáo")` → `openReportTemplateEditSheet(null)`, mở THẲNG sheet Tạo (không qua danh sách trước) — đúng cách Excel đặt lệnh "New" lên ribbon: 1 click ra thẳng hành động.
- Xoá hẳn khối toolbar rời (đếm số dòng + nút đặc) đã thêm ở đợt 1 — hết cần thiết.

Kiểm bằng Playwright thật: chụp ribbon "Cấu hình" thấy nút mới nằm cuối dải, đúng style icon+nhãn như "Kỳ lương"/"Phân quyền"/...; bấm vào mở thẳng "Template báo cáo mới"; `grep` xác nhận 0 dấu vết JSX nút cũ còn lại trong `TinhLuongExcel.tsx` (chỉ còn dòng comment lịch sử). `tsc`/`eslint` sạch (3 lỗi tiền tồn tại `payslip-lib.test.ts` không đổi).

## Trạng thái git (sau đợt 4)

`Core System-frontend@feature_v2`: 4 file sửa (`TinhLuongExcel.tsx`, `ReportTemplateModal.tsx`, `ReportTemplateModal.test.ts`, `ribbon-static.ts`), **chưa commit** (gộp cả 4 đợt). `Core System-backend@release/uat-180826`: không đụng.

---

## Phase 5 (đợt thi hành thứ năm) — 5 ý tưởng cải thiện bảng "Cột/dòng"

User gửi ảnh chụp bảng "Cột/dòng" với dòng "Công thức tuỳ chỉnh" thật (chèn/kiểm/mã nội bộ/ẩn/ghi chú) và nhận xét dòng đó cao gấp ~5 lần dòng thường, cột "Mã cột" phải rộng bất thường cho dòng đơn giản khác — yêu cầu gợi ý cải thiện theo style Excel. Đề xuất 5 ý, user chốt "lên plan rồi thực hiện" (không cần hỏi lại vì đây là quyết định UI/UX kỹ thuật thuần, không phải hành vi nghiệp vụ):

### Phase 1 — Popover cho công thức tuỳ chỉnh
Ô "Mã cột" của dòng `expr` rút về 1 dòng: text công thức (ellipsis), badge mã nội bộ (nếu có), badge "Ẩn" (nếu `hidden`), dấu ✓/✗ (nếu đã kiểm), icon bút để mở popover. Toàn bộ khối sửa đầy đủ cũ (input công thức + overlay tô màu, chèn mã, kiểm tra, mã nội bộ, checkbox ẩn, ghi chú, kết quả kiểm) dời sang 1 popover nổi (`reportExprPopover` state), render **không dùng `createPortal(document.body)`** — theo đúng bài học Phase 2 đợt trước (biến CSS `--tl-*` không resolve ngoài `.tl-root`).

### Phase 2 — Icon thay nút chữ
"Kiểm tra" → icon ✓ trong popover. "Xoá dòng" (cột Thao tác, mọi dòng) → icon thùng rác — right-click ở gutter (đợt trước) đã có mục chữ đầy đủ nên nút này chỉ cần icon + `title`.

### Phase 3 — Bôi đậm dòng đang chọn
`onFocusCapture` ở mỗi `<tr>` set `activeReportLineIdx`; số dòng (gutter) của dòng đó tô nền `accent` + chữ trắng, khớp hành vi Excel luôn tô nổi số dòng active. Không cần `onBlur` (dòng active giữ nguyên tới khi dòng khác được focus — tránh nhấp nháy).

### Phase 4 — Kéo giãn độ rộng cột
Tái dùng NGUYÊN `startColResize`/`effW`/`resizeRef` đã có cho lưới chính (chỉ đổi key sang tiền tố `rtpl_*` để không đụng cột lưới khác) — thêm 1 viền kéo 6px ở mép phải mỗi ô chữ cái. `RTPL_COL_BASE.rtpl_code` (Mã cột) đặt mặc định 340px (đủ cho ô rút gọn ở Phase 1, không cần rộng bất thường như bản cũ).

### Phase 5 — Đóng băng cột A khi cuộn ngang
Thêm `stickyColA` (`position:sticky, left:"34px"`) cho cột "Nhãn hiển thị" (letter "A", field-header, và mọi `<td>` dữ liệu) + gutter số dòng luôn `sticky left:0` — khớp cặp "freeze rows + freeze columns" của Excel.

### 2 bug tự phát hiện + tự sửa khi kiểm bằng Playwright (không có trong dự tính ban đầu)

1. **`table-layout:fixed` không đặt `width` cho `<table>`** → trình duyệt áp "shrink-to-fit", ép bảng co lại đúng bằng khung nhìn hiện có, ĐÈ lên toàn bộ độ rộng đã khai trong `colgroup` mỗi khi tổng vượt khung — kéo cột D rộng ra vẫn bị ép co lại ngay, không có cuộn ngang thật. Bắt bằng cách so `table.getBoundingClientRect().width` (đo được 1238px) với tổng cột khai báo (2462px) qua Playwright — ảnh chụp không đủ để thấy vì trông vẫn "gọn gàng". Sửa: đặt thẳng `width` cho `<table>` bằng tổng đúng các cột, đúng quy tắc CSS 17.5.2 (table width = MAX(width khai báo, tổng cột)).
2. **Cột A bị cột khác đè hình dù đã bám đúng vị trí** — 2 hàng tiêu đề (chữ cái + nhãn cột) đặt `position:sticky` cho MỌI cột (để đứng lại khi cuộn DỌC, làm ở đợt trước), nên B/C/D/E CŨNG là "positioned element" ngang hàng cột A; z-index bằng nhau → trình duyệt vẽ theo thứ tự DOM, cột D (khai sau, rộng 1740px) đè lên cột A. Bắt bằng truy vấn `getBoundingClientRect()` + `getComputedStyle()` thật của TỪNG ô qua Playwright (không phải suy luận từ ảnh — ảnh dễ đọc nhầm vị trí chữ tâm-căn giữa trong ô cực rộng). Sửa: z-index cột A ở 2 hàng tiêu đề đặt cao hẳn (8/9) so với cột thường (5/6), độc lập thứ tự DOM.

## Kiểm chứng (đợt 5)

`tsc`/`eslint`/`vitest` (24/24) sạch xuyên suốt. Playwright thật trên dev server local, số liệu đo trực tiếp (không chỉ ảnh chụp) cho: dòng `expr` cao bằng dòng thường sau Phase 1; popover mở đúng, đóng đúng, giá trị lưu đúng (mockup tính lại `[GROSS]*0.1` ra `11.604.295,50`); dòng active tô đậm đúng; kéo cột A thành công (đo `boundingBox` trước/sau); cột D sau khi kéo rộng 1740px và cột A đóng băng đúng vị trí (`rectX:54`) kể cả sau khi thu nhỏ lại viewport — cả 2 bug trên đều được xác nhận SỬA XONG bằng đo lại y hệt, không chỉ nhìn ảnh.

## Trạng thái git (sau đợt 5)

`Core System-frontend@feature_v2`: vẫn 4 file sửa (gộp cả 5 đợt), commit `e3a3c88`, đã push lên `origin/feature_v2` (MR !44 tự cập nhật). `Core System-backend@release/uat-180826`: không đụng.

---

## Phase 6 (đợt thi hành thứ sáu, sau khi push) — sửa nút "+ Thêm dòng" trôi vị trí

Sau khi push đợt 5, user chụp ảnh báo nút "+ Thêm dòng" trôi lệch — nằm NGANG HÀNG bên phải bảng (ngay cạnh dòng 5/6) thay vì xuống dòng dưới bảng như thiết kế.

**Nguyên nhân:** div bọc `<table>` (Phase 4/5, cần `display:"inline-block"` để co khít đúng tổng độ rộng cột — điều kiện bắt buộc để table-layout:fixed tôn trọng độ rộng cột đã kéo giãn, xem Phase 5) và `<button>` "+ Thêm dòng" ngay sau nó (mặc định UA stylesheet của `<button>` CŨNG là `display:inline-block`) — 2 phần tử inline-level liền kề không có ranh giới block giữa chúng bị trình duyệt xếp CÙNG 1 dòng như 2 chữ trong 1 câu, đẩy nút trôi theo baseline của dòng đầu tiên bên trong div bọc bảng (đúng như quan sát: nút nằm ngang hàng dòng 5-6, không phải dòng cuối).

**Sửa:** ép `display:"block"` cho chính `<button>` (buộc luôn xuống dòng mới, không phụ thuộc từng nơi gọi phải tự bọc thêm `<div>`) kèm `width:"fit-content"` (display:block mặc định chiếm hết chiều ngang khung chứa — fit-content giữ nguyên kích thước ôm sát chữ như trước). Kiểm bằng Playwright thật: dựng 4 dòng, chụp ảnh xác nhận nút nằm đúng ngay dưới dòng cuối, căn trái, không còn trôi.

## Kiểm chứng (đợt 6)

`tsc`/`eslint` sạch, `vitest` 24/24 pass. Chỉ sửa 1 style object trong `TinhLuongExcel.tsx`, không đụng file khác.

## Trạng thái git (sau đợt 6)

`Core System-frontend@feature_v2`: commit `87e0db4`, đã push (`e3a3c88..87e0db4`).

---

## Phase 7 (đợt thi hành thứ bảy) — dời "+ Thêm dòng" lên ruy-băng, đồng bộ với "Cấu hình rule lương"

User hỏi so sánh: bên "Danh sách cột lương" (`FORMULAS_LIST_SHEET_ID`, tab Công thức) có nút "+ Thêm cột"/"Xóa cột" là nút RUY-BĂNG JSX thật (`FormulasRibbon.tsx`, prop `onAddColumn`), khác nút chữ rời dưới lưới — hỏi có nên áp style đó cho Report Config không. Đã khảo sát bằng agent con trước khi trả lời (không đoán): xác nhận nút thêm ở bên lương đã CHUYỂN lên ruy-băng từ trước (`develop`, comment dòng 7427-7428), sửa công thức bên đó dùng inline-expand TẠM THỜI (double-click, chỉ 1 dòng, không phải luôn-mở-mọi-dòng như bản Report Config CŨ đã gây phàn nàn) — nên khuyến nghị: **giữ popover cho công thức** (đã đúng, khác biệt có chủ đích) nhưng **đồng bộ vị trí nút "+ Thêm dòng" lên ruy-băng** cho khớp quy ước "+ Thêm cột" bên lương. User chốt làm.

**Thi hành:** `SettingsRibbon.tsx` thêm prop `onAddReportLine?: () => void` (optional — chỉ truyền khi đang mở đúng sheet Sửa/Tạo template báo cáo), render 1 tile ruy-băng JSX thật (icon lưới+dấu cộng xanh, khuôn y hệt các tile khác trong `SETTINGS_STATIC`) ngay sau "Thêm template báo cáo" — khác các nút TĨNH (dangerouslySetInnerHTML) vì nút này phải ẨN/HIỆN theo sheet đang mở, không thể nhét cứng vào chuỗi HTML luôn hiện. `TinhLuongExcel.tsx`: truyền `onAddReportLine={sheet.id === REPORT_TEMPLATE_EDIT_SHEET_ID && state.reportTemplateEditForm ? addReportTemplateEditLine : undefined}`; xoá hẳn nút `<button>` rời dưới bảng (đã sửa lỗi trôi vị trí ở Phase 6 — nay không cần nữa vì bỏ hẳn).

## Kiểm chứng (đợt 7)

`tsc`/`eslint`/`vitest` (24/24) sạch. Playwright thật: xác nhận nút ruy-băng **KHÔNG hiện** khi chưa mở sheet Sửa (đúng hành vi ẩn/hiện theo context, khác các nút tĩnh khác luôn hiện); nút cũ dưới bảng **không còn tồn tại** trong DOM (đếm 0); mở sheet Tạo → nút xuất hiện đúng cuối ruy-băng; bấm 2 lần → thêm đúng 2 dòng (3→5); đóng sheet (Huỷ) → nút ẩn lại. Không có test tạm sót lại.

## Trạng thái git (sau đợt 7)

`Core System-frontend@feature_v2`: 2 file sửa (`SettingsRibbon.tsx`, `TinhLuongExcel.tsx`), chưa commit.

---

## Phase 8 (đợt thi hành thứ tám, 220826) — 3 ý tưởng tối ưu tạo template nhiều cột (copy/paste kiểu Office)

User đặt vấn đề thật: nếu 1 report cần ~100 cột, bấm tay "+ Thêm dòng" 100 lần rất chậm. Đề xuất 3 ý tưởng, user chốt làm cả 3 theo thứ tự DỄ → KHÓ:

### Ý #1 — Chọn nhiều dòng (Shift/Ctrl+click) + Sao chép/Xoá theo lô
State mới `reportSelectedLines: Set<number>` + `reportSelectAnchor: number | null`. Click ở gutter: thường = chọn đúng 1 dòng; Shift+click = chọn dải từ neo; Ctrl/Cmd+click = thêm/bớt riêng 1 dòng. Dòng trong tập chọn tô nền `#dbe9fb` (đè lên màu theo Vai trò), gutter tô `#8fb8e8`. Right-click TRONG tập đang chọn (≥2 dòng) → menu đổi thành "Sao chép N dòng"/"Xoá N dòng" (2 hàm mới `duplicateReportTemplateEditLines`/`removeReportTemplateEditLines`, tái dùng đúng logic đơn-dòng nhân rộng ra); right-click NGOÀI tập chọn → thu về đúng 1 dòng đó (khớp hành vi Excel thật).

### Ý #2 — Dialog "Thêm nhiều dòng từ cột lương" (checkbox)
Dùng lại component `Modal` chung của app (Tailwind, không phụ thuộc biến CSS `.tl-root` nên không dính lỗi "nền trong suốt" đã gặp ở popover/menu chuột phải trước đó — Modal này render bình thường trong cây React, không portal). Dialog: chọn "Vai trò cho các dòng mới" (áp dụng chung cho cả lô — `SalaryComponent` không mang khái niệm "Vai trò" của báo cáo nên không có cách suy tự động đúng), ô tìm kiếm, checkbox "Chọn tất cả" + danh sách 148 cột lương thật (`data.allComponents`, đã tải sẵn, không gọi API riêng). Tick N → sinh N dòng `sourceKind="component"` cùng lúc (Nhãn hiển thị = tên cột lương).

**Bug tự phát hiện + tự sửa khi kiểm bằng Playwright:** checkbox trong dialog bị kéo giãn rộng hết hàng (đẩy chữ nhãn trôi lệch xa) — nguyên nhân: `app/globals.css` có 1 rule toàn cục `input { width: 100%; }` (dành cho input CHỮ khác trong app) vô tình áp cả lên `<input type="checkbox">`. Sửa bằng ép `style={{width:"15px",height:"15px",flex:"none"}}` trực tiếp trên từng checkbox — đúng khuôn đã dùng cho mọi checkbox khác trong `TinhLuongExcel.tsx` (tiền lệ có sẵn, không phải giải pháp mới).

### Ý #3 — Dán từ Excel (Ctrl+V, TSV) — khó nhất
Viết hàm THUẦN `parseReportLinesFromClipboardText(text, allComponents)` trong `ReportTemplateModal.tsx` (test được, không cần DOM) — quy ước 4 cột TSV (Nhãn hiển thị/Vai trò/Nguồn dữ liệu/Mã cột), khớp ĐÚNG nhãn dropdown thật trên UI. Nếu thiếu cột "Nguồn dữ liệu", TỰ SUY từ cột "Mã cột": có `[` → công thức tuỳ chỉnh, có `,` → tổng nhiều cột, khớp tên/mã 1 cột lương thật → 1 cột lương, khớp nhãn trường định danh → Thông tin NV; không suy được gì → fallback "Thông tin NV > Mã nhân viên" + cảnh báo. Không throw — luôn best-effort + mảng `warnings` cho từng dòng có vấn đề. 14 test mới (đủ 4 cột, thiếu cột tự suy đủ 4 nhánh, dán 1 cột duy nhất khớp tên cột lương, Vai trò sai vẫn tạo dòng, dòng thiếu nhãn bị bỏ qua, dòng trắng dư bị bỏ qua, input rỗng không throw).

Nối vào UI: `onPaste` gắn ở CHÍNH input "Nhãn hiển thị" (không phải wrapper toàn bảng) — chỉ can thiệp khi clipboard chứa TAB hoặc xuống dòng (chắc chắn là dữ liệu nhiều cột/dòng thật), nếu không thì để hành vi dán-vào-1-ô mặc định chạy bình thường (không ảnh hưởng gõ/dán 1 chữ thường vào ô nhãn, cũng không ảnh hưởng dán vào ô công thức/mã nội bộ trong popover — onPaste không đặt ở cấp cao hơn nên không bị bắt nhầm). Luôn APPEND vào cuối (không chèn tại vị trí dòng đang gõ) — cùng quy ước với Ý #1/#2 để hành vi 3 tính năng nhất quán, không có rủi ro âm thầm đè dữ liệu dòng đang có. Có cảnh báo (`toast.warning`, liệt kê tối đa 5 dòng lỗi + đếm số còn lại) khi có dòng cần tự kiểm tra lại, `toast.success` khi mọi dòng khớp sạch.

## Kiểm chứng (đợt 8)

`tsc`/`eslint` sạch. `vitest`: **38/38 pass** (24 cũ + 14 mới cho `parseReportLinesFromClipboardText`). Playwright thật trên dev server local (backend `:8080` + frontend `:3000` phải khởi động lại tay vì đã tắt từ phiên trước — dùng `go run ./cmd/Core System` + `npx next dev` trực tiếp, không qua `dev-local.sh` vì script đó dùng cổng 8082 khác với cổng `devLogin.ts`/`.env.local` đang trỏ tới):
- Ý #1: chọn 3 dòng bằng Shift+click → tô màu đúng cả dòng; menu chuột phải đổi đúng thành "Sao chép 3 dòng"/"Xoá 3 dòng"; sao chép ra đúng 8 dòng (5+3), xoá lại đúng 5.
- Ý #2: dialog hiện đủ 148 cột lương thật; tick 3 → nút đổi thành "Thêm 3 dòng"; bấm ra đúng 3 dòng mới đúng Vai trò/Mã cột đã chọn, mockup tính đúng.
- Ý #3: dán 3 dòng TSV (2 dòng khớp chuẩn + 1 dòng cố ý sai) qua `ClipboardEvent` giả lập thật (Playwright không copy được từ Excel thật nên dispatch trực tiếp `paste` event với `DataTransfer` chứa TSV) → thêm đúng 3 dòng, dòng khớp cột lương thật (GROSS) ra đúng giá trị demo trong mockup, dòng sai hiện toast liệt kê rõ 2 lỗi cụ thể.

**LƯU Ý (yêu cầu trực tiếp của user giữa phiên):** đợt này CHỈ dừng ở test kỹ tại local — KHÔNG tự commit/push như các đợt trước, chờ user xác nhận trước khi đẩy lên GitLab.

## Trạng thái git (sau đợt 8)

`Core System-frontend@feature_v2`: 4 file sửa (`TinhLuongExcel.tsx`, `SettingsRibbon.tsx`, `ReportTemplateModal.tsx`, `ReportTemplateModal.test.ts`), **chưa commit, chưa push** — chờ user xác nhận.

---

## Phase 9 (220826, sang 210826→220826) — Sửa bug PRE-EXISTING: ruy-băng "Cấu hình" đứng hình khi mở Kỳ lương/Phân quyền

**Không liên quan tới việc sửa UI/UX Report Template (Phase 1-8)** — mục này gộp vào cùng file vì cùng
là công việc trên ruy-băng "Cấu hình" trong đợt làm việc này, phát hiện lúc user tự test Phase 7/8.

### Triệu chứng user báo (qua 4 lượt phản hồi)
"button thêm template báo cáo không hoạt động" → sau khi loại trừ nhiều khả năng khác (đã ghi log debug
riêng, không lưu ở đây) thu hẹp lại đúng: **mở sheet "Kỳ lương" HOẶC "Phân quyền" (nút ruy-băng Cấu hình)
xong thì MỌI nút khác trên ruy-băng Cấu hình (kể cả "+ Thêm template báo cáo") không bấm được nữa** — tới
khi chuyển sang sheet khác thì bấm lại được. User tự xác nhận thêm: mở sheet Sửa/Tạo template báo cáo
(`REPORT_TEMPLATE_EDIT_SHEET_ID`, overlay tuyệt đối) KHÔNG bị — chỉ 2 sheet trên bị.

### Xác minh KHÔNG PHẢI do code Phase 1-8 (bằng chứng, không suy đoán)
Dựng `git worktree` tại commit `6beacd1` (commit NGAY TRƯỚC toàn bộ việc sửa Report Template ruy-băng
của đợt này), chạy trên cổng 3001 riêng: **bug tái hiện y hệt trên bản CŨ**, kết luận đây là lỗi tồn tại
từ trước, không phải do các đợt Phase 1-8 gây ra.

### Đo triệu chứng thật bằng Playwright (không suy đoán)
`MutationObserver` scoped vào `.tl-ribbon` (childList+subtree) đo được **~3.800-5.760 node add/remove
mỗi giây LIÊN TỤC** trong lúc "Kỳ lương"/"Phân quyền" đang là sheet active — ĐÚNG 0 khi ở sheet dạng
"list" (Danh sách cấu hình/Danh sách cột lương/Bảng công phụ cấp/Template báo cáo) hoặc sheet Sửa/Tạo.
Patch trực tiếp `Element.prototype.innerHTML` (setter) xác nhận: chính div `dangerouslySetInnerHTML`
của `SettingsRibbon.tsx` (chuỗi tĩnh `SETTINGS_STATIC`) bị React ghi lại innerHTML ~240 lần/giây —
**luôn CÙNG một giá trị `__html`** (so `sameAsPrev` bằng `WeakMap`, không phải suy đoán) — nghĩa là bản
thân component cha (`TinhLuongExcel`) đang tự render lại ~240 lần/giây trong lúc 2 sheet này đang mở.

### Đã loại trừ (đo trực tiếp, không suy đoán) nhưng KHÔNG tìm ra được nguyên nhân sâu gây ra 240 lần render/giây đó
- Wrapper `setState` chung của component: patch đếm số lần gọi + in stack trace — chỉ bắt được **1 lần**
  gọi trong suốt cả cửa sổ đo (không phải nguồn gây lặp).
- Toàn bộ 15 hook `useState` riêng khác trong `TinhLuongExcel` (`viewportH`, `headerRowH`, `noteRowH`,
  `sheetTabsEdge`, `ribbonCollapsed`, `periodSearch`, `deptSearch`, `deptDropdownOpen`, `isFullscreen`,
  `inlineFormulaEdit`, `reportBulkAddOpen/Query`, `sheetTabsMenuOpen`, `formulasNoticeOpen`, `scrollTop`) —
  patch từng effect liên quan (2 `ResizeObserver` đo `viewportH`/`headerRowH`) chỉ fire **1 lần lúc mount**.
- `usePayrollData()` (hook `data`): patch diff toàn bộ state nội bộ (`page`, `loadedRows.length`,
  `chamRequested`, `periodId`, `company`, `search`, `total`, `hasMore`, và `.data`/`.loading` của cả 6
  `useApi()` con) — **0 thay đổi** giữa các lần gọi trong lúc lặp xảy ra.
- `useAuth()`/`useToast()`/`useRouter()` — reference ổn định, không đổi giữa các lần render.
- Vòng lặp `requestAnimationFrame` auto-scroll khi kéo chọn (dòng ~2024) — luôn tự lặp lại vô điều kiện
  nhưng chỉ gọi `setState` khi `draggingRef.current === true`; không phải nguồn (không có phím chuột nào
  đang giữ trong lúc đo).
- React DevTools global hook (`onCommitFiberRoot`) — có tồn tại (`window.__REACT_DEVTOOLS_GLOBAL_HOOK__`)
  nhưng KHÔNG bao giờ được gọi khi không có extension DevTools thật gắn vào — không dùng được để bắt fiber
  commit từ ngoài trang.
- Đo `dt` giữa các lần render liên tiếp: ổn định ~7.3-9.4ms — không khớp nhịp `requestAnimationFrame`
  (~16.7ms ở 60Hz), gợi ý cơ chế lập lịch nội bộ khác của React 18 (không xác nhận được chính xác là gì).

**Kết luận trung thực:** không tìm ra được CƠ CHẾ CHÍNH XÁC khiến `TinhLuongExcel` tự render lại liên tục
trong lúc 2 sheet này mở, dù đã đo qua mọi hook/effect/state có trong component và hook custom nó gọi.
Nghi vấn hợp lý nhất (không có bằng chứng đủ mạnh để khẳng định) là hành vi lập lịch nội bộ của React 18
cho 1 update ưu tiên thấp không bao giờ ổn định — nhưng KHÔNG loại trừ được khả năng còn 1 nguồn khác
chưa đo tới.

### Fix đã áp dụng: chặn đúng điểm gây treo (không cần biết nguyên nhân sâu vì sao cha render lại)
Vì `SettingsRibbon` (và div `dangerouslySetInnerHTML` cho `HOME_CLIPBOARD` dùng chung trong
`commonControls`) KHÔNG được `React.memo`, mỗi lần cha render lại thì React đều đi xuống diff lại đúng
div `dangerouslySetInnerHTML` đó — và (không rõ vì sao ở tầng React nội bộ) KHÔNG bail-out dù giá trị
`__html` y hệt, gây ghi lại/reflow hàng trăm lần/giây làm ribbon đứng hình. Tạo file mới
`StaticRibbonHtml.tsx`: 1 component lá `React.memo(forwardRef(...))`, props CHỈ có `html` (string hằng
số cấp module `SETTINGS_STATIC`/`HOME_CLIPBOARD` — luôn cùng reference) → memo LUÔN bail-out, không bao
giờ re-render/re-commit bất kể cha bị gọi lại bao nhiêu lần. `onClick` (event delegation `.closest(".xbtn")`)
giữ nguyên trên div NGOÀI (đã có sẵn ở `SettingsRibbon`; thêm 1 div bọc mới cho `HOME_CLIPBOARD` trong
`commonControls`) — event vẫn bubble lên bình thường, không đổi hành vi click. `ref` đi qua `forwardRef`
(kênh riêng của React, không phải prop thường) nên không phá bail-out của memo — giữ nguyên cơ chế
`SettingsRibbon` tự dò `.xbtn` theo text để tô nền "đang mở".

### Kiểm chứng
- `tsc --noEmit`: sạch (chỉ còn lỗi tiền tồn tại KHÔNG liên quan ở `public/backup/payslip-lib.test.ts`).
- `eslint` trên 5 file đã sửa/thêm: sạch.
- `vitest run`: 97 pass / 4 fail — **4 fail đó tiền tồn tại**, xác nhận bằng `git stash` chạy lại đúng
  file `payrollTemplateExport.test.ts` cho cùng 4 fail khi KHÔNG có patch của tôi.
- Playwright thật (script tạm, đã xoá sau khi dùng): `MutationObserver` trên `.tl-ribbon` đo được
  **0 mutation** trong 2.5 giây khi "Kỳ lương" hoặc "Phân quyền" đang mở (trước khi sửa: hàng nghìn); bấm
  sang sheet cấu hình khác ngay sau đó phản hồi tức thì (~336-348ms, chủ yếu do `waitForTimeout` cố ý
  trong test, không phải lag thật).
- **Phát hiện phụ, KHÔNG sửa (ngoài phạm vi bug được yêu cầu):** tile "Kỳ lương" trên ruy-băng không bao
  giờ được tô nền "đang mở" (khác "Phân quyền" — tô đúng) vì `SettingsRibbon.tsx` so khớp
  `label === activeConfigLabel` bằng SO SÁNH TUYỆT ĐỐI, còn tile "Kỳ lương" hiện kèm icon chữ "₫ " phía
  trước nên `textContent` không bao giờ khớp đúng `sheet.name` ("Kỳ lương" không tiền tố). Xác nhận bằng
  `git log -S` đây là bug có từ commit tạo file `SettingsRibbon.tsx` (tách ruy-băng), không liên quan gì
  tới đợt sửa này — cosmetic, không phải bug người dùng đã báo, để lại cho lần sau nếu cần.

### Trạng thái git (sau Phase 9)
`Core System-frontend@feature_v2`: thêm `StaticRibbonHtml.tsx`, sửa `SettingsRibbon.tsx` +
`TinhLuongExcel.tsx` — **chưa commit, chưa push** (đúng yêu cầu "test local trước, chờ xác nhận mới
push" đã áp dụng từ Phase 8, tiếp tục giữ nguyên cho Phase 9).
