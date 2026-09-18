---
id: self-docs/engine/report-perf-optimize-phase2-plan
canonical_question: 'Technical guide and specification: 🚀 Kế hoạch Tối ưu Hiệu năng
  Renderer Báo cáo — Phase 2'
aliases:
- 🚀 Kế hoạch Tối ưu Hiệu năng Renderer Báo cáo — Phase 2
- 150926 Report Perf Optimize Phase2 PLAN
entity_type: how_to
domain: self-docs > engine
last_verified: 2026-09-17
---

# 🚀 Kế hoạch Tối ưu Hiệu năng Renderer Báo cáo — Phase 2 (PLAN)

> **Mục tiêu cốt lõi**:
> - **Ưu tiên #1**: Các báo cáo có template đóng gói sẵn (`.xlsx` embedded generators) — triệt tiêu triệt để N+1 query ngân hàng còn sót, tối ưu thao tác dọn dòng thừa template trong Excelize.
> - **Ưu tiên #2**: Hiệu năng renderer của báo cáo tuỳ chỉnh (Configurable Report Templates) — Pre-compiled AST engine cho `evalExpression` (biên dịch 1 lần, chạy N lần) và Zero-copy Layered Scope cho biến alias.
> - **Hỗ trợ Preview**: Tối ưu cache formatter trên client-side `report-preview.ts`.
>
> **Thời gian**: 15/09/2026  
> **Nhánh thực hiện**:
> - Backend: `feature/report-perf-optimize-150926` (từ `develop`)
> - Frontend: `feature/report-perf-optimize-150926` (từ `develop_v1`)

---

## I. TỔNG QUAN VẤN ĐỀ & MỤC TIÊU ĐO LƯỜNG PHASE 2

| Phân hệ | Vấn đề hiện tại | Giải pháp Phase 2 | Kỳ vọng Cải thiện |
|:---|:---|:---|:---:|
| **Báo cáo có template (Bank Generators)** | `report_gen_bank_tpbank.go` & `report_gen_bank_khac.go` gọi `bankAcctRepo.GetByEmployee` trong vòng lặp records | Gom `empIDs` và gọi batch 1 lần `bankAcctRepo.GetByEmployeeIDs(ctx, empIDs)` (đã có từ Phase 1) | **Giảm 100% N+1** (từ 6.000 queries xuống 2 queries) |
| **Báo cáo có template (Excelize Wipe)** | 7 generator (`pit_nam`, `trich_thuong`, `bao_viet`, `bao_hiem`, `muc_luong`, `gdda`, `dieu_chinh`) duyệt 2 chiều `45` cột x `(lastRow - firstData)` dòng để `SetCellValue("")` | Chỉ dọn rác các dòng thật sự dư thừa (`lastRow > firstData + len(data) - 1`). Với dữ liệu thật > số dòng mẫu, **bỏ qua 100% vòng lặp dọn** | **Tiết kiệm 20.000 - 30.000 ops DOM** trong Excelize |
| **Báo cáo Custom (Expression Engine)** | `ReportRunService.Run()` parse lại chuỗi công thức từ đầu cho mỗi NV (3.000 lần parse regex/AST) | Tiền biên dịch AST 1 lần trước vòng lặp (`CompileExpression`), trong vòng lặp chỉ thực thi cây node (`ast.Eval`) | **Giảm 85 - 90% CPU** xử lý công thức custom |
| **Báo cáo Custom (Memory Allocations)** | Copy toàn bộ map `rec.ComputedValues` (100+ phần tử) cho mỗi NV để lưu alias | Sử dụng `LayeredScope`: Alias lưu ở map nhỏ riêng, lookup fallback vào `ComputedValues` mà không cần clone map | **Giảm 95% Memory Allocations** & áp lực GC |
| **Frontend Preview** | `report-preview.ts` chạy regex kiểm tra `numFmt` liên tục trên hàng vạn cell | Memoize kết quả phân tích `numFmt` (phần trăm, số thập phân) | Preview grid mượt mà, **giảm 40% CPU thread chính** |

---

## II. DANH SÁCH FILE THAY ĐỔI

