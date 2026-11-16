---
id: software/architecture/web-application/read-model-va-view-model
canonical_question: "Vì sao không nên dùng lại Entity của Write Model để hiển thị và cần tách riêng Read Model, View Model?"
aliases:
- read model và view model
- tách write model và read model
- vì sao không dùng entity để hiển thị
- read repository trong web architecture
- CQRS read model
- view model DTO cho UI và API
entity_type: book_chapter
domain: software > architecture > web-application
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Kiến trúc ứng dụng web\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Read Model và View Model trong Kiến trúc Web

## TL;DR
Tái sử dụng **Entity** của mô hình ghi (Write Model) cho mục đích đọc và hiển thị khiến đối tượng bị phình to, lộ các phương thức thay đổi trạng thái ra tầng giao diện và làm giảm hiệu năng truy vấn. Giải pháp là tách riêng **Read Model** và **View Model** kèm các **Read Repository** chuyên biệt, chỉ trả về dữ liệu bất biến, gọn nhẹ và định dạng sẵn sàng cho màn hình UI hoặc phản hồi JSON API.

## Vì sao không dùng lại Write Model (Entity) để đọc?

- **Trao thừa quyền thay đổi trạng thái**: Entity được thiết kế cho nghiệp vụ ghi nên mang theo các hàm biến đổi dữ liệu (như đổi giá, ẩn sản phẩm, hủy đơn). Khi tầng hiển thị nhận toàn bộ Entity, code giao diện có nguy cơ gọi nhầm các hàm này và gây lỗi ngoài ý muốn.
- **Đối tượng phình to và ôm đồm hai vai trò**: Vừa phải bảo vệ các quy tắc bất biến khi ghi, vừa phải chiều theo hàng loạt nhu cầu hiển thị, thống kê và báo cáo khiến class ngày càng cồng kềnh, khó sửa đổi vì sợ ảnh hưởng dây chuyền.
- **Lãng phí tài nguyên và rò rỉ thông tin**: Nạp cả một Aggregate lớn chỉ để lấy một vài trường hiển thị gây tốn bộ nhớ; đồng thời dễ vô tình trả luôn các trường nhạy cảm nội bộ ra ngoài API nếu không lọc kỹ.

## So sánh Write Model, Read Model và View Model

| Tiêu chí | Write Model (Domain Entity) | Read Model | View Model |
|---|---|---|---|
| **Mục đích chính** | Thực thi quy tắc nghiệp vụ, kiểm tra bất biến và cập nhật trạng thái | Phục vụ tra cứu, lấy thông tin nhẹ nhàng trong ứng dụng | Đóng gói dữ liệu khớp chính xác với một màn hình HTML hoặc JSON API |
| **Đặc tính dữ liệu** | Có thể thay đổi trạng thái (mutable), chứa hành vi nghiệp vụ | Bất biến (immutable), không chứa hàm thay đổi trạng thái | DTO bất biến, kiểu dữ liệu nguyên thủy (`string`, `number`) dễ tuần tự hóa |
| **Nguồn truy vấn** | Tương tác theo từng thực thể gốc qua `Write Repository` | Truy vấn chọn lọc cột hoặc bảng tổng hợp qua `Read Repository` | Có thể `JOIN` nhiều bảng (đơn hàng, khách hàng, thanh toán) trong một lần đọc |
| **Ví dụ** | `Order`, `Ebook` (có `changePrice()`, `confirm()`) | `EbookReadModel` (chỉ gồm `id`, `title`, `price`) | `OrderListViewModel` (gồm `orderId`, `customerName`, `formattedPrice`) |

## Các mức độ triển khai Read Model và Read Repository

- **Truy vấn giá trị đơn lẻ**: Nếu luồng xử lý chỉ cần một thông tin đơn giản (như tra đơn giá e-book theo ID), không nhất thiết phải tạo class mới mà chỉ cần một interface nhỏ trả thẳng về kiểu nguyên thủy hoặc Value Object.
- **Dùng chung Database nhưng tách Read Repository**: Tạo `EbookReadRepository` hoặc `OrderListViewRepository` chạy câu lệnh `SELECT` hoặc `JOIN` trực tiếp trên các bảng hiện có rồi đóng gói kết quả vào `ReadModel` / `ViewModel`. Cách này đơn giản, không tốn công đồng bộ dữ liệu nhưng vẫn giữ tách biệt ở tầng code.
- **Tách riêng kho dữ liệu đọc (hướng tới CQRS)**: Với các báo cáo hoặc danh sách phức tạp, duy trì bảng tổng hợp, view hoặc công cụ tìm kiếm riêng. Khi Write Model thay đổi trạng thái sẽ phát ra **Domain Event**, và một Event Handler sẽ cập nhật sang kho dữ liệu đọc.

```text
// Giả mã ViewModel và Read Repository cho API danh sách đơn hàng
class OrderListViewModel(
    readonly orderId: string,
    readonly customerName: string,
    readonly formattedTotal: string
)

interface OrderListViewRepository:
    findRecentOrders(limit: int): List<OrderListViewModel>
```

## Khi nào dùng và Cách áp dụng
- **Mọi thao tác chỉ đọc dữ liệu**: Áp dụng nguyên tắc không bao giờ dùng đối tượng có khả năng biến đổi trạng thái (mutable) và chứa logic phức tạp cho tác vụ chỉ đọc.
- **Xây dựng API danh sách hoặc trang giao diện tổng hợp**: Tạo View Model riêng cho từng màn hình hoặc endpoint, định dạng sẵn chuỗi tiền tệ, ngày tháng hoặc cung cấp hàm chuyển đổi mảng/JSON để Controller và View không phải xử lý lại.
- **Viết kiểm thử tích hợp khi dùng chung bảng dữ liệu**: Khi Read Repository đọc trực tiếp từ bảng của Write Model, cần có integration test kiểm tra hai bên hiểu đúng định dạng cột (ví dụ đơn vị tiền lưu theo xu hay số thập phân).

## Sai lầm thường gặp
- **Trả trực tiếp Domain Entity ra JSON API**: Làm cấu trúc phản hồi API bị phụ thuộc chặt vào cấu trúc nội tại của tầng Domain và có nguy cơ lộ trường dữ liệu nhạy cảm.
- **Nhồi nhét các hàm định dạng hiển thị vào trong Entity**: Thêm các phương thức xuất chuỗi HTML, định dạng tiền tệ theo giao diện hoặc nối tên khách hàng ngay trong Domain Entity.
- **Lệch cách diễn giải dữ liệu giữa chiều ghi và chiều đọc**: Đổi quy ước lưu trữ ở Write Repository nhưng quên cập nhật câu truy vấn ở Read Repository khi cả hai cùng đọc/ghi trên một bảng.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Kiến trúc ứng dụng web" (Nguyễn Thế Huy). Không chép nguyên văn.*
