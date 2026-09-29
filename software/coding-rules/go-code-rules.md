---
id: software/coding-rules/go-code-rules
canonical_question: What code rules (layout, errors, context and DB, function size, naming, tests, dependencies, refactoring patterns, lint tuning) should every Go service follow, and which are machine-checkable?
aliases:
- Go coding rules
- golangci-lint rule set
- quy tắc code Go
- go error wrapping context transaction rules
- go service layering handler repository
- go refactor giant function cyclomatic complexity
entity_type: coding_rule_set
domain: software > coding-rules
last_verified: '2026-09-29'
---

# Go — bộ rule code

**rule_set:** `go` · **rule_set_version:** `0.2.0` · **status:** pilot (schema đang thử; số đo đã chạy `golangci-lint` thật)

Nguồn: audit một service Go nhỏ (SQL + HTTP) và lint thật trên hai service Go lớn (mỗi service hàng chục nghìn dòng, vài trăm file). Không chứa tên công ty hay mã nguồn nội bộ. Chỉ đọc, không sửa repo nguồn.

Schema giống `js-ts-code-rules`. Loại `refactor` là kinh nghiệm cấu trúc rút từ hàm phức tạp nhất, không phải rule lint.

## Phương pháp và giới hạn

- Công cụ: `golangci-lint` 2.14.0, config = bộ `.golangci.yml` của service nhỏ + `errcheck.check-blank: true` (bắt cả `_ =`), chạy với `--max-issues-per-linter=0 --max-same-issues=0`, loại thư mục worktree `.claude`.
- **Bẫy đã dính:** golangci-lint mặc định cắt ở 50 lỗi mỗi linter và 3 lỗi giống nhau. Chạy lần đầu không tắt giới hạn cho số "đẹp" sai (revive luôn ra 50). Luôn đặt hai cờ trên khi đo.
- **Sửa số đo cũ:** bản 0.1.0 dùng `rg` heuristic và có ba số sai: `gofmt` không "sạch" (thực tế 19 / 10 / 2 file lệch), `%v` với err không phải 232 chỗ (errorlint chỉ ra vài chục lỗi thật), và "gọi DB không ctx" ở adapter không phải 241 (noctx ở code chạy thật gần 0). Đã thay bằng số dưới đây. Bài học: heuristic `rg` chỉ để định hướng, không đưa vào KU làm số đo.
- Không đo hiệu năng (không profiling, không benchmark). Phần "optimize" chỉ là cấu trúc; chưa có bằng chứng tốc độ.
- Repo service nhỏ đang có thay đổi chưa commit làm build lỗi, nên đo trên `git archive HEAD` (bản sạch).

## Số đo (lint thật)

| Chỉ số | Service nhỏ | Backend lớn | Adapter |
|---|---:|---:|---:|
| Tổng issue | 106 | 2503 | 309 |
| Trong file `_test.go` | 14 | 462 | 57 |
| `gofmt` file lệch | 2 | 19 | 10 |
| `errcheck` (có `_ =`) | 31 | 842 | 98 |
| `noctx` tổng / trong test | 8 / 7 | 281 / ~270 | 25 / 25 |
| `errorlint` | 5 | 20 | 9 |
| `gocyclo` (>15) | 2 | 116 | 36 |
| `gocyclo` ≥ 30 | 0 | 29 | 7 |
| Hàm phức tạp nhất | 22 | 90 | 106 |
| `revive` | 55 | 931 (725 thiếu doc exported) | 118 |
| `goimports` | 0 | 253 | 0 |

Đọc số:
- **`noctx` gần như chỉ ở test** (`httptest.NewRequest`, `db.Exec` trong test). Code chạy thật hầu như đã dùng ctx. Cần loại `noctx` khỏi `_test.go`, nếu không 96% cảnh báo là nhiễu.
- **`revive:exported` (725 ở backend) là nhiễu** với service nội bộ không phải thư viện; chỉ bật nơi có API công khai.
- **`errcheck` tập trung ở vài mẫu lặp:** thư viện Excel (`SetCellValue` 118, `CoordinatesToCellName` 57, `SetCellStyle` 50), `Close` (70), `json.Marshal` (50), `Body.Close` (47), `RowsAffected` (42), `Rollback` (27). Sửa mẫu, không sửa từng dòng.
- **Độ phức tạp dồn vào vài hàm khổng lồ:** hàm tệ nhất đo được là 90 và 106; 29 + 7 hàm ≥ 30. Không phải phân tán đều.
- Thư mục dồn nhiều issue nhất (code chạy thật): tầng `service` (833) và `repository` (378) ở backend; `report` (69) và tầng tích hợp với hệ thống ngoài (55) ở adapter.

