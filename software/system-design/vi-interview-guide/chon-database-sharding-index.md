---
id: software/system-design/vi-interview-guide/chon-database-sharding-index
canonical_question: "Cách chọn cơ sở dữ liệu SQL/NoSQL, thiết kế Sharding và tối ưu Index cho hệ thống lớn như thế nào?"
aliases:
- chọn SQL hay NoSQL
- sharding vs partitioning
- database indexing B-Tree composite index
- OLTP vs OLAP polyglot persistence
- phân mảnh cơ sở dữ liệu
- thiết kế database trong system design
entity_type: book_chapter
domain: software > system-design > vi-interview-guide
last_verified: 2026-11-16
source_type: summary
source: "Tóm tắt bằng lời riêng từ ebook \"Hướng dẫn cách tiếp cận phỏng vấn System Design\" (Nguyễn Thế Huy). Không chép nguyên văn."
---

# Lựa Chọn Cơ Sở Dữ Liệu, Sharding và Tối Ưu Chỉ Mục (Index)

## TL;DR
Thiết kế tầng lưu trữ cho hệ thống lớn đòi hỏi chọn đúng loại data store theo cấu trúc dữ liệu và đặc tính truy vấn (SQL, NoSQL hay kết hợp đa cơ sở dữ liệu - polyglot persistence), thay vì dùng một công nghệ cho mọi bài toán. Khi dữ liệu vượt ngưỡng hàng triệu bản ghi và một máy chủ trở thành nút thắt cổ chai, kỹ sư cần kết hợp đánh chỉ mục (Index) hợp lý để tăng tốc đọc và phân mảnh ngang (Sharding) theo khóa phân tán đều.

## So sánh SQL và NoSQL cùng các tiêu chí lựa chọn lưu trữ
| Tiêu chí | CSDL Quan hệ (SQL / RDBMS) | CSDL Phi quan hệ (NoSQL) |
|---|---|---|
| Cấu trúc & Schema | Bảng (dòng/cột) cố định, định nghĩa schema chặt chẽ từ đầu | Linh hoạt: Document (JSON), Key-Value, Wide-column, Graph |
| Toàn vẹn & Truy vấn | Tuân thủ ACID, hỗ trợ JOIN nhiều bảng và truy vấn phức tạp | Thường ưu tiên BASE / Eventual Consistency, hạn chế JOIN |
| Khả năng mở rộng | Thường mở rộng dọc (scale-up); sharding ngang thủ công phức tạp | Thiết kế sẵn để mở rộng ngang (scale-out) trên nhiều cụm máy |
| Ví dụ & Ứng dụng | MySQL, PostgreSQL, Oracle (ngân hàng, thương mại điện tử, kế toán) | MongoDB, Cassandra, Redis, DynamoDB, Neo4j (mạng xã hội, log, giỏ hàng) |

### 5 yếu tố cân nhắc khi chọn giải pháp lưu trữ cho hệ thống lớn
- **Đặc tính Workload (OLTP vs OLAP vs HTAP):** Giao dịch trực tuyến đọc/ghi nhỏ liên tục cần ACID (OLTP → RDBMS, Key-Value) khác với truy vấn phân tích tổng hợp theo lô lớn (OLAP → Columnar storage, Data Warehouse).
- **Bản chất mô hình dữ liệu:** Dữ liệu quan hệ chặt dùng SQL; truy xuất theo khóa đơn giản dùng Key-Value (Redis/DynamoDB); cấu trúc lồng nhau linh hoạt dùng Document DB (MongoDB); mạng lưới kết nối bạn bè dùng Graph DB (Neo4j); file ảnh/video dung lượng lớn bắt buộc tách ra Object Storage (AWS S3, GCS) và chỉ lưu metadata trong DB.
- **Quy mô và độ trễ nhất quán:** Dữ liệu hàng tỷ bản ghi cần khả năng tự phân vùng tốt (như Cassandra); dữ liệu nhạy cảm tài chính cần CP/Strong Consistency thay vì AP.
- **Chi phí và năng lực đội ngũ:** Cân nhắc giữa mã nguồn mở miễn phí (PostgreSQL) với bản quyền thương mại (Oracle) và ưu tiên công nghệ mà đội ngũ đã nắm vững vận hành.
- **Polyglot Persistence:** Trong kiến trúc microservices, mỗi dịch vụ có thể chọn loại data store tối ưu riêng (ví dụ: PostgreSQL cho sổ cái giao dịch tiền tệ kết hợp MongoDB cho nhật ký hoạt động và gợi ý khuyến mãi).

