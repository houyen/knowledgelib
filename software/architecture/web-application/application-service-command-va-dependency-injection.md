---
id: software/architecture/web-application/application-service-command-va-dependency-injection
canonical_question: "Cách tổ chức Application Service, Command Pattern và Dependency Injection để giữ Controller mỏng là gì?"
aliases:
- application service và command pattern
- giữ controller mỏng thin controller
- command handler trong ứng dụng web
- service locator vs dependency injection
- tách logic use case khỏi controller
- DTO command đầu vào
entity_type: book_chapter
domain: software > architecture > web-application
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Kiến trúc ứng dụng web\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Application Service, Command Pattern và Dependency Injection

## TL;DR
Để tránh tình trạng Controller phình to và gắn chặt logic nghiệp vụ vào giao thức HTTP, mỗi trường hợp sử dụng (use case) cần được tách thành một **Application Service** (hoặc **Command Handler**) nhận đầu vào là một **Command DTO**. Các phụ thuộc của service được truyền từ bên ngoài qua **Dependency Injection** thay vì gọi Service Locator toàn cục, giúp mã nguồn độc lập khỏi framework và dễ dàng tái sử dụng trên Web, API, CLI hay hàng đợi.

## Vai trò của Controller mỏng, Command và Application Service

| Thành phần | Trách nhiệm chính | Những việc KHÔNG được làm |
|---|---|---|
| **Controller (Delivery)** | Đọc tham số từ HTTP Request, đóng gói thành đối tượng Command, gọi Application Service và trả về HTTP Response | Không tính toán nghiệp vụ, không gọi trực tiếp ORM/SQL, không kiểm tra quy tắc miền |
| **Command Object (DTO)** | Gom toàn bộ dữ liệu đầu vào của một use case thành một đối tượng bất biến, thể hiện rõ ý định của người dùng (`PlaceOrderCommand`) | Không chứa logic xử lý nghiệp vụ hay truy cập cơ sở dữ liệu |
| **Application Service / Handler** | Điều phối luồng thực thi use case: gọi Repository lấy Entity, kích hoạt hành vi trên Domain, lưu kết quả, quản lý transaction và phát sự kiện | Không đọc trực tiếp `Request` hay `Session`; không tự ôm logic tính toán chi tiết thuộc về Entity |

```text
// Giả mã luồng phối hợp giữa Controller, Command và Handler
class PlaceOrderCommand(readonly customerId: string, readonly productId: string, readonly qty: int)

class PlaceOrderHandler(orderRepo: OrderRepository, productRepo: ProductRepository):
    handle(cmd: PlaceOrderCommand): OrderId
        product = productRepo.getById(cmd.productId)
        order = Order.create(orderRepo.nextIdentity(), cmd.customerId, product, cmd.qty)
        orderRepo.save(order)
        return order.id()
```

## Quy trình thực thi một Use Case chuẩn

- **Bước 1 — Chuyển đổi giao thức**: Controller trích xuất dữ liệu thô từ form web, JSON body hoặc tham số dòng lệnh để khởi tạo `PlaceOrderCommand`. Có thể kiểm tra định dạng đầu vào cơ bản ngay trước hoặc trong khi tạo Command.
- **Bước 2 — Điều phối nghiệp vụ tại Application Layer**: `PlaceOrderService` (hoặc `PlaceOrderHandler`) nhận Command, dùng các Repository đã được inject để nạp thực thể (`Product`), kiểm tra điều kiện (như tồn kho), yêu cầu Domain Entity thực hiện tính toán và lưu trạng thái mới qua `OrderRepository`.
- **Bước 3 — Phản hồi theo ngữ cảnh**: Service trả về kết quả đơn giản (như `OrderId` hoặc DTO kết quả). Controller nhận giá trị này và quyết định chuyển hướng trang (redirect), render HTML view hoặc trả mã JSON.

## Dependency Injection (DI) so với Service Locator

Khi Application Service cần dùng các thành phần như `OrderRepository`, `ProductRepository` hay dịch vụ gửi thư, cách cung cấp phụ thuộc quyết định khả năng kiểm thử và mức độ độc lập của lớp đó.

| Tiêu chí | Dependency Injection (Khuyên dùng) | Service Locator (Nên tránh trong Core) |
|---|---|---|
| **Cách thức hoạt động** | Khai báo rõ các interface cần dùng tại constructor; nơi khởi tạo (Composition Root / Container) truyền đối tượng cụ thể vào | Bên trong hàm xử lý tự gọi container toàn cục để lấy đối tượng (ví dụ gọi hàm helper lấy service theo tên) |
| **Tính minh bạch** | Nhìn vào chữ ký constructor biết ngay class phụ thuộc vào những thành phần nào | Phụ thuộc bị che giấu sâu bên trong thân hàm, phải đọc hết mã nguồn mới phát hiện được |
| **Độc lập Framework** | Class hoàn toàn thuần túy, không biết tới sự tồn tại của IoC Container | Bị trói chặt vào container toàn cục của framework |
| **Khả năng kiểm thử** | Dễ dàng truyền trực tiếp fake/mock repository qua constructor khi chạy unit test | Phải khởi tạo và cấu hình cả container toàn cục mới chạy được bài kiểm thử |

## Khi nào dùng và Cách áp dụng
- **Tái sử dụng cùng một tính năng cho nhiều kênh giao tiếp**: Khi ứng dụng cần hỗ trợ đặt hàng qua cả Web UI, REST API cho ứng dụng di động, lệnh CLI import hàng loạt hoặc worker xử lý bất đồng bộ, mọi kênh chỉ cần tạo `PlaceOrderCommand` và gọi chung một `PlaceOrderService`.
- **Cấu hình phụ thuộc tại điểm khởi đầu (Composition Root)**: Đặt toàn bộ việc ánh xạ từ Interface sang Implementation cụ thể tại tầng hạ tầng (ví dụ trong Service Provider của framework), giữ cho tầng Application và Domain sạch bóng mã cấu hình.

## Sai lầm thường gặp
- **Truyền thẳng đối tượng HTTP Request vào Application Service**: Khiến service không thể gọi lại từ CLI, cronjob hay unit test nếu không giả lập môi trường HTTP.
- **Biến Application Service thành nơi chứa toàn bộ logic thủ tục**: Viết hết công thức tính tiền, kiểm tra điều kiện nghiệp vụ trong Service còn Entity chỉ chứa getter/setter rỗng (mô hình miền nghèo nàn - Anemic Domain Model).
- **Truyền hàng chục tham số rời rạc vào hàm của Service**: Không gom nhóm thành Command DTO làm chữ ký hàm dài dòng, khó đọc và dễ truyền nhầm thứ tự tham số.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Kiến trúc ứng dụng web" (Nguyễn Thế Huy). Không chép nguyên văn.*
