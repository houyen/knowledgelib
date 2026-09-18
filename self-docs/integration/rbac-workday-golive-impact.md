---
id: self-docs/integration/rbac-workday-golive-impact
canonical_question: 'Technical guide and specification: Ảnh hưởng của việc golive
  Workday lên phân quyền/bảo mật'
aliases:
- Ảnh hưởng của việc golive Workday lên phân quyền/bảo mật
- RBAC Workday Golive Impact 160726
entity_type: how_to
domain: self-docs > integration
last_verified: 2026-07-16
---

# Ảnh hưởng của việc golive Workday lên phân quyền/bảo mật (RBAC/company-scoping)

**Ngày:** 2026-07-16
**Phạm vi:** Đây là tài liệu canonical duy nhất cho hạng mục "kiểm tra việc đổi nguồn dữ liệu nhân viên sang Workday có gây trở ngại cho công việc phân quyền/bảo mật đã triển khai hay không". Không lặp lại phần triển khai G1/G4/G9/G10 (xem `RBAC-Improvement-Analysis-160726.md`) hay phần scoping gốc (xem `RBAC-Hybrid-Scoping-Implementation-140726.md`).

## 1. Bối cảnh và câu hỏi đặt ra

Dữ liệu hiện có trong DB là hỗn hợp: một phần lấy từ hệ thống cũ, một phần là dữ liệu thử nhập từ Workday trong giai đoạn chuẩn bị. Khi Workday chính thức golive, ba loại mã định danh dùng trong dữ liệu nhân viên — **mã nhân viên** (`employee_code`), **mã phòng ban/công trường**, và **mã công ty** (`company_code`) — sẽ được đồng bộ liên tục từ Workday qua API, và các mã này hoàn toàn có thể khác giá trị đang có trong DB hôm nay (Workday cấp mã nhân viên mới, đổi tên/cấu trúc phòng ban, v.v.).

Công việc của đội bảo mật/phân quyền không đụng vào cấu trúc dữ liệu (schema, luồng đồng bộ HRIS) — nhưng toàn bộ logic RBAC/company-scoping đã triển khai từ 140726 đến nay đều **neo vào các trường dữ liệu cụ thể** của nhân viên/công ty/phòng ban. Câu hỏi cần trả lời: những điểm neo đó có phụ thuộc vào giá trị có khả năng đổi khi golive Workday hay không, và nếu có thì hậu quả thực tế là gì.

Phương pháp: đọc trực tiếp code middleware scoping (`internal/middleware/scope.go`), các migration liên quan (`v40`, `v41`, `v6`, `v22`/`v23`), logic upsert nhân viên (`internal/repository/employee_repo.go`), và query lọc theo phòng ban (`internal/repository/hris_attendance_daily_query_repo.go`) — không suy đoán, mọi kết luận dưới đây đều trích dẫn `file:dòng` cụ thể.

## 2. Company-scope — an toàn với việc đổi TÊN công ty, nhưng có rủi ro thật ở suy luận `company_code`

`ResolveCompanyScope` (`internal/middleware/scope.go:33-58`) và RLS trên bảng `employees` (`atlas/migrations/20260715000000_employees_row_level_security.sql:26-31`) đều so khớp `employee_roles.scope_company_code` với `employees.company_code` — một **mã ngắn ổn định** (`Enterprise`/`UNI`/`CVT`), hoàn toàn tách biệt khỏi `companies.name` (tên pháp nhân đầy đủ, có thể đổi theo Workday mà không ảnh hưởng gì tới scoping).

Rủi ro thật nằm ở chỗ khác: `company_code` của một nhân viên hiện tại **không phải một trường Workday cấp trực tiếp**, mà được DB tự suy luận từ tiền tố `employee_code` tại thời điểm migration:

```sql
-- v40_employees_company_code_unique.sql:6-11
UPDATE public.employees
SET company_code = CASE
    WHEN employee_code LIKE '1%' OR employee_code LIKE 'MB%' THEN 'UNI'
    ELSE 'Enterprise'
END
WHERE company_code = '' OR company_code IS NULL OR company_code = 'CTC';
```

