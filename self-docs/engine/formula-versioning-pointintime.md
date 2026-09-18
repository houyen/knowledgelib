---
id: self-docs/engine/formula-versioning-pointintime
canonical_question: 'Technical guide and specification: Versioning công thức theo
  thời điểm — cơ chế, khuyết tật, và quyết định `effective_from = now`'
aliases:
- Versioning công thức theo thời điểm — cơ chế, khuyết tật, và quyết định `effective_from
  = now`
- Formula Versioning PointInTime 050826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-08-05
---

# Versioning công thức theo thời điểm — cơ chế, khuyết tật, và quyết định `effective_from = now()`

**Canonical cho hạng mục "formula versioning point-in-time", bắt đầu 2026-08-05.**
Tài liệu để bàn giao và đọc lại sau này. Mọi khẳng định dưới đây kiểm bằng đọc code thật + truy vấn DB
`payroll_engine` ngày 2026-08-05, không chép lại từ tài liệu khác.

Liên quan: `Report-Template-Config-Analysis-040826.md` mục 0.5 (chỗ phát hiện, gọi là **L11**),
`Core System-backend/HANDOVER-giatbh.md` mục J (tính năng gốc),
`llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md` **Task 1** (nơi thi hành).

---

## 1. Tính năng này để giải bài toán gì

Bàn giao của `giatbh` mục J nói thẳng vấn đề: *"trước đây sửa 1 formula hôm nay sẽ **tính lại luôn cả
các kỳ lương QUÁ KHỨ** theo formula mới (sai) — không có cách nào biết formula nào đang hiệu lực tại
1 thời điểm cũ."*

Ví dụ cụ thể để hình dung: kỳ 06/2026 đã chốt và trả lương xong với công thức phụ cấp
`PHONE_ALLOW = 500000`. Tháng 9 chính sách đổi thành `800000`, C&B sửa công thức. Nếu ai đó mở lại kỳ
06/2026 tính lại (đối chiếu, kiểm toán, sửa một nhân viên), hệ thống cũ sẽ tính bằng `800000` — ra số
khác với số đã trả thật. Đó là sai lệch không thể giải thích với thanh tra thuế/BHXH.

Cách giải: mỗi lần sửa công thức thì **lưu một phiên bản có ngày hiệu lực**, và khi tính lương thì đọc
phiên bản **hiệu lực tại kỳ đó** thay vì phiên bản mới nhất.

---

## 2. Cơ chế thật, đọc từ code

### 2.1 Bảng `salary_component_versions`

Tạo bởi const `migrationSalaryComponentVersionsTable` (`internal/database/database.go:3032`):

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `id` | uuid PK | |
| `component_code` | varchar(50) NOT NULL | **khoá tham chiếu — theo CODE, không theo `salary_components.id`** |
| `formula`, `name`, `rounding` | text/varchar | giá trị của phiên bản này |
| `effective_from` | timestamptz NOT NULL | phiên bản có hiệu lực từ lúc nào |
| `effective_until` | timestamptz NULL | **NULL = đang mở** (phiên bản hiện hành) |
| `created_by`, `reason`, `created_at` | | vết audit |

Index: `salary_component_versions_pkey` (id), `idx_salary_component_versions_lookup`
(`component_code, effective_from DESC`).

**Điểm cực kỳ quan trọng cho việc thi hành: KHÔNG có unique constraint nào trên `component_code`** (và
đúng ra không nên có — nhiều phiên bản cho một mã chính là mục đích của bảng). Hệ quả:
`ON CONFLICT` **không dùng được** để làm seed idempotent — xem bẫy 1 ở mục 5.

Việc khoá theo `component_code` thay vì `id` là chủ ý và đã được `giatbh` sửa qua một vòng đau (bàn giao
mục K: bảng của họ bị xoá sạch 3 lần liên tiếp khi còn khoá theo `id`, vì
`migrationSalaryComponentsV4` chạy `DELETE FROM salary_components` mỗi boot). Nhờ khoá theo code, dữ
liệu version **sống qua reseed**.

### 2.2 Ghi phiên bản — `InsertVersion` (`internal/repository/salary_component_repo.go:155`)

Hai câu trong một transaction:

```sql
-- (1) đóng phiên bản đang mở
UPDATE salary_component_versions SET effective_until = $1
 WHERE component_code = $2 AND effective_until IS NULL;
-- (2) chèn phiên bản mới
INSERT INTO salary_component_versions
  (id, component_code, formula, name, rounding, effective_from, effective_until, created_by, reason, created_at)
VALUES (...);
```

⇒ Bất biến: **mỗi mã có tối đa MỘT phiên bản đang mở** (`effective_until IS NULL`).

Lưu ý dễ nhầm: `SalaryComponentRepo.Update` (`:121`) **không** ghi version — nó chỉ `UPDATE
salary_components`. Việc ghi version do tầng service gọi `InsertVersion` riêng. Đừng tìm logic version
trong `Update`.

### 2.3 Đọc phiên bản — `ListActiveAsOf` là COALESCE **3 tầng**

`internal/repository/salary_component_repo.go`, được `payroll_service.go` gọi ở **5 điểm** (`:214`,
`:575`, `:705`, `:867`, `:1572`) thay cho `ListActive()` cũ:

```sql
COALESCE(ver.formula, earliest.formula, sc.formula) AS formula
...
LEFT JOIN LATERAL (            -- TẦNG 1: phiên bản hiệu lực ĐÚNG tại ngày asOf
  SELECT formula, name, rounding FROM salary_component_versions v
  WHERE v.component_code = sc.code
    AND v.effective_from <= $1
    AND (v.effective_until IS NULL OR v.effective_until > $1)
  ORDER BY v.effective_from DESC LIMIT 1
) ver ON true
LEFT JOIN LATERAL (            -- TẦNG 2: phiên bản SỚM NHẤT đã biết (KHÔNG lọc theo ngày)
  SELECT formula, name, rounding FROM salary_component_versions v2
  WHERE v2.component_code = sc.code
  ORDER BY v2.effective_from ASC LIMIT 1
) earliest ON true
-- TẦNG 3 (ngầm): sc.formula — giá trị HIỆN TẠI trong salary_components
```

Ý nghĩa từng tầng, nói bằng lời:
- **Tầng 1** — biết chính xác: "tại ngày đó công thức là gì".
- **Tầng 2** — không biết chính xác nhưng có mốc sớm nhất: dùng cho kỳ **trước** khi ta bắt đầu ghi lịch
  sử. Đây là tầng quan trọng nhất để hiểu quyết định ở mục 4.
- **Tầng 3** — không biết gì cả: rơi về công thức hiện tại. **Đây là tầng "mất tính năng"**.

---

## 3. Khuyết tật đang tồn tại (L11): tính năng VÔ HIỆU vì bảng rỗng

Đo trên DB thật 2026-08-05:

```
select to_regclass('salary_component_versions');  -->  salary_component_versions   (bảng CÓ tồn tại)
select count(*) from salary_component_versions;    -->  0                            (nhưng RỖNG)
```

Bảng rỗng ⇒ tầng 1 và tầng 2 **luôn** NULL ⇒ **luôn rơi về tầng 3** ⇒ `ListActiveAsOf(bất kỳ ngày nào)`
trả về công thức **hôm nay** cho **mọi kỳ**. Tức là đúng cái bug mục J được xây để diệt **vẫn còn
nguyên**, chỉ là bây giờ có thêm một lớp cơ sở hạ tầng trông như đã giải quyết.

### 3.1 Vì sao rỗng — cùng gốc nguyên nhân với L4

`database.go` chỉ có `CREATE TABLE IF NOT EXISTS`, **không một câu `INSERT` nào** (đã grep). Backfill
nằm **duy nhất** ở hai file Atlas:

- `atlas/migrations/20260803000000_salary_component_versions.sql:26`
- `atlas/migrations/20260803020000_salary_component_versions_fix_key.sql:28`

Và **backend không bao giờ chạy Atlas** — `cmd/Core System/main.go:67-82` chỉ gọi `RunMigrations()` +
`RunFileMigrations()`. Đây là **cùng một họ lỗi** với L4 (`employee_payroll_templates` cũng chỉ có trong
Atlas): *bootstrap đặt sai chỗ*. Không phải lỗi logic của `giatbh`.

### 3.2 Bằng chứng test

`TestIntegrationCalculateOnePointInTimeFormula` (`internal/service/salary_component_versioning_integration_test.go:134`)
fail **tất định** (2/2 khi chạy cách ly):

```
TASK-REF fail: ListActiveAsOf(kỳ CŨ) sau khi sửa = "1", muốn vẫn "0" (kỳ cũ không được đổi theo)
```

Diễn giải: test sửa công thức từ `0` sang `1` rồi hỏi lại kỳ CŨ, kỳ cũ trả `1` — tức nó **đổi theo**.
Với bảng rỗng thì việc sửa tạo ra **phiên bản đầu tiên và duy nhất** (`effective_from` = lúc sửa), nên
tầng 2 (`earliest`, không lọc ngày) trả về chính phiên bản mới đó → ra `1`. Đây là **cùng một lỗi**, chỉ
nhìn từ phía test.

Lưu ý cho người đọc sau: test này **không** nằm trong danh sách "6 test fail sẵn" ở `HANDOVER-giatbh.md`
mục 3 — danh sách đó thiếu nó. Baseline đo thật là **7 case**.

---

## 4. QUYẾT ĐỊNH: `effective_from = now()`

**Người quyết:** người dùng (`user@company.test`), 2026-08-05. **Trạng thái: đã chốt, không đảo.**

Nội dung: khi seed phiên bản khởi điểm cho các component chưa có phiên bản nào, đặt
`effective_from = now()` (thời điểm migration chạy lần đầu ở môi trường đó), `effective_until = NULL`
(để ngỏ), `formula`/`name`/`rounding` lấy từ `salary_components` **tại thời điểm đó**.

### 4.1 Khái niệm cần nhớ: "chân trời lịch sử" (history horizon)

Mốc `now()` đó trở thành **chân trời lịch sử** của hệ thống: từ mốc đó trở đi, mọi thay đổi công thức
đều được ghi lại và tính lại kỳ nào cũng đúng. **Trước** mốc đó, hệ thống không có dữ liệu lịch sử để
tái tạo — vì lịch sử đó **chưa từng được ghi**, không phải vì ta chọn bỏ.

Đây là điểm quan trọng nhất của quyết định này, và nó là một **giới hạn của dữ liệu, không phải của
thiết kế**. Không có lựa chọn nào khôi phục được công thức của tháng 5/2026 nếu tháng 5/2026 không ai
ghi nó lại.

### 4.2 Diễn biến chi tiết — điều gì xảy ra ở từng ca

Ký hiệu: `T0` = lúc seed (chân trời) = 2026-08-05. `F0` = công thức tại `T0`.
Sau đó ngày `T1` = 2026-09-10, C&B sửa công thức thành `F1` (qua CRUD → `InsertVersion`).

