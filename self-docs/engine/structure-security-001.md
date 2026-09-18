---
id: self-docs/engine/structure-security-001
canonical_question: 'Technical guide and specification: Mô Hình Ủy Quyền Lai: Sự Kết
  Hợp Giữa RBAC Phân Cấp Và ABAC Động'
aliases:
- 'Mô Hình Ủy Quyền Lai: Sự Kết Hợp Giữa RBAC Phân Cấp Và ABAC Động'
- Structure Security 001
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# Mô Hình Ủy Quyền Lai: Sự Kết Hợp Giữa RBAC Phân Cấp Và ABAC Động

## 1. Triển Khai RBAC Theo Tiêu Chuẩn Phân Cấp Và Phân Tách Nhiệm Vụ (SoD)

Mô hình phân quyền dựa trên vai trò (RBAC) cung cấp một cấu trúc quản trị rõ ràng, ánh xạ trực tiếp cơ cấu tổ chức của doanh nghiệp vào hệ thống phần mềm⁶. Theo tiêu chuẩn quốc tế ANSI/INCITS 359 (mô hình NIST RBAC), việc thiết lập RBAC cần được nâng cấp qua bốn cấp độ trưởng thành để đảm bảo tính an toàn¹⁰:

| Cấp Độ Trưởng Thành | Tên Mô Hình | Đặc Điểm Kỹ Thuật | Ứng Dụng Trong Hệ Thống Bảng Lương |
| --- | --- | --- | --- |
| Cấp độ 1 | Flat RBAC | Người dùng được gán trực tiếp vào các vai trò độc lập; vai trò mang các quyền hạn cụ thể⁹. | Nhân viên tự phục vụ chỉ có quyền đọc phiếu lương của chính mình⁹. |
| Cấp độ 2 | Hierarchical RBAC | Hỗ trợ kế thừa quyền lực; vai trò quản lý cấp trên tự động kế thừa quyền hạn của vai trò cấp dưới⁹. | Giám đốc nhân sự kế thừa toàn bộ quyền xem báo cáo của Trưởng phòng nhân sự⁶. |
| Cấp độ 3 | Constrained RBAC | Bổ sung các ràng buộc phân tách nhiệm vụ (Separation of Duties - SoD) để ngăn ngừa gian lận⁹. | Kế toán viên tạo bảng lương không được đồng thời là người phê duyệt bảng lương đó¹⁰. |
| Cấp độ 4 | Symmetric RBAC | Yêu cầu rà soát quyền hạn định kỳ và thu hồi các quyền không còn sử dụng⁹. | Hệ thống tự động cảnh báo hoặc thu hồi quyền truy cập bảng lương khi nhân sự chuyển phòng ban¹. |

Để áp dụng thực tế vào ứng dụng bảng lương, cấu trúc vai trò nghiệp vụ (Job Roles), vai trò chức năng (Duty Roles) và vai trò dữ liệu (Data Roles) cần được định nghĩa rõ ràng thông qua bảng cấu hình quyền hạn dưới đây⁶:

| Vai Trò Hệ Thống (Role Name) | Vai Trò Thành Phần (Inherited Duties) | Phạm Vi Dữ Liệu (Data Scope) | Ràng Buộc Bảo Mật & Phân Tách Nhiệm Vụ |
| --- | --- | --- | --- |
| Quản trị viên Nhân sự (HR Admin) | Quản lý hồ sơ nhân viên, cập nhật thông tin vị trí công tác³⁴. | Toàn bộ nhân sự trong doanh nghiệp³⁴. | Không có quyền xem thông tin tài khoản ngân hàng và mức lương chi tiết¹. |
| Chuyên viên Chế độ (Benefits Specialist) | Quản lý các khoản khấu trừ bảo hiểm và phúc lợi¹. | Toàn bộ nhân sự thuộc phạm vi phụ trách¹. | Chỉ được quyền xem và chỉnh sửa thông tin khấu trừ, không được quyền xem lịch sử lương¹. |
| Kế toán viên Tiền lương (Core System Processor) | Nhập liệu tăng ca, thưởng phạt, tính toán bảng lương sơ bộ⁶. | Các phòng ban được phân công cụ thể³⁴. | Được quyền tạo bảng lương nhưng bị chặn hoàn toàn quyền phê duyệt thanh toán¹⁰. |
| Kế toán trưởng (Core System Approver) | Phê duyệt bảng lương cuối cùng, xuất file thanh toán ngân hàng⁶. | Toàn bộ doanh nghiệp hoặc chi nhánh lớn⁶. | Không được tự ý chỉnh sửa số liệu lương; chỉ có quyền phê duyệt hoặc từ chối gửi trả lại¹⁰. |
| Nhân viên (Employee) | Xem phiếu lương, cập nhật tài khoản nhận lương cá nhân⁵. | Chỉ dữ liệu của bản thân người dùng¹⁹. | Không được phép xem thông tin của bất kỳ nhân sự nào khác trong hệ thống³⁴. |