Và khoá upsert nhân viên hiện tại là `(employee_code, company_code)` (`internal/repository/employee_repo.go:788`, xem thêm mục 3). Khi Workday cấp **mã nhân viên mới**, nếu luồng đồng bộ không tự set đúng `company_code` tương ứng cho dòng employee hiện hữu, upsert theo khoá `(employee_code, company_code)` sẽ **tạo ra một dòng employee hoàn toàn mới** thay vì cập nhật dòng cũ.

## 3. Rủi ro trung tâm: khoá upsert nhân viên không dùng `hris_id` sẵn có

Đây là phát hiện quan trọng nhất của tài liệu này. Bảng `employees` **đã có sẵn cột `hris_id` (uuid)** từ migration `v41_hris_employee_levels_job_rotation_schema.sql:34` — một định danh ổn định, độc lập với `employee_code`/`company_code`, đúng loại field cần dùng làm khoá định danh xuyên suốt các lần đồng bộ lại. Cột này **được ghi vào mỗi lần insert** (`employee_repo.go:720`), nhưng **khoá `ON CONFLICT` của upsert lại KHÔNG dùng `hris_id`** — vẫn là `(employee_code, company_code)` (`employee_repo.go:788`).

So sánh với các bảng tham chiếu HRIS khác trong cùng codebase — chúng đều dùng đúng `hris_id` làm khoá upsert:

- `job_rotation_types`: `ON CONFLICT (hris_id) DO UPDATE` (`migrations/v41_hris_employee_levels_job_rotation_schema.sql`, mục comment dòng 8-9).
- `org_structures`: liên kết ngược từ `employees.department_hris_id` sang `org_structures.hris_id` qua `LinkOrgStructures` (`employee_repo.go:545-554`, "matching department_hris_id (uppercase, from SP1) against org_structures.hris_id (lowercase, from SP15)").

`employees` là bảng **duy nhất trong nhóm này** vẫn dùng mã nghiệp vụ (`employee_code`, `company_code`) — thứ có thể thay đổi khi đổi nguồn dữ liệu — làm khoá đồng nhất, thay vì `hris_id` sẵn có nhưng bị bỏ không dùng.

**Hậu quả cụ thể khi golive:** nếu Workday cấp mã nhân viên mới cho một người đã có `employee_roles` (phân quyền) gán theo `employee_id` cũ, và luồng import không tự khớp đúng `company_code`, thì:
1. Upsert theo khoá cũ tạo ra một dòng `employees` mới với `employee_id` mới.
2. Toàn bộ `employee_roles` trỏ theo `employee_id` cũ trở thành "mồ côi" — không gắn với dòng employee mới.
3. Nhân viên đó mất toàn bộ phân quyền đã được cấp trước đó cho tới khi có người chạy lại JML (Joiner-Mover-Leaver, xem `RBAC-JML-Checklist-Van-Hanh-150726.md`) gán quyền thủ công.

Đây không phải một lỗ hổng bảo mật (không có ai được cấp *thừa* quyền) — mà là một rủi ro **gián đoạn vận hành**: người dùng bị khoá ngoài phạm vi quyền của họ một cách âm thầm, đúng lúc golive là thời điểm nhạy cảm nhất để phát hiện và xử lý kịp.

### Quyết định mục 3 — khoá nhân viên (xác nhận với người dùng 2026-07-16)

**Chuyển hẳn sang `hris_id` làm khoá định danh chính cho upsert nhân viên**, thay cho `(employee_code, company_code)`. Điều kiện tiên quyết mà tài liệu bản đầu nêu ra ("Workday có thực sự cấp một ID nội bộ ổn định tách biệt khỏi mã nhân viên hiển thị hay không") **đã được người dùng xác nhận trực tiếp cùng ngày**: dữ liệu Workday trả về cho nhân viên gồm cả **id do Workday cấp** (ổn định) và **employee_code mới** (mã nghiệp vụ, có thể đổi) — đúng hình dạng cần thiết để dùng `hris_id` làm khoá.

Điều kiện còn lại trước khi triển khai:
- `hris_id` phải được backfill đầy đủ (NOT NULL, có unique constraint) cho toàn bộ dòng `employees` hiện có trước khi chuyển khoá — hiện cột này là nullable, một số dòng cũ (chưa từng qua sync Workday) có thể chưa có giá trị.
- Sau khi đổi khoá, `(employee_code, company_code)` vẫn giữ unique constraint hiện có để tránh trùng lặp hiển thị, nhưng không còn là điểm neo nhận diện "đây có phải cùng một nhân viên hay không" giữa các lần đồng bộ.

