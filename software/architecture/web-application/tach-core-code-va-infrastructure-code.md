---
id: software/architecture/web-application/tach-core-code-va-infrastructure-code
canonical_question: "Làm thế nào để phân biệt và tách rời core code khỏi infrastructure code trong ứng dụng web?"
aliases:
- tách core code và infrastructure code
- core code vs infrastructure code
- tách biệt nghiệp vụ và hạ tầng
- decoupling core and infrastructure
- dependency inversion trong web app
- nhận diện code trộn lẫn hạ tầng
entity_type: book_chapter
domain: software > architecture > web-application
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Kiến trúc ứng dụng web\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Tách biệt Core Code và Infrastructure Code

## TL;DR
**Core code** chứa logic nghiệp vụ thuần túy, chạy hoàn toàn trong bộ nhớ mà không cần hệ thống ngoài hay môi trường đặc thù. **Infrastructure code** đảm nhiệm kết nối với cơ sở dữ liệu, mạng, hệ thống file, đồng hồ hệ thống hoặc framework. Tách bạch hai phần này qua các giao diện trừu tượng (interface) giúp bảo vệ miền nghiệp vụ trước biến động công nghệ và tăng tốc độ kiểm thử tự động.

## Phân biệt Core Code và Infrastructure Code

Một đoạn mã chỉ được coi là core code khi thỏa mãn đồng thời hai quy tắc: không chạm tới hệ thống ngoài và không đòi hỏi môi trường thực thi đặc biệt. Mọi thành phần vi phạm một trong hai điều kiện đều thuộc về infrastructure.

| Tiêu chí | Core Code (Mã lõi) | Infrastructure Code (Mã hạ tầng) |
|---|---|---|
| **Mục đích** | Thể hiện quy tắc, tính toán và quy trình của miền nghiệp vụ (domain) | Giao tiếp với DB, HTTP API, file system, mail server, framework |
| **Điều kiện chạy** | Chạy độc lập trong bộ nhớ và CPU, không gây side effect ra ngoài | Đòi hỏi kết nối mạng, dịch vụ ngoài, hoặc container của framework |
| **Tính di động** | Mang sang CLI, web app, worker hoặc script nhỏ đều chạy nguyên vẹn | Gắn chặt với ngữ cảnh cụ thể (HTTP Request, Session, ORM) |
| **Kiểm thử** | Unit test cô lập, chạy cực nhanh, không cần dựng DB hay mạng | Cần integration test với môi trường thật hoặc dịch vụ giả lập |
| **Ví dụ điển hình** | Tính thuế đơn hàng, kiểm tra tồn kho trên Entity, Value Object `Money` | Truy vấn SQL/ORM, gọi REST API, đọc file cấu hình, Web Controller |

## Dấu hiệu nhận biết code bị trộn lẫn

- **Chi tiết kỹ thuật nằm giữa luồng nghiệp vụ**: Hàm xử lý đơn hàng vừa nhân đơn giá với số lượng, vừa chứa câu lệnh SQL `INSERT`, đọc biến từ `Request` và ghi vào `Session`.
- **Không thể chạy unit test nếu thiếu DB hoặc framework**: Muốn kiểm thử một phép tính nghiệp vụ nhưng phải khởi động toàn bộ framework hoặc kết nối database.
- **Dữ liệu thiếu nhất quán**: Nhiều nơi tự chèn bản ghi vào bảng dữ liệu mà không đi qua lớp kiểm tra bất biến (invariant) trung tâm.
- **Đổi công nghệ kéo theo sửa logic**: Thay đổi cấu trúc bảng, đổi thư viện gửi thư hoặc thêm cổng giao tiếp CLI buộc phải sửa lại hàm tính toán nghiệp vụ.
- **Interface rò rỉ chi tiết hạ tầng**: Dùng interface nhưng phương thức lại mang đặc thù lưu trữ như `insert(table, rowData)` khiến lớp gọi vẫn lệ thuộc vào khái niệm bảng cơ sở dữ liệu.

## Các kỹ thuật tách rời Core và Infrastructure