```yaml
rules:
  - id: GO-LAYOUT-01
    severity: error
    kind: review
    statement: "Tầng domain/DB không import net/http. Handler mỏng — parse input, gọi tầng dưới, ghi response; không viết SQL, không viết business rule. cmd/* chỉ wiring."
    scope: [prod]
    origin: "service nhỏ + hai service lớn"
    evidence: "Cả ba dùng layering; tên tầng khác nhau (domain/api/web hoặc handler/service/repository). Bất biến là hướng phụ thuộc, không phải tên thư mục."
  - id: GO-LAYOUT-02
    severity: warn
    kind: review
    statement: "panic và log.Fatal chỉ ở cmd/ (hoặc init không thể lỗi)."
    scope: [prod]
    origin: "service nhỏ"
  - id: GO-ERR-01
    severity: error
    kind: machine
    check: "golangci:errorlint"
    statement: "Wrap error khi qua ranh giới bằng fmt.Errorf(\"...: %w\", err). So bằng errors.Is/As, không dùng ==/!= hay type assertion trên error."
    scope: [prod, tests]
    origin: "service nhỏ"
    evidence: "errorlint 5 / 20 / 9 (chủ yếu so sánh == / != với error, vài chỗ verb không wrap). Ít hơn nhiều so với ước lượng cũ."
  - id: GO-ERR-02
    severity: error
    kind: machine
    check: "golangci:errcheck (check-blank true)"
    statement: "Không nuốt error, kể cả bằng _ =. Chỗ cố ý phải có comment lý do. Với mẫu lặp (ghi ô Excel, Marshal, RowsAffected) gom vào helper thay vì rải _ = hay bỏ qua."
    scope: [prod]
    origin: "hai service lớn"
    evidence: "backend 842, adapter 98; chỉ vài mẫu lặp chiếm phần lớn."
  - id: GO-ERR-03
    severity: warn
    kind: review
    statement: "Map error → HTTP status ở MỘT chỗ (writeError). Không rải map[string]string{\"error\": ...} literal; dùng helper writeErrorMsg(w, status, msg)."
    scope: [prod]
    origin: "service nhỏ"
    evidence: "service nhỏ ~53 chỗ literal; backend 21; adapter 0 (đã có helper)."
  - id: GO-ERR-04
    severity: warn
    kind: machine
    check: "golangci:errcheck (exclusions có điều kiện)"
    statement: "Close/Rollback trong defer là mẫu hợp lệ nhưng phải nhất quán. Đọc file/response: defer Close bỏ qua lỗi có chủ đích. Transaction: defer Rollback sau Commit bỏ qua ErrTxDone. Ghi rõ trong config exclusion, không tắt errcheck cả repo."
    scope: [prod]
    origin: "hai service lớn + service nhỏ"
    evidence: "Close 70/42/19 và Rollback 27/19/6 là mẫu lớn nhất còn lại của errcheck ở cả ba repo."
  - id: GO-CTX-01
    severity: error
    kind: machine
    check: "golangci:noctx, golangci:contextcheck"
    statement: "Hàm nhận ctx context.Context đầu tiên. Chỉ dùng ExecContext/QueryContext/QueryRowContext; trong handler dùng r.Context(). context.Background() chỉ ở main và test. Loại noctx khỏi _test.go."
    scope: [prod]
    origin: "service nhỏ"
    evidence: "noctx ở code chạy thật rất thấp (backend vài chỗ Exec/NewRequest, adapter 0); 96% cảnh báo noctx là trong test."
  - id: GO-DB-01
    severity: error
    kind: review
    statement: "Nhiều statement ghi → một transaction; truyền interface (DBTX) để cùng hàm chạy được trong/ngoài tx. SQL luôn tham số hoá ($1), không nối chuỗi. Kiểm rows.Err() sau vòng lặp rows."
    scope: [prod]
    origin: "service nhỏ"
    evidence: "rowserrcheck bắt 2 chỗ thiếu rows.Err() ở service nhỏ."
  - id: GO-SIZE-01
    severity: warn
    kind: machine
    check: "golangci:gocyclo (15), golangci:funlen (50), golangci:nestif"
    statement: "Hàm ≲ 50 dòng, complexity ≤ 15, nhánh lồng ≤ 3, file ≲ 300 dòng. Là warn có ratchet: baseline theo hàm, cấm tăng. Hàm ≥ 30 là ứng viên refactor ưu tiên."
    scope: [prod]
    origin: "service nhỏ + hai service lớn"
    evidence: "36 hàm ≥ 30 ở hai service lớn (29 + 7), tệ nhất 90 và 106."
  - id: GO-STYLE-01
    severity: error
    kind: machine
    check: "gofmt, goimports (local-prefixes = module path)"
    statement: "gofmt/goimports bắt buộc; import 3 nhóm std, third-party, nội bộ. Chạy gofmt -l (không chỉ tin vào hook) vì repo lớn vẫn còn file lệch."
    scope: [prod, tests]
    origin: "service nhỏ"
    evidence: "file lệch 2 / 19 / 10; goimports lệch 253 ở backend (nhóm import)."
  - id: GO-STYLE-02
    severity: warn
    kind: machine
    check: "golangci:revive (var-naming, unused-parameter, context-as-argument); revive:exported chỉ bật cho package có API công khai"
    statement: "Tên package ngắn, số ít, không util/common/helpers. Getter không tiền tố Get. Viết tắt giữ hoa (ID, URL, HTTP). Không bắt doc comment cho mọi exported symbol trong service nội bộ."
    scope: [prod]
    origin: "service nhỏ + hai service lớn"
    evidence: "725 cảnh báo thiếu doc exported ở backend là nhiễu; var-naming chỉ 6, unused-parameter 68 + 38."
  - id: GO-STYLE-03
    severity: warn
    kind: review
    statement: "Comment giải thích vì sao, không ghi lịch sử thay đổi. Ngày/ghi chú đổi (\"[2026-08-11]\", \"theo yêu cầu ...\") thuộc về git log hoặc CHANGELOG, không nằm trong doc comment của hàm."
    scope: [prod]
    origin: "adapter lớn"
    evidence: "doc comment của một hàm entrypoint dài hàng chục dòng, tích luỹ theo từng lần thêm bộ lọc, kèm ngày."
  - id: GO-TEST-01
    severity: warn
    kind: review
    statement: "Test table-driven với t.Run, t.Helper() trong helper. Logic domain test bằng DB thật, không mock DB. Test tích hợp DB là opt-in (bỏ qua khi thiếu biến môi trường) để go test ./... không cần DB. Bug fix đi kèm test tái hiện."
    scope: [prod, tests]
    origin: "service nhỏ + backend lớn"
  - id: GO-DEP-01
    severity: error
    kind: machine
    check: "go mod tidy -diff (rỗng)"
    statement: "Dep dùng trực tiếp không đánh // indirect; chạy go mod tidy sau khi đổi import. Thêm dep cần lý do, ưu tiên stdlib."
    scope: [prod]
    origin: "service nhỏ"
    evidence: "cả hai service lớn tidy sạch; service nhỏ từng chưa chạy tidy."
  - id: GO-REFACTOR-01
    severity: warn
    kind: refactor
    statement: "Hàm chạy nhiều pha tuần tự (truy vấn → gom nhóm → áp override → tính → tổng hợp) mà phân cách bằng comment \"// ── ... ──\" là dấu hiệu cần tách. Mỗi pha thành hàm thuần (nhận input, trả output, không chạm DB), hàm gốc chỉ điều phối. Viết test đặc trưng (ghi lại đầu ra hiện tại) TRƯỚC khi tách."
    scope: [prod]
    origin: "hai service lớn"
    evidence: "hàm truy vấn ma trận ~515 dòng, complexity 90, có ~6 pha ngăn bằng comment; hàm Load của báo cáo trải ~950 dòng, complexity 106."
  - id: GO-REFACTOR-02
    severity: warn
    kind: refactor
    statement: "Tham số lọc tuỳ chọn tích luỹ theo thời gian (chuỗi rỗng = không lọc; mã đơn hoặc danh sách phân cách dấu phẩy) → gom vào struct Filter hoặc functional options, có phương thức parse. Không thêm tham số vị trí thứ N."
    scope: [prod]
    origin: "adapter lớn"
    evidence: "một entrypoint nhận nhiều bộ lọc chuỗi (theo đối tượng, trạng thái, đơn vị tổ chức...), mỗi bộ thêm ở một thời điểm khác nhau."
  - id: GO-REFACTOR-03
    severity: warn
    kind: refactor
    statement: "Quy tắc nghiệp vụ mã cứng theo ID/UUID bên trong hàm tính (if/switch theo mã loại) → bảng dữ liệu (map hoặc slice struct) + hàm tra cứu, kiểm bằng test table-driven. Thêm loại mới = thêm một dòng bảng, không thêm nhánh."
    scope: [prod]
    origin: "backend lớn"
    evidence: "hàm tính giá trị theo phân loại bản ghi bằng chuỗi nhánh theo mã loại, mỗi nhánh một quy tắc riêng."
  - id: GO-REFACTOR-04
    severity: warn
    kind: refactor
    statement: "Hàm render báo cáo (xuất bảng tính) tách theo phần (tiêu đề, hàng dữ liệu, tổng) và bọc thư viện ghi ô trong một writer giữ lỗi đầu tiên (sticky error), kiểm lỗi một lần cuối. Loại bỏ hàng trăm lời gọi ghi ô không kiểm."
    scope: [prod]
    origin: "hai service lớn"
    evidence: "hàm render bảng tính complexity 34–35 ở hai báo cáo; SetCellValue/SetCellStyle không kiểm 118 + 50 lần ở backend."
  - id: GO-LINT-01
    severity: warn
    kind: review
    statement: "Cấu hình lint cho repo lớn — loại noctx, errcheck, gocyclo khỏi _test.go; revive:exported chỉ nơi có API công khai; bật ratchet theo linter thay vì bắt sạch một lần. Luôn đặt --max-issues-per-linter=0 --max-same-issues=0 khi đo baseline."
    scope: [prod, tests]
    origin: "hai service lớn"
    evidence: "462 / 57 issue nằm trong test; noctx 96% ở test; revive 725 nhiễu."
```

