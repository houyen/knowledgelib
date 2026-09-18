---
type: fix
title: Modal tạo cột lương chặn 4/5 loại cột — chẩn đoán và sửa
status: done
timestamp: 2026-07-29
id: self-docs/engine/salary-component-modal-type-gating
canonical_question: 'Technical guide and specification: 290726 — Modal "Thêm cột lương"
  chặn 4/5 loại cột: chẩn đoán và sửa'
aliases:
- '290726 — Modal "Thêm cột lương" chặn 4/5 loại cột: chẩn đoán và sửa'
- Salary Component Modal Type Gating 290726
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# 290726 — Modal "Thêm cột lương" chặn 4/5 loại cột: chẩn đoán và sửa

**Status:** đã sửa xong, đã commit (chưa push). Chưa kiểm tay trên trình duyệt.

File canonical cho hạng mục "điều kiện lưu của `SalaryComponentModal` theo loại cột". Đây là hạng mục **riêng**, không phải phần tiếp của `Salary-Column-Sync-Impact-280726.md` — nó chạm `canSubmit` và khối công thức của modal, vốn thuộc đợt S004 (`240726-formulas-tab-fe.md`), không chạm ba route đồng bộ cột lương của ngày 28/07.

## Triệu chứng người dùng báo

Mở modal "Thêm cột lương", điền đủ **Mã cột** (`DEMO_TEST`) và **Tên cột** (`Demoo_111`), chọn **Loại thành phần = `input`**, **Định dạng = `currency`**, để trống Công thức. Nút **Lưu** xám, bấm không có phản ứng, và không có bất kỳ thông báo nào nói tại sao.

## Nguyên nhân gốc

`Core System-frontend/components-page/tinh-luong/SalaryComponentModal.tsx`, điều kiện `canSubmit` (trước khi sửa):

```js
const canSubmit =
  code.trim() !== "" &&
  name.trim() !== "" &&
  formula.trim() !== "" &&     // áp VÔ ĐIỀU KIỆN cho mọi componentType
  validation.checked &&        // đòi đã bấm "Kiểm tra công thức"
  validation.valid &&
  (!isEdit || reason.trim() !== "") &&
  !submitting;
```

Loại `input` là cột nhập liệu — giá trị đến từ chấm công hoặc do người dùng gõ trên lưới, **không có công thức nào để nhập**. Nhưng điều kiện `formula.trim() !== ""` không phân biệt loại cột.

### Vì sao đây là bế tắc tuyệt đối, không chỉ là bất tiện

```js
const runValidate = async () => {
  if (formula.trim() === "") return;   // thoát sớm, KHÔNG set validation.checked
  ...
};
```

Công thức trống thì bấm "Kiểm tra công thức" **không làm gì**, nên `validation.checked` vĩnh viễn là `false`. Không tồn tại chuỗi thao tác nào của người dùng làm nút Lưu sáng lên cho cột `input`. Đây không phải "khó dùng" mà là ngõ cụt kín.

### Phạm vi

`TYPE_OPTIONS` có 5 loại: `input`, `config`, `formula`, `system`, `manual`. Chỉ loại **`formula`** thoả được cả 5 điều kiện. **4/5 loại còn lại đều không tạo được.**

### Backend hoàn toàn không đòi công thức

```go
func (s *SalaryComponentService) Create(ctx context.Context, comp *models.SalaryComponent) error {
	comp.ID = uuid.New()
	comp.IsVisible = true
	normalizeSalaryComponentCustom(comp)
	return s.repo.Create(ctx, comp)   // không có một dòng validate formula nào
}
```

Cột `input` với công thức rỗng là hợp lệ hoàn toàn ở server. Rào chắn này thuần frontend — tự dựng lên rồi tự chặn mình.

## Không phải hồi quy của đợt 280726

Đã kiểm bằng `git log -S`, không suy đoán:

| | |
|---|---|
| Dòng `formula.trim() !== "" &&` có từ | `64f90a5` — **24/07**, ThaiDT, đợt S004 T0022-T0028 gốc |
| Commit đợt 280726 đụng file này (`e81bb22`) | chỉ thêm `import FormulaImpactPanel`, prop `periodId`, và khối render panel |
| Có sửa `canSubmit` không | **Không** — `git show e81bb22` không có dòng nào chạm |

