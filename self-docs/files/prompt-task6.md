---
id: self-docs/files/prompt-task6
canonical_question: 'Technical guide and specification: Brief thi hành — Task 6'
aliases:
- Brief thi hành — Task 6
- prompt Task6 060826
entity_type: how_to
domain: self-docs > files
last_verified: 2026-09-17
---

# Brief thi hành — Task 6 (PLAN 040826-Core System-template-on-giatbh-engine)

**Đây là phiên THI HÀNH theo brief đã chốt, không phải phiên thiết kế.** Xác minh bằng lệnh thật,
dừng và hỏi nếu code thật khác brief hoặc gặp quyết định thiết kế chưa chốt.

## Bối cảnh

PLAN: `llmwiki/wiki/sources/draft/040826-Core System-template-on-giatbh-engine-PLAN.md`, mục "### Task 6
— Mở lại UI + đóng 3 lỗ UX" (đọc nguyên văn 8 bước trong đó — brief này bổ sung dòng/file thật đã
grep lại ở 060826, không thay thế PLAN). **Chạy SAU Task 5** (PLAN nói rõ: "Chỉ làm bước này SAU Task
0-4" — Task 5 đã dọn dữ liệu demo + nghiệm thu enforce hoạt động đúng; mở UI trước khi Task 5 xong là
mời HR tạo cấu hình trên nền chưa kiểm chứng).

Nếu Task 5 CHƯA xong khi brief này được giao — DỪNG, báo lại, không tự làm Task 6 trước.

## Đối tượng sửa — đã grep xác nhận thật (060826)

```
Core System-frontend/components-page/tinh-luong/TinhLuongExcel.tsx
  :57   const SALARY_STRUCTURE_FEATURE_VISIBLE = false;
  :4276 <PayrollTemplateModal allComponents={data.allComponents} onClose=... onSaved=... />
  :4283 <EmployeeTemplateAssignPanel templates={templatesForAssign} onClose=... />
  :4290 <AllAssignmentsModal onClose=... />
  :4483,4491,4501  3 nút ribbon gated bởi `sheet.id === FORMULAS_LIST_SHEET_ID && canManageSalaryComponents && SALARY_STRUCTURE_FEATURE_VISIBLE`

Core System-frontend/components-page/tinh-luong/PayrollTemplateModal.tsx (172 dòng)
  :20  type FormState = { id?: string; name: string; description: string; isDefault: boolean; componentCodes: string[] }
  :30  const [enforceEnabled, setEnforceEnabled] = useState<boolean | null>(null);
  :32  api.getTemplateEnforceStatus().then((r) => setEnforceEnabled(r.enabled)).catch(() => setEnforceEnabled(null));
  :47  setForm({ name: "", description: "", isDefault: false, componentCodes: [] });  // isDefault set nhưng KHÔNG có checkbox
  :107-110  banner 2 nhánh, nhánh "TẮT" nói "Xem trước tác động bằng nút \"Xem trước tác động\"" — NÚT ĐÓ ĐÃ BỊ XOÁ 270727
  :118  {t.name}{t.isDefault ? " (mặc định)" : ""}  — chỉ HIỂN THỊ, không SỬA được isDefault ở đâu

Core System-frontend/components-page/tinh-luong/EmployeeTemplateAssignPanel.tsx (140 dòng)
  :24  const [enforceEnabled, setEnforceEnabled] = useState<boolean | null>(null);  // banner CÓ ở đây
  :93-94  banner 2 nhánh (khác nội dung PayrollTemplateModal, không nói tới nút đã xoá — không cần sửa)
  :107-111  hiển thị lịch sử (history.map) — KHÔNG có nút sửa/xoá từng dòng

Core System-frontend/components-page/tinh-luong/AllAssignmentsModal.tsx (108 dòng)
  KHÔNG có banner nào (đối chiếu 2 modal trên đều có — bất đối xứng, PLAN mục bước 6 yêu cầu thêm)

Core System-frontend/lib/api/config.ts
  :252  updateEmployeeTemplateAssignment(id, data)   — 0 điểm gọi trong 3 file .tsx trên
  :256  deleteEmployeeTemplateAssignment(id)          — 0 điểm gọi
  :260  resolveEmployeeTemplate(employeeId, asOf?)    — 0 điểm gọi

Core System-frontend/lib/api/types.ts
  EmployeePayrollTemplate { id, employeeId, templateId, effectiveFrom, effectiveTo?, createdBy,
    updatedBy, createdAt, updatedAt, employeeCode?, employeeName?, templateName? }
```

## Các bước

### Bước 1 — mở UI (chỉ sau khi xác nhận Task 5 đã xong thật)

