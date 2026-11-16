---
id: software/system-design/vi-interview-guide/chiu-loi-phuc-hoi-va-do-tin-cay
canonical_question: "Làm thế nào để thiết kế hệ thống chịu lỗi (Resilience), phân biệt HA với Fault Tolerance và đo lường Uptime, SLA, MTBF, MTTR?"
aliases:
- khả năng chịu lỗi fault tolerance vs high availability
- chiến lược phục hồi sự cố hệ thống phân tán
- uptime SLA MTBF MTTR MTTF
- graceful degradation circuit breaker retry backoff
- loại bỏ single point of failure SPOF
- độ tin cậy hệ thống trong system design
entity_type: book_chapter
domain: software > system-design > vi-interview-guide
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Hướng dẫn cách tiếp cận phỏng vấn System Design\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Khả Năng Chịu Lỗi, Phục Hồi Sự Cố và Đo Lường Độ Tin Cậy

## TL;DR
Trong hệ thống phân tán quy mô lớn, sự cố phần cứng, mạng và con người là điều tất yếu xảy ra. Thiết kế hướng tới độ bền vững (Resilience) không cố ngăn chặn 100% lỗi, mà tập trung xóa bỏ các điểm lỗi đơn (SPOF), kết hợp dự phòng, tự động chuyển đổi (Failover), giảm cấp dịch vụ có kiểm soát (Graceful Degradation) và giám sát sức khỏe để duy trì cam kết SLA với thời gian khôi phục (MTTR) ngắn nhất.

## 5 nhóm sự cố phổ biến và 6 chiến lược tăng độ bền vững (Resilience)
Hệ thống thực tế luôn đối mặt với 5 nguồn gây lỗi: **Lỗi phần cứng** (cháy nguồn, hỏng ổ đĩa, sập node), **Lỗi phần mềm** (rò rỉ bộ nhớ - memory leak, lỗi logic gây hiệu ứng dây chuyền), **Sự cố mạng** (rớt gói tin, độ trễ cao, phân vùng mạng - network partition), **Lỗi con người** (cấu hình sai, xóa nhầm dữ liệu/tắt nhầm server) và **Quá tải đột biến** (CPU 100%, cạn kiệt kết nối).

| Chiến lược Resilience | Cơ chế vận hành cốt lõi | Tác dụng thực tế |
|---|---|---|
| Redundancy & Replication (Dự phòng & Nhân bản) | Triển khai nhiều máy chủ ứng dụng song song và sao chép dữ liệu sang nhiều node/ổ đĩa ở các vùng (AZ) khác nhau | Xóa bỏ điểm lỗi đơn (Single Point of Failure - SPOF); một máy chết vẫn còn máy khác thay thế |
| Failover (Chuyển đổi dự phòng) | Tự động phát hiện node chính (active) gặp sự cố để điều hướng lưu lượng sang node dự phòng (passive/standby) | Giảm thiểu thời gian gián đoạn dịch vụ mà không cần con người can thiệp thủ công |
| Load Balancing (Cân bằng tải) | Phân bổ đều yêu cầu giữa cụm máy chủ và tự động rút máy bị hỏng ra khỏi danh sách nhận việc | Ngăn ngừa một máy bị ép quá tải đến sập; duy trì hệ thống chạy tiếp với phần công suất còn lại |
| Retry kèm Exponential Backoff | Tự động gửi lại yêu cầu khi gặp lỗi mạng thoáng qua với khoảng chờ tăng dần (VD: chờ 2s → 4s → 8s) và giới hạn số lần thử | Vượt qua các lỗi chập chờn tạm thời mà không dồn dập "bắn phá" làm sập luôn dịch vụ đang yếu |
| Graceful Degradation & Circuit Breaker | Ngắt mạch (circuit breaker) tới dịch vụ con đang lỗi để chống lan truyền; tạm tắt tính năng phụ để giữ luồng chính | "Thà chạy hạn chế còn hơn chết hẳn" (VD: tắt bình luận trực tiếp để giữ news feed, hạ video HD xuống SD) |
| Health Check & Monitoring | Định kỳ ping kiểm tra sức khỏe (VD: mỗi 5 giây ping 1 lần, trượt 3 lần thì báo hỏng) và cảnh báo qua Prometheus/PagerDuty | Phát hiện sự cố tức thì để kích hoạt failover tự động hoặc gọi kỹ sư trực xử lý trước khi lan rộng |

*(Các kỹ thuật nâng cao khác có thể nhắc thêm: cách ly khoang lỗi bằng **Bulkhead pattern** hoặc cơ chế tự chữa lành **Self-healing** qua Auto-scaling group).*

