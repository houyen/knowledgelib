---
id: software/system-design/vi-interview-guide/bao-mat-monitoring-observability
canonical_question: "Cách thiết kế bảo mật nhiều lớp (Authentication, Authorization, API/Data Security) và hệ thống Monitoring, Observability (Logs, Metrics, Traces) như thế nào?"
aliases:
- authentication vs authorization JWT OAuth2 RBAC ABAC
- bảo mật API rate limiting CORS XSS CSRF cookie
- monitoring vs observability
- ba trụ cột observability logs metrics traces
- prometheus grafana elk jaeger opentelemetry
- bảo mật và giám sát trong system design
entity_type: book_chapter
domain: software > system-design > vi-interview-guide
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Hướng dẫn cách tiếp cận phỏng vấn System Design\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Bảo Mật Hệ Thống, Phân Quyền, Monitoring và Observability

## TL;DR
Một thiết kế hệ thống hoàn chỉnh không dừng ở việc chạy đúng tính năng mà phải được bảo vệ theo nguyên tắc phòng thủ nhiều lớp (Defense in Depth) từ xác thực, phân quyền đến mã hóa đường truyền/lưu trữ. Song song với bảo mật, việc tích hợp Monitoring (cảnh báo khi chỉ số vượt ngưỡng) và Observability (điều tra nguyên nhân gốc rễ qua Logs, Metrics, Traces) giúp đội ngũ vận hành phát hiện sớm và khoanh vùng sự cố nhanh chóng trong môi trường phân tán.

## Bảo mật hệ thống phân tán: Xác thực (Authentication) và Phân quyền (Authorization)
| Phân nhóm | Cơ chế / Tiêu chuẩn | Đặc điểm kỹ thuật & Lưu ý thiết kế |
|---|---|---|
| Authentication (Xác minh danh tính: Bạn là ai?) | Mật khẩu + MFA/2FA | Mật khẩu bắt buộc băm kèm chuỗi ngẫu nhiên (`hash + salt` bằng Argon2, bcrypt, PBKDF2) để chống bảng dò rainbow table; thêm OTP/SMS cho giao dịch nhạy cảm |
| Authentication | Session-based | Lưu trạng thái phiên trên server và gửi `session_id` qua cookie; dễ thu hồi (revoke) ngay lập tức khi đăng xuất nhưng cần đồng bộ trạng thái giữa các server |
| Authentication | JWT (JSON Web Token) | Token tự chứa (header, payload, chữ ký số) truyền qua HTTP header, không cần server lưu trạng thái (stateless); lưu ý payload chỉ được ký chứ không mã hóa nên cấm để lộ dữ liệu nhạy cảm và khó thu hồi trước hạn |
| Authorization (Kiểm soát quyền hạn: Được làm gì?) | RBAC (Theo vai trò) | Gán quyền theo nhóm vai trò (`Admin`, `Editor`, `Viewer`); đơn giản dễ quản lý nhưng dễ gặp hiện tượng bùng nổ vai trò (role explosion) khi quy tắc chi tiết hóa |
| Authorization | ABAC (Theo thuộc tính) | Đánh giá điều kiện linh hoạt dựa trên thuộc tính người dùng, tài nguyên và môi trường (VD: phòng Kế toán + giờ hành chính + IP nội bộ); rất mịn nhưng thiết lập phức tạp |
| Authorization | OAuth2 (+ OIDC) | Giao thức ủy quyền cấp `access token` có giới hạn phạm vi (`scope`) cho ứng dụng bên thứ ba truy cập Resource Server mà không cần chia sẻ mật khẩu gốc (thêm OpenID Connect nếu cần xác thực định danh) |

## Bảo mật API, Dữ liệu, HTTPS/TLS và Cookie
- **Bảo vệ tầng API:** Không nhúng cứng API Key ở code client (lưu ở biến môi trường/server, giới hạn quyền và xoay vòng định kỳ); cấu hình **CORS** chỉ mở cho các domain tin cậy; áp dụng **Rate Limiting** (ví dụ khóa tạm thời nếu nhập sai mật khẩu quá 5 lần/10 phút) để chống DoS/brute-force; kiểm tra đầu vào theo danh sách trắng (**Input Validation**) từ sớm để chặn SQL Injection.
- **Chống tấn công trình duyệt & Bảo vệ dữ liệu:** Escape/encode dữ liệu hiển thị kèm header **CSP** để chống chèn mã độc **XSS**; dùng CSRF token kết hợp thuộc tính cookie `SameSite=Strict/Lax` và xác nhận lại mật khẩu/OTP để chống giả mạo yêu cầu **CSRF**. Mã hóa dữ liệu khi truyền bằng **HTTPS/TLS** (kèm HSTS, thuật toán AES-GCM/ECC) và mã hóa dữ liệu nhạy cảm khi lưu trữ (at-rest) trên đĩa/DB/HSM.
- **Thiết lập cờ bảo mật cho Cookie:** Luôn bật `Secure` (chỉ truyền qua HTTPS), `HttpOnly` (chặn mã JavaScript đọc cookie khi dính XSS), `SameSite`, đặt thời gian hết hạn hợp lý và dùng tiền tố `__Host-` hoặc `__Secure-`.