Sau seed, bảng version có: `(F0, from=T0, until=NULL)`.
Sau khi sửa ở `T1`, bảng có: `(F0, from=T0, until=T1)` và `(F1, from=T1, until=NULL)`.

| Ca | `asOf` (kỳ đang tính) | Tầng nào khớp | Kết quả | Đúng chưa |
|---|---|---|---|---|
| A | 2026-07-20 (**trước** chân trời), sau seed, trước khi sửa | tầng 1 trượt → **tầng 2** (earliest = F0) | `F0` | Ổn định. Không tái tạo được lịch sử thật trước `T0`, nhưng **không còn trôi theo mỗi lần sửa** |
| B | 2026-08-31 (sau `T0`, trước `T1`), trước khi sửa | **tầng 1** (F0 mở) | `F0` | ✔ chính xác |
| C | 2026-07-20 (**trước** chân trời), **sau khi đã sửa** thành `F1` | tầng 1 trượt → **tầng 2** (earliest vẫn là F0) | `F0` | ✔ **Đây chính là chỗ bug được diệt.** Trước khi seed, ca này trả `F1` (sai) |
| D | 2026-08-31 (**giữa** `T0` và `T1`), sau khi sửa | **tầng 1** (F0: `from<=asOf`, `until=T1>asOf`) | `F0` | ✔ chính xác — kỳ đã chốt không bị công thức mới làm lệch |
| E | 2026-09-30 (sau `T1`) | **tầng 1** (F1 mở) | `F1` | ✔ chính xác |
| F | (bảng rỗng — hiện trạng khi chưa seed) | tầng 1 + 2 trượt → **tầng 3** | công thức **hôm nay** | ✘ Đây là L11 |

Đọc bảng trên theo một câu: **seed bằng `now()` biến tầng 2 từ "cái bẫy" thành "cái chốt"**. Khi bảng
rỗng, tầng 2 trả về phiên bản của lần sửa gần nhất (ca F → sai). Khi đã có phiên bản khởi điểm, tầng 2
luôn trả về công thức **tại chân trời**, và không bao giờ đổi nữa dù sau này sửa bao nhiêu lần (ca C).

### 4.3 Cái quyết định này KHÔNG giải quyết

Phải ghi rõ để sau này không ai tưởng đã xong:

1. **Không tái tạo lịch sử trước chân trời.** Kỳ 05/2026, 06/2026, 07/2026 tính lại sẽ dùng công thức
   tại `T0`, không phải công thức đã dùng thật lúc đó. Nếu cần đúng cho các kỳ đó thì phải **nhập tay
   lịch sử** vào `salary_component_versions` từ nguồn khác (file lương đã chốt, bản Excel gốc) — đó là
   việc riêng, chưa làm, chưa có kế hoạch.
2. **Không tự bảo đảm số đã trả khớp số tính lại.** Nó chỉ bảo đảm *công thức* ổn định. Dữ liệu đầu vào
   (chấm công, lương cơ bản nhập từ Excel) là trục khác.
3. **Chân trời khác nhau giữa các môi trường.** Dev seed hôm nay, staging seed hôm khác, production seed
   hôm khác nữa → ba mốc khác nhau. Hệ quả vận hành: **một kỳ tính ở dev và ở production có thể ra khác
   nhau** nếu kỳ đó nằm giữa hai chân trời. Khi so số giữa hai môi trường, phải kiểm chân trời trước:
   ```sql
   SELECT min(effective_from) AS chan_troi, count(*) FROM salary_component_versions;
   ```
4. **Không thay `payroll_formula_snapshots`.** Snapshot lúc `Finalize` vẫn là bằng chứng đóng băng của
   kỳ đã chốt; versioning là nguồn để *tính*, snapshot là vết để *đối chiếu*. Hai thứ khác nhau, giữ cả
   hai.

---

## 5. Bốn bẫy khi thi hành — đọc trước khi viết một dòng SQL

**Bẫy 1 — idempotency: PHẢI dùng `WHERE NOT EXISTS`, KHÔNG dùng `ON CONFLICT`.**
Bảng **không có** unique constraint trên `component_code` (mục 2.1), nên `ON CONFLICT` không có gì để
bám. Migration trong `RunMigrations()` **chạy lại mỗi boot** (không transaction, không tracking —
`database.go:288-296`). Nếu seed không có guard, mỗi lần restart sẽ chèn thêm một bộ phiên bản mới với
`now()` mới ⇒ bảng phình vô hạn và chuỗi version thành rác. Guard đúng:
```sql
INSERT INTO salary_component_versions (component_code, formula, name, rounding, effective_from, effective_until, created_by, reason)
SELECT sc.code, sc.formula, sc.name, sc.rounding, now(), NULL, 'seed-050826', 'Phiên bản khởi điểm — chân trời lịch sử (self-docs/Formula-Versioning-PointInTime-050826.md)'
FROM salary_components sc
WHERE NOT EXISTS (SELECT 1 FROM salary_component_versions v WHERE v.component_code = sc.code);
```

**Bẫy 2 — KHÔNG chép nguyên file Atlas.** File
`atlas/migrations/20260803020000_salary_component_versions_fix_key.sql:28` là
`INSERT ... SELECT ... FROM salary_components` **không có guard nào** và dùng
`effective_from = sc.created_at`. Chép nó vào `RunMigrations()` sẽ vướng cả bẫy 1 lẫn bẫy 3. File Atlas
chỉ nên đọc để tham khảo *ý định*, không phải để copy.