Đổi dòng 57: `const SALARY_STRUCTURE_FEATURE_VISIBLE = true;`. PLAN gợi ý cân nhắc thay bằng cờ đọc
từ `template-enforce-status` — KHÔNG làm việc này ở Task 6 (mở rộng phạm vi không cần thiết, hằng số
tĩnh đủ dùng vì chỉ dev/thai bật cờ enforce cục bộ; nếu muốn cờ động, đó là quyết định riêng cần hỏi).

### Bước 2 — sửa banner trỏ nút đã xoá (`PayrollTemplateModal.tsx:107-110`)

**Quyết định đã chốt: KHÔNG dựng lại modal "Xem trước tác động"** (dù PLAN khuyến nghị dựng lại) —
lý do: nó cần nhập `salaries` (map mã NV → lương cơ bản) mà UI hiện tại không có chỗ nhập tay hợp lý
(dữ liệu 3273-12044 NV/kỳ, không thể gõ tay); dựng đúng UI cho việc này là một tính năng riêng, không
phải "1 bước trong Task 6". Bỏ câu nhắc nút đó khỏi banner, thay bằng câu trung lập.

Thay 3 dòng 106-110 hiện có (2 nhánh) bằng khuôn 3 nhánh dùng hàm thuần (bắt buộc theo bước 3 PLAN —
"Sửa fail-unsafe của banner"), gộp làm 1 lần luôn cả bước 2 và bước 3 của PLAN (cùng đoạn code, tách
riêng sẽ phải sửa lại đúng chỗ 2 lần):

Tạo file mới `Core System-frontend/lib/enforce-banner.ts`:
```ts
// 060826 (Task 6, PLAN 040826): hàm thuần resolve banner enforce — 3 trạng thái rõ ràng, KHÔNG
// coi API lỗi (status=null) là "đang TẮT" (fail-unsafe cũ). Test được không cần jsdom, khuôn
// lib/permission-resolve.ts.
export type EnforceBanner = "on" | "off" | "unknown";

export function resolveEnforceBanner(
  status: { enabled: boolean; healthy: boolean } | null,
): EnforceBanner {
  if (status === null) return "unknown";
  if (!status.healthy) return "unknown";
  return status.enabled ? "on" : "off";
}
```

Sửa `PayrollTemplateModal.tsx`:
- Đổi `const [enforceEnabled, setEnforceEnabled] = useState<boolean | null>(null);` thành
  `const [enforceStatus, setEnforceStatus] = useState<{ enabled: boolean; healthy: boolean } | null>(null);`
- Đổi `useEffect` gọi `getTemplateEnforceStatus()` để lưu NGUYÊN response (không chỉ `.enabled`) vào
  `enforceStatus`. BE (`internal/handler/payroll_template_enforce_status_handler.go:19-26`) ĐÃ trả
  `{enabled, healthy, reason?}` — chỉ cần sửa type TS `getTemplateEnforceStatus()` trong
  `lib/api/config.ts` (hiện khai `Promise<{ enabled: boolean }>`, dòng ~213) thêm `healthy: boolean`
  vào type trả về, KHÔNG cần sửa BE.
- Thay khối banner (dòng 106-110) bằng:
```tsx
const banner = resolveEnforceBanner(enforceStatus);
const BANNER_TEXT: Record<"on" | "off" | "unknown", string> = {
  on: "Cấu hình enforce ĐANG BẬT — cấu trúc lương bạn tạo/sửa ở đây SẼ ảnh hưởng bảng lương thật ngay khi có nhân viên được gán.",
  off: "Cấu hình enforce đang TẮT — lưu ở đây chỉ là cấu hình, chưa ảnh hưởng bảng lương thật. Liên hệ đội kỹ thuật/vận hành khi cần bật thật (không tự bật được trong màn hình này).",
  unknown: "CHƯA XÁC ĐỊNH được trạng thái enforce (không đọc được cấu hình hệ thống). Đừng dựa vào màn hình này để kết luận lương có bị ảnh hưởng hay không — hỏi đội kỹ thuật trước khi sửa.",
};
```
```tsx
<div style={{ padding: "8px 18px", fontSize: "12.5px",
  color: banner === "on" ? "#a15c00" : banner === "unknown" ? "#8a5700" : "#1e5a96",
  background: banner === "on" ? "#fff6e5" : banner === "unknown" ? "#fff8e1" : "#eaf1fb",
  borderBottom: "1px solid var(--tl-divider)" }}>
  {BANNER_TEXT[banner]}
</div>
```

### Bước 3 — thêm control cho `isDefault`

