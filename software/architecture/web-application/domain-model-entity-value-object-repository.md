---
id: software/architecture/web-application/domain-model-entity-value-object-repository
canonical_question: "Domain Model gồm những thành phần nào và Repository kết nối tầng nghiệp vụ với cơ sở dữ liệu ra sao?"
aliases:
- domain model entity value object repository
- phân biệt entity và value object
- repository pattern trong DDD
- in-memory repository cho unit test
- bảo vệ invariant trong entity
- aggregate và repository interface
entity_type: book_chapter
domain: software > architecture > web-application
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Kiến trúc ứng dụng web\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Domain Model: Entity, Value Object và Repository Pattern

## TL;DR
**Domain Model** đóng gói dữ liệu và quy tắc nghiệp vụ vào các đối tượng sống trong bộ nhớ như **Entity**, **Value Object** và **Aggregate**, thay thế cho lối viết thủ tục rải rác (Transaction Script). Để lưu trữ và khôi phục các đối tượng này mà không làm bẩn tầng lõi, **Repository Pattern** định nghĩa giao diện (interface) tại tầng Domain và đẩy toàn bộ chi tiết truy vấn SQL, ORM hoặc lưu trữ in-memory sang tầng Infrastructure.

## Các thành phần cốt lõi của Domain Model

Thay vì truyền các mảng dữ liệu vô danh qua nhiều hàm, Domain Model biến các khái niệm nghiệp vụ thành những đối tượng có trạng thái hợp lệ và hành vi rõ ràng.

| Thành phần | Đặc điểm nhận diện | Vai trò trong thiết kế | Ví dụ |
|---|---|---|---|
| **Entity** | Có định danh duy nhất (ID) xuyên suốt vòng đời; trạng thái có thể biến đổi theo quy tắc nghiệp vụ | Đại diện thực thể nghiệp vụ; tự kiểm tra điều kiện bất biến (invariant) ngay từ constructor và các phương thức hành vi | `Order`, `User`, `Product` |
| **Value Object** | Không có ID riêng; so sánh bằng giá trị các thuộc tính; bất biến (immutable) sau khi khởi tạo | Bao bọc các giá trị đặc thù kèm logic tự kiểm tra định dạng và phép tính chuẩn xác, thay thế kiểu nguyên thủy thô | `EmailAddress`, `Money`, `Price`, `DateRange` |
| **Aggregate** | Cụm các Entity và Value Object gắn kết thành một đơn vị nhất quán, có một Entity gốc (Aggregate Root) | Đảm bảo tính toàn vẹn dữ liệu trong toàn cụm; mọi thao tác lưu trữ hay tham chiếu từ ngoài đều đi qua thực thể gốc | `Order` cùng danh sách `OrderLine` |
| **Domain Service** | Lớp xử lý không trạng thái (stateless), chứa quy tắc liên quan đến nhiều Entity | Giải quyết nghiệp vụ thuộc miền nhưng không thuộc riêng về một đối tượng đơn lẻ nào | Dịch vụ tính cước vận chuyển hoặc quy đổi chiết khấu phức tạp |

```text
// Giả mã Entity tự bảo vệ bất biến (invariant) ngay khi khởi tạo
class Order:
    constructor(ebookId: int, email: EmailAddress, qty: int, unitPrice: Money):
        assert ebookId > 0 and qty > 0 and unitPrice >= 0
        this.ebookId = ebookId
        this.email = email
        this.qty = qty
        this.totalAmount = unitPrice.multiply(qty)
```

## Repository Pattern: Cầu nối giữa Domain và Dữ liệu

Repository đóng vai trò như một bộ sưu tập đối tượng trong bộ nhớ, giúp tầng nghiệp vụ thêm, tìm kiếm hoặc xóa thực thể gốc (Aggregate/Entity) mà không cần biết cơ chế lưu trữ vật lý.

| Khía cạnh | Giao diện tại Domain (Contract) | Cài đặt tại Infrastructure (Implementation) |
|---|---|---|
| **Vị trí** | Nằm trong tầng Domain (thuộc core code) | Nằm trong tầng Infrastructure |
| **Trách nhiệm** | Khai báo các hành động theo ngôn ngữ nghiệp vụ (`save(Order)`, `getById(id)`, `nextIdentity()`) | Chuyển đổi qua lại giữa Domain Entity và cấu trúc lưu trữ (bảng SQL, ORM Model, tài liệu NoSQL) |
| **Phụ thuộc** | Chỉ biết tới các Entity, Value Object và ngoại lệ của Domain | Phụ thuộc vào thư viện kết nối DB, Query Builder, Active Record (như Eloquent) hoặc HTTP API |

### Các phương án triển khai Repository thực tế
- **Query Builder / SQL thuần (Data Mapper thủ công)**: Trích dữ liệu từ Entity thành mảng cột để `INSERT`/`UPDATE`, và đọc bản ghi thô từ DB rồi truyền vào constructor tái tạo lại Entity. Tách biệt hoàn toàn khỏi ORM.
- **Bọc Active Record / ORM ẩn bên trong**: Giữ Entity thuần túy ở Domain, còn bên trong class Repository hạ tầng dùng một ORM Model nội bộ để ánh xạ bảng và lưu trữ. Không cho phép ORM Model rò rỉ ra ngoài Repository.
- **In-Memory Repository phục vụ kiểm thử**: Cài đặt interface Repository bằng một cấu trúc mảng hoặc danh sách ngay trong bộ nhớ RAM. Khi chạy unit test cho luồng nghiệp vụ, tiêm `InMemoryOrderRepository` vào giúp kiểm tra trạng thái đơn hàng đã lưu cực nhanh mà không cần dựng cơ sở dữ liệu thật.

## Khi nào dùng và Cách áp dụng
- **Mẹo thiết kế từ trong ra ngoài (Wishful Thinking)**: Khi viết logic nghiệp vụ, hãy giả định đã có sẵn phương thức mình cần (như `orderRepo.save(order)`), định nghĩa interface ngay tại Domain rồi mới viết phần kết nối DB ở hạ tầng sau.
- **Đảm bảo đối tượng hợp lệ ngay từ cửa vào**: Yêu cầu đầy đủ các thuộc tính bắt buộc trong constructor hoặc hàm khởi tạo tĩnh của Entity; tự tính các trường dẫn xuất (như tổng tiền = số lượng × đơn giá) bên trong đối tượng thay vì nhận con số tính sẵn từ bên ngoài.

## Sai lầm thường gặp
- **Cho Domain Entity kế thừa trực tiếp từ ORM Model (Active Record)**: Khiến thực thể nghiệp vụ bị trói chặt vào cơ sở dữ liệu và framework, phá hỏng ranh giới core/infrastructure.
- **Tạo đối tượng rỗng rồi gán từng thuộc tính qua setter**: Dễ sinh ra trạng thái "nửa vời" thiếu thông tin bắt buộc hoặc quên tính toán lại các giá trị phụ thuộc.
- **Để lộ chi tiết lưu trữ lên chữ ký của Repository Interface**: Trả về đối tượng kết quả của ORM hoặc nhận tham số tên bảng, câu truy vấn SQL ngay trên interface của tầng Domain.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Kiến trúc ứng dụng web" (Nguyễn Thế Huy). Không chép nguyên văn.*