**Bẫy 3 — KHÔNG dùng `sc.created_at` làm `effective_from`.** `salary_components` bị V4 xoá + chèn lại
mỗi boot nên `created_at` của **mọi** component là *thời điểm boot gần nhất* (đo thật: cả 110 dòng có
`created_at` nằm trong cùng 4 ms). Nó **nói dối** về tuổi của component. Dùng `now()` tường minh — cùng
giá trị nhưng trung thực về ý nghĩa, và không im lặng đổi mỗi boot.

**Bẫy 4 — vị trí trong slice `migrations`.** Seed chụp lại `sc.formula`, nên phải đặt **SAU tất cả**
migration còn sửa công thức: `migrationSalaryComponentsV4` **và** cả chuỗi self-heal `BG → BN`
(`migrationPITSystemToFormula`, `migrationSelfHealInsuranceCapsAndPIT`, `...HealthIns`, `...OTTax`,
`...CCComponents`, `...ComponentDescriptions`, `...HideOfficialDays`) **và** `BO`
(`MigrationDurableComponentCode`, thêm 050826, hiện ở `database.go:294`). Đặt sai chỗ sẽ đóng băng một
giá trị **giữa chuỗi** — ví dụ chụp `INS_SAL_BH` với trần BHXH cũ 46.8tr thay vì 50.6tr mà `BH` sửa
sau đó. Mốc kế tiếp là **BP**, đặt cuối slice.

Ghi chú phụ, không phải bẫy: `effective_until` của dòng seed **phải là NULL**, để `InsertVersion` (mục
2.2) đóng nó đúng cách khi có lần sửa đầu tiên. Nếu seed đóng luôn thì lần sửa sau sẽ không có phiên bản
mở nào để đóng, và tầng 1 sẽ có lỗ giữa hai mốc.

---

## 6. Nghiệm thu

**Đã thi hành 050826 (Core System-backend@feature_v2, PLAN Task 1 bước 5) — kết quả đo thật:**

1. `select count(*) from salary_component_versions;` = **126** — đúng số component tại thời điểm
   seed (110 gốc + self-heal `CONS_ALLOW`/nhóm `_CC`... theo chuỗi BG→BN). ✔
2. `select min(effective_from), max(effective_from) from salary_component_versions;` = cùng một mốc
   **`2026-08-05 10:06:06.333616+07`** cho cả 126 dòng — đây là **chân trời lịch sử** của DB dev
   `payroll_engine`. Ghi vào tài liệu bàn giao môi trường này. ✔
3. Chạy migration BQ **hai lần liên tiếp** vào `payroll_engine`: lần 1 `INSERT 0 126`, lần 2
   `INSERT 0 0` — `count(*)` không đổi. Bẫy 1 (idempotency) đã đóng, xác nhận bằng lệnh thật. ✔
4. `TestIntegrationCalculateOnePointInTimeFormula` chạy **cách ly**
   (`go test ./internal/service/... -run TestIntegrationCalculateOnePointInTimeFormula`): **PASS**.
   Đây là phép nghiệm thu tự nhiên, xác nhận đúng như dự kiến — không chỉ nhìn full suite. ✔
5. Baseline đo lại tại thời điểm thi hành Task 1 là **8** case (không phải 7 — giữa lúc viết tài liệu
   này và lúc thi hành, một phiên khác đã chạy `go run ./cmd/Core System` để nghiệm thu Task 0, và điều đó
   vô tình tạo bảng `salary_component_versions` lần đầu, khiến 16/24 fail cũ tự biến mất trước khi
   Task 1 bắt đầu — xem `Report-Template-Config-Analysis-040826.md` mục 0.6). Sau Task 1: **7** case —
   đúng giảm 1, khớp dự đoán của mục này dù con số tuyệt đối khác 7→6 như dự kiến ban đầu. ✔
6. Chưa kiểm tay ca C bằng một sửa công thức thật không ảnh hưởng tiền (việc này để dành cho lần đầu
   C&B thực sự sửa một công thức qua CRUD sau chân trời — không mô phỏng thêm trong phiên này vì
   `TestIntegrationCalculateOnePointInTimeFormula` (mục 4) đã kiểm đúng ca C bằng dữ liệu tự tạo/tự
   dọn, cùng bản chất).

---

## 7. Câu hỏi mở / nợ còn lại

| # | Nội dung | Ai quyết |
|---|---|---|
| V1 | Có nhập tay lịch sử công thức **trước chân trời** (từ file lương đã chốt / Excel gốc) không? Nếu cần đối chiếu thanh tra cho kỳ 05–07/2026 thì phải làm | Nghiệp vụ (C&B) |
| V2 | Chân trời khác nhau giữa dev/staging/production — có cần đồng bộ về một mốc chung khi deploy production không, hay chấp nhận mỗi môi trường một mốc | Người dùng + ops |
| V3 | `PIT` **không** dùng cơ chế versioning này (quyết định có chủ ý của `giatbh`, bàn giao mục D: giữ formula Excel-syntax cho HR). Nghĩa là thuế TNCN vẫn có thể tính lại kỳ cũ theo công thức mới | Đã chốt bởi `giatbh`, nhưng nên xác nhận lại vì PIT là cột ảnh hưởng tuân thủ thuế |
| V4 | Test `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` assert số đếm **toàn cục** `payroll_records` → fail ngẫu nhiên khi các package test chạy song song. Sửa bằng cách đếm theo `period_id` của chính test | Kỹ thuật, không cần quyết định nghiệp vụ |

---

## 8. Hệ quả sau khi seed: `sc.formula` không còn ảnh hưởng tính lương — bẫy cài sẵn cho lần sửa công thức tới

