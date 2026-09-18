---
id: self-docs/files/prompt-report-task1
canonical_question: 'Technical guide and specification: Prompt dispatch — Report v1
  Task 1'
aliases:
- Prompt dispatch — Report v1 Task 1
- prompt Report Task1 060826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Prompt dispatch — Report v1 Task 1 (dán làm tin nhắn ĐẦU TIÊN của session mới)

Soạn 2026-08-06. Nguồn: `llmwiki/wiki/sources/draft/060826-report-template-config-v1-PLAN.md`
**Task 1** (đã qua cổng harness R7/R18, `exit 0`). Phần dưới dấu phân cách là nội dung để copy nguyên
văn.

---

Đây là phiên **THI HÀNH theo PLAN đã gate-clean**. Task 1 trong PLAN đã có sẵn code thật + lệnh chạy +
output mong đợi theo từng bước — làm đúng theo đó là đủ. Brief này chỉ bổ sung phần PLAN không thể biết
trước (trạng thái repo tại THỜI ĐIỂM BẠN CHẠY, không phải lúc viết PLAN).

Repo: `/Users/thaidt/Documents/Enterprise/Core System/Core System-backend`. Nhánh: `feature_v2`. Đây là **hạng
mục hoàn toàn khác** với PLAN `040826-Core System-template-on-giatbh-engine` (cấu trúc lương theo cấp bậc)
— đừng lẫn, đừng đọc nhầm task của PLAN kia.

## Đọc trước khi sửa

1. `llmwiki/wiki/sources/draft/060826-report-template-config-v1-PLAN.md`:
   `## Global constraints` (G1–G8, **bắt buộc**) → `### Task 1` (brief chi tiết, có code + lệnh + output
   mong đợi theo từng bước, làm theo đúng thứ tự).
2. `self-docs/Report-Template-Config-Analysis-040826.md` mục 0 — vì sao **tuyệt đối không FK vào
   `salary_components.id`** (G1): `migrationSalaryComponentsV4` xoá + reseed bảng đó **mỗi lần backend
   boot**, không `ON CONFLICT`. Hai bảng mới của task này **không đụng `salary_components` ở đâu cả**
   nên an toàn, nhưng phải hiểu tại sao trước khi viết SQL.

## ⚠️ Việc PLAN không biết trước — TỰ KIỂM LẠI, đừng tin số trong PLAN

**Mốc chữ cái `BY` mà PLAN ghi (dòng "sau `MigrationSeedInitialComponentVersions`") đã đúng tại thời
điểm viết PLAN (2026-08-06), nhưng nhánh này bị nhiều người cùng thêm migration liên tục** — mốc `BO`
đã từng phải đổi thành `BV`, `BP`→`BW`, `BQ`→`BX` vì đồng nghiệp `giatbh` chiếm trước lúc rebase. Trước
khi thêm dòng mới:

```bash
cd Core System-backend
grep -n '^\t\t// B[A-Z]\.' internal/database/database.go | tail -5
```

Nếu dòng cuối cùng in ra **không phải** `// BX. ...` thì mốc `BY` đã bị ai đó chiếm — chọn mốc chữ cái
tiếp theo còn trống, **không** dùng `BY` nếu nó đã tồn tại. Xác nhận luôn phần tử cuối slice thật là
`MigrationSeedInitialComponentVersions,` (không phải tên nào khác) trước khi chèn ngay sau nó:

```bash
grep -n "MigrationSeedInitialComponentVersions,$" internal/database/database.go
```

## Sự thật đã xác minh 2026-08-06 — dùng luôn

- `MigrationSeedInitialComponentVersions,` là phần tử **cuối cùng** trong slice `migrations` của
  `RunMigrations()` (`internal/database/database.go`, khoảng dòng 374). Mốc chữ cái liền trước là `BX`.
- `RunMigrations` (`:377-381` cùng file): lặp `db.Exec` từng chuỗi, **không transaction, không
  tracking, fail-fast** ⇒ mọi migration chạy lại **mỗi boot**, phải idempotent —
  `CREATE TABLE IF NOT EXISTS`/`CREATE INDEX IF NOT EXISTS` tự đáp ứng, đúng như PLAN đã viết.
- Backend **không bao giờ chạy Atlas** — `cmd/Core System/main.go` chỉ gọi `RunMigrations()` +
  `RunFileMigrations()` (G2). Đừng ghi gì vào `atlas/migrations/`.
- Helper test DB có sẵn: `internal/testutil/dbtest` (`dbtest.Open(t)` tự `t.Skip` khi thiếu
  `TEST_DATABASE_URL`) — PLAN Task 1 tự viết `openTestDB` riêng trong file test mới, cũng được, nhưng
  nếu muốn dùng lại helper chung thì đây là nơi có sẵn.
- Baseline test hiện tại (đo lúc viết brief này): **6 case fail** cố định
  (`TestPermissionGateCoverageReport`, `TestG1AllProtectedRoutesRequireRoleGateExceptAllowlist`,
  `TestReportPayrollSummaryRouteRequiresPeriodID`, `TestReportBankTransferRouteRequiresPeriodID`,
  `TestPipelineProtectedRunRouteWithDevAuthReachesHandler`,
  `TestPipelineProtectedLogsRouteWithDevAuthReachesHandler`). Có **1 test fail NGẪU NHIÊN** ngoài danh
  sách này —`TestIntegrationComputeFormulaImpactComputesDeltaWithoutWriting` (assert số đếm TOÀN CỤC
  `payroll_records`, fail khi các package test chạy song song trên cùng DB dev). Gặp nó thì **chạy cách
  ly test đó** trước khi kết luận hồi quy, đừng sửa code vì nó. **PLAN của task này yêu cầu tự đo lại
  baseline trước khi sửa dòng đầu tiên — làm đúng vậy, đừng chép số ở đây.**
