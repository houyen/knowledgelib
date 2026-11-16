---
id: software/system-design/vi-interview-guide/load-balancer-va-caching
canonical_question: "Load Balancer (L4 vs L7) và các chiến lược Caching hoạt động ra sao để mở rộng hệ thống?"
aliases:
- load balancer layer 4 vs layer 7
- thuật toán cân bằng tải round robin least connections
- chiến lược cập nhật cache
- cache-aside write-through write-back refresh-ahead
- các tầng đặt bộ nhớ đệm caching
- tối ưu hiệu suất hệ thống với cache và load balancer
entity_type: book_chapter
domain: software > system-design > vi-interview-guide
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Hướng dẫn cách tiếp cận phỏng vấn System Design\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Cân Bằng Tải (Load Balancer) và Bộ Nhớ Đệm (Caching)

## TL;DR
Load Balancer và Caching là bộ đôi cốt lõi giúp hệ thống mở rộng ngang và giảm độ trễ phản hồi. Trong khi Load Balancer đứng ở cửa ngõ để phân phối đều lưu lượng giữa các máy chủ và cô lập node hỏng (ở tầng mạng L4 hoặc tầng ứng dụng L7), thì Caching lưu trữ bản sao dữ liệu nóng tại nhiều lớp (từ trình duyệt, CDN đến RAM server) kèm các chiến lược đồng bộ để tránh quá tải cơ sở dữ liệu gốc.

## Cân bằng tải (Load Balancer): Thuật toán và Phân tầng
Load Balancer đóng vai trò điểm truy cập duy nhất (ẩn toàn bộ cụm server phía sau dưới một IP/URL), giúp chia tải, tăng tính sẵn sàng (tự động ngắt lưu lượng tới server chết qua health-check) và đôi khi kiêm nhiệm giải mã SSL, nén dữ liệu hoặc tường lửa WAF.

### Các thuật toán phân phối tải phổ biến
| Thuật toán | Nguyên lý điều phối | Tình huống sử dụng phù hợp |
|---|---|---|
| Round Robin | Xoay vòng tuần tự qua từng server (A → B → C rồi quay lại A) | Các máy chủ có cấu hình tương đương và thời gian xử lý mỗi request đồng đều |
| Weighted Round Robin | Chia vòng xoay theo trọng số sức mạnh phần cứng (VD: máy A nhận 5 phần, máy B nhận 1 phần) | Cụm máy chủ không đồng nhất về dung lượng CPU/RAM |
| Least Connections | Ưu tiên đẩy request mới sang máy chủ đang có ít kết nối hoạt động nhất | Các request có độ dài và chi phí xử lý chênh lệch lớn |
| IP Hash | Băm địa chỉ IP của client để gán cố định một người dùng vào một máy chủ cụ thể | Cần giữ trạng thái phiên cục bộ (session stickiness) khi chưa tách session ra kho chung |
| Least Response Time / Geo | Ưu tiên máy có thời gian phản hồi nhanh nhất hoặc nằm gần vị trí địa lý của người dùng nhất | Hệ thống phân tán nhiều khu vực hoặc hiệu năng giữa các node biến động |

### So sánh Load Balancer Tầng 4 (Layer 4) và Tầng 7 (Layer 7)
| Đặc điểm | Load Balancer Layer 4 (Transport Layer) | Load Balancer Layer 7 (Application Layer) |
|---|---|---|
| Dữ liệu quan sát | Chỉ đọc thông tin gói tin mạng: địa chỉ IP và cổng (Port) TCP/UDP | Đọc hiểu toàn bộ nội dung HTTP/HTTPS: URL path, Header, Cookie, Body |
| Khả năng định tuyến | Chuyển tiếp gói tin đơn thuần theo IP/Port, không phân biệt nội dung bên trong | Định tuyến thông minh theo nội dung (VD: `/video/1080p` sang cụm server khác `/video/720p`) |
| Tính năng bổ trợ | Không hỗ trợ đọc cookie hay xử lý nội dung ứng dụng | Hỗ trợ SSL Termination (giải mã HTTPS), sticky session bằng cookie, nén/cache nhẹ |
| Hiệu năng & Chi phí | Rất nhanh, tốn ít tài nguyên CPU/RAM hơn | Chậm hơn một chút và tốn tài nguyên hơn do phải giải mã và phân tích gói tin ứng dụng |

## Các tầng đặt bộ nhớ đệm (Cache Placement)
Để đưa dữ liệu lại gần người dùng và giảm thiểu truy cập đĩa/mạng chậm chạp, hệ thống lớn thường kết hợp nhiều lớp cache:
- **Client Cache (Trình duyệt / Ứng dụng Mobile):** Lưu file tĩnh (CSS, JS, ảnh) trên trình duyệt hoặc lưu danh sách bài viết trong bộ nhớ điện thoại để mở lại tức thì mà không tốn băng thông mạng.
- **CDN Cache (Edge Server):** Đặt bản sao nội dung tĩnh tại các trạm máy chủ biên gần vị trí địa lý của người dùng trên toàn cầu.
- **Reverse Proxy Cache:** Đặt Nginx hoặc Varnish ngay trước App Server để lưu kết quả trả về của các trang phổ biến (như cache trang chủ báo điện tử trong 60 giây cho hàng nghìn lượt xem đồng thời).
- **Application & Distributed Cache:** Lưu kết quả tính toán nặng trong biến bộ nhớ của ứng dụng hoặc dùng cụm bộ nhớ đệm phân tán trên RAM (Redis, Memcached) dùng chung cho nhiều App Server.
- **Database Cache:** Tận dụng cơ chế sẵn có bên trong hệ quản trị CSDL như Buffer Pool (giữ trang dữ liệu nóng trong RAM) hoặc Query Cache.