Phát hiện khi kiểm chứng độc lập Task 1 (050826). **Hôm nay chưa sai số nào**, nhưng đây là bẫy đã được
nạp đạn, và nó vô hiệu hoá đúng cái cơ chế mà repo này dùng để sửa công thức.

### 8.1 Sự thật mới: tầng 3 đã thành code chết

Sau khi Task 1 seed, **cả 126/126 mã đều có ít nhất một dòng version**. Nhớ lại tầng 2 của
`ListActiveAsOf` (mục 2.3):

```sql
LEFT JOIN LATERAL (            -- TẦNG 2: KHÔNG lọc theo ngày
  SELECT formula, name, rounding FROM salary_component_versions v2
  WHERE v2.component_code = sc.code
  ORDER BY v2.effective_from ASC LIMIT 1
) earliest ON true
```

Tầng 2 **không có điều kiện ngày nào** — nó khớp bất cứ khi nào mã đó có **ít nhất một** version. Vì
mọi mã giờ đều có, **tầng 3 (`sc.formula`) không bao giờ được với tới nữa**.

⇒ Nói bằng một câu để nhớ: **kể từ 05/08/2026, `salary_components.formula` không còn ảnh hưởng kết quả
tính lương.** Mọi phép đọc đi qua một dòng version. `sc.formula` chỉ còn là "giá trị hiện hành để hiển
thị và để làm nguồn cho version kế tiếp".

### 8.2 Vì sao hôm nay vẫn đúng — và vì sao đó là may, không phải thiết kế

Đo thật 050826: **0/126 mã lệch** giữa `sc.formula` và formula trong version. Kể cả hai mã mà đồng nghiệp
`giatbh` vừa sửa trong `7e1928b` (`INS_SAL_BH`, `INS_SAL_UI` — nay là
`IF(AND([CONTRACT_TYPE]=="Chính thức", [HAS_SECOND_CONTRACT]==0), MIN([BASIC_SAL], 50600000), 0)`) cũng
khớp.

Lý do khớp: migration seed được đặt **CUỐI slice** (Bẫy 4, mục 5), nên trong cùng một lượt boot nó chạy
**sau** toàn bộ chuỗi self-heal — chụp đúng giá trị đã được sửa. Đặt đúng chỗ đã cứu một bàn.

Nhưng điều đó chỉ đúng cho **lượt boot đầu tiên**, vì seed có guard `WHERE NOT EXISTS` nên **không bao
giờ chạy lại** cho mã đã có version.

### 8.3 Bẫy: mọi lần sửa công thức bằng migration từ nay sẽ ÂM THẦM KHÔNG CÓ HIỆU LỰC

Quy ước sửa công thức của repo này (ghi trong `CLAUDE.md`, đã dùng ít nhất 8 lần — `BG` PIT, `BH` trần
BHXH, `BI` HEALTH_INS, `BJ` OT_TAX, và `BO`–`BU` của `giatbh`) là: **thêm một migration self-heal ghi
thẳng vào `salary_components`**. Kiểm bằng grep: trong `database.go` chỉ có **đúng 1** câu
`INSERT INTO salary_component_versions` — chính là seed. Tức **không migration self-heal nào tạo version**.

Diễn biến của lần sửa công thức tiếp theo:

| Bước | Điều gì xảy ra |
|---|---|
| 1 | Ai đó phát hiện `PHONE_TAX` sai, viết migration self-heal `UPDATE salary_components SET formula=... WHERE code='PHONE_TAX'` — đúng quy ước repo |
| 2 | Restart backend. `sc.formula` của `PHONE_TAX` **đã đổi đúng**. Kiểm bằng `psql` thấy đúng. |
| 3 | Nhưng version đang mở (seed 05/08) vẫn giữ formula **CŨ**, và không ai đóng nó |
| 4 | `Calculate` gọi `ListActiveAsOf(periodEnd)` → **tầng 1 khớp** dòng version đang mở → trả **formula CŨ** |
| 5 | ⇒ Bản sửa **không có hiệu lực**. `psql` nói đã sửa, lương vẫn tính kiểu cũ. Không lỗi, không cảnh báo. |

Đây đúng loại lỗi tệ nhất mà toàn bộ tập tài liệu này liên tục cảnh báo: **bằng chứng bề mặt nói đã sửa,
hành vi thật thì không**. Và nó còn khó lần ra hơn bình thường, vì người sửa sẽ đi kiểm đúng chỗ
(`salary_components`) và thấy đúng.

Ghi chú phạm vi: đường **CRUD qua UI** không bị bẫy này, vì tầng service gọi `InsertVersion` (mục 2.2) —
đóng version cũ rồi mở version mới. Chỉ đường **migration** bị.

### 8.4 Hai mã đang ở trạng thái không nhất quán (`OT_TAX`, `TRANSPORT_ALLOW`)

Đo thật: **124/126** mã có version đang mở. Hai mã thiếu:

```
TRANSPORT_ALLOW | from=2026-08-05 10:06:06 | until=2026-08-05 10:06:40
OT_TAX          | from=2026-08-05 10:06:06 | until=2026-08-05 10:06:17
```

Tổng số dòng vẫn đúng 126 ⇒ **không có dòng thay thế nào được chèn**. Nguyên nhân: một test gọi
`InsertVersion` (đóng version đang mở + chèn version mới), rồi `t.Cleanup` **xoá dòng mới** nhưng
**không mở lại** dòng seed → để lại mã không có version nào đang mở. Đây là **rác test**, không phải lỗi
logic của Task 1.

