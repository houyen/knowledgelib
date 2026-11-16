---
id: software/system-design/vi-interview-guide/khai-niem-nen-tang-va-thanh-phan-he-thong
canonical_question: "Các chỉ số nền tảng và thành phần cốt lõi trong thiết kế hệ thống gồm những gì?"
aliases:
- latency throughput scalability availability reliability
- các thành phần trong system design
- kiến trúc cấp cao high level architecture
- web server app server database cache cdn queue
- khái niệm cơ bản thiết kế hệ thống
- vertical scaling vs horizontal scaling
entity_type: book_chapter
domain: software > system-design > vi-interview-guide
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Hướng dẫn cách tiếp cận phỏng vấn System Design\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Khái Niệm Nền Tảng và Các Thành Phần Hệ Thống

## TL;DR
Mọi hệ thống phân tán phức tạp đều được đánh giá qua 5 thuộc tính cốt lõi (Latency, Throughput, Scalability, Availability, Reliability) và lắp ghép từ các khối kiến trúc cơ bản. Trước khi đi vào chi tiết kỹ thuật, kỹ sư cần phác thảo kiến trúc cấp cao (High-Level Architecture) để định hình luồng tương tác giữa Web/App Server, Database, Load Balancer, Cache, CDN và Message Queue.

## 5 chỉ số và tính chất nền tảng của hệ thống
| Khái niệm | Bản chất đo lường | Mục tiêu thiết kế & Đánh đổi |
|---|---|---|
| Latency (Độ trễ) | Thời gian chờ từ lúc gửi một request đến khi nhận phản hồi (thường đo bằng ms) | Càng thấp càng mượt; giảm bằng cách đặt máy chủ gần user, tối ưu mạng và dùng cache |
| Throughput (Thông lượng) | Khối lượng yêu cầu hoặc dữ liệu xử lý thành công trong một đơn vị thời gian (VD: req/s) | Phản ánh sức tải đồng thời; hệ thống quá tải có thể có throughput cao nhưng kéo latency tăng vọt |
| Scalability (Khả năng mở rộng) | Khả năng duy trì hiệu năng khi lượng người dùng hoặc dữ liệu tăng mạnh (và thu nhỏ khi tải giảm) | Ưu tiên mở rộng ngang (thêm máy chủ) kết hợp cân bằng tải hơn là chỉ nâng cấp cấu hình 1 máy |
| Availability (Tính khả dụng) | Tỷ lệ phần trăm thời gian hệ thống sẵn sàng phản hồi hợp lệ (đo bằng các con số 9: 99.9%, 99.999%) | Tăng bằng máy chủ dự phòng, cân bằng tải và triển khai đa vùng (multi-zone, multi-region) |
| Reliability (Độ tin cậy) | Khả năng vận hành đúng đắn, bền bỉ qua thời gian dài và bảo toàn dữ liệu không bị mất mát/sai lệch | Bao hàm cả tính khả dụng cao cộng với tính toàn vẹn dữ liệu (nhờ sao lưu, replication, xóa SPOF) |

### Phân biệt hai hướng mở rộng (Scaling)
- **Vertical Scaling (Mở rộng chiều dọc / Scale-up):** Nâng cấp CPU, RAM, ổ cứng trên chính máy chủ hiện tại. Đơn giản nhưng sớm chạm trần phần cứng và vẫn tiềm ẩn rủi ro hỏng máy đơn lẻ.
- **Horizontal Scaling (Mở rộng chiều ngang / Scale-out):** Bổ sung thêm nhiều máy chủ chạy song song để chia tải. Linh hoạt và chịu lỗi tốt hơn, nhưng bắt buộc phải có cơ chế điều phối (Load Balancer) và quản lý dữ liệu phân tán.

### Phân biệt Availability và Reliability
- Một hệ thống **Reliable** (tin cậy) gần như chắc chắn có **Availability** cao vì nó hiếm khi gặp sự cố.
- Ngược lại, hệ thống có **Availability** cao (hiếm khi downtime) chưa chắc đã **Reliable** nếu khi xảy ra lỗi chuyển đổi nó làm thất thoát hoặc ghi sai giao dịch của người dùng.