### 3 kịch bản thiết kế bảo mật điển hình từ thực tế
| Kịch bản hệ thống | Các lớp bảo vệ bắt buộc triển khai |
|---|---|
| Upload tài liệu / File | Bắt buộc đăng nhập (Authentication) → lọc định dạng trắng (chỉ nhận PNG/JPG...), giới hạn dung lượng, quét virus → đổi sang tên file ngẫu nhiên, lưu vào bucket tách biệt chỉ cho server đọc → phân quyền (Authorization) chỉ người tải lên hoặc nhóm được phép mới xem/xóa được |
| Quản lý người dùng (User Management) | Phân quyền RBAC tách biệt `Admin` và `User` → lưu mật khẩu bằng `hash + salt` → khóa tạm thời khi đăng nhập sai nhiều lần (chống brute-force) → bật MFA (OTP) cho tài khoản nhạy cảm → ghi audit log mọi thao tác |
| Ứng dụng tài chính / Ngân hàng | Xác thực mạnh (mật khẩu + OTP SMS) cho mọi lệnh chuyển tiền → truyền qua HTTPS/TLS → mã hóa số thẻ/CCCD/tài khoản trong DB hoặc HSM → phân quyền ABAC (chặn giao dịch ngoài giờ hoặc ngoài vùng IP hợp lệ, giao dịch lớn cần admin duyệt) |

## Phân biệt Monitoring và Observability cùng 3 trụ cột dữ liệu
| Tiêu chí | Monitoring (Giám sát hệ thống) | Observability (Khả năng quan sát nội tại) |
|---|---|---|
| Câu hỏi trả lời | *"Điều gì đang xảy ra? Hệ thống có đang bất thường không?"* (Ví như đèn báo nhiệt độ động cơ trên táp-lô xe) | *"Tại sao sự cố này lại xảy ra?"* (Ví như cắm máy chẩn đoán đọc sâu từng bộ phận dưới nắp capo) |
| Cách tiếp cận | Theo dõi các chỉ số cố định đã biết trước (known unknowns) và phát cảnh báo (alert) khi vượt ngưỡng (VD: CPU > 90%, lỗi HTTP 5xx > 1%) | Chủ động khám phá và truy vấn linh hoạt để tìm nguyên nhân gốc rễ của cả những lỗi mới chưa từng dự đoán trước |

### Ba trụ cột của Observability và Công cụ phổ biến
1. **Metrics (Chỉ số định lượng chuỗi thời gian):** Đo lường tổng quan xu hướng như RPS, độ trễ trung bình, tỷ lệ lỗi, % CPU/RAM để phát hiện đột biến (spike/drop). *Công cụ:* **Prometheus** (thu thập & cảnh báo), **Grafana** (vẽ dashboard), **Nagios/Zabbix**.
2. **Logs (Nhật ký sự kiện):** Ghi lại chi tiết ngữ cảnh từng hành động, thông điệp lỗi và stack trace để lần dấu lịch sử. *Công cụ:* **ELK Stack** (Logstash thu thập, Elasticsearch lưu/tìm kiếm, Kibana hiển thị tập trung).
3. **Traces (Dấu vết phân tán - Distributed Tracing):** Gắn một ID duy nhất xuyên suốt hành trình của một request đi qua nhiều microservices (chia thành các đoạn *span*) để chỉ đích danh service nào gây nghẽn hay timeout. *Công cụ:* **Jaeger**, **Zipkin**.
- *Hệ sinh thái tích hợp:* Dùng chuẩn mở **OpenTelemetry** để gắn mã thu thập (instrument) cả 3 trụ cột trong code, hoặc dùng các nền tảng thương mại tất-cả-trong-một như **Datadog**, **New Relic**, **Honeycomb**, **Lightstep**.

## Cách áp dụng và trình bày khi phỏng vấn
- **Nêu tư duy Defense in Depth và đánh đổi hiệu năng:** Trình bày bảo mật xuyên suốt từ mạng (Firewall/TLS), cổng API (Rate limit, OAuth2/JWT), ứng dụng (Input validation, RBAC) xuống dữ liệu (Hash+salt, mã hóa DB), đồng thời nhắc tới chi phí CPU của TLS handshake và thuật toán băm.
- **Chủ động gắn Giám sát vào cuối bài thiết kế:** Nêu rõ các KPI sẽ đo (RPS, latency, error rate, CPU), ngưỡng bắn cảnh báo (ví dụ: lỗi > 2% hoặc CPU > 80% kéo dài thì báo qua Slack/SMS) và cách kết hợp Prometheus/Grafana + ELK + Jaeger để rút ngắn thời gian điều tra sự cố.

## Sai lầm thường gặp
- Lưu thông tin nhạy cảm (như mật khẩu, số thẻ ngân hàng) vào phần payload của JWT vì lầm tưởng JWT đã được mã hóa ẩn đi (thực tế payload chỉ được mã hóa Base64 ai cũng đọc được).
- Lưu mật khẩu người dùng dưới dạng văn bản thuần (plaintext) hoặc dùng hàm băm nhanh không có chuỗi ngẫu nhiên (salt), khiến toàn bộ tài khoản bị lộ ngay khi rò rỉ bảng dữ liệu.
- Chỉ dựng bảng biểu Monitoring theo dõi CPU/RAM máy chủ mà thiếu Distributed Tracing và Centralized Logging trong kiến trúc microservices, dẫn đến khi có cảnh báo lỗi 500 thì không biết request bị chết ở dịch vụ con nào.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Hướng dẫn cách tiếp cận phỏng vấn System Design" (Nguyễn Thế Huy). Không chép nguyên văn.*
