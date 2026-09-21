---
id: self-docs/docs/plan-phase-a
canonical_question: 'Technical guide and specification: Phase A Plan — Engine tính
  lá số'
aliases:
- Phase A Plan — Engine tính lá số
- PLAN phase a
entity_type: architecture_explainer
domain: self-docs > docs
last_verified: 2026-09-21
---

# Phase A Plan — Engine tính lá số (Claude, 2026-09-18)

## Mục tiêu
Module tính toán thuần (pure logic), không phụ thuộc UI, test độc lập được. Input: ngày-giờ-năm sinh dương lịch. Output: lá số cơ bản (âm lịch, can chi, tứ trụ).

## Stack
TypeScript, Node runtime, không framework. Lý do: dùng chung ngôn ngữ với Phase B (frontend), tránh boundary language ở POC nhỏ này. Test: Vitest.

## Cấu trúc thư mục
```
src/
  engine/
    lunar.ts        # chuyển đổi dương lịch -> âm lịch
    canchi.ts        # tính can-chi (năm/tháng/ngày/giờ)
    tuTru.ts          # ráp tứ trụ từ can-chi 4 trụ
    types.ts          # kiểu dữ liệu chung (SolarDate, LunarDate, CanChi, TuTru...)
    index.ts          # public API: tinhLaSo(input): LaSo
  engine/__tests__/
    lunar.test.ts
    canchi.test.ts
    tuTru.test.ts
```

## API công khai (Phase B sẽ import cái này)
```ts
// types.ts
export interface SolarDateTimeInput {
  year: number; month: number; day: number;
  hour: number; minute: number;     // 24h, giờ sinh
  timezone?: string;                 // default "Asia/Ho_Chi_Minh"
}

export interface CanChi { can: string; chi: string }  // vd: { can: "Giáp", chi: "Tý" }

export interface TuTru {
  nam: CanChi; thang: CanChi; ngay: CanChi; gio: CanChi;
}

export interface LaSo {
  solar: SolarDateTimeInput;
  lunar: { year: number; month: number; day: number; isLeapMonth: boolean };
  tuTru: TuTru;
}

// index.ts
export function tinhLaSo(input: SolarDateTimeInput): LaSo;
```

## Thuật toán / nguồn tham chiếu
1. **Dương lịch → âm lịch**: thuật toán Hồ Ngọc Đức (âm lịch Việt Nam, timezone UTC+7) — công thức Julian Day Number chuẩn, well-known, public domain. Không gọi API ngoài (offline, pure function).
2. **Can Chi năm**: từ năm dương lịch, công thức modulo chuẩn (Giáp=0..Quý=9 can chu kỳ 10; Tý=0..Hợi=11 chi chu kỳ 12), mốc tham chiếu năm 4 SCN = Giáp Tý (theo quy ước phổ biến).
3. **Can Chi tháng/ngày/giờ**: tính từ can chi năm + số ngày Julian, theo công thức chuẩn tứ trụ (ngũ thử độn nguyên cho giờ, ngũ dần độn nguyên cho tháng).
4. **Tứ trụ**: ráp 4 cặp can-chi (năm, tháng, ngày, giờ) thành object `TuTru`.

## Acceptance criteria (Phase A xong khi)
- [ ] `tinhLaSo()` chạy được, không phụ thuộc DOM/network.
- [ ] Test: tối thiểu 5 case ngày sinh đã biết kết quả (chọn ngày dễ verify chéo, vd 01/01/2000, một ngày có tháng nhuận âm lịch, một ngày trước/sau giao thừa).
- [ ] `npm test` xanh, `npm run build` (tsc) không lỗi.
- [ ] README.md cập nhật: cách chạy test, cách import module.
- [ ] Không đụng vào thư mục UI (chưa tồn tại ở Phase A) — chỉ tạo `src/engine/`, `package.json`, config test/build, README.

## Ranh giới / not-in-scope Phase A
- Không làm UI (Phase B).
- Không tính các yếu tố tử vi nâng cao (đại vận, tiểu vận, sao...) — chỉ dừng ở tứ trụ + âm lịch cơ bản.
- Không cần lưu DB, không cần API server.

## Bàn giao cho Gemini (worker code)
Implement đúng theo cấu trúc + API + acceptance criteria trên. Nếu thuật toán can-chi/âm-lịch có sai số biên (giờ Tý, giao thừa), ưu tiên đúng theo tài liệu thuật toán Hồ Ngọc Đức, ghi chú rõ trong code nếu có giả định.