```
Core System-backend/
├── internal/service/
│   ├── report_gen_bank_tpbank.go      # Task 1: Batch load tài khoản ngân hàng TPBank
│   ├── report_gen_bank_khac.go        # Task 1: Batch load tài khoản ngân hàng Khác
│   ├── report_wipe_helper.go          # Task 2: Helper dọn dòng mẫu dư thừa (mới)
│   ├── report_gen_pit_nam.go          # Task 2: Áp dụng dọn thông minh PIT năm
│   ├── report_gen_trich_thuong.go     # Task 2: Áp dụng dọn thông minh Trích thưởng
│   ├── report_gen_bao_viet.go         # Task 2: Áp dụng dọn thông minh Bảo Việt
│   ├── report_gen_bao_hiem.go         # Task 2: Áp dụng dọn thông minh Bảo hiểm
│   ├── report_gen_muc_luong.go        # Task 2: Áp dụng dọn thông minh Mức lương
│   ├── report_gen_phan_bo_gdda.go     # Task 2: Áp dụng dọn thông minh GĐDA
│   ├── report_gen_dieu_chinh.go       # Task 2: Áp dụng dọn thông minh Điều chỉnh
│   ├── engine.go                      # Task 3: AST Compiled Expression Parser
│   └── report_run_service.go          # Task 3 & 4: Run() dùng AST compiled + LayeredScope
Core System-frontend/
└── components-page/tinh-luong/
    └── report-preview.ts              # Task 5: Formatter cache & fast-path parser
```

---

## III. KẾ HOẠCH CHI TIẾT TỪNG TASK (TRACER BULLETS)

---

### Task 1: Triệt tiêu N+1 Bank Account Queries trong 2 Generator Ngân Hàng (Ưu tiên #1)

**Mục tiêu**: Thay thế vòng lặp gọi `s.bankAcctRepo.GetByEmployee(ctx, emp.ID)` bằng batch query `s.bankAcctRepo.GetByEmployeeIDs(ctx, empIDs)`.

**Files:**
- Sửa: `Core System-backend/internal/service/report_gen_bank_tpbank.go:90-120`
- Sửa: `Core System-backend/internal/service/report_gen_bank_khac.go:90-120`

**Interfaces:**
- Consumes: `s.bankAcctRepo.GetByEmployeeIDs(ctx context.Context, employeeIDs []uuid.UUID) (map[uuid.UUID][]models.EmployeeBankAccount, error)` (đã tạo ở Phase 1).
- Produces: `acctsByEmpID map[uuid.UUID][]models.EmployeeBankAccount` được tra cứu trực tiếp trong $O(1)$.

**Các bước thực hiện:**
1. **Trong `report_gen_bank_tpbank.go`**:
   - Trước vòng lặp duyệt records:
     ```go
     empIDs := make([]uuid.UUID, 0, len(records))
     for _, r := range records {
         if r.ComputedValues.Get("NET_PAY") > 0 {
             empIDs = append(empIDs, r.EmployeeID)
         }
     }
     acctsByEmpID, err := s.bankAcctRepo.GetByEmployeeIDs(ctx, empIDs)
     if err != nil {
         return nil, fmt.Errorf("bank-tpbank: get bank accounts: %w", err)
     }
     ```
   - Trong vòng lặp:
     ```go
     accts := acctsByEmpID[emp.ID]
     if len(accts) == 0 {
         continue
     }
     ```
2. **Trong `report_gen_bank_khac.go`**:
   - Áp dụng logic batch tương tự với `acctsByEmpID`.
3. **Verify**:
   - Chạy test: `go test ./internal/service -run "Test.*Bank.*" -v`
   - Build backend: `go build ./...`

---

### Task 2: Dọn Dòng Mẫu Thông Minh (Wipe Loop Optimization) trong 7 Generators (Ưu tiên #1)

**Mục tiêu**: Thay vì set rỗng toàn bộ vùng mẫu một cách mù quáng (ví dụ 45 cột x 500 dòng = 22.500 ops), chỉ dọn những dòng thật sự thừa nếu số dòng dữ liệu thật ít hơn số dòng mẫu của template.

**Files:**
- Tạo mới helper: `Core System-backend/internal/service/report_wipe_helper.go`
- Sửa:
  - `Core System-backend/internal/service/report_gen_pit_nam.go:187-196`
  - `Core System-backend/internal/service/report_gen_trich_thuong.go:187-196`
  - `Core System-backend/internal/service/report_gen_bao_viet.go:187-196`
  - `Core System-backend/internal/service/report_gen_bao_hiem.go:160-190`
  - `Core System-backend/internal/service/report_gen_muc_luong.go:160-170`
  - `Core System-backend/internal/service/report_gen_phan_bo_gdda.go:260-275`
  - `Core System-backend/internal/service/report_gen_dieu_chinh.go:160-170`