## 5 chiến lược cập nhật và đồng bộ Cache
| Chiến lược | Cơ chế Đọc / Ghi | Ưu điểm | Nhược điểm & Rủi ro |
|---|---|---|---|
| Cache-Aside (Lazy Loading) | Đọc: kiểm tra cache trước, nếu miss thì đọc DB rồi nạp vào cache. Ghi: cập nhật DB rồi xóa (invalidate) hoặc cập nhật mục cache đó | Đơn giản, chỉ nạp dữ liệu thực sự có người hỏi; cache sập hệ thống vẫn chạy qua DB | Lần đọc đầu tiên luôn bị chậm (cache miss); dễ trả dữ liệu cũ (stale data) nếu quên xóa cache khi ghi |
| Write-Through | Mỗi thao tác ghi đều cập nhật đồng thời vào cả Cache lẫn Database trước khi báo thành công | Dữ liệu trong cache luôn tươi mới, nhất quán chặt với DB gốc | Tốc độ ghi chậm vì phải chờ cả 2 nơi; tốn bộ nhớ cho cả những dữ liệu ghi xong nhưng ít ai đọc lại |
| Write-Back (Write-Behind) | Ghi thẳng vào Cache và báo xong ngay cho user; tiến trình nền sẽ gom lô (batch) các mục đánh dấu "dirty" để ghi xuống DB sau | Tốc độ ghi cực nhanh, chịu tải ghi cao và gộp được nhiều lần sửa liên tiếp trên cùng 1 bản ghi | Nguy cơ mất dữ liệu vĩnh viễn nếu máy chủ cache (RAM) sập trước khi kịp đồng bộ xuống đĩa DB |
| Write-Around | Khi ghi chỉ lưu thẳng xuống DB (bỏ qua cache); dữ liệu chỉ vào cache khi có truy vấn đọc theo kiểu Cache-Aside | Tránh làm tràn bộ nhớ đệm bởi các dữ liệu mới ghi một lần nhưng hiếm khi được đọc | Lần đọc ngay sau khi vừa tạo mới chắc chắn gặp cache miss và phải xuống DB |
| Refresh-Ahead (Prefetching) | Chủ động nạp lại dữ liệu mới vào cache ngay trước khi thời gian sống (TTL) sắp hết hạn | Người dùng luôn gặp cache nóng, không bị khựng ở thời điểm hết hạn TTL | Lãng phí tài nguyên tính toán nếu dự đoán sai và làm mới những dữ liệu không còn ai truy cập |

## Khi nào dùng và cách kết hợp
- **Chọn Load Balancer L4:** Khi cần tốc độ chuyển tiếp gói tin thuần túy cực nhanh hoặc dùng giao thức ngoài HTTP (như server game UDP, kết nối VPN, cơ sở dữ liệu).
- **Chọn Load Balancer L7:** Cho hầu hết ứng dụng Web/API hiện đại cần tách luồng traffic theo đường dẫn URL (tĩnh vs động, dịch vụ ảnh vs dịch vụ thanh toán) và quản lý SSL tập trung.
- **Chọn chiến lược Cache:** Dùng **Cache-Aside** kèm TTL làm mặc định cho dữ liệu đọc nhiều ghi ít (như tỷ giá ngoại tệ đổi 2 lần/ngày, danh sách sản phẩm bán chạy); dùng **Write-Through** cho cấu hình hệ thống cần đọc chính xác ngay sau khi đổi; chỉ dùng **Write-Back** khi tải ghi cực lớn và đã có cơ chế log/cluster chống mất dữ liệu.

## Sai lầm thường gặp
- Đặt nhiều App Server sau Load Balancer dùng thuật toán Round Robin nhưng lại lưu trạng thái đăng nhập (session) trong RAM của từng máy mà không bật Sticky Session (IP Hash/Cookie) hoặc chuyển session sang Redis chung.
- Lưu dữ liệu vào Cache mà không thiết lập thời gian hết hạn (TTL) và không có cơ chế xóa cache khi cập nhật Database, khiến người dùng nhìn thấy thông tin sai lệch vĩnh viễn.
- Dùng chiến lược Write-Back trên một node Redis đơn lẻ cho dữ liệu giao dịch quan trọng, dẫn đến mất sạch dữ liệu chưa kịp ghi xuống đĩa khi server khởi động lại.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Hướng dẫn cách tiếp cận phỏng vấn System Design" (Nguyễn Thế Huy). Không chép nguyên văn.*
