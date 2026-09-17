# KnowledgeLib Memory Index (self-docs)
> **Generated:** 2026-09-17 | **Active Units:** 1 | **Mode:** High-Density Working Memory

Use this index to recall verified internal decisions, runbooks, and gotchas before querying external LLM.

### Operations & Runbooks
- **`self-docs/workday_job_change_api_guide`** (how_to): How to integrate Workday API for Job Change and Data Change business processes [Aliases: Workday Job Change API integration, Workday Submit_Change_Job SOAP Staffing, Workday Staffing Web Service v45.2]
  - ⚠️ *Constraint:* Submit_Change_Job requires SOAP Staffing Service v45.2+ with WS-Security UsernameToken, not REST
  - 📌 *Core:* Trong hệ thống Workday, **Job Change** (thuyên chuyển vị trí, thăng chức, đổi phòng ban, thay đổi địa điểm làm việc, v.v.) không được xử lý như một thao tác CRUD/Update dữ liệu thông thường. Thay vào đó, nó được quản lý như một **Business Process (BP
