---
id: software/system-design/vi-interview-guide/giao-thuc-va-thiet-ke-api
canonical_question: "Khi nào nên chọn HTTP, TCP, UDP, RPC (gRPC) hay REST trong thiết kế hệ thống và API?"
aliases:
- so sánh TCP và UDP
- REST vs RPC gRPC
- giao thức HTTP stateless
- thiết kế RESTful API trong system design
- các phương thức giao tiếp giữa các service
- khi nào dùng UDP TCP HTTP gRPC
entity_type: book_chapter
domain: software > system-design > vi-interview-guide
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Hướng dẫn cách tiếp cận phỏng vấn System Design\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Các Phương Thức Giao Tiếp và Thiết Kế API (HTTP, TCP, UDP, RPC, REST)

## TL;DR
Lựa chọn giao thức truyền thông và phong cách thiết kế API quyết định trực tiếp đến độ trễ, độ tin cậy và khả năng mở rộng của hệ thống phân tán. Ở tầng giao vận, kỹ sư đánh đổi giữa tính toàn vẹn thứ tự của TCP và tốc độ thời gian thực của UDP; ở tầng ứng dụng, RESTful HTTP mang lại khả năng tương thích rộng rãi cho các client bên ngoài, trong khi RPC (như gRPC) tối ưu hóa hiệu năng giao tiếp nội bộ giữa các microservices.

## So sánh các giao thức ở tầng Giao vận (Transport) và Ứng dụng (Application)
| Giao thức / Cơ chế | Tầng & Đặc tính kết nối | Cơ chế đảm bảo & Định dạng | Ưu điểm nổi bật | Nhược điểm & Giới hạn |
|---|---|---|---|---|
| TCP | Giao vận; hướng kết nối (bắt tay 3 bước - 3-way handshake) | Đánh số thứ tự gói tin, xác nhận (ACK), tự gửi lại gói mất, kiểm soát luồng | Đảm bảo dữ liệu đến đích đầy đủ, nguyên vẹn và đúng thứ tự ban đầu | Tốn độ trễ thiết lập kết nối và chi phí quản lý phiên |
| UDP | Giao vận; không kết nối (connectionless, "gửi là quên" - fire-and-forget) | Header rất nhỏ, không bắt tay, không ACK, không tự gửi lại gói rớt | Tốc độ cực nhanh, độ trễ thấp, hỗ trợ gửi multicast/broadcast | Gói tin có thể thất lạc hoặc đến lộn xộn; ứng dụng phải tự chịu rủi ro |
| HTTP | Ứng dụng (thường chạy trên TCP cổng 80/443; HTTP/3 chạy trên QUIC/UDP) | Mô hình Request-Response, phi trạng thái (stateless) giữa các lần gọi | Chuẩn mặc định của web, dễ mở rộng ngang vì server không giữ phiên | Phải kèm cookie/token nếu muốn duy trì trạng thái đăng nhập |
| RPC (gRPC, Thrift, Dubbo) | Ứng dụng; gọi hàm từ xa thông qua client stub và server skeleton | Thường dùng định dạng nhị phân (Protocol Buffers trên HTTP/2 với gRPC) | Độ trễ cực thấp, tiết kiệm băng thông, gọi hàm từ xa trực quan như hàm nội bộ | Khớp nối chặt (tight coupling) qua file IDL/`.proto`; trình duyệt web khó gọi trực tiếp |
| REST | Phong cách kiến trúc API xây dựng trên nền giao thức HTTP | Lấy tài nguyên (Resource URL) làm trung tâm, trao đổi dạng text (JSON/XML) | Đơn giản, chuẩn hóa, mọi nền tảng (web, mobile, đối tác) đều tích hợp được ngay | Payload văn bản (JSON) nặng và parse chậm hơn nhị phân; dễ thiếu đồng bộ nếu thiết kế ẩu |

## Nguyên tắc thiết kế RESTful API và HTTP Verbs chuẩn mực
REST tận dụng trực tiếp các động từ (verbs) và mã trạng thái của HTTP để thao tác trên các danh từ chỉ tài nguyên (ví dụ `/tasks` hoặc `/users`):