## 4 chiến lược phân mảnh dữ liệu (Sharding / Partitioning)
| Chiến lược | Cơ chế phân chia | Ưu điểm chính | Nhược điểm & Rủi ro |
|---|---|---|---|
| Range-based (Theo phạm vi) | Chia theo khoảng giá trị của khóa (VD: ID 1–1M vào shard 1, hoặc tên A–I, J–S, T–Z) | Dễ cài đặt, rất hiệu quả khi truy vấn theo dải liên tục (range query) | Phân bố lệch gây điểm nóng (hot spot) nếu một khoảng có quá nhiều dữ liệu |
| Hash-based (Theo hàm băm) | Dùng hàm băm trên khóa phân mảnh (VD: `hash(userID) mod N`) để gán shard | Dữ liệu rải đều giữa các node, giảm thiểu nguy cơ nghẽn cục bộ | Khó truy vấn theo khoảng; thêm/bớt node làm xáo trộn vị trí nếu không dùng Consistent Hashing |
| Directory / Key-based (Bảng tra cứu) | Dùng bảng ánh xạ riêng để chỉ định nhóm dữ liệu (VD: khách Doanh nghiệp → A, Cá nhân → B) | Cực kỳ linh hoạt, dễ gom nhóm theo bất kỳ quy tắc nghiệp vụ nào | Bảng tra cứu trở thành điểm nghẽn/SPOF và phức tạp khi phải cập nhật lại quy tắc chia |
| Geo-based (Theo địa lý) | Đặt dữ liệu theo khu vực người dùng (VD: cụm máy chủ US, EU, APAC riêng biệt) | Giảm độ trễ mạng, đáp ứng luật định cư dữ liệu (như GDPR tại châu Âu) | Tải không đều giữa các châu lục; phức tạp khi cần đồng bộ xuyên vùng (cross-region) |

*Mẹo kết hợp:* Có thể phối hợp đa tầng, chẳng hạn chia theo địa lý (Geo-sharding) ở tầng ngoài cho 10 triệu user toàn cầu, sau đó trong cụm US quá đông lại tiếp tục chia nhỏ bằng Hash-based theo `userID`.

## Tối ưu hóa truy vấn bằng Chỉ mục (Index)
Index (phổ biến nhất là cấu trúc cây cân bằng **B-Tree** hỗ trợ cả `=`, `>`, `<`, `BETWEEN`, `ORDER BY`; hoặc **Hash Index** chỉ hỗ trợ so sánh bằng `=`) giúp định vị bản ghi nhanh mà không phải quét toàn bộ bảng (full table scan), nhưng làm tốn thêm dung lượng lưu trữ và làm chậm thao tác ghi (`INSERT`/`UPDATE`/`DELETE`):
- **Đánh đúng chỗ:** Chỉ đánh index cho bảng từ mức trung bình–lớn (ví dụ trên ~100.000 dòng) trên các cột hay xuất hiện ở `WHERE`, `JOIN`, `ORDER BY`, `GROUP BY`.
- **Tránh cột độ phân biệt thấp (Low Cardinality):** Không đánh index cho cột giới tính, trạng thái boolean hoặc cột chứa quá nhiều giá trị `NULL`. Không đánh index B-Tree trên trường văn bản dài (như `description`) — hãy chuyển sang công cụ tìm kiếm toàn văn như Elasticsearch.
- **Thứ tự cột trong Composite Index:** Index kết hợp `(country, name)` hỗ trợ tốt truy vấn lọc theo `country` hoặc `(country, name)`, nhưng vô tác dụng nếu câu lệnh chỉ tìm theo `name`. Luôn đặt cột lọc phổ biến nhất lên đầu.
- **Tránh trùng lặp và dọn dẹp định kỳ:** Khóa chính (Primary Key) và cột `UNIQUE` đã được tạo index tự động; cần xóa bỏ các index cũ không còn khớp với logic ứng dụng.

## Cách áp dụng và trình bày khi phỏng vấn
1. **Đi từ yêu cầu dữ liệu:** Tóm tắt khối lượng đọc/ghi, mức độ quan hệ và yêu cầu ACID trước khi mở lời chọn SQL hay NoSQL.
2. **Phác thảo thực thể và mô hình hóa:** Nêu nhanh các bảng và khóa ngoại (nếu dùng SQL, như `User` – `Post`) hoặc cấu trúc gom nhóm document (nếu dùng NoSQL cho dữ liệu hay đọc kèm nhau).
3. **Trình bày lộ trình mở rộng theo giai đoạn:** Bắt đầu với 1 DB đơn giản cho MVP → thêm Read-Replicas kèm Cache khi tải đọc tăng 10 lần → thực hiện Sharding kèm chọn Shard Key phân bố đều khi vượt ngưỡng dung lượng 1 máy.

## Sai lầm thường gặp
- Chọn NoSQL chỉ vì nghe nói "nó nhanh hơn SQL" trong khi bài toán cốt lõi là quản lý số dư tài chính cần giao dịch ACID nhiều bảng.
- Đánh index tràn lan trên mọi cột của bảng khiến tốc độ ghi dữ liệu sụt giảm nghiêm trọng khi lưu lượng tăng cao.
- Chọn Shard Key theo thời gian tạo hoặc khu vực quá hẹp khiến toàn bộ lưu lượng mới dồn vào một node duy nhất (tạo hot spot làm sập shard đó).

---
*Nguồn: Tóm tắt bằng lời riêng từ ebook "Hướng dẫn cách tiếp cận phỏng vấn System Design" (Nguyễn Thế Huy). Không chép nguyên văn.*