## Phân biệt High Availability (HA) và Fault Tolerance (FT)
| Tiêu chí | High Availability (Độ sẵn sàng cao - HA) | Fault Tolerance (Chịu lỗi tuyệt đối - FT) |
|---|---|---|
| Mục tiêu vận hành | Giảm thiểu tối đa thời gian ngừng, nhưng chấp nhận có gián đoạn rất ngắn (vài chục giây đến vài phút) khi chuyển đổi | Không có bất kỳ gián đoạn nào (zero downtime) ngay cả khi một thành phần đang chạy bị hỏng đột ngột |
| Kiến trúc điển hình | Cụm máy chủ kèm bản dự phòng nóng/ấm (Active-Passive failover) | Nhân đôi toàn bộ phần cứng/dữ liệu chạy song song đồng bộ tức thời (Active-Active) |
| Chi phí & Độ phức tạp | Chi phí hợp lý, kiến trúc vừa phải; là lựa chọn của đa số dịch vụ web thương mại | Chi phí cực kỳ đắt đỏ, phức tạp cao; vẫn có thể sập nếu dính lỗi logic phần mềm (bug) giống nhau trên cả 2 nhánh |
| Ví dụ liên hệ | Nhà hàng có nhiều đầu bếp dự phòng (1 người nghỉ thì phục vụ chậm đi chút); ứng dụng web thông thường | Máy bay thương mại 2 động cơ hoặc bệnh viện có máy phát điện tức thời; hệ thống điều khiển không lưu, lõi tài chính |

## Các chỉ số đo lường độ tin cậy: Uptime, SLA, MTBF, MTTR
- **Uptime (Độ sẵn sàng):** Tỷ lệ % thời gian hệ thống hoạt động tốt. Mức **"3 số 9" (99.9%)** tương đương khoảng **8.8 giờ** downtime mỗi năm; mức **"4 số 9" (99.99%)** chỉ cho phép khoảng **53 phút** downtime mỗi năm; mức **"5 số 9" (99.999%)** rút xuống còn khoảng **5 phút** mỗi năm.
- **SLA (Service Level Agreement):** Cam kết hợp đồng giữa nhà cung cấp và khách hàng về ngưỡng uptime tối thiểu (ví dụ sách nêu AWS S3 cam kết 99,99%; con số thực tế cần đối chiếu trang SLA hiện hành) và thời gian phản hồi sự cố; vi phạm SLA sẽ phải bồi thường.
- **MTBF (Mean Time Between Failures) & MTTF:** MTBF đo thời gian hoạt động trung bình giữa hai lần xảy ra sự cố có thể sửa chữa: MTBF = tổng thời gian uptime / số lần sự cố (ví dụ: trong 168 giờ có 3 lần sập mất tổng cộng 3 giờ → uptime 165 giờ → MTBF = 55 giờ). Với linh kiện hỏng là phải vứt bỏ thay mới, người ta dùng **MTTF** (Mean Time To Failure).
- **MTTR (Mean Time To Recovery / Repair):** Thời gian trung bình để khôi phục dịch vụ trở lại bình thường sau sự cố: MTTR = tổng thời gian downtime / số lần sự cố (ví dụ: 4 sự cố trong tháng gây tổng downtime 2 giờ → MTTR = 30 phút). Hệ thống lý tưởng hướng tới **MTBF thật cao** và **MTTR thật thấp**.

## Cách áp dụng và trình bày khi phỏng vấn
1. **Chốt yêu cầu độ tin cậy từ đầu:** Hỏi người phỏng vấn bài toán chấp nhận downtime vài chục giây (chọn HA đa Availability Zone) hay bắt buộc zero-downtime (chọn FT Active-Active đắt đỏ).
2. **Rà soát SPOF trên sơ đồ vừa vẽ:** Chỉ tay vào từng khối (Load Balancer, App Server, Database) và đặt câu hỏi *"Nếu khối này sập thì sao?"* để bổ sung cặp dự phòng và cơ chế Failover tương ứng.
3. **Kết hợp phòng thủ lỗi dây chuyền:** Nêu rõ việc dùng Retry có Exponential Backoff kèm Circuit Breaker ở giao tiếp liên dịch vụ và thiết lập cảnh báo tự động để kéo giảm chỉ số MTTR.

## Sai lầm thường gặp
- Thiết kế kiến trúc Fault Tolerance (Active-Active đa vùng) quá phức tạp và đắt đỏ cho một ứng dụng nội bộ hoặc mạng xã hội thông thường vốn chỉ cần mức High Availability (over-engineering).
- Cài đặt vòng lặp Retry liên tục ngay lập tức (không có khoảng nghỉ Backoff và không có Circuit Breaker) khiến một dịch vụ đang quá tải bị chính các service gọi tới đánh sập hoàn toàn.
- Chỉ nhân bản tầng Application Server mà để quên một cơ sở dữ liệu duy nhất không có Read-Replica hay cơ chế tự động Failover (vẫn còn nguyên Single Point of Failure ở tầng dữ liệu).

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Hướng dẫn cách tiếp cận phỏng vấn System Design" (Nguyễn Thế Huy). Không chép nguyên văn.*