| Phương thức (HTTP Verb) | Ví dụ Endpoint | Ý nghĩa thao tác trên tài nguyên | Đặc tính trạng thái & Phản hồi điển hình |
|---|---|---|---|
| `GET` | `GET /tasks`, `GET /tasks/123` | Chỉ đọc danh sách hoặc chi tiết một tài nguyên | An toàn, idempotent, không sửa dữ liệu trên server; trả về JSON |
| `POST` | `POST /tasks` | Tạo mới một tài nguyên hoặc gửi form/upload xử lý | Gửi payload JSON trong body; tạo bản ghi mới nên mặc định không idempotent |
| `PUT` | `PUT /tasks/123` | Cập nhật thay thế toàn bộ thông tin tài nguyên `123` | Mang tính idempotent; ghi đè trạng thái tài nguyên tại URL |
| `PATCH` | `PATCH /tasks/123` | Cập nhật một phần (chỉ sửa vài trường cụ thể) của tài nguyên | Tiết kiệm băng thông hơn `PUT` khi chỉ đổi 1–2 thuộc tính |
| `DELETE` | `DELETE /tasks/123` | Xóa tài nguyên `123` khỏi hệ thống | Thường trả về mã trạng thái `204 No Content` khi xóa thành công |
| `OPTIONS` | `OPTIONS /tasks` | Hỏi máy chủ danh sách các phương thức HTTP được hỗ trợ | Thường được trình duyệt gọi tự động khi kiểm tra tiền điều kiện CORS |

- **Tận dụng tính Stateless của HTTP/REST:** Mỗi request tự mang đủ thông tin xác thực (như header token) mà không bắt server ghi nhớ phiên trước đó, giúp hệ thống dễ dàng nhân bản nhiều máy chủ đứng sau Load Balancer.

## Khi nào dùng giao thức nào trong bài toán System Design
1. **Khi nào chọn TCP vs UDP:**
   - Chọn **TCP** cho mọi tác vụ không chấp nhận mất mát hay sai lệch dữ liệu: kết nối ứng dụng tới Database (MySQL, PostgreSQL), truyền file (FTP), gửi email (SMTP), giao dịch tài chính và nền tảng cho HTTP chuẩn.
   - Chọn **UDP** cho các luồng thời gian thực ưu tiên tốc độ hơn độ hoàn hảo (mất vài khung hình còn hơn bị trễ/đứng hình): gọi thoại/video (VoIP, RTP), livestream, game hành động trực tuyến, thu thập số liệu cảm biến IoT liên tục và truy vấn phân giải tên miền (DNS).
2. **Khi nào chọn REST vs RPC (gRPC):**
   - Chọn **REST over HTTP/HTTPS** cho API công khai (Public API), cổng giao tiếp với trình duyệt web, ứng dụng di động hoặc đối tác bên thứ ba cần tính tương thích rộng (interoperability), dễ kiểm thử bằng cURL/Postman và khớp nối lỏng (loose coupling).
   - Chọn **RPC (như gRPC)** cho giao tiếp nội bộ giữa các dịch vụ phía sau (backend-to-backend microservices) do cùng một tổ chức kiểm soát, hoặc các bài toán đòi hỏi phản hồi tính bằng mili-giây như đấu giá quảng cáo thời gian thực.
3. **Mô hình kết hợp thực tế:** Dùng một lớp **API Gateway chuẩn RESTful** ở biên ngoài cùng để phục vụ trình duyệt và mobile, sau đó từ API Gateway vào các microservices bên trong thì chuyển sang giao tiếp bằng **gRPC** để tối ưu tốc độ.

## Sai lầm thường gặp
- Đề xuất dùng UDP cho các tính năng truyền file tài liệu, thanh toán hoặc chat văn bản cần đảm bảo không mất tin nhắn mà không tự xây dựng thêm tầng kiểm soát lỗi.
- Dùng gRPC thuần để gọi trực tiếp từ mã JavaScript trên trình duyệt web của người dùng mà quên mất trình duyệt không hỗ trợ đầy đủ HTTP/2 framing cho gRPC (bắt buộc phải có gRPC-Web proxy hoặc API Gateway chuyển đổi).
- Thiết kế API tự xưng là RESTful nhưng dùng toàn bộ phương thức `POST` cho mọi thao tác đọc/xóa (như `POST /getTask`, `POST /deleteTask`) hoặc lưu trạng thái phiên cục bộ trên từng server làm mất khả năng mở rộng ngang.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Hướng dẫn cách tiếp cận phỏng vấn System Design" (Nguyễn Thế Huy). Không chép nguyên văn.*
