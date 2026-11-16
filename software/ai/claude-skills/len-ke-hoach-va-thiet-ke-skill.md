---
id: software/ai/claude-skills/len-ke-hoach-va-thiet-ke-skill
canonical_question: "Làm thế nào để lên kế hoạch, chọn nhóm use case và viết SKILL.md hiệu quả cho Claude?"
aliases:
- lên kế hoạch và thiết kế skill claude
- cách viết SKILL.md frontmatter
- ba nhóm use case claude skill
- viết description cho claude skill
- tiêu chí thành công của skill
- claude skill yaml frontmatter
entity_type: book_chapter
domain: software > ai > claude-skills
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ \"Cẩm nang đầy đủ xây dựng Skill cho Claude\" (bản dịch cộng đồng tiếng Việt của tài liệu hướng dẫn của Anthropic). Không chép nguyên văn."
---

# Lên kế hoạch và Thiết kế Skill

## TL;DR
Trước khi viết code hay tạo thư mục, hãy chọn 2–3 tình huống sử dụng (use cases) cụ thể và xác định rõ điều kiện kích hoạt, công cụ cần dùng cùng kết quả đầu ra. Phân loại skill vào một trong ba nhóm (tạo sản phẩm, tự động hóa quy trình, hoặc tăng cường MCP) sẽ giúp chọn đúng cấu trúc. Trọng tâm quan trọng nhất khi thiết kế là YAML frontmatter (đặc biệt là `description`) và phần hướng dẫn từng bước rõ ràng.

## Bắt đầu từ Use Case và Ba nhóm phổ biến
Một use case rõ ràng cần trả lời bốn câu hỏi: người dùng muốn hoàn thành việc gì, gồm những bước nào, cần công cụ gì (sẵn có hay MCP), và cần cài sẵn tri thức chuyên môn nào.

| Nhóm Use Case | Mục tiêu chính | Ví dụ thực tế | Kỹ thuật cốt lõi |
|---|---|---|---|
| **1. Tạo tài liệu & sản phẩm** | Sinh đầu ra đồng nhất, chất lượng cao (code, giao diện, tài liệu, slide...) | `frontend-design`, các skill xử lý `docx`, `pptx`, `xlsx` | Cài sẵn bộ nhận diện/chuẩn trình bày, dùng template mẫu, có checklist rà soát cuối, tận dụng công cụ sẵn có của Claude |
| **2. Tự động hóa quy trình** | Điều phối quy trình nhiều bước theo phương pháp thống nhất | `skill-creator` (dẫn dắt tạo và kiểm tra skill mới) | Chia bước kèm chốt kiểm tra, dùng mẫu cấu trúc chuẩn, tích hợp bước tự rà soát và vòng lặp tinh chỉnh |
| **3. Tăng cường cho MCP** | Bổ sung quy trình nghiệp vụ lên trên quyền truy cập công cụ của MCP server | `sentry-code-review` (phân tích và sửa lỗi PR từ dữ liệu Sentry MCP) | Gọi chuỗi lệnh MCP theo thứ tự, cung cấp sẵn ngữ cảnh lĩnh vực, hướng dẫn xử lý các lỗi MCP thường gặp |

## Tiêu chí đánh giá thành công
Các chỉ số định hướng giúp đo lường hiệu quả của skill trước và sau khi triển khai:

| Phân loại | Tiêu chí mục tiêu | Cách đo lường và kiểm chứng |
|---|---|---|
| **Định lượng** | Kích hoạt đúng ở ~90% câu hỏi liên quan | Chạy thử 10–20 câu hỏi mục tiêu; đếm số lần tự nạp so với số lần phải bật thủ công |
| **Định lượng** | Hoàn thành trong số lần gọi công cụ tối ưu | So sánh cùng một tác vụ khi bật/tắt skill về số lệnh gọi tool và tổng lượng token tiêu thụ |
| **Định lượng** | 0 lệnh gọi API thất bại trong quy trình | Theo dõi log của MCP server khi chạy thử, đếm mã lỗi và số lần phải thử lại (retry) |
| **Định tính** | Không cần nhắc bước kế tiếp | Đếm số lần người dùng phải can thiệp chỉnh hướng trong phiên chạy thử |
| **Định tính** | Chạy xong không cần sửa tay & ổn định | Chạy lặp lại một yêu cầu 3–5 lần để so độ đồng nhất; xem người mới có làm thành công ngay lần đầu không |