Hệ quả: nhẹ, vì tầng 2 luôn đỡ (`earliest` không lọc ngày, trả về chính dòng seed đã đóng) nên formula
trả về vẫn đúng. Nhưng **bất biến "mỗi mã có tối đa MỘT version đang mở" ở mục 2.2 nay bị vi phạm theo
chiều ngược lại** ("có mã KHÔNG có version nào mở"), và **seed không tự chữa được** — đã kiểm bằng thực
nghiệm: chạy seed hai lần, hai mã đó vẫn mồ côi, vì guard là `NOT EXISTS (version nào)` chứ không phải
`NOT EXISTS (version ĐANG MỞ)`.

### 8.5 Đề xuất sửa: một migration "hoà giải lệch" đặt cuối slice — **ĐÃ LÀM (050826, đợt 2)**

Ý tưởng: giữ `sc.formula` làm **nguồn sự thật cho HÔM NAY**, versions làm **lịch sử**, và để migration tự
đồng bộ hai bên mỗi boot. Hai câu, idempotent tự nhiên (hết lệch thì không làm gì) — **đã thi hành đúng
2 câu này, thay thế hoàn toàn seed một-lần cũ** (`MigrationSeedInitialComponentVersions`, giữ nguyên tên
const). Số đo thật + nghiệm thu ở mục **9**.

```sql
-- (1) Đóng version đang mở nếu sc.formula/name/rounding đã lệch (do migration self-heal ghi trực tiếp)
UPDATE salary_component_versions v SET effective_until = now()
  FROM salary_components sc
 WHERE v.component_code = sc.code AND v.effective_until IS NULL
   AND (v.formula <> sc.formula OR v.name <> sc.name OR v.rounding <> sc.rounding);

-- (2) Mở version mới cho mọi mã KHÔNG còn version đang mở
--     (bao gồm: mã vừa bị đóng ở (1), mã mới thêm, và 2 mã mồ côi do rác test ở 8.4)
INSERT INTO salary_component_versions
  (component_code, formula, name, rounding, effective_from, effective_until, created_by, reason)
SELECT sc.code, sc.formula, sc.name, sc.rounding, now(), NULL, 'reconcile-drift',
       'Dong bo version voi salary_components (migration self-heal ghi truc tiep khong tao version)'
FROM salary_components sc
WHERE NOT EXISTS (
  SELECT 1 FROM salary_component_versions v
   WHERE v.component_code = sc.code AND v.effective_until IS NULL);
```

Câu (2) **thay luôn cho seed hiện tại** (guard `NOT EXISTS (version ĐANG MỞ)` chặt hơn guard
`NOT EXISTS (version nào)`), nên có thể gộp — không cần giữ hai migration.

Ưu điểm: (a) khôi phục hiệu lực cho quy ước sửa-công-thức-bằng-migration mà repo đang dùng; (b) mỗi lần
sửa như vậy tự được ghi thành một mốc lịch sử có ngày, đúng tinh thần tính năng; (c) tự chữa 2 mã mồ côi
ở 8.4; (d) idempotent thật (hết lệch là no-op).

Điểm phải cân nhắc trước khi làm: nó khiến **mọi** thay đổi `sc.formula` sinh một mốc version mới với
`effective_from = now()`. Nghĩa là kỳ **trước** thời điểm sửa vẫn giữ formula cũ (đúng mong muốn), nhưng
kỳ **đang mở** cũng sẽ dùng formula mới kể từ mốc đó — cần xác nhận đây đúng là hành vi nghiệp vụ muốn,
không phải "áp cho cả kỳ đang tính".

### 8.6 Việc cần làm ngay ở tầng quy ước (không phải code) — **ĐÃ HẾT HẠN, quy ước sửa formula bằng
migration hoạt động lại bình thường**

Trước bản sửa 8.5, quy ước trong `CLAUDE.md` về sửa công thức bằng self-heal migration **không còn đủ**
— phải tự tay đóng/mở version, nếu không bản sửa sẽ vô hiệu (đúng cách đã dùng ≥8 lần: `BG`/`BH`/`BI`/
`BJ`, và `BO`-`BU` của `giatbh`). **Từ 050826 (đợt 2), migration hoà giải tự chạy sau MỌI migration khác
trong `RunMigrations()` mỗi boot**, nên quy ước cũ **hoạt động lại như trước** — sửa `sc.formula` bằng
một migration self-heal bình thường (không cần gọi `InsertVersion` tay) là đủ; migration hoà giải sẽ tự
phát hiện lệch và mở version mới đúng ngay lần boot kế tiếp. Không cần thêm bước thủ công nào.

## 9. Kết quả thi hành bản hoà giải (050826, đợt 2) — đã xong

Thi hành đúng theo `self-docs/files/prompt-L12-L13-050826.md` trên `Core System-backend@feature_v2`
(sau Task 0/1, commit `b4d5ec6`). Đóng cả **L12** (sửa formula bằng migration từ nay vô hiệu) và **L13**
(2 mã mồ côi không có version mở) bằng một migration duy nhất, **thay hẳn** seed một-lần cũ
(`MigrationSeedInitialComponentVersions`, giữ nguyên tên const — không có test/code nào khác tham chiếu
tên này nên không cần grep sửa chỗ khác).

**Baseline đo lại tại thời điểm này** (không chép "6 case" trong brief — con số đó đo ở thời điểm khác):
`go test ./...` = **859 passed / 7 failed**, khớp đúng danh sách 7 fail đã có từ sau Task 1 (RBAC gate +
report period-id). Không liên quan bản sửa này.

**Trạng thái trước khi sửa** (đo thật 050826): `124/126` version đang mở (2 mã mồ côi `OT_TAX`,
`TRANSPORT_ALLOW`), `0/126` lệch giữa `sc.formula` và version đang mở, tổng `126` dòng, chân trời
`2026-08-05 10:06:06.333616+07`.