**Việc CHƯA làm:** thay đổi này chưa được code trong phiên này — tài liệu này chỉ ghi nhận phân tích + quyết định hướng xử lý. Triển khai thật cần một phiên riêng, có test evidence (đặc biệt: test mô phỏng một nhân viên đổi `employee_code` giữa 2 lần sync, xác nhận `employee_roles` KHÔNG bị mồ côi) trước khi coi là xong.

## 3b. Phát hiện thêm cùng ngày: company-scope có cùng loại rủi ro, nhưng ở diện RỘNG hơn — cả một công ty, không chỉ một nhân viên

Sau khi người dùng xác nhận Workday cấp id+code+name cho cả nhân viên, phòng ban, VÀ công ty (không chỉ nhân viên), đối chiếu lại cho thấy **company-scope và department-scope không đối xứng như nhau** — một bên đã đúng chuẩn từ đầu, một bên có cùng lỗ hổng như mục 3 nhưng nặng hơn.

**Department-scope đã đúng chuẩn sẵn:** `employee_roles.scope_department_id` là **FK thật** (uuid) trỏ tới `org_structures.id` — không phải chuỗi tên/mã snapshot. Và `org_structures` **đã upsert đúng theo `hris_id`** (`internal/repository/org_structure_repo.go:126`: `ON CONFLICT (hris_id) DO UPDATE`). Vì vậy nếu Workday đổi mã/tên của một phòng ban đã tồn tại, `org_structures` được UPDATE đúng dòng cũ (cùng `id`), FK trong `employee_roles.scope_department_id` không hề bị ảnh hưởng — quyền vẫn đúng xuyên suốt. Đây chính là lý do mục 4 kết luận department-scope "an toàn hơn nhận định ban đầu".

**Company-scope KHÔNG theo mẫu đó:**
- `employee_roles.scope_company_code` lưu **chuỗi code snapshot** (gán trực tiếp khi HR cấp quyền, `internal/handler/role_handler.go:172`), **không phải FK** tới bảng `companies`.
- Bảng `companies` **không có cột `hris_id`** (`internal/db/schema.sql:366-379`: chỉ có `id`, `code`, `name`, không có trường nào neo về Workday).
- `SyncFromHRIS` (`internal/repository/company_repo.go:27-53`) — cơ chế hiện tại tạo công ty mới từ `employees.company_code` — upsert bằng `INSERT INTO companies (code, name) VALUES ($1, $2) ON CONFLICT (code) DO NOTHING`: khớp theo `code` (không phải id), và **DO NOTHING** (không cả cập nhật tên nếu code đã tồn tại).

**Hậu quả cụ thể:** nếu Workday cấp lại `code` mới cho một công ty đã tồn tại (cùng một pháp nhân thật, chỉ đổi mã hiển thị), `SyncFromHRIS` sẽ **tạo ra một dòng `companies` hoàn toàn mới** dưới code mới, không liên kết gì với dòng cũ. Mọi `employee_roles.scope_company_code` đã cấp theo code cũ sẽ không còn khớp `employees.company_code` mới của nhân viên thuộc công ty đó — toàn bộ nhân viên được cấp quyền theo phạm vi công ty đó (`RequireCompanyScopeMatch`, `ResolveReadCompanyScope`, RLS) sẽ mất quyền cùng lúc, không phải từng người lẻ như rủi ro ở mục 3 mà là **cả một công ty**, cho tới khi rà soát lại thủ công.

### Quyết định mục 3b — company-scope (xác nhận với người dùng 2026-07-16)

**Đưa company-scope về đúng kiến trúc FK mà department-scope đang dùng đúng**, thay vì tiếp tục dùng chuỗi code làm điểm neo:
1. Thêm cột `hris_id` vào bảng `companies` (giống `org_structures.hris_id` đã có).
2. Đổi upsert của `SyncFromHRIS`/luồng tạo công ty sang khớp theo `hris_id`, dùng `DO UPDATE` (không phải `DO NOTHING`) để tên/code đổi vẫn cập nhật đúng dòng cũ.
3. Đổi `employee_roles.scope_company_code` (string) → `scope_company_id` (uuid, FK tới `companies.id`), kèm migration dữ liệu chuyển các dòng `employee_roles` hiện có từ code sang id tương ứng.
4. Sửa `internal/middleware/scope.go` (`ResolveCompanyScope`, `RequireCompanyScopeMatch`, `ResolveReadCompanyScope`, RLS trên `employees`) để so khớp theo id thay vì code.

