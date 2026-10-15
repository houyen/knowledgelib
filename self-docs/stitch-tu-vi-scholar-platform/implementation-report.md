---
id: self-docs/stitch-tu-vi-scholar-platform/implementation-report
canonical_question: 'Technical guide and specification: Báo Cáo Triển Khai Thiết Kế
  "Imperial Scholar Zi Wei"'
aliases:
- Báo Cáo Triển Khai Thiết Kế "Imperial Scholar Zi Wei"
- IMPLEMENTATION REPORT
- Imperial Scholar Zi Wei implementation report (tu-vi-app-poc)
- Báo cáo áp dụng design token Stitch vào tu-vi-app-poc
entity_type: runbook
domain: self-docs > stitch-tu-vi-scholar-platform
last_verified: 2026-09-23
---

# Báo Cáo Triển Khai Thiết Kế "Imperial Scholar Zi Wei" (Gửi Stitch)

**Dự án**: `tu-vi-app-poc` (Production React 19 + TypeScript + Vite)  
**Ngày thực hiện**: 2026-09-23  
**Dựa trên**: `imperial_scholar_zi_wei/DESIGN.md`  

---

## 1. Các thành phần đã tiếp thu và tích hợp vào hệ thống thật

### 1.1 Design Tokens (Bảng màu Giấy Dó & Mực Cổ)
Đã chuyển hóa toàn bộ biến `:root` trong `App.css` sang bảng màu Khâm Thiên của Stitch:
- **Nền & Viền**:
  - `--bg-parchment`: `#FAF7F0` (Giấy xuyến chỉ cổ)
  - `--bg-card`: `#FFFDF9` (Thẻ trắng ngà)
  - `--bg-palace`: `#F3EEDF` (Nền từng ô cung vị)
  - `--border-dark`: `#8C6D37` (Nâu đồng cổ)
  - `--border-light`: `#E8DFCE` (Viền ngà nhạt)
  - `--text-dark`: `#1F1C18` (Mực nho đen nâu)
  - `--text-muted`: `#5C5549` (Mực xám đá)
- **Điểm nhấn & Ngũ Hành**:
  - Chu Sa: `--accent-red: #9B2226`
  - Vàng Hoàng Kim: `--accent-gold: #C5A059`
  - Ngũ Hành: Kim `#5A6578`, Mộc `#1D7A46`, Thủy `#1A5FB4`, Hỏa `#BA2626`, Thổ `#8A5A2B`
  - Cát Tinh: `--tone-cat: #15803D`, Sát Tinh: `--tone-hung: #B91C1C`
- **Quan hệ Cung (Tia chiếu)**:
  - Tam Hợp: `--rel-tamhop: #0F766E` (Lam ngọc sâu)
  - Xung Chiếu: `--rel-xungchieu: #C2410C` (Hỏa son)
  - Nhị Hợp: `--rel-nhihop: #B45309` (Hổ phách đồng)

### 1.2 Hiệu chỉnh đo độ tương phản (WCAG AA Compliance)
Đo bằng thuật toán độ tương phản chuẩn WCAG 2.1 (yêu cầu chữ nhỏ < 18px đạt tối thiểu `4.5:1`):
- `text-dark` (`#1F1C18`) trên `bg-parchment`: **15.86:1** (Đạt)
- `text-muted` (`#5C5549`) trên `bg-parchment`: **6.89:1** (Đạt)
- `tone-cat-text` (`#0F5C2C`) trên `bg-card`: **7.99:1** (Đạt)
- `tone-hung-text` (`#8F1616`) trên `bg-card`: **9.01:1** (Đạt)
- **Cải tiến mực Hãm (`ink-400`)**: Giá trị cũ `#968A7F` trên nền `#F3EEDF` chỉ đạt `2.90:1` (không đạt chuẩn đọc). Đã hiệu chỉnh độ sáng về `#726A61` đạt **4.58:1** (Đạt chuẩn AA); đồng thời cân chỉnh bậc `ink-500` (`#625A52` - 5.83:1) và `ink-700` (`#4F473F` - 7.85:1) để bảo đảm độ dốc sắc độ giảm dần đều từ Miếu (M) đến Hãm (H).