**Preview bằng `BEGIN;...ROLLBACK;` trước khi áp thật:** `UPDATE 0` (đúng — chưa có mã nào lệch lúc
này), `INSERT 0 2` (đúng 2 mã mồ côi) → `126/126`, `0` lệch. Khớp tuyệt đối kỳ vọng.

**Áp thật vào `payroll_engine`** (xác nhận qua `AskUserQuestion`) — lần 1: `UPDATE 0` / `INSERT 0 2`,
khớp preview. **Idempotent — chạy lại lần 2:** `UPDATE 0` / `INSERT 0 0`. Kết quả sau cả hai lần:
`126/126`, `0` lệch, tổng **128** dòng (126 cũ + 2 version mới cho 2 mã mồ côi — dòng cũ đã đóng của 2
mã đó **không bị xoá**, giữ nguyên lịch sử).

**2 test mới** (`internal/repository/salary_component_versions_reconcile_integration_test.go`):
- `TestReconcile_MigrationFormulaFixTakesEffect` (L12) — tạo component `ZZ_L12_TEST` (formula `1`),
  chạy migration để có version mở, mô phỏng một self-heal migration (`UPDATE salary_components SET
  formula='2'` trực tiếp, không qua `InsertVersion`), chạy lại migration, khẳng định `ListActiveAsOf`
  trả `2`. **Đã chứng minh test thật sự bắt được bug** (không chỉ tin nó xanh): tạm bỏ câu (1) của
  migration (`cp`/sửa/khôi phục bằng diff, không dùng git vì file đang có sửa khác chưa commit) →
  chạy lại test → **FAIL đúng như kỳ vọng** (`formula = "1", want "2"`) → khôi phục nguyên văn (xác
  nhận bằng `diff` — giống hệt bản gốc) → chạy lại → xanh.
- `TestReconcile_RepairsCodeWithNoOpenVersion` (L13) — mô phỏng đúng cơ chế gây ra rác test (đóng tay
  version đang mở của 1 component dùng-một-lần, không mở lại — đúng cách 1 test khác đã làm với
  `OT_TAX`/`TRANSPORT_ALLOW`), chạy migration, khẳng định lại có đúng 1 version mở.

`go test ./...` sau sửa: **7 fail**, danh sách khớp tuyệt đối baseline (so bằng `diff`) — 0 hồi quy.

**Nghiệm thu ở tầng thật (bắt buộc theo brief):** `go run ./cmd/Core System` — log xác nhận
`Database migrations completed successfully`. Đây là **lần đầu backend thật chạy `RunMigrations` sau
khi rebase `feature_v2` lên `origin/giatbh`** (050826, việc push trước đó) nên chuỗi self-heal mới của
đồng nghiệp (`BR`: 9 mã `BONUS_SAVE_*` + `BUDGET_SAVE` + `PROB_SAL` + `NET_PAY_HOME`; `BQ` của họ:
`PAID_LEAVE_BALANCE_DAYS` + `EARNED_PAID_LEAVE`...) chạy thật lần đầu, nâng tổng component từ 126 lên
**141**. Kết quả sau restart: **141/141** version mở, **0** lệch — đúng bất biến, chỉ khác về số lượng
tuyệt đối do có thêm component mới (không phải lỗi). Restart **lần 2** để chứng minh idempotent qua
đường `RunMigrations` thật (không chỉ `psql -f`): log `0 applied` (file migration, khác cơ chế), số liệu
sau lần 2 **giữ nguyên y hệt** `141/141`, `0` lệch, tổng `153` dòng — không tăng. Xác nhận không có mã
nào bị trùng version cùng trạng thái, không có mã nào thiếu version mở. Dừng backend sau nghiệm thu.

**Nợ còn lại (ghi rõ, không phải bug mới của bản sửa này):**
1. Rác test gây ra L13 (`OT_TAX`/`TRANSPORT_ALLOW` từng mất version mở) **chưa sửa tận gốc** — migration
   hoà giải tự lành mỗi boot nên không còn gây hại, nhưng test gốc (gọi `InsertVersion` rồi `t.Cleanup`
   xoá dòng mới mà không mở lại dòng cũ) vẫn còn trong codebase, sẽ tái tạo lại mã mồ côi mỗi lần chạy.
   Việc riêng, chưa xác định file test cụ thể trong phiên này.
2. `TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` vẫn **fail ngẫu nhiên** (assert số
   đếm toàn cục `payroll_records`, không liên quan bản sửa này) — xem V4 ở mục 7.

---

## 10. Kiểm chứng độc lập bản hoà giải (050826) — ĐẠT, và L12 hoá ra đã xảy ra THẬT

Phiên khác thi hành bản sửa L12+L13 (commit `bf42175`, `Core System-backend@feature_v2`, working tree sạch).
Phiên này kiểm lại bằng lệnh thật.

**Bất biến đã đạt, đo trên `payroll_engine`:**

| Phép đo | Kết quả |
|---|---|
| `salary_components` | **140** |
| dòng version | **153** |
| mã **không** có version đang mở | **0** ✓ |
| mã có **nhiều hơn một** version đang mở | **0** ✓ (bất biến mục 2.2 được giữ) |
| lệch `sc.formula` vs version đang mở | **0** ✓ |
| nhãn chữ cái | đổi `BO→BV`, `BP→BW`, `BQ→BX` (tránh trùng nhãn `giatbh` chiếm) — thuần comment |

