---
type: draft
title: Vá lỗ hổng audit trail + xử lý cấu hình mồ côi phát hiện từ review bảo mật
  rule lương
status: approved
timestamp: 2026-08-20
task: null
id: self-docs/engine/salary-formula-audit-orphan-config-hardening
canonical_question: 'Technical guide and specification: Salary Formula Audit Orphan
  Config Hardening 200826'
aliases:
- Salary Formula Audit Orphan Config Hardening 200826
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

**Quyết định của user (20/08/2026):** Việc 1 → **Phương án A** (chỉ bổ sung ghi log vào `salary_component_history`, không đổi cơ chế ghi đè). Việc 2 → **Phương án 3** (giữ nguyên `ot_multiplier_configs`, chỉ ghi nhận chờ quyết định HR, không sửa code đợt này).

## Yêu cầu (một câu)

Xử lý 2 rủi ro đã xác nhận bằng chứng thật (không phải suy đoán) từ đợt đối chiếu bảo mật/configurability của `salary_components`: (1) audit log `salary_component_history` bị bỏ qua bởi các UPDATE formula chạy thẳng SQL trong migration self-heal, và (2) bảng `ot_multiplier_configs` có dữ liệu thật + code đọc thật nhưng không nơi nào gọi tới ("cấu hình ma").

## Context

Ghi chú quy ước máy local: SPEC này nằm ở `self-docs/` (không phải `llmwiki/wiki/sources/draft/`) vì quy ước máy local cấm tạo companion `.html` mà validator R7 lại đòi hỏi cho draft trong thư mục đó — cùng lý do đã áp dụng ở `self-docs/Salary-Column-Sync-Impact-280726.md`.

Nguồn gốc 2 việc này: `self-docs/Handoff-Salary-Rule-Security-Configurability-200826.md` mục 6 ("Kết quả đối chiếu 7 mục chưa kiểm", cập nhật 20/08/2026) — verify bằng psql thật trên `payroll_engine` dev + grep code trên nhánh `release/uat-180826`:

- **Mục 3 đã xác nhận**: `SaveHistory` (`internal/repository/salary_component_repo.go:194-203`) luôn ghi `changed_by` khi gọi qua handler production. NHƯNG các khối self-heal migration trong `internal/database/database.go` (dòng 2890-3053, ví dụ `UPDATE salary_components SET formula = ... WHERE code = 'SI_CTY'`) chạy `UPDATE` bằng SQL thô lúc boot, **không gọi `SaveHistory` cũng không qua `InsertVersion`** — không để lại vết trong audit log.
- **Mục 6 đã xác nhận**: `ot_multiplier_configs` có repo riêng (`ot_multiplier_repo.go`) với `SELECT` thật, nhưng `grep -rn "NewOtMultiplierRepo\|OtMultiplierRepo{"` trong `internal/` (ngoài file định nghĩa) = 0 kết quả — không ai khởi tạo/gọi nó.

Bối cảnh cơ chế versioning (bắt buộc hiểu trước khi đụng vào đường ghi formula): `self-docs/Formula-Versioning-PointInTime-050826.md`, đặc biệt **L11-L13** — các lỗ hổng tinh vi trước đây đều thuộc họ "trông như đã sửa đúng nhưng số tính ra vẫn dùng công thức cũ, không cảnh báo gì" vì version "đang mở" (`effective_until IS NULL`) bị ghi đè/che khuất âm thầm. Đây chính xác là kiểu rủi ro mà việc UPDATE thẳng SQL trong self-heal migration (mục 3) đang tái tạo — nếu sửa sai cách, dễ đẻ ra đúng loại lỗi L11-L13 mới.

Chưa tìm thấy concept/ADR liên quan trong `llmwiki/wiki/concepts/` hoặc `sources/adr/` cho `salary_component`/`formula`/`ot_multiplier` — grep ra rỗng. Nguồn chân lý cho hạng mục này là các file `self-docs/` liệt kê ở trên, không phải wiki.

## Global constraints

- **Nhánh làm việc:** `release/uat-180826` (đã xác nhận: chứa toàn bộ commit của `develop` — kể cả nội dung `sec_dev` vừa merge vào `develop` — cộng thêm 50 commit riêng của `feature_v2`/dọn DB/Workday bridge chưa lên `develop`). Theo `CLAUDE.md` gốc, hạng mục bảo mật/phân quyền phải làm ở `sec_dev`, nhưng `sec_dev` đã merge vào `develop` và nội dung đó đã có mặt đầy đủ trong `release/uat-180826` — **tiếp tục làm trên `release/uat-180826`**, không tạo nhánh mới (theo chỉ đạo trực tiếp của user trong phiên này).
- **Không phá cơ chế Point-in-Time versioning hiện tại** (`InsertVersion`, `effective_until IS NULL` = version đang mở) — mọi sửa đổi vào đường ghi formula phải đối chiếu với L11-L13 ở `Formula-Versioning-PointInTime-050826.md` trước khi chốt.
- **`go test ./...` không được hồi quy** — baseline tham chiếu gần nhất theo nhật ký `CLAUDE.md` (180826): 975 pass / 20 fail, fail-list phải giữ nguyên (không thêm fail mới).
- **Máy local: KHÔNG tạo file HTML trong `llmwiki/html/`** dù skill gợi ý — chỉ SPEC/PLAN markdown.
- Đây là thay đổi chạm vào cơ chế ghi/audit công thức lương — thuộc nhóm "sửa auth/authorization/audit code" cần xác nhận rõ với user trước khi thi hành thật (không tự chọn phương án).

