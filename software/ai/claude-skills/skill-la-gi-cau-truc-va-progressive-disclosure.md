---
id: software/ai/claude-skills/skill-la-gi-cau-truc-va-progressive-disclosure
canonical_question: "Skill cho Claude là gì, cấu trúc thư mục và cơ chế progressive disclosure hoạt động như thế nào?"
aliases:
- claude skill là gì
- cấu trúc thư mục skill claude
- progressive disclosure claude skill
- SKILL.md structure
- skill vs MCP connector
- claude agent skills architecture
entity_type: book_chapter
domain: software > ai > claude-skills
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ \"Cẩm nang đầy đủ xây dựng Skill cho Claude\" (bản dịch cộng đồng tiếng Việt của tài liệu hướng dẫn của Anthropic). Không chép nguyên văn."
---

# Skill là gì: Cấu trúc thư mục và cơ chế Progressive Disclosure

## TL;DR
Skill là một thư mục đóng gói hướng dẫn, tài liệu và script nhằm dạy Claude thực hiện lặp lại một quy trình chuyên môn một cách nhất quán. Nhờ cơ chế nạp theo từng lớp (progressive disclosure), Claude chỉ đọc metadata ở đầu phiên và nạp chi tiết khi thực sự cần, giúp tiết kiệm context token. Khi đi kèm MCP, MCP cung cấp công cụ và dữ liệu (như căn bếp), còn skill đóng vai trò công thức nấu ăn.

## Cấu trúc thư mục của một Skill
Mỗi skill nằm trong một thư mục đặt tên theo chuẩn `kebab-case` (không khoảng trắng, không gạch dưới, không chữ hoa):

| Thành phần | Bắt buộc | Vai trò trong skill | Quy tắc lưu ý |
|---|---|---|---|
| `SKILL.md` | Có | Chứa YAML frontmatter và hướng dẫn thực thi bằng Markdown | Phải viết đúng chính xác tên và chữ hoa/thường (`SKILL.md`) |
| `scripts/` | Tùy chọn | Chứa code thực thi được (Python, Bash...) để kiểm tra hoặc xử lý dữ liệu | Gọi trực tiếp từ các bước hướng dẫn trong `SKILL.md` |
| `references/` | Tùy chọn | Tài liệu tra cứu chuyên sâu (API guide, quy ước, mẫu dữ liệu) | Chỉ nạp khi Claude cần tra cứu thêm |
| `assets/` | Tùy chọn | Biểu mẫu (templates), font chữ, icon phục vụ đầu ra | Dùng để giữ định dạng kết quả đồng nhất |

*Lưu ý:* Không đặt `README.md` bên trong thư mục của skill; mọi hướng dẫn cho agent phải nằm ở `SKILL.md` hoặc `references/`.

## Nguyên tắc thiết kế cốt lõi

### 1. Tiết lộ theo từng lớp (Progressive Disclosure)
Cơ chế ba lớp giúp duy trì kiến thức sâu mà không làm phình system prompt:

| Lớp | Thành phần | Thời điểm nạp vào context | Mục đích |
|---|---|---|---|
| Lớp 1 | YAML frontmatter (`name`, `description`) | Luôn nạp sẵn trong system prompt | Giúp Claude nhận diện khi nào cần kích hoạt skill |
| Lớp 2 | Phần thân của `SKILL.md` | Nạp khi yêu cầu của người dùng khớp với mục đích skill | Cung cấp quy trình, lệnh chạy và cách xử lý lỗi |
| Lớp 3 | Các file trong `references/`, `scripts/`, `assets/` | Claude chủ động tìm và đọc khi bước thực thi yêu cầu | Cung cấp chi tiết kỹ thuật, script hoặc mẫu biểu |

### 2. Khả năng kết hợp và tính đa nền tảng
- **Kết hợp linh hoạt (Composability):** Nhiều skill có thể được bật đồng thời. Khi viết skill, không giả định đây là năng lực duy nhất đang hoạt động.
- **Đa nền tảng (Portability):** Cùng một thư mục skill có thể chạy trên Claude.ai, Claude Code và qua API mà không cần viết lại, miễn là môi trường đích hỗ trợ công cụ mà skill gọi.

## Quan hệ giữa Skill và MCP (Model Context Protocol)
Nếu ví hệ thống như một nhà bếp chuyên nghiệp thì **MCP là căn bếp** (cung cấp thiết bị, nguyên liệu, kết nối dữ liệu thời gian thực), còn **Skill là công thức nấu ăn** (chỉ rõ trình tự các bước để tạo ra món ăn hoàn chỉnh).

| Tiêu chí | MCP (Lớp kết nối) | Skill (Lớp kiến thức) |
|---|---|---|
| Chức năng chính | Kết nối Claude với dịch vụ ngoài (Linear, Notion, Asana, Sentry...) | Hướng dẫn Claude cách phối hợp công cụ hiệu quả |
| Câu hỏi giải quyết | Claude *có thể chạm tới* dữ liệu/hành động nào? | Claude *nên thực hiện* quy trình đó theo thứ tự nào? |
| Khi thiếu lớp còn lại | Có dữ liệu nhưng không có chuẩn làm việc chung | Có quy trình nhưng thiếu quyền truy cập hệ thống ngoài (với tác vụ cần tích hợp) |

Lợi ích khi bổ sung skill lên trên MCP server:
- Quy trình tự động kích hoạt đúng ngữ cảnh, người mới không phải hỏi "bước tiếp theo làm gì".
- Giảm lỗi gọi công cụ sai thứ tự và giữ chất lượng kết quả ổn định giữa các phiên chat.

## Khi nào dùng
- Khi bạn phải lặp lại cùng một đoạn prompt hướng dẫn quy trình, chuẩn trình bày hoặc quy tắc nghiệp vụ qua nhiều cuộc trò chuyện.
- Khi đã có MCP server kết nối dịch vụ nhưng người dùng vẫn lúng túng hoặc tạo ra kết quả thiếu đồng nhất.
- Khi cần đóng gói quy trình chuẩn của nhóm để chia sẻ trên Claude.ai, Claude Code hoặc gọi qua API.

## Sai lầm thường gặp
- **Sai tên file hoặc thư mục:** Đặt tên `skill.md`, `SKILL.MD`, hoặc dùng tên thư mục có dấu cách/chữ hoa khiến hệ thống từ chối nạp.
- **Đặt `README.md` trong thư mục skill:** Gây dư thừa và nhầm lẫn; `README.md` chỉ nên đặt ở cấp ngoài cùng của GitHub repository dành cho người đọc.
- **Nhồi toàn bộ tài liệu dài vào `SKILL.md`:** Bỏ qua thư mục `references/` làm phình ngữ cảnh mỗi khi skill kích hoạt, khiến phản hồi chậm và giảm độ chính xác.

---
*Nguồn: Tóm tắt bằng lời riêng từ "Cẩm nang đầy đủ xây dựng Skill cho Claude" (bản dịch cộng đồng tiếng Việt của tài liệu hướng dẫn của Anthropic). Không chép nguyên văn.*
