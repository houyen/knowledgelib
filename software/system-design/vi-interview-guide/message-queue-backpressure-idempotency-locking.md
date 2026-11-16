---
id: software/system-design/vi-interview-guide/message-queue-backpressure-idempotency-locking
canonical_question: "Khi nào cần dùng Message Queue, Backpressure, Idempotency Key và cơ chế khóa (Pessimistic vs Optimistic Locking)?"
aliases:
- message queue rabbitmq kafka sqs
- cơ chế backpressure trong hàng đợi
- idempotency key tính bất biến API
- pessimistic locking vs optimistic locking
- khóa bi quan và khóa lạc quan
- xử lý bất đồng bộ và chống trùng lặp giao dịch
entity_type: book_chapter
domain: software > system-design > vi-interview-guide
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Hướng dẫn cách tiếp cận phỏng vấn System Design\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Message Queue, Backpressure, Idempotency và Cơ Chế Khóa

## TL;DR
Để xử lý tải cao mà không làm treo luồng người dùng hay sai lệch dữ liệu khi chạy song song, hệ thống phân tán tách các tác vụ nặng sang xử lý bất đồng bộ qua Message Queue kèm cơ chế kiểm soát tràn hàng đợi (Backpressure). Đồng thời, ở tầng dữ liệu và API, kỹ sư kết hợp Idempotency Key để chống thực thi trùng lặp khi mạng lỗi (retry) và chọn đúng chiến lược khóa (Pessimistic hoặc Optimistic Locking) khi nhiều tiến trình cùng sửa một bản ghi.

## Mô hình Message Queue và Xử lý bất đồng bộ
Thay vì bắt thành phần gửi phải đứng chờ thành phần nhận xử lý xong (đồng bộ), Message Queue tạo ra vùng đệm trung gian giúp tách rời (decouple) các dịch vụ:
- **Producer (Nhà sản xuất):** Tạo thông điệp mô tả công việc (ví dụ: `"resize ảnh X.png"` hoặc `"chuyển đổi định dạng video 123"`) đẩy vào hàng đợi rồi trả phản hồi ngay cho người dùng.
- **Message Queue (Hàng đợi):** Lưu giữ thông điệp (thường theo thứ tự vào trước ra trước - FIFO) trong RAM hoặc trên đĩa và thường được gom cụm (cluster) để tránh điểm lỗi đơn.
- **Consumer (Người tiêu thụ):** Các tiến trình worker chạy độc lập lấy thông điệp ra khỏi queue (qua cơ chế poll hoặc subscribe) để thực thi theo năng lực xử lý của mình; có thể dễ dàng tăng số lượng consumer để chạy song song.

### So sánh các hệ thống Message Queue phổ biến
| Hệ thống | Đặc trưng kiến trúc | Trường hợp sử dụng phù hợp nhất |
|---|---|---|
| RabbitMQ | Message broker mã nguồn mở theo giao thức AMQP; mạnh về định tuyến linh hoạt (exchange/routing key), xác nhận tin (ack) và retry | Hàng đợi tác vụ nền (background jobs), giao tiếp nghiệp vụ cần đảm bảo chuyển phát tin cậy |
| Apache Kafka | Nền tảng event streaming phân tán; thông lượng (throughput) cực cao, lưu trữ log bền vững trên đĩa để đọc lại lịch sử theo nhóm pub-sub | Thu thập sự kiện thời gian thực quy mô lớn, tracking hành vi click/view, luồng log và phân tích dữ liệu |
| AWS SQS | Dịch vụ hàng đợi đám mây quản lý hoàn toàn (serverless), tự động mở rộng và tính phí theo lượt dùng (tương tự Azure Service Bus, Google Pub/Sub) | Hệ thống chạy trên cloud muốn triển khai nhanh mà không tốn công vận hành cụm máy chủ queue |

## Cơ chế Backpressure (Phản áp lực) khi hàng đợi quá tải
Khi tốc độ gửi của Producer vượt xa tốc độ xử lý của Consumer trong thời gian dài, hàng đợi sẽ ùn ứ, tràn bộ nhớ/đĩa và gây sập toàn bộ cụm queue. Backpressure giải quyết tình trạng "ngộp tải" này qua 3 hướng:
1. **Chặn hoặc từ chối từ phía Queue:** Đặt ngưỡng dung lượng bộ nhớ/độ dài hàng đợi (như trong RabbitMQ); khi chạm trần, queue từ chối nhận thêm hoặc trả lỗi để chặn Producer.
2. **Điều tiết tốc độ ở phía Producer:** Ứng dụng gửi theo dõi độ dài hàng đợi (ví dụ: phát hiện tồn đọng trên 10.000 message chưa xử lý) để chủ động giảm tần suất gửi hoặc tạm dừng nhận việc mới.
3. **Mở rộng phía tiêu thụ (Scale-out Consumer):** Thiết lập cảnh báo khi hàng đợi dài ra để tự động bật thêm các worker xử lý song song hoặc chuyển sang lưu đệm xuống đĩa.