## Non-goals

- **Không** thêm rate limit middleware cho route `/salary-components/*` (mục 2, việc khác vẫn còn mở, chưa được yêu cầu xử lý trong SPEC này).
- **Không** động vào `salary_formula_configs` (bảng mồ côi khác, đã xác nhận không ảnh hưởng hành vi tính lương thật).
- **Không** tiếp tục 19 câu hỏi đối chiếu Excel/HR đang chờ ở session gốc (việc khác, không liên quan bảo mật/audit).
- **Không** tự quyết định giữ hay xoá `ot_multiplier_configs`/repo của nó — đây là quyết định nghiệp vụ (có tính năng dở dang hay đã bỏ) cần hỏi HR/user trước.
- **Không** viết lại toàn bộ migration self-heal cũ trong `database.go` (đã chạy ổn định trên prod nhiều đợt) — chỉ xử lý phần audit trail thiếu, không đổi logic tính đúng-sai của các UPDATE đó.
- **Không** dispatch cho CLI agent khác chạy headless — làm trực tiếp trong phiên tương tác này theo yêu cầu user ("thảo luận kĩ rồi mới tiến hành sửa").

## Approaches

### Việc 1 — Audit trail thiếu cho UPDATE formula trong self-heal migration

**Phương án A — Chỉ bổ sung ghi log, không đổi cơ chế ghi đè (khuyến nghị, rủi ro thấp nhất)**
Thêm 1 lệnh `INSERT INTO salary_component_history` ngay sau mỗi `UPDATE salary_components SET formula = ...`/`fixed_value = ...` trong `database.go` (dòng 2890-3053), `changed_by = 'system_migration_self_heal'`, `reason` ghi rõ tên migration. Không gọi `InsertVersion` — giữ nguyên cơ chế ghi đè hiện tại (self-heal đã chạy ổn định qua nhiều đợt, các block này tự idempotent qua điều kiện `WHERE` nên sau lần chạy đầu sẽ match 0 dòng, không ghi log lặp).
- *Ưu:* thay đổi nhỏ, không đụng logic đã chạy ổn định trên prod, rủi ro hồi quy gần như không có, giải quyết đúng triệu chứng "không có audit trail".
- *Nhược:* không giải quyết gốc rễ — self-heal vẫn ghi đè `formula` trực tiếp thay vì qua `InsertVersion`, nên nếu kỳ lương quá khứ đã chốt bằng version cũ, việc ghi đè này **vẫn có thể lặp lại đúng lỗi họ L11-L13** (số kỳ cũ bị tính lại sai nếu re-run) — chỉ khác là giờ có log để phát hiện, không phải để phòng.

**Phương án B — Chuyển hẳn sang pipeline chính thức (`InsertVersion` + `SaveHistory`), coi self-heal như một lần sửa công thức thật**
Sửa các block self-heal gọi đúng hàm nghiệp vụ (`InsertVersion` rồi `SaveHistory`) thay vì UPDATE thô — tự động thừa hưởng toàn bộ bảo vệ point-in-time đã có.
- *Ưu:* nhất quán hoàn toàn với đường ghi production, xử lý tận gốc rủi ro L11-L13 cho các lần self-heal.
- *Nhược:* rủi ro cao hơn nhiều — các block này đã chạy ổn định qua nhiều đợt fix trên prod với hành vi ghi-đè-trực-tiếp; đổi sang tạo version mới có thể làm lộ ra các version "đang mở" cũ chưa đóng đúng cách (chính là loại bug L11-L13 đã từng xảy ra), cần audit lại toàn bộ chuỗi version hiện có trên DB thật trước khi đổi — khối lượng việc lớn hơn hẳn phạm vi "vá audit trail".

**Phương án C — Không sửa, chỉ ghi nhận rủi ro vào tài liệu (bảo thủ nhất)**
Giữ nguyên, chỉ dừng ở mức đã ghi vào `Handoff-Salary-Rule-Security-Configurability-200826.md` mục 6.
- *Ưu:* 0 rủi ro thay đổi.
- *Nhược:* lỗ hổng audit trail vẫn còn nguyên, mất khả năng truy vết nếu self-heal migration mới thêm sau này lại vô tình sửa sai công thức.

*(Chưa chọn — cần user quyết định A/B/C.)*

### Việc 2 — `ot_multiplier_configs` mồ côi

**Phương án 1 — Xoá bảng + repo (coi là nợ code từ nỗ lực dở dang)**
Theo đúng tinh thần đã làm với 10 bảng chết/6 bảng ref chết ở các đợt dọn DB 170826-180826: xác nhận 0 code nào gọi, backup data, `DROP TABLE`, xoá `ot_multiplier_repo.go`.
- *Ưu:* dọn sạch, giảm bề mặt "cấu hình ma" tương lai.
- *Nhược:* nếu đây thực ra là tính năng HR đang chờ (hệ số tăng ca theo từng mốc) mà đội khác dự định nối dây sau, xoá nhầm sẽ mất công làm lại.

**Phương án 2 — Nối dây thật: cho một component OT trong `salary_components` gọi `OtMultiplierRepo` qua formula/engine**
Hoàn thiện tính năng: thêm hàm built-in trong DSL công thức (hoặc sửa OT calculation) đọc `ot_multiplier_configs` theo đúng thiết kế ban đầu của repo.
- *Ưu:* tận dụng dữ liệu + code đã có sẵn, đúng như tên bảng gợi ý (đang có dữ liệu thật, không phải seed rỗng).
- *Nhược:* đây là thay đổi hành vi tính lương thật (đổi cách tính OT) — cần xác nhận với HR/kế toán trước (đúng bài học ở mục 2.4 "đừng vội kết luận sai khi chỉ khác Excel"), phạm vi việc lớn hơn nhiều so với "vá lỗ hổng bảo mật".

**Phương án 3 — Giữ nguyên, chỉ hỏi HR/nghiệp vụ xem đây là tính năng bỏ dở hay đang chờ, quyết định sau (khuyến nghị cho đợt này)**
Không xoá không nối dây ngay — vì cả 2 đều là quyết định nghiệp vụ ảnh hưởng thật (Phương án 1 có thể xoá nhầm việc dở dang, Phương án 2 đổi cách tính lương thật). Ghi rõ vào tài liệu là "biết, đang chờ quyết định", để 1 mục hỏi riêng ngoài phạm vi sửa code đợt này.
- *Ưu:* không rủi ro sai quyết định nghiệp vụ.
- *Nhược:* rủi ro "cấu hình ma" vẫn tồn tại đến khi có câu trả lời.

*(Chưa chọn — cần user quyết định 1/2/3, đây thuộc nhóm quyết định nghiệp vụ không nên tự chọn theo đúng quy ước `CLAUDE.md`.)*

## Requirements (FR)

**TASK-REF**: Nếu chọn Phương án A/B cho Việc 1 — mọi UPDATE `formula`/`fixed_value` trong `database.go` (self-heal) PHẢI ghi một dòng tương ứng vào `salary_component_history` với `changed_by` xác định được nguồn gốc (không phải chuỗi rỗng/NULL).
**TASK-REF**: Việc ghi audit bổ sung (TASK-REF) KHÔNG được ghi trùng lặp ở các lần boot sau (khi điều kiện `WHERE` của self-heal không còn match dòng nào).
**TASK-REF**: Nếu chọn Phương án 1 (xoá) cho Việc 2 — phải backup dữ liệu `ot_multiplier_configs` bằng `pg_dump --data-only` trước khi `DROP TABLE`, theo đúng quy trình đã áp dụng ở các đợt dọn DB trước.
**TASK-REF**: Nếu chọn Phương án 2 (nối dây) cho Việc 2 — phải có xác nhận bằng văn bản/chat từ user rằng đây là thay đổi cách tính lương thật đã được duyệt, trước khi sửa engine tính OT.
**TASK-REF**: Mọi thay đổi phải giữ nguyên fail-list của `go test ./...` so với baseline đo trước khi sửa (không hồi quy).

## Success criteria (SC)

**TASK-REF**: Người review bảo mật sau này mở `salary_component_history` cho bất kỳ `component_code` nào từng bị self-heal sửa, thấy đủ dòng ghi nhận thay đổi — không còn khoảng trống "không rõ ai/khi nào sửa formula này".
**TASK-REF**: Không còn bảng cấu hình nào trong `payroll_engine` ở trạng thái "có dữ liệu thật + có code đọc được + không ai gọi" mà không được ghi chú rõ ràng là "đã biết, chờ quyết định X" — tránh lặp lại kiểu phát hiện tình cờ như đợt này.
**TASK-REF**: `go test ./...` chạy sau khi sửa cho kết quả pass/fail giống hệt baseline đo trước khi sửa (đối chiếu bằng `comm`, không chỉ nhìn tổng số).

## Plan

- [x] Đo baseline `go test ./...` trên `release/uat-180826` trước khi sửa gì: **759 passed / 6 failed / 141 skipped** (skipped vì thiếu `TEST_DATABASE_URL` khi chạy suite thường — 6 fail đều thuộc nhóm role-gate/permission-report tiền tồn tại, không liên quan salary component).
- [x] Việc 1 → **Phương án A đã chọn**, nhưng cách triển khai đổi khác literal mô tả ban đầu: thay vì chèn INSERT vào từng ~10-11 khối self-heal riêng lẻ, phát hiện điểm chèn tổng quát duy nhất tại `MigrationSeedInitialComponentVersions` (`internal/database/database.go`, const bắt đầu dòng ~3346) — thêm **câu (0)** ngay trước câu (1) đã có sẵn, tái dùng đúng điều kiện đối chiếu `v.formula <> sc.formula OR v.name <> sc.name OR v.rounding <> sc.rounding` để `INSERT INTO salary_component_history` với `old_formula = v.formula` (version đang mở, trước khi bị đóng), `new_formula = sc.formula` (giá trị self-heal vừa ghi), `changed_by = 'system_migration_self_heal'`. Bắt được audit trail cho **toàn bộ 11 khối SelfHeal hiện có + khối tương lai**, không phải sửa tay từng khối — quyết định đổi cách làm này đã hỏi lại user qua `AskUserQuestion` trước khi thi hành (chọn "sửa 1 điểm tổng quát").
- [x] Verify thật trên **bản clone dữ liệu dev thật** (`pg_dump -Fc payroll_engine` → `pg_restore` vào DB tạm `payroll_engine_audit_test_200826`, xoá ngay sau khi xong — không đụng DB dev thật): cố ý tạo drift (sửa tay `salary_component_versions.formula` của `SI_CTY` thành giá trị rác), chạy `RunMigrations` thật → xác nhận `salary_component_history` ghi đúng 1 dòng `old_formula='JUNK_...'`, `new_formula='[INS_SAL_BH] * 0.17'`, `changed_by='system_migration_self_heal'`; cơ chế đóng/mở version (câu 1/2 cũ) vẫn hoạt động đúng, không bị ảnh hưởng. Chạy `RunMigrations` **lần 2** → vẫn đúng 1 dòng, không ghi trùng (TASK-REF đạt).
- [x] Việc 2 → **Phương án 3 đã chọn** (giữ nguyên `ot_multiplier_configs`, không sửa code) — đã ghi vào `self-docs/Handoff-Salary-Rule-Security-Configurability-200826.md` mục 6 phần "Việc còn mở", chờ hỏi HR/nghiệp vụ ở đợt khác.
- [x] Chạy lại `go test ./...` sau khi sửa: **759 passed / 6 failed** — đúng y hệt baseline (đối chiếu danh sách 6 fail giống hệt tên test), `go vet ./...` sạch. 0 hồi quy.
- [x] Cập nhật `self-docs/Handoff-Salary-Rule-Security-Configurability-200826.md` mục 6 với kết quả thi hành thật.
- [ ] Ghi 1 dòng vào "Nhật ký công việc theo ngày" trong `CLAUDE.md` gốc repo (làm ở bước cuối cùng của phiên).
- [ ] Commit thay đổi `internal/database/database.go` trên `release/uat-180826` — **chưa commit, chờ user xác nhận** (đúng nguyên tắc "chỉ commit khi user yêu cầu rõ").

## Assumptions

- (default) Baseline test hiện tại vẫn là ~975 pass/20 fail như ghi trong `CLAUDE.md` nhật ký 180826 — sẽ tự đo lại trước khi sửa, không tin số cũ mù quáng (đúng bài học đã ghi nhiều lần trong nhật ký dự án).
- (default) `changed_by = 'system_migration_self_heal'` là giá trị hợp lý cho TASK-REF nếu Phương án A/B được chọn — có thể đổi tên khác nếu user muốn quy ước khác.
- (default, find-out-later) Chưa xác nhận `ot_multiplier_configs` có được HR dự định dùng hay không — đây chính là câu hỏi cần đặt ra ở Việc 2, không tự đoán.

## Self-review

1. **Phủ yêu cầu** — cả 2 việc user chỉ định (audit gap + orphan config) đều có task tương ứng trong Plan. Đạt.
2. **Quét placeholder** — không còn `TBD`/`TODO`/"xử lý phù hợp" nào trong SPEC; các nhánh phương án đều ghi cụ thể hành động, không mơ hồ.
3. **Nhất quán tên** — dùng thống nhất `salary_component_history`, `InsertVersion`, `SaveHistory`, `ot_multiplier_configs`/`OtMultiplierRepo` xuyên suốt, khớp tên thật trong code (đã đối chiếu lại với agent report).