### 1.3 Typography (Thư pháp & Kỹ thuật số)
- Tích hợp Google Fonts: `Noto Serif` (tiêu đề, tên 12 cung, can chi) + `Be Vietnam Pro` (thông số sao, độ sáng, nội dung giải đoán).
- Giữ fallback an toàn cho hệ thống.

### 1.4 Viền đôi "Song chỉ" (Double Border)
- Ứng dụng qua pseudo-element `::after` với `inset: 3px` (`.palace-cell`) và `inset: 4px` (`.modal-content`), opacity `0.35`/`0.25`.
- Hoàn toàn tách biệt khỏi các trạng thái tương tác `box-shadow` (hover, ghim, highlight tam hợp/xung chiếu).

### 1.5 Segmented Control ("Ấn Triện Action")
- Thay thế dropdown `<select>` chọn Giới Tính bằng bộ 2 nút bấm segmented Nam / Nữ với hiệu ứng đóng dấu triện chu sa (`#9B2226`), không độ trễ.

### 1.6 Tách 2 cột Cát / Hung trong Ô Cung (PalaceCell)
- **Cột Trái**: Chính Tinh (14 chủ tinh kèm độ sáng `[M, V, Đ, B, H]`) + Cát Tinh / Quý Tinh.
- **Cột Phải**: Sát Tinh / Bại Tinh + Bàng Tinh / Vòng sao phụ.
- Cung Vô Chính Diệu hiển thị chữ `(Vô Chính Diệu)` trang trọng bên cột trái, cân đối thị giác.

---

## 2. Các điểm cố tình LOẠI BỎ & RÀO CHẶN KỸ THUẬT

Để giữ tính chân thực và chuẩn mực học thuật, hệ thống **không** đưa vào các chi tiết sau từ bản prototype của Stitch:
1. **Dữ liệu Bát Tự giả định**: Không đưa `% Tàng Can`, `Thập Thần`, `Dụng Thần`, `% Vượng Suy` vì engine Tử Vi tính toán thuần suy diễn cổ bản, không sinh số liệu chưa có trong engine core.
2. **Khẩu hiệu marketing / Badge AI**: Không đưa các nhãn "100% Deterministic Engine", "RULE-VERIFIED", "Zero Hallucination" nhằm giữ phong thái thư viện học thuật điềm tĩnh, trung thực.
3. **Icon font & Emoji**: Đã loại bỏ sạch 100% icon emoji trang trí thừa thãi kiểu AI-slop (`material-symbols`, `👑`, `🌟`, `⚡`,...). Chỉ dùng typography, con dấu mộc bản và đường nét viền kép.
4. **Kiến trúc CSS**: Không nhúng runtime Tailwind CDN; giữ 1 file `App.css` chuẩn module hóa để bảo đảm tốc độ bundle và không rò rỉ vào bundle engine (`pnpm verify` 8/8 cổng xanh).

---

## 3. Yêu cầu thiết kế cho đợt lặp tiếp theo (Next Iteration for Stitch)

1. **Chiến lược Bàn cờ 12 Cung trên Mobile (< 768px)**:
   - Hiện bàn cờ 4x4 cần `min-width: 980px` nên mobile phải cuộn ngang.
   - Nhờ Stitch thiết kế chi tiết giải pháp: **Mini-Map 4x4 (Grid thu gọn tỉ lệ 100% viewport)** kết hợp **Drawer trượt đáy (Bottom Sheet)** khi chạm vào từng cung.
2. **Slide-over Drawer trên Desktop (thay thế Modal toàn màn hình)**:
   - Khi click vào 1 cung trên Desktop (>= 1024px), thiết kế dạng Drawer trượt từ mép phải (rộng ~440px), bàn cờ bên trái tự co nhẹ để người đọc vừa xem luận giải vừa đối chiếu đường chiếu quan hệ trên bàn cờ.
3. **Bảng Bát Tự Tứ Trụ 4 thẻ mộc bản**:
   - Thiết kế 4 thẻ trụ Năm / Tháng / Ngày / Giờ chỉ dựa trên dữ liệu thật của engine: Can Chi, Nạp Âm, Âm Dương, Cục Số (không có Thập Thần / % Tàng can).