## Tính bất biến (Idempotency) và Idempotency Key
**Idempotency** đảm bảo việc thực thi cùng một yêu cầu một lần hay nhiều lần liên tiếp đều để lại kết quả cuối cùng trên hệ thống hoàn toàn giống nhau:
- **Trong giao thức HTTP/REST:** Các phương thức `GET`, `PUT`, `DELETE` tự nhiên mang tính idempotent, trong khi `POST` và `PATCH` mặc định không idempotent (gọi lặp lại sẽ tạo nhiều đơn hàng hoặc cộng/trừ dồn nhiều lần).
- **Giải pháp Idempotency Key:** Client sinh một mã định danh duy nhất (token/UUID) gắn kèm vào mỗi yêu cầu tạo giao dịch (chuyển tiền, thanh toán, đặt hàng). Server kiểm tra khóa này: nếu đã xử lý trước đó (do client retry khi mạng chập chờn), hệ thống chỉ trả lại kết quả cũ thay vì trừ tiền lần thứ hai.

## So sánh Khóa bi quan (Pessimistic) và Khóa lạc quan (Optimistic Locking)
| Tiêu chí | Pessimistic Locking (Khóa bi quan) | Optimistic Locking (Khóa lạc quan) |
|---|---|---|
| Giả định cốt lõi | Xung đột dữ liệu rất dễ xảy ra → khóa chặn ngay từ lúc bắt đầu đọc để sửa | Xung đột hiếm khi xảy ra → cứ cho đọc/sửa song song, chỉ kiểm tra lúc ghi (commit) |
| Cơ chế thực thi | Giữ khóa độc quyền trên bản ghi suốt giao dịch (VD: `SELECT ... FOR UPDATE`), luồng khác phải xếp hàng chờ | Thêm cột `version` hoặc `timestamp`; chỉ ghi khi phiên bản chưa bị ai đổi (`UPDATE ... WHERE id = ? AND version = ?`) |
| Ưu điểm | Bảo vệ tính nhất quán tuyệt đối, không tốn công hủy bỏ và làm lại từ đầu | Không giữ khóa cứng, thông lượng đồng thời rất cao, loại bỏ nguy cơ deadlock |
| Nhược điểm | Nghẽn cổ chai, giảm hiệu năng khi tải đồng thời cao và dễ phát sinh khóa chết (deadlock) | Nếu đụng độ thật, giao dịch đến sau bị thất bại và ứng dụng phải tự xử lý rollback/retry |

## Khi nào dùng từng kỹ thuật
- **Dùng Message Queue:** Khi tác vụ không cần trả kết quả ngay (gửi email xác nhận, nén video), khi cần làm phẳng đỉnh tải đột biến (flash sale, livestream) hoặc khi cần tách rời các microservices (Order Service phát sự kiện cho Inventory và Payment).
- **Bắt buộc có Idempotency Key:** Cho mọi API thay đổi trạng thái quan trọng (thanh toán, trừ ví, tạo đơn) có cơ chế tự động thử lại (retry) qua mạng.
- **Chọn Optimistic vs Pessimistic Locking:** Dùng **Optimistic Locking** cho các ứng dụng web thông thường có tỷ lệ đọc cao và ít va chạm trực tiếp (như sửa thông tin hồ sơ, đếm lượt xem); dùng **Pessimistic Locking** cho nghiệp vụ tài chính/ngân hàng hoặc đặt chỗ số lượng cực hiếm nơi xung đột xảy ra liên tục và không được phép sai lệch.

## Sai lầm thường gặp
- Đưa Message Queue vào hệ thống để chống sập giờ cao điểm nhưng quên thiết kế cơ chế Backpressure và giới hạn độ dài queue, dẫn đến tràn RAM làm chết chính cụm Message Broker.
- Bật cơ chế tự động Retry (thử lại khi timeout) ở phía client/service gọi API thanh toán nhưng phía nhận không kiểm tra Idempotency Key, gây trừ tiền khách hàng nhiều lần.
- Áp dụng Pessimistic Locking (`FOR UPDATE`) cho các giao dịch kéo dài có gọi API bên thứ ba ở giữa, khiến kết nối Database bị treo hàng loạt và gây deadlock toàn hệ thống.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Hướng dẫn cách tiếp cận phỏng vấn System Design" (Nguyễn Thế Huy). Không chép nguyên văn.*
