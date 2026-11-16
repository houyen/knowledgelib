---
id: software/architecture/web-application/kien-truc-phan-lop-va-hexagonal-ports-adapters
canonical_question: "Kiến trúc phân lớp (Layered Architecture) và Hexagonal (Ports & Adapters) tổ chức các tầng, thư mục và chiến lược kiểm thử ra sao?"
aliases:
- kiến trúc phân lớp và hexagonal
- layered architecture vs hexagonal architecture
- ports and adapters trong ứng dụng web
- domain application infrastructure layers
- chiến lược kiểm thử unit test và integration test theo tầng
- cấu trúc thư mục DDD và hexagonal
entity_type: book_chapter
domain: software > architecture > web-application
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Kiến trúc ứng dụng web\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Kiến trúc Phân lớp và Hexagonal (Ports & Adapters)

## TL;DR
**Kiến trúc phân lớp hiện đại** chia ứng dụng thành ba tầng **Domain**, **Application** và **Infrastructure** với quy tắc phụ thuộc một chiều từ ngoài vào trong. **Hexagonal Architecture (Ports & Adapters)** bổ sung cho kiến trúc phân lớp bằng cách tường minh hóa mọi điểm giao tiếp ngoại vi thành các cổng trừu tượng (**Ports**) ở lõi và các bộ chuyển đổi cụ thể (**Adapters**) ở hạ tầng, cho phép hoán đổi linh hoạt công nghệ lưu trữ, kênh giao diện hoặc bộ giả lập kiểm thử.

## Ba tầng cốt lõi và Quy tắc phụ thuộc

Khác với lối phát triển từ dưới lên lấy cơ sở dữ liệu làm trung tâm, kiến trúc hướng miền đặt tầng Domain ở vị trí lõi độc lập và bắt buộc các tầng ngoài phụ thuộc hướng vào trong.

| Tầng (Layer) | Thành phần chứa bên trong | Quy tắc phụ thuộc | Chiến lược kiểm thử |
|---|---|---|---|
| **Domain (Miền nghiệp vụ)** | Entity, Aggregate, Value Object, Domain Service, Domain Event, Repository Interface, Factory | Hoàn toàn độc lập; không biết tới Application hay Infrastructure (nguyên tắc Hollywood: *"Đừng gọi chúng tôi, chúng tôi sẽ gọi bạn"*) | **Unit test** thuần túy trong bộ nhớ, chạy tức thì, không cần boot framework hay DB |
| **Application (Ứng dụng)** | Application Service, Command / Query Object, Command Handler, Event Listener điều phối use case | Phụ thuộc vào Domain; không chứa chi tiết kỹ thuật hạ tầng; quản lý ranh giới transaction | **Unit / Use-case test** bằng cách tiêm các Adapter giả lập (In-Memory Repository, Fake Notification) |
| **Infrastructure (Hạ tầng)** | Web Controller, CLI Command, ORM / SQL Repository, Mailer, Payment Gateway, DI Service Provider | Phụ thuộc vào Application và Domain để cài đặt các interface đã định nghĩa (theo nguyên lý DIP) | **Integration test** kết nối cơ sở dữ liệu thật, dịch vụ ngoài hoặc môi trường thực tế |

## Mô hình Ports & Adapters (Hexagonal Architecture)

Do Alistair Cockburn đề xuất năm 2005, kiến trúc hình lục giác xem lõi ứng dụng (Domain + Application) như một khối trung tâm giao tiếp với thế giới bên ngoài hoàn toàn qua các **Port** (hợp đồng/interface) và **Adapter** (bộ chuyển đổi công nghệ), tương tự như cổng USB có thể cắm nhiều thiết bị khác nhau.

| Loại cổng | Vai trò | Ví dụ Port (Tại Core) | Ví dụ Adapter (Tại Infrastructure) |
|---|---|---|---|
| **Primary / Input Port** (Cổng đầu vào) | Điểm tiếp nhận yêu cầu thực thi use case từ tác nhân bên ngoài | Các Application Service / Handler (`PlaceOrderHandler`) hoặc giao diện cổng vào | `OrderController` (Web HTTP), `ImportOrderCommand` (nhập từ file CSV qua CLI) |
| **Secondary / Output Port** (Cổng đầu ra) | Hợp đồng để lõi gửi dữ liệu hoặc yêu cầu dịch vụ bên ngoài | `OrderRepository`, `OrderNotification`, `PaymentGateway`, `CustomerContext` | `SqlOrderRepository` / `InMemoryOrderRepository`, `EmailOrderNotification` / `LogOrderNotification` |

- **Quan hệ 1–N giữa Port và Adapter**: Mỗi Port thường có ít nhất hai Adapter — một Adapter thật chạy trên môi trường production (như gửi thư qua SMTP, lưu MySQL) và một Adapter giả phục vụ kiểm thử nhanh (như ghi log, lưu mảng trong RAM).
- **Tích hợp giữa các Bounded Context**: Khi phân hệ Đặt hàng cần thông tin từ phân hệ Khách hàng, phân hệ Đặt hàng định nghĩa một Output Port riêng và dùng một HTTP Adapter gọi sang REST API của phân hệ kia, giữ cho miền nội tại không bị nhiễm giao thức mạng.

## Tổ chức thư mục mẫu

```text
src/
├── Domain/Order/          # Entity (Order), ValueObject, Event, OrderRepository (Output Port)
├── Application/Order/     # PlaceOrderCommand, PlaceOrderHandler, Port/OrderNotification
└── Infrastructure/
    ├── Order/UI/          # Http/OrderController, Console/ImportOrderCommand (Input Adapters)
    ├── Order/Persistence/ # SqlOrderRepository, InMemoryOrderRepository (Output Adapters)
    ├── Order/Notification/# EmailOrderNotification, LogOrderNotification (Output Adapters)
    └── Providers/         # Đăng ký Dependency Injection nối Port với Adapter theo môi trường
```

## Khi nào dùng và Cách áp dụng
- **Ứng dụng đa kênh hoặc thường xuyên thay đổi tích hợp**: Khi cần mở thêm kênh CLI, REST API, ứng dụng di động hoặc ghi dữ liệu song song ra nhiều nguồn lưu trữ, chỉ cần viết thêm Adapter mới và khai báo trong DI Provider mà không sửa một dòng nào ở Domain/Application.
- **Tập trung vào những điểm có khả năng thay đổi hoặc khó kiểm thử**: Không cần tạo quá nhiều tầng trừu tượng cho các tác vụ CRUD cực kỳ đơn giản; hãy ưu tiên dựng Port & Adapter tại các ranh giới I/O (DB, mạng, thanh toán, thông báo) và các phân hệ cốt lõi.

## Sai lầm thường gặp
- **Rò rỉ logic giữa các tầng**: Viết quy tắc tính toán nghiệp vụ ngay trên Controller hoặc cho phép tầng nghiệp vụ gọi thẳng xuống cơ sở dữ liệu bỏ qua Repository Interface.
- **Thiết kế ngược từ cơ sở dữ liệu lên (Bottom-up)**: Tạo bảng dữ liệu và ORM Model trước rồi ép toàn bộ tầng nghiệp vụ phụ thuộc vào cấu trúc cột của bảng.
- **Lạm dụng phân lớp máy móc (Lasagna Code)**: Tạo quá nhiều lớp vỏ trung gian chỉ chuyển tiếp lệnh mà không mang lại giá trị tách biệt, khiến việc lần theo luồng xử lý trở nên rối rắm.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Kiến trúc ứng dụng web" (Nguyễn Thế Huy). Không chép nguyên văn.*