Thêm checkbox trong form (ngay sau ô "Mô tả", trước danh sách cột):
```tsx
<label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12.5px", marginBottom: "10px" }}>
  <input type="checkbox" checked={form.isDefault} onChange={(e) => setForm({ ...form, isDefault: e.target.checked })} />
  Đặt làm cấu trúc mặc định (gợi ý khi gán cho nhân viên chưa có cấu trúc)
</label>
```
Ngữ nghĩa "chỉ một template là default": kiểm BE `PayrollTemplateService.Create`/`Update` — nếu BE
hiện KHÔNG có guard này (grep `is_default` trong `internal/service/payroll_template_service.go`), để
NGUYÊN không guard ở lần này (nhiều `isDefault=true` cùng lúc không gây sai số liệu — `templates.find
(t => t.isDefault)` ở `EmployeeTemplateAssignPanel.tsx:56` chỉ lấy PHẦN TỬ ĐẦU khớp, không phải lỗi
nghiêm trọng). Nếu muốn guard "chỉ 1 default", đó là mở rộng phạm vi — hỏi trước khi làm.

### Bước 4 — thêm đường sửa/xoá assignment

Sửa `EmployeeTemplateAssignPanel.tsx`, khối hiển thị lịch sử (dòng 107-111) — thêm 2 nút Sửa/Xoá mỗi
dòng:
```tsx
{(history ?? []).map((h) => (
  <div key={h.id} style={{ fontSize: "12.5px", padding: "4px 0", borderBottom: "1px solid var(--tl-divider)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
    <span>{h.templateName} — từ {h.effectiveFrom} {h.effectiveTo ? `đến ${h.effectiveTo}` : "(còn hiệu lực)"}</span>
    <span style={{ display: "flex", gap: "6px" }}>
      <button onClick={() => startEditAssignment(h)} style={{ fontSize: "11px", border: "none", background: "transparent", color: "#1e5a96", cursor: "pointer" }}>Sửa</button>
      <button onClick={() => deleteAssignment(h.id)} style={{ fontSize: "11px", border: "none", background: "transparent", color: "#c5221f", cursor: "pointer" }}>Xoá</button>
    </span>
  </div>
))}
```
Thêm state + hàm xử lý (đặt cạnh `assign` hiện có, dòng 65-84):
```tsx
const [editingId, setEditingId] = useState<string | null>(null);

const startEditAssignment = (h: EmployeePayrollTemplate) => {
  setEditingId(h.id);
  setNewTemplateId(h.templateId);
  setNewFrom(h.effectiveFrom);
  setNewTo(h.effectiveTo ?? "");
};

const deleteAssignment = async (id: string) => {
  if (!selected) return;
  if (!confirm("Xoá bản ghi gán này?")) return;
  await api.deleteEmployeeTemplateAssignment(id);
  const data = await api.getEmployeeTemplateAssignments(selected.id);
  setHistory((data || []).sort((a, b) => b.effectiveFrom.localeCompare(a.effectiveFrom)));
};
```
Sửa hàm `assign` hiện có (dòng 65-84) để rẽ nhánh theo `editingId`:
```tsx
const assign = async () => {
  if (!selected) return;
  if (!newTemplateId) { setFormError("Chọn cấu trúc lương"); return; }
  if (!newFrom) { setFormError("Chọn ngày hiệu lực từ"); return; }
  setSubmitting(true);
  setFormError(null);
  try {
    if (editingId) {
      await api.updateEmployeeTemplateAssignment(editingId, {
        templateId: newTemplateId, effectiveFrom: newFrom, effectiveTo: newTo || undefined,
      });
    } else {
      await api.createEmployeeTemplateAssignment({
        employeeId: selected.id, templateId: newTemplateId,
        effectiveFrom: newFrom, effectiveTo: newTo || undefined,
      });
    }
    const data = await api.getEmployeeTemplateAssignments(selected.id);
    setHistory((data || []).sort((a, b) => b.effectiveFrom.localeCompare(a.effectiveFrom)));
    setNewTemplateId(""); setNewFrom(""); setNewTo(""); setEditingId(null);
  } catch (e) {
    setFormError(e instanceof Error ? e.message : String(e));
  } finally {
    setSubmitting(false);
  }
};
```
Đổi label nút submit (dòng 134) theo `editingId`: `{submitting ? "Đang lưu..." : editingId ? "Cập nhật" : "Gán"}`.

