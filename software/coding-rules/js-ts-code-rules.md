---
id: software/coding-rules/js-ts-code-rules
canonical_question: What code rules (structure, safety, async, style, lint thresholds) should every JavaScript/TypeScript repo follow, and which are machine-checkable?
aliases:
- JS TS coding rules
- eslint rule set
- quy tắc code JavaScript TypeScript
- code quality rules js ts
- lint ratchet scope override
entity_type: coding_rule_set
domain: software > coding-rules
last_verified: '2026-09-29'
---

# JavaScript / TypeScript — bộ rule code

**rule_set:** `js-ts` · **rule_set_version:** `0.1.0` · **status:** pilot (schema đang thử)

Nguồn: audit pmkit (2026-09-29) + áp thực tế vào `tu-vi-app-poc` (170 file TS, lint lần đầu). Mỗi rule có `origin` để truy nguồn và `evidence` để biết vì sao có.
`kind: machine` = có rule lint kiểm được (harness sinh config). `kind: review` = chỉ người/agent soát, không có lint.

## Schema của một rule

`id` (ổn định, không đổi số) · `severity` (`error` chặn, `warn` đếm ratchet) · `kind` · `check` (tên rule lint nếu machine) · `statement` (một câu) · `scope` (phạm vi áp: `prod`, `scripts`, `tests`) · `origin` · `evidence`.

```yaml
rules:
  - id: JS-SEC-01
    severity: error
    kind: machine
    check: "eslint:no-restricted-syntax (innerHTML gán template có nội suy / nối chuỗi)"
    statement: "Không nhúng dữ liệu người dùng/server vào innerHTML hay template HTML; dùng textContent/createElement/escapeHtml."
    scope: [prod]
    origin: "pmkit"
    evidence: "pmkit có 10 chỗ innerHTML nội suy, không có hàm escape. tu-vi-app-poc: 0 chỗ."
  - id: JS-SEC-02
    severity: error
    kind: review
    statement: "Không eval, new Function, document.write, inline handler (onclick=); React dangerouslySetInnerHTML cấm như innerHTML."
    scope: [prod]
    origin: "pmkit"
  - id: JS-SEC-03
    severity: error
    kind: review
    statement: "Không lưu token/secret ở localStorage; session đi bằng cookie httpOnly."
    scope: [prod]
    origin: "pmkit"
  - id: JS-ERR-01
    severity: error
    kind: machine
    check: "eslint:no-empty (allowEmptyCatch=false)"
    statement: "catch rỗng phải xử lý lỗi hoặc có comment nêu lý do; không nuốt lỗi im lặng."
    scope: [prod, scripts, tests]
    origin: "pmkit + tu-vi-app-poc"
    evidence: "tu-vi-app-poc có 11 catch rỗng, 3 trong code chạy thật (src/server/index.ts)."
  - id: JS-ERR-02
    severity: error
    kind: review
    statement: "Mỗi lời gọi async ở handler có try/catch hiển thị lỗi cho user; chặn double-submit (disable nút, bật lại trong finally)."
    scope: [prod]
    origin: "pmkit"
  - id: JS-TYPE-01
    severity: error
    kind: machine
    check: "@typescript-eslint/no-explicit-any"
    statement: "Không any; dùng unknown rồi narrow. Không // @ts-ignore (dùng @ts-expect-error kèm lý do)."
    scope: [prod]
    origin: "pmkit + tu-vi-app-poc"
    evidence: "tu-vi-app-poc có 221 any; 44 trong code chạy thật, 177 trong scripts/tests (parse JSON, LLM output)."
  - id: JS-TYPE-02
    severity: warn
    kind: machine
    check: "@typescript-eslint/no-explicit-any"
    statement: "Ở scripts/tests, any hạ xuống warn và đếm ratchet, giảm dần khi chạm file."
    scope: [scripts, tests]
    origin: "tu-vi-app-poc"
  - id: JS-STYLE-01
    severity: error
    kind: machine
    check: "eslint:eqeqeq, eslint:no-var, eslint:prefer-const"
    statement: "Luôn ===; const mặc định, let khi cần gán lại, cấm var."
    scope: [prod, scripts, tests]
    origin: "pmkit"
    evidence: "tu-vi-app-poc có 21 == (đều trong scripts/book); đổi == null sang === null phải xét từng chỗ vì đổi hành vi."
  - id: JS-STYLE-02
    severity: error
    kind: machine
    check: "@typescript-eslint/no-unused-vars (args after-used), @typescript-eslint/no-shadow"
    statement: "Không biến/import thừa, không biến bóng."
    scope: [prod, scripts, tests]
    origin: "pmkit"
  - id: JS-SIZE-01
    severity: warn
    kind: machine
    check: "eslint:max-lines (300), max-lines-per-function (50), complexity (12), max-depth (3)"
    statement: "File ≲ 300 dòng, hàm ≲ 50 dòng, complexity ≤ 12, lồng ≤ 3. Là warn để ratchet, không refactor hàng loạt."
    scope: [prod, scripts, tests]
    origin: "pmkit"
    evidence: "tu-vi-app-poc vượt ngưỡng 353 lần (153 max-depth, 112 hàm dài, 64 complexity, 14 file dài); 129 max-depth nằm trong scripts."
  - id: JS-LOG-01
    severity: warn
    kind: machine
    check: "eslint:no-console (allow error)"
    statement: "Code chạy thật không dùng console để báo lỗi cho user. scripts/ (CLI) được phép in ra: tắt rule ở đó."
    scope: [prod]
    origin: "tu-vi-app-poc"
    evidence: "272 no-console, 247 trong scripts/ (CLI in ra là đúng)."
  - id: JS-STRUCT-01
    severity: warn
    kind: review
    statement: "Tách 3 tầng api (fetch, không đụng DOM) → state → render; render không gọi fetch. Mọi request qua một hàm bọc duy nhất."
    scope: [prod]
    origin: "pmkit"
  - id: JS-STRUCT-02
    severity: warn
    kind: review
    statement: "Chuỗi hiển thị gom một chỗ, không rải trong logic; magic number/string thành hằng có tên."
    scope: [prod]
    origin: "pmkit"
```

## Quy tắc áp dụng (rút từ thực tế)

- **Không áp một chuẩn cho cả repo.** Tách phạm vi: `prod` sạch tuyệt đối; `scripts` và `tests` dùng ngưỡng nới kèm ratchet (số warn không được tăng so với baseline).
- **Ratchet thay vì sửa hàng loạt** cho rule kích cỡ: lưu baseline theo rule, cổng fail khi tăng.
- **Thứ tự áp dụng:** copy rule + config → fix nền (format) → lint chỉ báo cáo → duyệt → sửa theo mức nguy hiểm (XSS, lỗi nuốt, code chết/==, kích cỡ), mỗi nhóm một commit.
- **TS cần parser:** ESLint 9 trần không đọc TS; cần `typescript-eslint`. Bỏ `no-undef` cho TS (tsc đã kiểm).
- Cài công cụ lint vào devDependencies để cổng chạy được trên máy khác/CI, không chạy từ thư mục tạm.

## Cạm bẫy đã gặp

- Config chép từ repo JS thuần sang repo TS không chạy (thiếu parser).
- Repo có lint riêng cho frontend (oxlint, rule React hooks): giữ song song, đừng thay.
- `zsh`: `rg`/`grep --include=*.go` phải bọc nháy `-g '*.go'`.