**Logic Helper (`report_wipe_helper.go`):**
```go
package service

import "github.com/xuri/excelize/v2"

// clearSurplusTemplateRows dọn dẹp các dòng mẫu cũ còn dư lại từ template gốc.
// Nếu số dòng dữ liệu thật (actualDataCount) >= số dòng mẫu trong file (lastTemplateRow - firstDataRow + 1),
// các dòng dữ liệu thật sẽ tự động ghi đè 100% -> KHÔNG CẦN DỌN (0 op).
// Chỉ dọn khi file mẫu có nhiều dòng hơn dữ liệu thực tế.
func clearSurplusTemplateRows(f *excelize.File, sheet string, firstDataRow, actualDataCount, lastTemplateRow, maxCols int) {
    surplusStart := firstDataRow + actualDataCount
    if surplusStart > lastTemplateRow {
        return // Không có dòng dư thừa nào, dữ liệu thật đã phủ kín
    }
    for r := surplusStart; r <= lastTemplateRow; r++ {
        for c := 1; c <= maxCols; c++ {
            cell, err := excelize.CoordinatesToCellName(c, r)
            if err == nil {
                _ = f.SetCellValue(sheet, cell, "")
            }
        }
    }
}
```

**Các bước thực hiện:**
1. Tạo file `internal/service/report_wipe_helper.go` với hàm `clearSurplusTemplateRows`.
2. Thay thế vòng lặp 2 chiều tại 7 generators trên bằng lời gọi `clearSurplusTemplateRows`.
3. Đo lường: Khi xuất báo cáo với 3.000 NV, hàm sẽ lập tức `return` vì `surplusStart (3004) > lastTemplateRow (15)`, triệt tiêu hoàn toàn 30.000 thao tác set cell rác.

---

### Task 3: Pre-compiled AST & Expression Engine cho Report Custom (Ưu tiên #2)

**Mục tiêu**: Tách `evalExpression` trong `engine.go` thành:
1. `compileExpression(formula string) (ExprAST, error)`: Phân tích cú pháp chuỗi thành cây AST một lần duy nhất.
2. `ast.Eval(vals ValueScope) (formulaValue, error)`: Tính toán trên cây AST với zero parsing, zero regex.

**Files:**
- Sửa: `Core System-backend/internal/service/engine.go`
- Sửa: `Core System-backend/internal/service/report_run_service.go:160-195`

**Kiến trúc Cây AST tối giản (`engine.go`):**
```go
type ExprAST interface {
    Eval(scope ValueScope) (formulaValue, error)
}

type ValueScope interface {
    Get(name string) (interface{}, bool)
}
```

**Các bước thực hiện:**
1. Trong `engine.go`:
   - Thêm interface `ExprAST` và các AST nodes cơ bản.
   - Hàm `compileExpression(formula string) (ExprAST, error)`: Trả về cây node AST.
   - `evalExpression(formula, vals)` chuyển thành gọi `ast, err := compileExpression(formula)` rồi `ast.Eval(mapScope(vals))`. Tương thích ngược 100% với các callers hiện có.
2. Trong `report_run_service.go`:
   - Trước vòng lặp `for _, rec := range records`:
     ```go
     compiledExprs := make([]ExprAST, len(tpl.Lines))
     for i, l := range tpl.Lines {
         if l.SourceKind == "expr" {
             ast, err := compileExpression(l.SourceCode)
             if err == nil {
                 compiledExprs[i] = ast
             }
         }
     }
     ```
   - Trong vòng lặp từng nhân viên:
     ```go
     case "expr":
         ast := compiledExprs[i]
         if ast == nil {
             full[i] = "0"
             cellRaw = 0.0
         } else {
             v, err := ast.Eval(scope)
             // set cell value...
         }
     ```
3. **Verify**:
   - Chạy unit tests: `go test ./internal/service -run "Test.*Formula.*|Test.*Report.*" -v`

---

### Task 4: Zero-Copy Layered Scope cho Biến Alias trong Report Runner (Ưu tiên #2)

