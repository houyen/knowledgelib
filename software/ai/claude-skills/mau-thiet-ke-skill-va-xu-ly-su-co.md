---
id: software/ai/claude-skills/mau-thiet-ke-skill-va-xu-ly-su-co
canonical_question: "Các mẫu thiết kế (design patterns) phổ biến cho Claude Skill là gì và cách xử lý sự cố thường gặp ra sao?"
aliases:
- mẫu thiết kế claude skill
- claude skill design patterns
- xử lý sự cố claude skill
- troubleshooting claude skills
- lỗi invalid frontmatter SKILL.md
- phối hợp nhiều MCP trong skill
entity_type: book_chapter
domain: software > ai > claude-skills
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ \"Cẩm nang đầy đủ xây dựng Skill cho Claude\" (bản dịch cộng đồng tiếng Việt của tài liệu hướng dẫn của Anthropic). Không chép nguyên văn."
---

# Các Mẫu Thiết kế Skill và Xử lý Sự cố

## TL;DR
Khi thiết kế skill, bạn có thể xuất phát từ bài toán cần giải quyết (người dùng nêu mục tiêu, skill tự điều phối công cụ) hoặc từ công cụ sẵn có (người dùng đã nối MCP, skill bổ sung quy trình chuẩn). Năm mẫu thiết kế phổ biến dưới đây giúp giải quyết hầu hết kịch bản thực tế, đi kèm bảng tra cứu triệu chứng – nguyên nhân – cách sửa cho các lỗi từ lúc tải lên đến khi vận hành.

## Hai hướng tiếp cận và 5 Mẫu thiết kế (Design Patterns)
- **Hướng từ vấn đề (Problem-first):** Người dùng nêu kết quả mong muốn (ví dụ: "lập workspace dự án mới"), skill tự chọn và gọi đúng trình tự công cụ.
- **Hướng từ công cụ (Tool-first):** Người dùng đã kết nối sẵn một MCP (như Notion hoặc Linear), skill đóng vai trò dạy Claude các phương pháp làm việc tối ưu trên công cụ đó.

| Mẫu thiết kế | Khi nào nên dùng | Ví dụ minh họa | Kỹ thuật triển khai cốt lõi |
|---|---|---|---|
| **1. Điều phối quy trình tuần tự** | Tác vụ gồm nhiều bước phải chạy đúng thứ tự, bước sau dùng đầu ra của bước trước | Tiếp nhận khách hàng mới: tạo tài khoản → cài thanh toán → tạo gói đăng ký → gửi email | Quy định rõ thứ tự và tham số truyền giữa các bước, có chốt kiểm tra từng chặng và hướng dẫn hoàn tác (rollback) khi lỗi |
| **2. Phối hợp nhiều MCP** | Một quy trình nghiệp vụ đi xuyên qua nhiều dịch vụ khác nhau | Bàn giao thiết kế sang code: xuất tài nguyên (Figma MCP) → lưu file (Drive MCP) → tạo việc (Linear MCP) → báo tin (Slack MCP) | Tách rõ từng giai đoạn theo dịch vụ, truyền dữ liệu/link đầu ra giữa các MCP, kiểm tra trước khi chuyển chặng, xử lý lỗi tập trung |
| **3. Tinh chỉnh theo vòng lặp** | Chất lượng đầu ra cần được kiểm tra và nâng cấp dần qua nhiều lượt | Tạo báo cáo: dựng bản nháp → chạy `scripts/check_report.py` tìm mục thiếu/lỗi → sửa lại → lặp tới khi đạt chuẩn | Đặt tiêu chí chất lượng rõ ràng, dùng script kiểm tra khách quan, chỉ tạo lại phần bị lỗi và quy định điều kiện dừng vòng lặp |
| **4. Chọn công cụ theo ngữ cảnh** | Cùng một mục tiêu nhưng phải rẽ nhánh công cụ tùy thuộc tính đầu vào | Lưu file thông minh: file >10MB vào đám mây, tài liệu chung vào Notion/Docs, code vào GitHub, file tạm lưu cục bộ | Xây dựng cây quyết định (decision tree) rõ ràng, có phương án dự phòng và giải thích minh bạch lý do chọn công cụ cho người dùng |
| **5. Hiểu biết chuyên ngành** | Cần áp dụng quy tắc nghiệp vụ/tuân thủ nghiêm ngặt trước khi gọi công cụ | Xử lý thanh toán: kiểm tra danh sách trừng phạt, khu vực pháp lý và rủi ro trước khi cho phép giao dịch hoặc mở hồ sơ rà soát | Nhúng logic chuyên ngành vào bước tiền kiểm tra, phân nhánh xử lý rõ ràng và ghi nhật ký kiểm toán (audit log) đầy đủ |

## Bảng tra cứu Xử lý sự cố (Troubleshooting)

| Triệu chứng / Thông báo lỗi | Nguyên nhân gốc rễ | Cách khắc phục cụ thể |
|---|---|---|
| Lỗi tải lên: `"Could not find SKILL.md in uploaded folder"` | File chính bị đặt sai tên hoặc sai chữ hoa/thường (`skill.md`, `SKILL.MD`) | Đổi tên chính xác thành `SKILL.md` và kiểm tra lại bằng lệnh `ls -la` |
| Lỗi tải lên: `"Invalid frontmatter"` | Thiếu cặp dấu `---` bao quanh YAML hoặc chuỗi có dấu nháy kép chưa đóng | Bọc YAML trong hai dòng `---` và kiểm tra cú pháp chuỗi hợp lệ |
| Lỗi tải lên: `"Invalid skill name"` | Trường `name` chứa khoảng trắng hoặc chữ in hoa (ví dụ: `My Cool Skill`) | Đổi sang định dạng `kebab-case` toàn chữ thường (ví dụ: `my-cool-skill`) |
| Skill không bao giờ tự kích hoạt | `description` quá chung chung, thiếu cụm từ người dùng hay nói hoặc thiếu tên đuôi file | Viết lại `description` cụ thể hơn; hỏi trực tiếp Claude *"Bạn sẽ dùng skill [tên] khi nào?"* để tìm chỗ hổng trong mô tả |
| Skill kích hoạt quá thường xuyên ở câu hỏi lạ | Phạm vi trong `description` quá rộng, không có ranh giới phân biệt với skill khác | Thu hẹp phạm vi ngữ cảnh và thêm câu loại trừ rõ ràng (ví dụ: *"KHÔNG dùng cho khám phá dữ liệu đơn giản"*) |
| Skill nạp được nhưng lệnh gọi MCP thất bại | MCP server bị ngắt kết nối, hết hạn API key/OAuth token, thiếu quyền, hoặc gọi sai tên tool | Kiểm tra trạng thái `Connected` ở `Settings > Extensions`, làm mới xác thực, gọi thử MCP độc lập ngoài skill, và đối chiếu chính xác tên tool (phân biệt hoa thường) |
| Claude nạp skill nhưng bỏ qua hướng dẫn | Hướng dẫn quá dài, ý quan trọng bị chìm, câu chữ mơ hồ, hoặc mô hình có xu hướng làm tắt | Rút gọn bằng danh sách gạch đầu dòng, đưa mục quan trọng lên đầu kèm nhãn `## Critical`, đóng gói bước kiểm tra thành script chạy code, và thêm lời nhắc ưu tiên chất lượng (đặt trong prompt của người dùng sẽ hiệu quả hơn trong `SKILL.md`) |
| Phản hồi chậm hoặc chất lượng câu trả lời giảm sút | Ngữ cảnh quá lớn do `SKILL.md` quá dài, không tách file phụ, hoặc bật quá nhiều skill cùng lúc | Giữ `SKILL.md` dưới 5.000 từ, chuyển tài liệu chi tiết sang `references/`, và tránh bật quá 20–50 skill đồng thời (nên bật chọn lọc hoặc gom theo gói) |

## Khi nào dùng
- Khi bắt đầu thiết kế kiến trúc luồng xử lý cho một skill mới và cần chọn mẫu phù hợp (tuần tự, đa dịch vụ, lặp kiểm tra, rẽ nhánh hay kiểm soát tuân thủ).
- Khi cần phân định rõ nên đi theo hướng xuất phát từ vấn đề (problem-first) hay xuất phát từ công cụ sẵn có (tool-first).
- Khi gặp lỗi tải gói skill lên Claude.ai/Claude Code hoặc khi hành vi thực thi của Claude lệch khỏi kịch bản thiết kế.
- Khi cần tối ưu tốc độ phản hồi và độ tuân thủ hướng dẫn cho các skill phức tạp hoặc dùng nhiều tài liệu tham khảo.

## Sai lầm thường gặp
- **Dùng lời văn tự nhiên cho các bước kiểm tra sống còn:** Diễn giải ngôn ngữ luôn có xác suất bị bỏ qua; với các điều kiện bắt buộc, nên viết script Python/Bash để kiểm tra tất định.
- **Đổ lỗi cho skill khi MCP bị đứt kết nối:** Không thử gọi trực tiếp công cụ MCP bên ngoài skill để cô lập nguyên nhân xem lỗi nằm ở kết nối dịch vụ hay ở câu lệnh hướng dẫn.
- **Bật toàn bộ skill cùng lúc và nhồi nhét vào một file:** Vượt ngưỡng 5.000 từ trong `SKILL.md` và bật hàng chục skill song song làm loãng sự chú ý của mô hình.

---
*Nguồn: Tóm tắt bằng lời riêng từ "Cẩm nang đầy đủ xây dựng Skill cho Claude" (bản dịch cộng đồng tiếng Việt của tài liệu hướng dẫn của Anthropic). Không chép nguyên văn.*