Lý do 5 ngày không ai gặp: modal này sinh ra cho tab "Công thức" nên trước giờ chỉ có ai đó tạo cột loại `formula`, mà nhánh đó thoả đủ điều kiện nên chạy bình thường.

## Sự thật kỹ thuật quan trọng — đính chính một nhận định sai giữa chừng

Trong lúc chẩn đoán tôi đã kết luận vội rằng công thức còn sót trên cột `input` là "code chết". **Sai.** Đọc lại `internal/service/engine.go`:

```go
switch c.ComponentType {
case "input", "config", "manual":
	if _, ok := vals[c.Code]; !ok {
		if c.Formula != "" {
			v, err := evalExpression(c.Formula, vals)   // CÓ đánh giá công thức
			...
		} else {
			vals[c.Code] = 0.0
		}
	}
case "formula":
	...
}
```

Engine **có** dùng `Formula` cho `input`/`config`/`manual`, làm **giá trị mặc định** khi ô chưa có dữ liệu. Nguy hiểm hơn: `buildOrder` chỉ trích phụ thuộc cho loại `formula` (`engine.go:86`, comment ghi rõ "Chỉ formula mới có dependency qua [CODE] trong formula string"), nên công thức đặt trên cột `input` được đánh giá **không đảm bảo thứ tự topo** — tham chiếu `[X]` bên trong có thể đọc phải giá trị chưa được tính.

Hệ quả trực tiếp cho việc sửa: nếu chỉ ẩn ô công thức mà vẫn gửi chuỗi còn sót trong state, sẽ tạo ra đúng loại lỗi tệ nhất — người dùng không nhìn thấy gì nhưng hệ thống vẫn lưu và vẫn tính. Xem mục "Thay đổi 3" bên dưới.

## Trạng thái loại `system`

`engine.go` **không có** `case "system"` và cũng **không có** `default:` trong `switch c.ComponentType`. Nhánh này đã bị gỡ ngày 27/07 khi chuyển PIT từ `component_type='system'` sang `formula` (xem `PIT-Formula-Fix-270726.md`). Nghĩa là một cột `system` tạo mới bây giờ sẽ bị bỏ qua im lặng, không bao giờ có giá trị trong `computed_values`, và sẽ luôn mang dấu `⚠ chưa tính` của nhãn Task 4 (đợt 280726).

Người dùng quyết định **giữ `system` trong danh sách chọn**. Đã tôn trọng quyết định đó, nhưng bổ sung cảnh báo nền vàng nói thẳng sự thật trên khi loại này được chọn.

## Kiểm dữ liệu thật trước khi sửa

Chạy trên DB dev `payroll_engine`, để biết việc ẩn khối công thức có phá dữ liệu đang chạy không:

```
 component_type | tong | co_formula
----------------+------+------------
 formula        |   41 |         41
 input          |   69 |          0
```

69 cột `input`, **không cột nào** có công thức. Không tồn tại cột `config`, `manual` hay `system` nào. Nên tính năng "công thức làm giá trị mặc định cho cột input" hiện không ai dùng, và mọi thay đổi dưới đây không đụng dữ liệu sẵn có.

## Ba thay đổi đã thực hiện

### 1. Gắn yêu cầu công thức theo đúng loại cột

```js
const needsFormula = componentType === "formula";
const canSubmit =
  code.trim() !== "" &&
  name.trim() !== "" &&
  (!needsFormula || (formula.trim() !== "" && validation.checked && validation.valid)) &&
  (!isEdit || reason.trim() !== "") &&
  !submitting;
```

Loại `formula` giữ **nguyên** cả ba ràng buộc cũ, kể cả TASK-REF (sửa công thức làm mất hiệu lực lần kiểm tra trước). Không nới lỏng gì cho nhánh đang chạy tốt.

### 2. Ẩn khối công thức với loại không dùng công thức + nói rõ đang thiếu gì