## Quy tắc viết YAML Frontmatter
Frontmatter nằm giữa hai dòng `---` ở đầu file `SKILL.md` và quyết định việc Claude có nạp skill hay không:

| Trường | Bắt buộc | Quy định kỹ thuật và nội dung |
|---|---|---|
| `name` | Có | Chỉ dùng `kebab-case` (chữ thường và dấu gạch ngang), không khoảng trắng, nên trùng tên thư mục |
| `description` | Có | Tối đa 1024 ký tự. Phải nêu đủ: **[Skill làm gì] + [Khi nào dùng / cụm từ người dùng hay nói] + [Năng lực/loại file hỗ trợ]** |
| `license` | Tùy chọn | Giấy phép khi phát hành mã nguồn mở (ví dụ: `MIT`, `Apache-2.0`) |
| `compatibility` | Tùy chọn | Từ 1–500 ký tự, nêu yêu cầu môi trường, gói hệ thống hoặc kết nối mạng |
| `allowed-tools` | Tùy chọn | Giới hạn quyền công cụ được phép chạy (ví dụ: `"Bash(python:*) WebFetch"`) |
| `metadata` | Tùy chọn | Các cặp khóa-giá trị tùy chỉnh như `author`, `version`, `mcp-server`, `category`, `tags` |

**Giới hạn bảo mật bắt buộc trong YAML:**
- Cấm dùng dấu ngoặc nhọn XML (`<` hoặc `>`) để ngăn chặn nguy cơ chèn lệnh (prompt injection) vào system prompt.
- Cấm đặt tên skill có chứa hoặc bắt đầu bằng chữ `claude` hoặc `anthropic` (tên riêng đã được bảo lưu).
- Không nhúng code thực thi trong YAML.

## Cách viết phần hướng dẫn trong thân `SKILL.md`
- **Cấu trúc chuẩn:** Chia thành các mục rõ ràng gồm: các bước thực thi tuần tự (mô tả, lệnh mẫu, kết quả mong đợi), ví dụ minh họa (câu nói của người dùng → hành động → đầu ra), và mục xử lý sự cố (lỗi → nguyên nhân → cách sửa).
- **Cụ thể và hành động được ngay:** Thay vì viết chung chung "kiểm tra dữ liệu trước khi chạy", hãy ghi rõ lệnh `python scripts/validate.py --input {filename}` và cách sửa từng lỗi định dạng.
- **Trỏ link rõ tới tài nguyên phụ:** Giữ `SKILL.md` gọn gàng và dẫn đường dẫn cụ thể tới `references/` (ví dụ: nhắc đọc `references/api-patterns.md` để xem giới hạn tần suất gọi và phân trang).

## Cách áp dụng
1. Chọn 2–3 tình huống thực tế và liệt kê các câu lệnh tự nhiên mà người dùng thường gõ.
2. Tạo thư mục `kebab-case` cùng file `SKILL.md` có `name` và `description` tuân thủ công thức `[Làm gì] + [Khi nào dùng]`.
3. Viết các bước hướng dẫn kèm ví dụ đầu vào/đầu ra, hướng dẫn bắt lỗi, và tách tài liệu dài sang `references/`.

## Sai lầm thường gặp
- **Viết `description` quá mơ hồ hoặc thuần kỹ thuật:** Ví dụ chỉ ghi "Giúp làm việc với dự án" hoặc dùng thuật ngữ kiến trúc nội bộ mà thiếu các cụm từ kích hoạt đời thường của người dùng.
- **Quên điều kiện kích hoạt hoặc loại file:** Chỉ mô tả tính năng mà không ghi "Dùng khi người dùng tải lên file `.fig` hoặc yêu cầu...".
- **Vi phạm cú pháp YAML và bảo mật:** Thiếu dấu `---`, quên đóng dấu nháy kép, hoặc chèn thẻ `< >` vào frontmatter làm hỏng quá trình tải skill.

---
*Nguồn: Tóm tắt bằng lời riêng từ "Cẩm nang đầy đủ xây dựng Skill cho Claude" (bản dịch cộng đồng tiếng Việt của tài liệu hướng dẫn của Anthropic). Không chép nguyên văn.*
