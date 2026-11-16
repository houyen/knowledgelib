---
id: software/system-design/vi-interview-guide/nhat-quan-kha-dung-cap-replication-quorum
canonical_question: "Làm thế nào để cân bằng giữa tính nhất quán và tính khả dụng bằng định lý CAP, Replication và Quorum?"
aliases:
- định lý CAP theorem
- strong consistency vs eventual consistency
- replication failover quorum
- nhất quán và khả dụng trong system design
- hệ thống CP và AP
- tunable consistency W R N
entity_type: book_chapter
domain: software > system-design > vi-interview-guide
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Hướng dẫn cách tiếp cận phỏng vấn System Design\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Tính Nhất Quán, Khả Dụng, Định Lý CAP, Replication và Quorum

## TL;DR
Trong hệ thống phân tán, tính nhất quán (Consistency - mọi node thấy cùng dữ liệu tại một thời điểm) và tính khả dụng (Availability - mọi yêu cầu hợp lệ đều được phản hồi) luôn giằng co nhau. Khi xảy ra phân vùng mạng (Partition), định lý CAP buộc kiến trúc sư phải chọn ưu tiên giữa CP hoặc AP, đồng thời kết hợp các cơ chế Replication, Failover và Quorum (W + R > N) để điều chỉnh mức độ đánh đổi theo đúng nghiệp vụ.

## So sánh 3 mô hình nhất quán (Consistency Models)
| Mô hình | Đặc điểm kỹ thuật | Ưu điểm & Đánh đổi | Trường hợp điển hình |
|---|---|---|---|
| Strong Consistency (Nhất quán mạnh) | Ngay sau khi thao tác ghi hoàn tất, mọi thao tác đọc tiếp theo trên bất kỳ node nào đều nhận được giá trị mới nhất | Tránh hoàn toàn sai lệch dữ liệu (như bán trùng 1 ghế máy bay cuối cùng), nhưng độ trễ cao và phải khóa/chờ đồng bộ | Giao dịch ngân hàng, rút tiền ATM, đặt vé/giữ chỗ |
| Eventual Consistency (Nhất quán cuối cùng) | Cho phép các node tạm thời trả về dữ liệu cũ sau khi ghi; nếu không có cập nhật mới, cuối cùng mọi bản sao sẽ hội tụ về cùng trạng thái | Phản hồi rất nhanh, chịu tải và sẵn sàng cao; chấp nhận lệch dữ liệu trong vài giây | Đổi ảnh đại diện mạng xã hội, bảng tin (news feed), CDN, DNS, Cassandra/DynamoDB |
| Weak Consistency (Nhất quán yếu) | Không cam kết đọc được dữ liệu mới nhất và không hứa hẹn mốc thời gian cụ thể để các node đồng bộ hoàn toàn | Tốc độ xử lý tối đa, giảm thiểu chi phí đồng bộ; chỉ dùng khi việc lệch dữ liệu lâu không gây hại | Cache dài hạn ít làm mới, bảng xếp hạng điểm số cập nhật định kỳ trong game online |

*Lưu ý:* Giữa hai thái cực mạnh và yếu còn có các biến thể thực tế như **Session Consistency** (nhất quán trong phạm vi phiên làm việc của một người dùng) hoặc **Read-your-writes** (người vừa ghi dữ liệu chắc chắn đọc thấy ngay thay đổi của chính mình).

## Các cơ chế kỹ thuật đảm bảo nhất quán và khả dụng
### 1. Nhân bản dữ liệu (Replication) và Chuyển đổi dự phòng (Failover)
- **Đồng bộ chặt (Strong/Synchronous Replication):** Giao dịch ghi chỉ báo thành công khi đã cập nhật xong trên cả node chính lẫn các bản sao. Đạt nhất quán mạnh nhưng làm tăng độ trễ ghi và giảm khả dụng nếu một replica bị treo.
- **Đồng bộ lỏng (Asynchronous Replication):** Ghi xong vào node chính (primary/master) là phản hồi ngay cho client, dữ liệu lan tỏa dần sang các bản sao (secondary/slave). Tốc độ cao nhưng dẫn đến Eventual Consistency.
- **Failover:** Khi máy chủ chính gặp sự cố, hệ thống tự động chuyển lưu lượng sang máy dự phòng. Để tránh người dùng nhìn thấy dữ liệu thụt lùi sau khi failover, quá trình đồng bộ giữa primary và secondary phải được duy trì sát sao.