Ẩn cùng lúc cả ba: ô nhập công thức, danh sách "Dùng trong công thức", và hàng nút "Kiểm tra công thức". Thay bằng một dòng giải thích nguồn giá trị, nội dung viết khớp đúng `switch` thật của engine chứ không phỏng đoán:

| Loại | Nội dung hiển thị |
|---|---|
| `input` | Giá trị đến từ dữ liệu chấm công hoặc do người dùng gõ trực tiếp trên lưới bảng lương |
| `manual` | HR nhập tay theo từng kỳ |
| `config` | Lấy giá trị từ bảng cấu hình |
| `system` | Cảnh báo nền vàng — engine không còn nhánh tính, cột sẽ không bao giờ có giá trị |

Đồng thời footer hiện danh sách điều kiện còn thiếu ngay cạnh nút Lưu, thay vì để nút xám câm:

```
Chưa lưu được — còn thiếu: mã cột, tên cột.
```

Với loại `formula` thì phân biệt được ba trạng thái khác nhau: thiếu công thức / chưa bấm Kiểm tra / công thức không hợp lệ. Đây chính là thứ đã làm ngõ cụt ban đầu mất rất lâu mới chẩn đoán ra — nút chết mà không nói gì.

### 3. Không gửi công thức còn sót khi khối đã ẩn

```js
formula: needsFormula ? formula : ""
```

Áp cho cả `createSalaryComponent` và `updateSalaryComponent`. Lý do nằm ở mục "đính chính" phía trên: ẩn ô mà vẫn gửi state ẩn là tạo ra hành vi người dùng không nhìn thấy được. Chuyển `formula → input` giờ lưu công thức rỗng; chuyển ngược lại thì chữ vẫn còn trong ô và vẫn được lưu — thấy gì lưu nấy, ở cả hai chiều.

## Verify

| Bước | Kết quả |
|---|---|
| `npx tsc --noEmit` | sạch |
| `npx eslint components-page/tinh-luong/SalaryComponentModal.tsx` | sạch |
| `npm run build` (next build sản xuất thật) | **✓ Compiled successfully** |
| `npx vitest run` | **20/20 pass**, 5 file — không hồi quy |
| Cấu trúc JSX sau khi sửa bằng script | kiểm mắt lại phần mở/đóng ternary và footer |

## Commit

| Commit | Nội dung |
|---|---|
| `Core System-frontend@b4216c4` | `fix(tinh-luong): chi doi cong thuc khi componentType la formula` — thay đổi 1 |
| `Core System-frontend@fd01c9e` | `feat(tinh-luong): an khoi cong thuc voi loai khong dung cong thuc + noi ro con thieu gi` — thay đổi 2 + 3 |

Nhánh `feature_1`. **Chưa push.**

## Còn nợ

- **Chưa kiểm tay trên trình duyệt.** Cần thử lại đúng luồng trong ảnh chụp: Thêm cột lương → loại `input` → điền mã + tên → nút Lưu phải sáng. Và thử loại `system` để xác nhận cảnh báo vàng hiện đúng.
- **Cần khởi động lại frontend mới thấy thay đổi.** Máy local đang chạy production (`next-server`, nạp build cũ). Phải `npm run build && npm start` lại, hoặc chuyển sang `npm run dev`.
- **Không có test tự động khoá bất biến này.** `vitest.config.ts` của repo cố ý chỉ dựng `environment: "node"` và không có hạ tầng mount component (lý do ghi trong chính file đó, từ Phase 1A ngày 20/07). `canSubmit` nằm trong thân component nên không tách ra test thuần được mà không refactor — chưa làm vì đó là quyết định riêng, chưa được yêu cầu.
- **Tính năng "công thức làm giá trị mặc định cho cột `input`/`config`/`manual`" vẫn còn trong engine nhưng nay không có đường nào từ UI để đặt nó**, và nó vốn đã có sẵn lỗi thiết kế (không được xét thứ tự phụ thuộc trong `buildOrder`). Hiện 0 cột dùng. Nếu sau này muốn mở lại thì phải sửa `buildOrder` trước, không chỉ mở lại ô nhập.