**Mục tiêu**: Loại bỏ việc clone toàn bộ map `rec.ComputedValues` (100+ phần tử) cho mỗi nhân viên trong 3.000 dòng.

**Files:**
- Sửa: `Core System-backend/internal/service/report_run_service.go:150-160, 185-200`

**Thiết kế `LayeredScope`:**
```go
type layeredScope struct {
    computed models.ComputedValues
    aliases  map[string]interface{}
}

func (s *layeredScope) Get(name string) (interface{}, bool) {
    if s.aliases != nil {
        if v, ok := s.aliases[name]; ok {
            return v, true
        }
    }
    if s.computed != nil {
        if v, ok := s.computed[name]; ok {
            return v, true
        }
    }
    return nil, false
}
```

**Các bước thực hiện:**
1. Thay thế dòng cấp phát nặng:
   ```go
   // CŨ: vals := make(models.ComputedValues, len(rec.ComputedValues)+len(aliasLine))
   // MỚI: Chỉ tạo map chứa alias nếu template có alias, ngược lại nil
   var aliasVals map[string]interface{}
   if len(aliasLine) > 0 {
       aliasVals = make(map[string]interface{}, len(aliasLine))
   }
   scope := &layeredScope{computed: rec.ComputedValues, aliases: aliasVals}
   ```
2. Khi một dòng khai báo alias: Ghi thẳng vào `aliasVals[l.Alias] = cellRaw`.
3. Đánh giá: 3.000 nhân viên sẽ **không còn tạo 300.000 map entries thừa**, giảm 95% heap allocations.

---

### Task 5: Fast-path Formatter & Numeric Cache trên Frontend (Preview Optimization)

**Mục tiêu**: Tránh việc gọi regex `/0\.0/.test(numFmt)` và `numFmt.includes("%")` hàng chục nghìn lần trên main thread trình duyệt khi giải mã file `.xlsx`.

**Files:**
- Sửa: `Core System-frontend/components-page/tinh-luong/report-preview.ts:60-78`

**Các bước thực hiện:**
1. Thêm LRU / Map cache cho kết quả format rule của `numFmt`:
   ```typescript
   interface FormatRule {
     isPercent: boolean;
     hasDecimal: boolean;
   }
   const numFmtCache = new Map<string, FormatRule>();

   function getFormatRule(numFmt?: string): FormatRule {
     if (!numFmt) return { isPercent: false, hasDecimal: false };
     let rule = numFmtCache.get(numFmt);
     if (!rule) {
       rule = {
         isPercent: numFmt.includes("%"),
         hasDecimal: /0\.0/.test(numFmt),
       };
       if (numFmtCache.size < 200) numFmtCache.set(numFmt, rule);
     }
     return rule;
   }
   ```
2. Áp dụng `getFormatRule` vào hàm `fmtNumber`.
3. Đảm bảo toàn bộ 312 tests của Vitest vẫn pass 100%.

---

## IV. BẢNG TIẾN ĐỘ THI HÀNH & KẾ HOẠCH VERIFY

| Task | Hạng mục | Ưu tiên | Trạng thái | Lệnh kiểm thử nghiệm thu |
|:---:|:---|:---:|:---:|:---|
| **Task 1** | Batch Bank Account Queries (`tpbank` & `khac`) | P1 | `[x] Đã xong` | `go test ./internal/service -run "Test.*Bank.*"` — PASS |
| **Task 2** | Smart Wipe Surplus Rows (7 Generators) | P1 | `[x] Đã xong` | `go test ./internal/service` — PASS |
| **Task 3** | Pre-compiled AST Engine (`evalExpression`) | P2 | `[x] Đã xong` | `go test ./internal/service -run "TestCompileExpression.*"` — PASS |
| **Task 4** | Zero-copy Layered Scope cho Alias | P2 | `[x] Đã xong` | `go test ./internal/service -run "TestCompileExpression_LayeredScopeWithAliases"` — PASS |
| **Task 5** | Frontend Formatter Cache (`report-preview.ts`) | P3 | `[x] Đã xong` | `npx vitest run report-preview.test.ts` — 8/8 tests PASS |

---
*Tài liệu này được tạo làm căn cứ chuẩn xác theo kỹ năng `/plan` để thi hành Phase 2.*