Hàm `resolveEmployeeTemplate` (config.ts:260) — KHÔNG có chỗ dùng rõ ràng trong phạm vi Task 6 (nó
trả về template đang hiệu lực tại 1 ngày, dùng cho việc HIỂN THỊ "hiện tại NV này đang dùng template
nào" — có thể thêm 1 dòng hiển thị nhỏ trong panel, nhưng KHÔNG bắt buộc theo PLAN gốc). Nếu muốn
dùng, thêm 1 dòng đơn giản sau khi `pickEmployee` — không bắt buộc, ghi vào tài liệu nếu bỏ qua.

### Bước 5 — banner cho `AllAssignmentsModal.tsx`

Copy khuôn banner đã sửa ở bước 2 (dùng chung `resolveEnforceBanner`/`BANNER_TEXT`, import từ
`lib/enforce-banner.ts`) — đọc file `AllAssignmentsModal.tsx` để tìm đúng chỗ chèn (đầu modal, trước
danh sách), thêm `useEffect` gọi `getTemplateEnforceStatus()` giống 2 modal kia.

### Bước 6 — test hàm thuần

Tạo `Core System-frontend/lib/enforce-banner.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { resolveEnforceBanner } from "./enforce-banner";

describe("resolveEnforceBanner", () => {
  it("null (API lỗi) -> unknown, KHÔNG được là off", () => {
    expect(resolveEnforceBanner(null)).toBe("unknown");
  });
  it("healthy=false (bảng thiếu dù enforce bật) -> unknown", () => {
    expect(resolveEnforceBanner({ enabled: true, healthy: false })).toBe("unknown");
  });
  it("enabled=true, healthy=true -> on", () => {
    expect(resolveEnforceBanner({ enabled: true, healthy: true })).toBe("on");
  });
  it("enabled=false, healthy=true -> off", () => {
    expect(resolveEnforceBanner({ enabled: false, healthy: true })).toBe("off");
  });
});
```

### Bước 7 — verify

`npx tsc --noEmit -p tsconfig.json 2>&1 | grep -v "^e2e/\|^playwright.config"` → 0 lỗi.
`npx eslint components-page/tinh-luong/TinhLuongExcel.tsx components-page/tinh-luong/PayrollTemplateModal.tsx components-page/tinh-luong/EmployeeTemplateAssignPanel.tsx components-page/tinh-luong/AllAssignmentsModal.tsx lib/enforce-banner.ts` → 0 error.
`npx vitest run lib/enforce-banner.test.ts` → 4/4 PASS.
`npx next build` → xác nhận build sản xuất KHÔNG hỏng thêm gì so với baseline đã biết (lỗi
`DevToolkit.tsx`/`devLogin` là pre-existing, không phải của Task 6 — xác nhận bằng `git stash` nếu
nghi ngờ, đừng tự sửa file đó).

**Kiểm tay trình duyệt bắt buộc** (đúng ràng buộc lặp lại nhiều đợt của dự án — build xanh không thay
thế được bước này, bug `overrideRefs=null` 280726 là bằng chứng): bật dev server thật, mở modal Cấu
trúc lương, xác nhận banner đúng 3 trạng thái (tắt server backend giữa chừng để giả lập `unknown`),
thêm 2 bản ghi gán cho 1 NV rồi Sửa 1 bản ghi + Xoá 1 bản ghi, xác nhận UI cập nhật đúng ngay không
cần F5. KHÔNG có browser tool trong môi trường agent — nếu đang chạy trong môi trường không có browser
tool, dừng ở bước build/test, ghi rõ debt "chưa kiểm tay" và báo lại cho người dùng tự kiểm (đúng như
Task 3/Report v1 đã làm).

## Ràng buộc tuyệt đối

- KHÔNG dựng lại modal "Xem trước tác động" (quyết định đã chốt ở brief này).
- KHÔNG thêm guard "chỉ 1 template default" trừ khi được hỏi và xác nhận.
- KHÔNG sửa `SALARY_STRUCTURE_FEATURE_VISIBLE` trước khi xác nhận Task 5 đã xong.

## DỪNG và hỏi khi

- Task 5 chưa xong.
- BE có guard `is_default` khác dự đoán (ví dụ tự động bỏ default của template khác khi tạo mới) —
  báo lại cách hành xử thật trước khi thêm checkbox, để UI không tạo cảm giác sai.

## Định nghĩa xong

1. UI mở lại, banner 3 trạng thái đúng cả 3 nhánh, không còn nhắc nút đã xoá.
2. `isDefault` có checkbox, gửi đúng giá trị lên API (xác nhận bằng Network tab hoặc log BE).
3. Sửa/xoá assignment hoạt động qua UI, không cần SQL tay.
4. `AllAssignmentsModal` có banner, khớp 2 modal kia.
5. 4 test `enforce-banner.test.ts` PASS.
6. tsc/eslint sạch, kiểm tay trình duyệt đã làm (hoặc ghi rõ debt nếu môi trường không cho phép).
7. Cập nhật PLAN cột TT Task 6 → `xong`, xoá L8/L9 khỏi bảng lỗi `00-START-HERE.md`, dòng nhật ký
   `CLAUDE.md`.
8. Commit (FE only) — hỏi xác nhận trước khi commit, không tự push.