---

## 2. Tích Hợp ABAC Để Tối Ưu Hóa Quyết Định Phân Quyền Động

Mặc dù RBAC cung cấp một bộ khung vững chắc, nhưng việc dựa hoàn toàn vào vai trò tĩnh sẽ dẫn đến tình trạng bùng nổ vai trò khi doanh nghiệp mở rộng quy mô hoặc hoạt động trên nhiều khu vực địa lý⁸. Việc kết hợp mô hình ABAC đóng vai trò là lớp tinh chỉnh (Refinement Layer) phía trên nền tảng RBAC¹⁰. Hệ thống sẽ đánh giá các yêu cầu truy cập dựa trên một hàm logic chứa bốn nhóm thuộc tính chính¹⁰:

- **Thuộc tính chủ thể (Subject)**: Chức danh, phòng ban, chứng chỉ bảo mật, trạng thái onboarding của nhân viên¹⁶.
- **Thuộc tính tài nguyên (Resource)**: Loại dữ liệu (Salary, Tax, Bonus), mức độ nhạy cảm của tài liệu, chi nhánh sở hữu tài nguyên¹⁰.
- **Thuộc tính hành động (Action)**: Đọc (Read), ghi (Write), phê duyệt (Approve), xuất tệp dữ liệu (Export)⁹.
- **Thuộc tính môi trường (Environment)**: Thời gian yêu cầu, dải địa chỉ IP, trạng thái thiết bị (Managed/Unmanaged Device), trạng thái kết nối mạng¹⁰.

Ví dụ, một Kế toán viên tiền lương (vai trò RBAC) bình thường có quyền cập nhật bảng lương của chi nhánh phía Nam, nhưng hệ thống sẽ chặn hành động này nếu yêu cầu được thực hiện ngoài giờ làm việc hành chính từ một địa chỉ IP công cộng không thuộc dải VPN an toàn của doanh nghiệp (ràng buộc ABAC)¹.

---

## 3. Triển Khai Kiểm Soát API Phân Tán Bằng Policy-as-Code Với Open Policy Agent (OPA)

Trong các hệ thống phân tán và microservices hiện đại, việc cài đặt trực tiếp các quy tắc phân quyền vào mã nguồn của từng dịch vụ bảng lương tạo ra sự phân mảnh, gây khó khăn cho công tác bảo trì và kiểm toán¹³. Giải pháp tối ưu là tách biệt hoàn toàn logic phân quyền ra khỏi mã nguồn nghiệp vụ bằng cách sử dụng cơ chế Policy-as-Code thông qua Open Policy Agent (OPA)¹³.

Khi một yêu cầu API (ví dụ: `POST /api/v1/Core System/approve`) được gửi từ trình duyệt của người dùng, quy trình xử lý phân quyền sẽ diễn ra tuần tự qua các bước sau¹³:

1. **Xác thực và chuyển đổi Token**: API Gateway (như Kong hoặc APISIX) tiếp nhận yêu cầu, phối hợp với máy chủ định danh để xác thực tính hợp lệ của mã thông báo (Access Token)¹⁵. Gateway thực hiện kiểm tra thô dựa trên phạm vi (Scope) được định nghĩa trong token³⁰.
2. **Thu thập dữ liệu ngữ cảnh**: Gateway trích xuất các thông tin định danh người dùng từ token (User ID, Roles, Department) và thu thập các tham số môi trường (IP, Timestamp) để đóng gói thành một đối tượng đầu vào dạng JSON¹³.
3. **Truy vấn dịch vụ OPA**: Gateway thực hiện một truy vấn HTTP POST tốc độ cao (thời gian phản hồi khuyến nghị dưới 100ms) tới dịch vụ OPA đang chạy dưới dạng sidecar kế bên ứng dụng¹³.
4. **Đánh giá chính sách bằng ngôn ngữ Rego**: OPA nạp chính sách phân quyền được viết bằng ngôn ngữ khai báo Rego để đưa ra quyết định¹³. Một ví dụ về chính sách Rego kiểm soát quyền phê duyệt bảng lương được định nghĩa như sau¹³:
