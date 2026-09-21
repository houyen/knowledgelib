---
id: self-docs/docs/plan-phase-b
canonical_question: 'Technical guide and specification: Phase B Plan — UI nhập ngày-giờ-năm
  sinh, hiển thị lá số'
aliases:
- Phase B Plan — UI nhập ngày-giờ-năm sinh, hiển thị lá số
- PLAN phase b
entity_type: how_to
domain: self-docs > docs
last_verified: 2026-09-18
---

# Phase B Plan — UI nhập ngày-giờ-năm sinh, hiển thị lá số (Claude, 2026-09-18)

## Mục tiêu
Frontend cơ bản: form nhập ngày-giờ-năm sinh dương lịch → gọi `tinhLaSo()` (đã có ở `src/engine/index.ts`, Phase A) → hiển thị kết quả lá số.

## Stack
Vite + React + TypeScript. Lý do: cùng ngôn ngữ với engine (TS, import trực tiếp không cần build API riêng), Vite khởi tạo/dev nhanh cho POC. Không cần backend/server — engine chạy thẳng trong browser (pure JS, không phụ thuộc Node API).

## Cấu trúc thư mục
```
web/                          # app Vite riêng, tách khỏi src/engine
  src/
    App.tsx                   # layout chính: Form + LaSoResult
    components/
      BirthInputForm.tsx       # nhập ngày/tháng/năm/giờ/phút
      LaSoResult.tsx            # hiển thị solar/lunar/tuTru
    engine -> ../../src/engine  # import trực tiếp qua alias hoặc relative path
    main.tsx
  index.html
  vite.config.ts
  package.json
  tsconfig.json
```

Ghi chú: nếu Vite import trực tiếp `../../src/engine` gặp vướng do khác package.json/tsconfig root, dùng vite alias `@engine -> ../../src/engine` trong `vite.config.ts` — không copy/duplicate code engine sang web/.

## Component contract

### `BirthInputForm`
```tsx
interface BirthInputFormProps {
  onSubmit: (input: SolarDateTimeInput) => void;
}
```
- Input: year (number), month (1-12), day (1-31), hour (0-23), minute (0-59).
- Validate cơ bản trước khi submit: ngày hợp lệ theo tháng/năm (dùng `Date` object check), không cho submit nếu invalid — hiển thị lỗi inline.
- Không cần chọn timezone ở UI (dùng default `Asia/Ho_Chi_Minh` trong engine).

### `LaSoResult`
```tsx
interface LaSoResultProps {
  laSo: LaSo | null;    // null = chưa submit lần nào, không render gì
}
```
- Hiển thị: ngày âm lịch (dd/mm/yyyy + nhuận nếu có), tứ trụ dạng bảng 4 cột (Năm/Tháng/Ngày/Giờ) mỗi cột 1 cặp Can-Chi.

### `App`
- State: `laSo: LaSo | null`.
- `handleSubmit(input)`: gọi `tinhLaSo(input)`, set state. Bọc try/catch — nếu engine throw (input biên, vd 30/2), hiển thị thông báo lỗi thay vì crash trắng trang.

## Acceptance criteria (Phase B xong khi)
- [ ] `cd web && npm install && npm run dev` chạy được, mở form nhập được ngày sinh.
- [ ] Nhập ngày hợp lệ (vd 01/01/2000, 10:30) → bấm submit → hiển thị đúng kết quả (âm lịch + tứ trụ) khớp với test case Phase A cho cùng input.
- [ ] Nhập ngày không hợp lệ (vd ngày 32, tháng 13) → không crash, hiển thị lỗi rõ ràng.
- [ ] `npm run build` (trong `web/`) không lỗi.
- [ ] README.md (root) cập nhật thêm mục "Chạy UI (Phase B)": `cd web && npm install && npm run dev`.

## Ranh giới / not-in-scope Phase B
- Không cần responsive/mobile polish, không cần styling nâng cao — form + bảng kết quả đơn giản, đọc được là đủ (POC).
- Không cần routing, không cần state management ngoài React state cơ bản.
- Không sửa `src/engine/` — chỉ import, không đổi API.
- Không cần deploy/hosting.

## Bàn giao cho Gemini (worker code)
Implement đúng theo cấu trúc + component contract + acceptance criteria trên. `src/engine/` đã có sẵn ở root repo (Phase A, đã merge vào main) — chỉ import, không viết lại logic tính toán.