| Kỹ thuật | Cách thực hiện | Tác dụng chính |
|---|---|---|
| **Dependency Inversion (DIP) & DI** | Core định nghĩa interface theo ngôn ngữ nghiệp vụ (`OrderRepository`, `Mailer`); Infrastructure viết class thực thi và tiêm (inject) qua constructor | Đảo ngược chiều phụ thuộc: hạ tầng phụ thuộc vào lõi, lõi không biết chi tiết bên dưới |
| **Ẩn chi tiết sau Interface hướng miền** | Đặt tên phương thức theo ý định nghiệp vụ (`save(Order)`, `nextIdentity()`) thay vì thao tác kỹ thuật (`query()`, `insertTable()`) | Cho phép hoán đổi SQL, NoSQL hoặc bộ nhớ tạm (in-memory) mà không chạm vào core |
| **Bọc thời gian và hệ thống ngoài** | Tạo interface `Clock` (với hàm `now()`) thay vì gọi trực tiếp đồng hồ hệ thống; bọc thư viện bên thứ ba sau Adapter | Kiểm soát hoàn toàn thời gian và phản hồi ngoại vi khi viết unit test |
| **Dùng Value Object thay kiểu thô** | Đóng gói tiền tệ (`Money`), khoảng thời gian (`DateRange`), địa chỉ email vào đối tượng bất biến tự kiểm tra hợp lệ | Ngăn dữ liệu sai lọt vào core, giảm lệ thuộc vào hàm tiện ích của hệ thống |
| **Cô lập đặc thù Framework ở rìa** | Giữ Controller, ORM Model (Active Record), Facade và Session ở lớp ngoài cùng; ánh xạ sang đối tượng Domain trước khi xử lý | Giảm rủi ro khi nâng cấp phiên bản framework hoặc tái sử dụng logic cho kênh giao tiếp mới |

```text
// Giả mã minh họa tách biệt qua Interface được inject
interface Clock { now(): Instant }
interface OrderRepository { save(order: Order): OrderId }

class PlaceOrderUseCase(repo: OrderRepository, clock: Clock):
    execute(ebookId, qty, unitPrice):
        order = new Order(ebookId, qty, unitPrice, clock.now())
        return repo.save(order)
```

## Khi nào dùng và Cách áp dụng
- **Dự án có vòng đời dài (từ 2 năm trở lên) hoặc nghiệp vụ phức tạp**: Tốc độ thay đổi của công nghệ ngoài (framework, DB, dịch vụ thứ ba) luôn lệch pha với tốc độ tiến hóa của nghiệp vụ; tách rời giúp mỗi bên thay đổi độc lập.
- **Quy tắc tự kiểm tra nhanh**: Trước mỗi class hoặc hàm, hãy hỏi *"Đoạn mã này có chạy được ngay trong bộ nhớ mà không cần mạng, file, DB hay boot framework không?"*. Nếu không, hãy tách phần tương tác ngoài sang Adapter.
- **Không xét theo tên thư mục**: Một class đặt trong `Services` hay `Utils` nhưng bên trong mở kết nối HTTP hoặc đọc biến môi trường trực tiếp thì bản chất vẫn là infrastructure code.

## Sai lầm thường gặp
- **Tưởng có Interface là thành Core Code**: Tạo interface `DatabaseConnection` rồi gọi `db.insert("orders", data)` ngay trong hàm nghiệp vụ. Dù đã qua interface, hàm đó vẫn gắn chặt với khái niệm bảng dữ liệu nên chưa phải là core code.
- **Lạm dụng Helper/Facade toàn cục của framework**: Gọi trực tiếp hàm tĩnh lấy thời gian, ghi log, đọc session hoặc ORM bên trong Entity làm mất khả năng chạy độc lập của đối tượng.
- **Truyền trực tiếp đối tượng Request hoặc ORM Model vào sâu trong lõi**: Làm tầng nghiệp vụ bị buộc chặt vào giao thức HTTP hoặc cấu trúc bảng vật lý.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Kiến trúc ứng dụng web" (Nguyễn Thế Huy). Không chép nguyên văn.*