### 2. Đa số phiếu (Quorum)
Trong cụm có tổng cộng N bản sao dữ liệu, hệ thống cấu hình ngưỡng ghi thành công tối thiểu W node và ngưỡng đọc tối thiểu R node (Tunable Consistency):
- **Công thức nhất quán mạnh:** Chọn W + R > N (thường lấy W = R = N/2 làm tròn xuống, cộng 1, ví dụ N = 5 thì W = 3, R = 3). Tập node đọc và tập node ghi luôn giao nhau ít nhất 1 node chứa bản ghi mới nhất.
- **Tối ưu tốc độ đọc/ghi:** Giảm W để ghi nhanh hơn hoặc giảm R để đọc nhanh hơn; khi W + R ≤ N, hệ thống chuyển sang trạng thái nhất quán yếu hơn.

## Định lý CAP trong thực tế thiết kế
Định lý CAP khẳng định khi xuất hiện sự cố đứt kết nối giữa các node (**P - Partition tolerance**), hệ thống phân tán không thể giữ đồng thời 100% **C (Consistency)** và 100% **A (Availability)**. Vì lỗi mạng là điều chắc chắn xảy ra trong thực tế, P luôn là điều kiện bắt buộc, đưa bài toán về việc chọn **CP** hoặc **AP**:

| Lựa chọn khi đứt mạng (P) | Hành vi của hệ thống | Hệ quả nghiệp vụ |
|---|---|---|
| Hệ thống CP (Consistency + Partition tolerance) | Tạm ngừng nhận ghi hoặc trả lỗi ở nhánh bị cô lập cho đến khi mạng thông và dữ liệu đồng bộ lại | Giảm uptime tạm thời nhưng bảo vệ tuyệt đối tính đúng đắn (không bán lố số lượng tồn kho, không sai lệch số dư) |
| Hệ thống AP (Availability + Partition tolerance) | Cho phép cả hai nhánh mạng tiếp tục nhận đọc/ghi độc lập dựa trên dữ liệu cục bộ hiện có | Dịch vụ luôn online 24/7, nhưng có thể phát sinh xung đột dữ liệu (bán trùng món hàng cuối) cần xử lý hậu kỳ khi mạng nối lại |

## Cách áp dụng và trình bày khi phỏng vấn
1. **Hỏi rõ yêu cầu nghiệp vụ trước:** Xác nhận với người phỏng vấn tính năng đang xét cần chính xác tức thì (như thanh toán) hay ưu tiên phản hồi mượt mà (như thông báo, lượt thích).
2. **Tách bạch từng phân hệ:** Trong cùng một hệ thống lớn, áp dụng **Strong Consistency / CP** cho module giao dịch tiền tệ và dùng **Eventual Consistency / AP** (kèm async replication hoặc cache có TTL ngắn 5 phút) cho module bảng tin/chat.
3. **Nêu giải pháp đi kèm cơ chế cụ thể:** Khi chọn nhất quán cao, đề xuất điều phối qua một Leader hoặc dùng Quorum (W + R > N); khi ưu tiên khả dụng, đề xuất Master-Slave bất đồng bộ kèm Failover đa trung tâm dữ liệu.

## Sai lầm thường gặp
- Tuyên bố hệ thống đạt đồng thời cả 3 yếu tố C, A, P ở mức 100% hoặc chọn mô hình "CA" cho một hệ thống phân tán qua mạng (bỏ qua thực tế là mạng luôn có thể đứt).
- Áp đặt Strong Consistency cho toàn bộ hệ thống mạng xã hội hoặc trang tin tức, gây nghẽn cổ chai và làm giảm trải nghiệm tải trang không cần thiết.
- Thiết kế cơ chế tự động Failover sang máy chủ phụ nhưng dùng Asynchronous Replication có độ trễ lớn mà không tính đến rủi ro mất dữ liệu vừa ghi hoặc đọc phải dữ liệu cũ sau khi chuyển đổi.

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Hướng dẫn cách tiếp cận phỏng vấn System Design" (Nguyễn Thế Huy). Không chép nguyên văn.*