## Kiến trúc cấp cao (High-Level Architecture)
Kiến trúc cấp cao là sơ đồ khối tổng quát mô tả các thành phần chính và luồng dữ liệu giữa chúng mà chưa đi sâu vào code thực thi. Trong phỏng vấn, vẽ High-Level Architecture trước giúp ứng viên và người phỏng vấn thống nhất bức tranh toàn cảnh, nhận diện sớm các mối quan hệ và điểm nghẽn cổ chai (bottleneck).

## Các thành phần phổ biến trong hệ thống lớn
| Thành phần | Vai trò chính trong kiến trúc | Ví dụ công nghệ / Tình huống điển hình |
|---|---|---|
| Web Server | Cửa ngõ tiếp nhận HTTP request từ client, trả nội dung tĩnh (HTML/CSS/JS/ảnh), lọc bảo mật cơ bản và chuyển tiếp yêu cầu vào trong | Nginx, Apache, IIS |
| Application Server | Thực thi nghiệp vụ cốt lõi (business logic), tính toán, gọi Database hoặc dịch vụ phụ trợ để tạo kết quả động (JSON/HTML) | Spring Boot (Java), Django/Flask (Python), Express (Node.js), .NET |
| Database | Lưu trữ và truy xuất dữ liệu lâu dài; thường tách riêng khỏi App Server và nhân bản (1 máy ghi, nhiều máy đọc) | SQL (MySQL, PostgreSQL, Oracle) hoặc NoSQL (MongoDB, Cassandra, DynamoDB) |
| Load Balancer | Đứng trước cụm server để chia đều lưu lượng, tự động ngắt máy hỏng khỏi vòng phân phối và hỗ trợ thêm/bớt server không gây gián đoạn | HAProxy, Nginx, Cloud Load Balancer (xoay vòng round-robin, least connections) |
| Cache | Bộ nhớ đệm tốc độ cao (thường trên RAM) lưu tạm dữ liệu đọc nhiều ít đổi để trả kết quả tức thì và giảm tải cho Database gốc | Client browser cache, In-memory app cache, Distributed cache (Redis, Memcached) |
| CDN | Mạng lưới máy chủ biên đặt tại nhiều khu vực địa lý giúp phân phát nội dung tĩnh từ trạm gần người dùng nhất | Cloudflare, Akamai, Amazon CloudFront |
| Message Queue | Kênh trung gian lưu giữ thông điệp giúp các service giao tiếp bất đồng bộ (producer đẩy việc vào, consumer lấy ra xử lý dần) | RabbitMQ, Apache Kafka, ActiveMQ, Amazon SQS |

## Khi nào dùng từng thành phần
- **Tách riêng Web Server và App Server (kèm Load Balancer):** Khi lưu lượng vượt quá sức chịu đựng của một máy đơn lẻ và cần triển khai nhiều instance ứng dụng giống hệt nhau chạy song song.
- **Bổ sung Cache và CDN:** Khi hệ thống có tỷ lệ đọc áp đảo ghi (như trang chủ tin tức, danh sách bài viết hot, file ảnh/video) và người dùng phân bố ở nhiều khu vực địa lý xa máy chủ gốc.
- **Đưa Message Queue vào luồng xử lý:** Khi có các tác vụ tốn thời gian nhưng không cần trả kết quả ngay cho người dùng (như gửi email xác nhận đăng ký) hoặc cần làm phẳng các đợt tải tăng đột biến.

## Sai lầm thường gặp
- Đồng nhất Latency với Throughput: tối ưu cho từng request chạy nhanh nhưng quên kiểm tra khả năng chịu tải khi hàng chục nghìn request đổ vào cùng lúc.
- Lạm dụng Cache cho dữ liệu yêu cầu chính xác tuyệt đối theo thời gian thực mà không tính đến bài toán đồng bộ và xóa bộ nhớ đệm (cache invalidation).
- Gộp chung mọi xử lý phụ (gửi email, thông báo, ghi log) vào luồng đồng bộ của Application Server khiến thời gian phản hồi người dùng bị kéo dài và dễ sập khi tải cao.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Hướng dẫn cách tiếp cận phỏng vấn System Design" (Nguyễn Thế Huy). Không chép nguyên văn.*