**Việc CHƯA làm:** đây là thay đổi schema + code RBAC thật (khác mục 4 — bổ sung `org_structure_id` cho `hris_attendance_daily`, cái đó thuộc phạm vi đội dữ liệu/connector). Quyết định hướng xử lý đã chốt, nhưng **chưa triển khai trong phiên này** — cần một phiên riêng có migration + test evidence (test mô phỏng công ty đổi code giữa 2 lần sync, xác nhận toàn bộ `employee_roles` của công ty đó KHÔNG mất quyền) trước khi coi là xong.

## 4. Department-scope theo tên — an toàn hơn nhận định ban đầu nhờ JOIN sống, nhưng lộ một khoảng trống ở dữ liệu chấm công đã nhập

Phân tích ban đầu (trước khi đọc kỹ code) nghi ngờ `ResolveDepartmentScope` (`scope.go:273-304`) là một rủi ro thật vì nó trả về **tên** phòng ban (`org_structures.name`) thay vì id — đúng như giới hạn đã được ghi chú sẵn trong code (`scope.go:264-266`: "dùng tên vì các endpoint hiện có (`orgName`, `dept`) lọc theo tên, không theo id").

Nhưng đọc kỹ hơn cho thấy cơ chế này **an toàn hơn nhận định ban đầu**: `ResolveDepartmentScope` không lưu cache tên phòng ban ở đâu cả — nó JOIN `employee_roles.scope_department_id` (khoá ngoại ổn định) sang `org_structures.name` **sống, ngay tại thời điểm mỗi request**. Nghĩa là nếu Workday sync **UPDATE cùng một dòng `org_structures`** (giữ nguyên `id`, chỉ đổi `name`), thì lần request kế tiếp của site_admin sẽ tự động thấy tên MỚI — không cần sửa code, không có rủi ro "tên cũ bị kẹt lại" ở tầng resolve scope.

**Khoảng trống thật nằm ở một bảng khác:** `hris_attendance_daily` — bảng lưu dữ liệu chấm công đã nhập — chỉ có cột `org_structure_name varchar(500)` (`internal/db/schema.sql:1315`), **hoàn toàn không có `org_structure_id`**. Đây là dữ liệu **denormalized tại thời điểm nhập** (snapshot tên phòng ban lúc đó), khác với bảng `attendance_computed` (mới hơn, `migrations/v29_attendance_computed.sql:12`) — bảng này ĐÃ có sẵn `org_structure_id uuid NOT NULL`, cho thấy hướng thiết kế đúng đã tồn tại ở phần code mới hơn nhưng chưa áp dụng ngược lại cho `hris_attendance_daily`.

Truy vấn lọc theo phòng ban cho site_admin hiện dùng chuỗi: `org_structure_name ILIKE '%'||orgName||'%'` (`internal/repository/hris_attendance_daily_query_repo.go:43-45`). Nếu Workday đổi tên phòng ban tại thời điểm golive, dữ liệu chấm công đã nhập TRƯỚC đó (mang tên cũ) và dữ liệu nhập SAU đó (mang tên mới) sẽ **không gộp được** khi site_admin lọc theo tên hiện tại — site_admin sẽ chỉ thấy một phần dữ liệu (theo tên đang hiệu lực), phần dữ liệu cũ dưới tên cũ bị "ẩn" khỏi kết quả cho tới khi có xử lý thủ công.

### Quyết định mục 4 — attendance department id (xác nhận với người dùng 2026-07-16)

**Đề xuất thêm cột `org_structure_id` vào `hris_attendance_daily`**, theo đúng mẫu hình đã có ở `attendance_computed`, rồi sửa filter từ so khớp tên (`ILIKE`) sang so khớp id. Đây là một **thay đổi cấu trúc dữ liệu** (thêm cột + yêu cầu connector HRIS/Workday phải set đúng giá trị khi nhập) — theo đúng ranh giới phạm vi mà người dùng đã xác định ("phần việc của chúng ta không liên quan tới cấu trúc dữ liệu"), nên **không tự triển khai ở đây**. Ghi nhận thành một đề xuất cần phối hợp với đội phụ trách connector HRIS/cấu trúc dữ liệu, để họ cân nhắc đưa vào cùng đợt chuẩn bị golive Workday (vì driver là thiếu sót schema có sẵn, không phải một tính năng RBAC mới).