- 2 commit vừa xong trên `feature_v2` (không liên quan task này, chỉ để bạn biết trạng thái nhánh):
  `fed1568` (backend), `52b1076` (frontend) — Task 3 của PLAN `040826` khác.

## Ràng buộc tuyệt đối (chép từ Global constraints — G1–G8 của PLAN, nhắc lại 3 cái áp dụng trực tiếp
cho Task 1)

1. **G1 — không FK vào `salary_components(id)`.** Hai bảng mới của task này không tham chiếu
   `salary_components` ở đâu cả (đúng thiết kế) — nếu thấy mình đang viết `REFERENCES
   salary_components`, dừng lại, đó là sai thiết kế.
2. **G2 — vào `RunMigrations()`, không vào `atlas/migrations/`.**
3. Đây là **Task 1/7**. **Không làm sang Task 2** (CRUD repo/service/handler) dù PLAN đã viết sẵn — mỗi
   task một commit, dừng đúng ranh giới `Step 5: commit` mà Task 1 PLAN đã ghi.

## Bẫy đã biết (rút từ các lần trước trên đúng file này)

- **Bẫy 1 — mốc chữ cái trùng.** Xem mục "⚠️ TỰ KIỂM LẠI" ở trên — đã xảy ra thật 2 lần.
- **Bẫy 2 — `gofmt -w` cả thư mục.** Đã từng làm hỏng một file không liên quan (đổi `''` thành
  smart-quote trong comment có sẵn). Chỉ chạy `gofmt -l <file bạn sửa>` để xem, không chạy trên cả
  `internal/`.
- **Bẫy 3 — quên xác nhận PASS thật trước khi coi "xong".** PLAN Step 1 cố ý viết test **FAIL trước**
  (bảng chưa tồn tại) rồi Step 3 mới chạy migration thật và xác nhận PASS. Đừng bỏ qua Step 1 — nếu
  không chạy nó trước, bạn không có bằng chứng test thật sự kiểm tra được điều nó tuyên bố kiểm tra.

## DỪNG và hỏi người dùng

- **Trước khi chạy migration thật vào DB dev `payroll_engine`** (Step 3 của PLAN Task 1) — xác nhận
  bằng cách trình bày SQL sẽ chạy.
- **Trước khi commit** (Step 5). Không tự push.
- Nếu mốc chữ cái `BY` đã bị chiếm khi bạn kiểm ở trên → **dừng, báo mốc nào đang trống**, đừng tự chọn
  một mốc rồi commit luôn — có thể trùng với một PR khác đang mở song song.
- Nếu PLAN lệch code thật ở bất kỳ dòng nào khác ngoài mốc chữ cái (tên hàm, số dòng, tên biến) → báo
  ngay, đừng đoán rồi làm tiếp.

## Định nghĩa "xong" (đúng PLAN Task 1, nhắc lại để không bỏ sót)

1. Step 1: test mới chạy và **FAIL đúng như PLAN mô tả** trước khi có migration (bằng chứng test thật
   sự kiểm tra được điều nó tuyên bố).
2. Step 2: 2 hằng SQL + wire vào slice, ở đúng mốc chữ cái đã tự xác nhận (không phải chép mù `BY`).
3. Step 3: migration thật chạy qua `go run ./cmd/Core System`, test chuyển **PASS**.
4. Step 4: chạy migration **lần hai**, không lỗi (xác nhận idempotent qua đường thật, không chỉ
   `psql -f`).
5. `go build ./...` + `go vet ./...` sạch; `go test ./...` khớp baseline tự đo ở bước đầu (không thêm
   fail mới, trừ test flaky đã biết).
6. Step 5: commit — **chỉ** 2 file PLAN đã liệt kê (`database.go` +
   `report_template_tables_test.go`), không kèm file nào khác.

## Khi xong thì ghi tài liệu

1. PLAN `060826-report-template-config-v1-PLAN.md` — nếu file có bảng tiến độ/cột trạng thái, cập nhật
   Task 1 → xong + commit hash. Nếu PLAN chưa có bảng tiến độ dạng đó (khác PLAN `040826`), tạo một mục
   ngắn "Tiến độ" ở đầu file theo đúng khuôn đã dùng cho PLAN kia, để phiên sau đọc được trạng thái mà
   không phải lục qua 7 task.
2. Một dòng nhật ký vào `CLAUDE.md` (mới nhất lên đầu, đúng format đang dùng trong file).
3. Nếu có phát hiện lệch giữa PLAN và code thật (kể cả nhỏ), ghi lại — đây là hạng mục còn rất mới, ghi
   sớm giúp Task 2 không lặp lại việc kiểm tra.

Bắt đầu bằng: đo baseline test, xác nhận mốc chữ cái còn trống, rồi làm Step 1. Báo kết quả 3 việc đó
cho tôi xem trước khi chạy migration thật.