## Thứ tự làm khi áp vào repo Go đã lớn

1. Đo baseline bằng lint thật với hai cờ không giới hạn; ghi số theo linter.
2. Sửa nền tức thì: `gofmt -w`, `goimports -w`, `go mod tidy`.
3. Chỉnh config để giảm nhiễu (GO-LINT-01) trước khi sửa code.
4. Sửa theo mức nguy hiểm: lỗi bị nuốt (mẫu lặp gom helper), so sánh error, thiếu ctx ở code chạy thật.
5. Refactor chỉ hàm ≥ 30, làm từng hàm: test đặc trưng → tách pha → xoá comment lịch sử (GO-REFACTOR-01..04).
6. Ratchet phần còn lại; không refactor hàng loạt.

## Cạm bẫy đã gặp

- Cờ mặc định của golangci-lint làm số đo ảo (xem trên).
- `gofmt -l` bọc trong `2>/dev/null` hoặc qua công cụ lọc có thể báo 0 sai; chạy trần và đếm.
- Thư mục worktree do công cụ tạo (`.claude/worktrees/...`) chứa bản sao mã: loại khỏi quét.
- Repo đang sửa dở có thể không biên dịch → lint ra một lỗi typecheck duy nhất. Đo trên `git archive HEAD`.
- `zsh`: `rg`/`grep --include=*.go` phải bọc nháy `-g '*.go'`.