Ba mốc `effective_from`, cộng lại đúng 153: **126** dòng ở `10:06:06` (seed gốc), **2** ở `11:06:36`
(chữa L13 cho `OT_TAX`/`TRANSPORT_ALLOW`), **25** ở `11:09:28` (lượt hoà giải sau restart thật).

### 10.1 Phát hiện quan trọng nhất: câu (1) đã đóng 10 cột — L12 không còn là giả thuyết

Bóc 25 dòng ở `11:09:28` thành hai nhóm bằng cách xem mã đó có dòng **đã đóng** trước đó hay không:

**10 mã bị ĐÓNG vì lệch rồi mở lại** — tức trước bản hoà giải, `Calculate` đang dùng **công thức CŨ**
trong khi `salary_components` đã có công thức mới:

```
CONTRACT_TOTAL, EARNED_SAL, HI_EMP, INS_SAL_BH, INS_SAL_UI,
KPCD_CTY, RESP_EARNED, SI_EMP, UI_EMP, UNION_FEE
```

**7 trong 10 mã đó là bảo hiểm/công đoàn** (`HI_EMP`, `SI_EMP`, `UI_EMP`, `INS_SAL_BH`, `INS_SAL_UI`,
`KPCD_CTY`, `UNION_FEE`), 3 còn lại là lương/tổng (`CONTRACT_TOTAL`, `EARNED_SAL`, `RESP_EARNED`).

⇒ Nghĩa là: chuỗi self-heal của `giatbh` **đã** sửa 10 công thức này, và nếu không có bản hoà giải thì
**toàn bộ 10 bản sửa đó bị vô hiệu hoá âm thầm** — bảng lương vẫn tính bằng công thức bảo hiểm cũ, không
lỗi, không cảnh báo. L12 đã chuyển từ "bẫy nạp đạn" sang "đã bóp cò", và bản hoà giải bắt được đúng lúc.

**15 mã MỚI** (chưa từng có version) — câu (2) tự phủ, không cần can thiệp:
`BONUS_SAVE_02_09`, `BONUS_SAVE_13M`, `BONUS_SAVE_30_04`, `BONUS_SAVE_ADD_2`, `BONUS_SAVE_CTD_DAY`,
`BONUS_SAVE_KPI`, `BONUS_SAVE_NEW_YEAR`, `BONUS_SAVE_TET`, `BONUS_SAVE_TRAVEL`, `BUDGET_SAVE`,
`EARNED_PAID_LEAVE`, `NET_PAY_HOME`, `PAID_LEAVE_BALANCE_DAYS`, `PROB_SAL`, `RESP_SAL`.

### 10.2 Hai đính chính nhỏ về số liệu báo cáo

**(a) Số component là 140, không phải 141.** Con số 141 là số **version đang mở**, lệch 1 so với số
component vì có **một version mồ côi**: `RESPONSIBILITY_ALLOW` còn version đang mở nhưng **đã không còn
trong `salary_components`** — `giatbh` bỏ/đổi tên nó (rất có thể thành `RESP_SAL`, xuất hiện trong nhóm 15
mã mới). Vô hại về tính toán vì mọi phép đọc đều `FROM salary_components` rồi mới `LEFT JOIN` version,
nên dòng mồ côi không bao giờ được đọc. Nhưng nó là dữ liệu chết, và nó làm bất biến phải phát biểu chính
xác hơn: **"mọi component ĐANG TỒN TẠI có đúng một version đang mở"** — điều này đúng (0 mã thiếu).

**(b) Baseline test: 6, không phải 7.** Phiên thi hành báo 7; phiên này đo được **6** (đúng danh sách 6
test RBAC của `HANDOVER-giatbh.md` mục 3). Chênh 1 chính là
`TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` — test **fail ngẫu nhiên** vì assert số
đếm toàn cục `payroll_records` trong khi Go chạy package test song song trên cùng DB dev. Cả hai lần đo
đều **không có hồi quy**; chỉ là con số dao động 6–7 tuỳ lần chạy. Ai đọc sau đừng đi truy con số này.

### 10.3 Một báo động sai của tôi, ghi lại để không ai lặp

Thấy `RESPONSIBILITY_ALLOW` biến mất, tôi lo có công thức còn tham chiếu `[RESPONSIBILITY_ALLOW]` → engine
trả 0 im lặng. Quét toàn bộ 140 công thức tìm `[MÃ]` không tồn tại thì ra 5 mã:
`CONTRACT_TYPE`, `EMP_TYPE`, `HAS_SECOND_CONTRACT`, `HAS_TAX_COMMITMENT`, `IS_FOREIGNER`.

**Không phải lỗi** — 5 mã đó là **biến bơm lúc runtime** từ `employees`, không phải component: xác nhận ở
`internal/service/payroll_service.go:1463-1472` (`"CONTRACT_TYPE": contractType`, …,
`"HAS_TAX_COMMITMENT": false`). Và `RESPONSIBILITY_ALLOW` **không** nằm trong danh sách treo ⇒ `giatbh`
đã rename sạch, không để lại tham chiếu chết.

**Bài học cho Task 2:** đồ thị phụ thuộc phải **loại 5 mã bơm-runtime này ra** khi phân loại cột
nguồn/dẫn xuất. Nếu coi mọi `[MÃ]` là tham chiếu component, một cột chỉ tham chiếu biến runtime sẽ bị
xếp nhầm thành "dẫn xuất" (không mask được) trong khi nó là cột nguồn. Phép đo ở mục 16 của
`Salary-Structure-Template-Analysis-260726.md` đã loại đúng (chỉ đếm `m in codes`), nhưng bản thi hành
phải làm y vậy — đây là một bẫy im lặng.