**Việc CHƯA làm:** không có thay đổi code nào cho mục này trong phiên này. Đây là input để đội dữ liệu quyết định có làm hay không, và nếu làm thì làm cùng lúc nào trong lộ trình golive Workday.

## 5. Điểm neo còn lại — email làm định danh người dùng, ổn định và không phụ thuộc Workday

`ResolveCompanyScope`/`ResolveDepartmentScope` xác định "ai đang gọi request" bằng `LOWER(e.email)` (`scope.go:45`, `scope.go:289`), không phải `employee_code`. Đây là điểm neo ổn định nhất trong toàn bộ hệ thống scoping — email nhân viên không thuộc phạm vi dữ liệu Workday quản lý theo cùng cách mã nhân viên/mã phòng ban bị đổi, nên không có rủi ro tương tự mục 3/4 ở đây.

Một hạn chế phụ đã được ghi nhận sẵn trong code (không phải phát hiện mới của tài liệu này): `EmpCodeCompanyResolver` (`scope.go:385-397`) tra `company_code` bằng `WHERE employee_code = $1 LIMIT 1` — nếu cùng một `employee_code` tồn tại ở nhiều `company_code` (được phép theo unique constraint hiện tại), hàm lấy dòng đầu tiên tuỳ tiện. Nếu chuyển sang khoá `hris_id` theo quyết định mục 3, endpoint dùng `empCode` để tra cứu (nhận trực tiếp từ client, không phải từ JWT) vẫn cần giữ nguyên cơ chế tra theo `employee_code` như hiện tại (vì đó là giá trị client gửi lên) — hạn chế này độc lập với việc đổi khoá upsert, không tự động được giải quyết bởi quyết định mục 3.

## 6. Tổng kết

Người dùng đã xác nhận (2026-07-16): dữ liệu Workday trả về cho nhân viên gồm cả **id ổn định do Workday cấp** và **employee_code mới**; cho công ty và phòng ban đều gồm **id, code, name**. Xác nhận này khớp đúng điều kiện tiên quyết mà mục 3 nêu ra, và làm lộ thêm bất đối xứng ở mục 3b.

| Điểm neo | Field hiện tại | Ổn định qua golive Workday? | Ghi chú |
|---|---|---|---|
| Company-scope (gán quyền) | `employee_roles.scope_company_code` (string snapshot) → nên đổi `scope_company_id` (FK) | **Không, rủi ro chính #2** | Xem mục 3b — `companies` không có `hris_id`, upsert theo `code` + `DO NOTHING`. Quyết định: đổi sang FK giống department, chưa triển khai. |
| **Khoá định danh nhân viên (upsert)** | `(employee_code, company_code)` hiện tại → nên đổi `hris_id` | **Không, rủi ro chính #1** | Xem mục 3 — đã quyết định hướng xử lý (tiền đề đã được xác nhận), chưa triển khai. |
| Department-scope (resolve quyền) | `scope_department_id` (FK thật) → JOIN sống ra `org_structures.name`, `org_structures` tự upsert theo `hris_id` | Có | Đã đúng chuẩn kiến trúc từ đầu — mẫu hình để company-scope (mục 3b) đi theo. |
| Department-scope (lọc dữ liệu chấm công đã nhập) | `hris_attendance_daily.org_structure_name` (không có id) | **Không, khoảng trống thật** | Xem mục 4 — đề xuất thêm cột, thuộc phạm vi đội dữ liệu, chưa triển khai. |
| Định danh người gọi request | `employees.email` | Có | Ổn định nhất trong toàn hệ thống. |

**Kết luận chung:** việc đổi nguồn dữ liệu nhân viên/công ty/phòng ban sang Workday **không làm gãy phần đã đúng chuẩn của RBAC** (department-scope, định danh người gọi bằng email) — nhưng có **hai rủi ro vận hành thật cùng một họ nguyên nhân** (thiếu FK/khoá ổn định, dùng chuỗi mã nghiệp vụ làm điểm neo thay vì id): khoá upsert nhân viên (mục 3) và cấu trúc company-scope (mục 3b), cả hai đã có quyết định hướng xử lý (chuyển sang `hris_id`/FK, đúng mẫu hình department-scope đã làm đúng) nhưng chưa triển khai; cộng thêm **một khoảng trống schema thật** ở bảng chấm công (mục 4) cần đội dữ liệu cân nhắc, ngoài phạm vi RBAC. Chưa có thay đổi code nào được thực hiện trong phiên này.

## 7. Đặc tả cột cụ thể để làm việc với đội data/adapter

Mục này ghi rõ **từng cột cần thêm**, cùng loại dữ liệu và nguồn Workday tương ứng — dùng làm nội dung trao đổi/giao việc trực tiếp với đội phụ trách connector/HRIS (những cột này nằm ngoài phạm vi RBAC thuần, chỉ có `employee_roles.scope_company_id` ở mục 7.4 là thuộc phạm vi RBAC). **Quyền quyết định quy cách dữ liệu cho các cột này thuộc về người phụ trách RBAC/bảo mật** — phần "Loại dữ liệu" dưới đây là quyết định đã chốt để giao cho đội data/adapter triển khai theo, không phải điểm còn mở để bàn lại; chỉ những mục ghi "cần đội data/adapter xác nhận" là các SỰ THẬT kỹ thuật phía Workday cần họ tra cứu và trả lời (ví dụ tên field thật trong response API), không phải quyết định thiết kế.

Một quan sát làm căn cứ cho quyết định: quy ước kiểu dữ liệu đã có sẵn trong toàn bộ schema hiện tại không đồng nhất — hầu hết các cột `hris_id` hiện có (bảng tham chiếu địa lý, danh mục) dùng kiểu `VARCHAR(100) UNIQUE`, kèm chú thích "UUID dạng FC41F7C5-... từ HRIS" (`migrations/v3_ref_tables.sql:157`, nghĩa là giá trị bên trong luôn có hình dạng UUID nhưng được lưu dưới dạng chuỗi văn bản). Chỉ 3 bảng dùng thẳng kiểu `uuid` gốc của Postgres: `employees.hris_id`, `org_structures.hris_id`, `employee_levels.hris_id` — và đây đúng là 2 trong 3 bảng liên quan trực tiếp tới RBAC (`employees`, `org_structures`).

### Quyết định (người phụ trách RBAC/bảo mật, 2026-07-16)

**Toàn bộ cột mới ở mục 7.1–7.2 dùng kiểu `uuid` gốc**, nhất quán với `employees.hris_id`/`org_structures.hris_id` đã có — không dùng `VARCHAR(100)` như các bảng danh mục/tham chiếu khác. Lý do: đây là các cột phục vụ trực tiếp RBAC/company-scoping (không phải bảng danh mục tra cứu đơn thuần), nên ưu tiên nhất quán với 2 bảng RBAC đã có sẵn thay vì với đa số bảng tham chiếu khác. Nếu trong quá trình triển khai, đội data/adapter phát hiện Workday trả về ID không đúng định dạng UUID chuẩn TASK-REF cho một loại thực thể cụ thể (company hoặc org structure), đó là một PHÁT HIỆN KỸ THUẬT cần báo lại để xem xét ngoại lệ — không tự đổi sang `VARCHAR` khi triển khai.

### 7.1 `companies.hris_id` — cột MỚI, cần thêm

- **Loại dữ liệu:** `uuid` (đã quyết định, xem trên).
- **Dữ liệu cần lưu:** ID nội bộ ổn định mà Workday cấp cho một **pháp nhân/công ty** (trong thuật ngữ Workday thường gọi là Company/Organization Reference ID hoặc WID của đối tượng Company) — KHÔNG phải `code` hiển thị (`Enterprise`/`UNI`/`CVT`...) và KHÔNG phải `name` (tên pháp nhân). Đây là giá trị KHÔNG đổi qua các lần đồng bộ dù `code`/`name` của công ty đó có được Workday cấp lại.
- **Ràng buộc:** nên có `UNIQUE`; nullable trong giai đoạn đầu (một số công ty có thể chưa từng qua Workday), nhưng cần `NOT NULL` sau khi đã backfill đầy đủ nếu muốn dùng làm khoá upsert chính thức (xem mục 3b).
- **Việc cần đội data/adapter xác nhận (sự thật kỹ thuật, không phải quyết định):** trường nào trong response API Workday là ID ổn định này (tên field cụ thể phía Workday), và ID này có thực sự bất biến qua các lần công ty đổi mã/tên hay không.

### 7.2 `hris_attendance_daily.org_structure_id` — cột MỚI, cần thêm

- **Loại dữ liệu:** `uuid` (đã quyết định, xem trên — khớp đúng kiểu của `org_structures.id`/`org_structures.hris_id` đã có, và khớp `attendance_computed.org_structure_id` đã tồn tại làm tiền lệ, `migrations/v29_attendance_computed.sql:12`).
- **Dữ liệu cần lưu:** ID Workday của phòng ban/công trường (Workday gọi là Supervisory Organization hoặc Cost Center tuỳ mô hình tổ chức đang dùng) — **giống hệt loại giá trị đang được map vào `org_structures.hris_id`** hiện nay (`employee_repo.go:545-554`, `LinkOrgStructures`). Nói cách khác: connector khi ghi một dòng `hris_attendance_daily` cần ghi kèm CÙNG giá trị id mà nó đã/sẽ dùng để upsert vào `org_structures.hris_id` cho phòng ban đó — không phải một id mới, chỉ là lưu thêm lần nữa ở bảng chấm công thay vì chỉ lưu `org_structure_name`.
- **Ràng buộc:** khuyến nghị `NOT NULL` cho dữ liệu MỚI nhập sau khi có cột này (dữ liệu chấm công cũ đã nhập trước đó sẽ NULL, cần một bước backfill riêng bằng cách join theo `org_structure_name` hiện tại — chấp nhận sai số cho các dòng đã đổi tên trước khi có cột này, không thể khắc phục hồi tố 100%).
- **Việc cần đội data/adapter xác nhận:** connector ghi `hris_attendance_daily` hiện có sẵn quyền truy cập vào id phòng ban lúc nhập hay không (có thể cần join thêm với response Workday tại bước ETL, chứ không chỉ nhận sẵn tên như hiện tại).

### 7.3 `employees.hris_id` — cột ĐÃ CÓ SẴN, cần đội data/adapter xác nhận cách populate nhất quán

- **Loại dữ liệu hiện tại:** `uuid`, nullable (`migrations/v41_hris_employee_levels_job_rotation_schema.sql:34`).
- **Dữ liệu cần lưu:** Worker ID ổn định do Workday cấp cho một nhân viên (theo xác nhận của người dùng ngày 2026-07-16: Workday trả về id này TÁCH BIỆT với `employee_code`). Đây chính là giá trị cần dùng làm khoá upsert chính (xem quyết định mục 3), thay cho `(employee_code, company_code)`.
- **Việc cần đội data/adapter xác nhận:** (a) id này có được ghi cho MỌI dòng nhân viên đồng bộ từ Workday hay không (không có trường hợp rỗng), và (b) id này có thực sự không đổi qua các lần đồng bộ lại kể cả khi `employee_code` của người đó bị Workday cấp lại — đây là điều kiện bắt buộc để quyết định mục 3 an toàn khi triển khai.

### 7.4 `employee_roles.scope_company_id` — cột MỚI thuộc phạm vi RBAC, KHÔNG cần đội data/adapter tạo dữ liệu

- **Loại dữ liệu:** `uuid`, FK tới `companies.id` (không phải `companies.hris_id` — trỏ tới khoá chính nội bộ của bảng `companies`, giống hệt cách `employee_roles.scope_department_id` đang trỏ tới `org_structures.id`).
- **Ghi chú:** cột này do đội RBAC tự quản lý khi HR cấp quyền (qua `role_handler.go`), không nhận dữ liệu trực tiếp từ Workday — liệt kê ở đây chỉ để đội data/adapter hiểu đầy đủ bức tranh: sau khi có `companies.hris_id` (mục 7.1) và migrate xong `scope_company_id`, việc Workday đổi `code`/`name` của một công ty sẽ không còn ảnh hưởng gì tới cột này, vì nó không neo theo `code`.
