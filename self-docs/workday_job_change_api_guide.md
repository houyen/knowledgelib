---
id: self-docs/workday_job_change_api_guide
canonical_question: "How to integrate Workday API for Job Change and Data Change business processes"
aliases:
  - "Workday Job Change API integration"
  - "Workday Submit_Change_Job SOAP Staffing"
  - "Workday Staffing Web Service v45.2"
  - "Tích hợp Workday API Job Change"
entity_type: how_to
domain: self-docs > integration > workday
last_verified: 2026-09-17
constraints:
  - "Submit_Change_Job requires SOAP Staffing Service v45.2+ with WS-Security UsernameToken, not REST"
---

# Hướng Dẫn Tích Hợp API Workday: Business Process Job Change & Data Change

---

## 1. Tổng Quan Kiến Trúc Workday API cho Job Change

Trong hệ thống Workday, **Job Change** (thuyên chuyển vị trí, thăng chức, đổi phòng ban, thay đổi địa điểm làm việc, v.v.) không được xử lý như một thao tác CRUD/Update dữ liệu thông thường. Thay vào đó, nó được quản lý như một **Business Process (BP)** trong **Business Process Framework (BPF)** của Workday.

### So sánh REST API vs SOAP Web Services (WWS)


| Tiêu chí                      | SOAP Web Services (`Staffing Service`)                                         | REST API (`/workers`, `/events`)                                      |
| ----------------------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| **Mục đích chính**            | Thực hiện Business Process phức tạp (`Submit_Change_Job`, `Hire`, `Terminate`) | Trích xuất dữ liệu, xem thông tin Worker, quản lý Event               |
| **Khả năng kích hoạt BP**     | **Đầy đủ** (Cấu hình BP, điều kiện validation, phê duyệt tự động/thủ công)     | **Hạn chế** (Chủ yếu read/query hoặc cập nhật custom object đơn giản) |
| **Giao thức &amp; Định dạng** | HTTPS / XML (WSDL)                                                             | HTTPS / JSON (OAuth 2.0)                                              |
| **Khuyên dùng khi**           | Cần khởi tạo hành động Change Job từ hệ thống bên ngoài                        | Cần lấy danh sách Worker hoặc theo dõi sự thay đổi (Change Data)      |


---

## 2. API Inbound: Khởi Tạo Change Job (`Submit_Change_Job`)

Để thực hiện một Job Change từ hệ thống bên ngoài vào Workday, phương thức chuẩn là gọi SOAP operation `**Submit_Change_Job**` thuộc **Staffing Web Service** (WSDL v45.2+).

### Endpoint Format

```text
https://{tenant_host}/ccx/service/{tenant_name}/Staffing/v45.2
```

### Cấu Trúc XML Payload (`Submit_Change_Job_Request`)

```xml
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3Cenv%3AEnvelope%20xmlns%3Aenv%3D%22http%3A%2F%2Fschemas.xmlsoap.org%2Fsoap%2Fenvelope%2F%22%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20xmlns%3Awd%3D%22urn%3Acom.workday%2Fbsvc%22%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%3Cenv%3AHeader%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%3Cwsse%3ASecurity%20xmlns%3Awsse%3D%22http%3A%2F%2Fdocs.oasis-open.org%2Fwss%2F2004%2F01%2Foasis-200401-wss-wssecurity-secext-1.0.xsd%22%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%3Cwsse%3AUsernameToken%3E]]
        [[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3Cwsse%3AUsername%3E]]ISU_Integration_User@{tenant}[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3C%2Fwsse%3AUsername%3E]]
        [[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3Cwsse%3APassword%3E]]Your_Password[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3C%2Fwsse%3APassword%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%3C%2Fwsse%3AUsernameToken%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%3C%2Fwsse%3ASecurity%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%3C%2Fenv%3AHeader%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%3Cenv%3ABody%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%3Cwd%3ASubmit_Change_Job_Request%20wd%3Aversion%3D%22v45.2%22%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%3Cwd%3ABusiness_Process_Parameters%3E]]
        [[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3Cwd%3AAuto_Complete%3E]]true[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3C%2Fwd%3AAuto_Complete%3E]]
        [[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3Cwd%3ARun_As_User_Workday_ID%3E]]WID_STRING[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3C%2Fwd%3ARun_As_User_Workday_ID%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%3C%2Fwd%3ABusiness_Process_Parameters%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%3Cwd%3AChange_Job_Data%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3C!--%201.%20%C4%90%E1%BB%8Bnh%20danh%20Worker%20c%E1%BA%A7n%20thay%20%C4%91%E1%BB%95i%20--%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3Cwd%3AWorker_Reference%3E]]
          [[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3Cwd%3AID%20wd%3Atype%3D%22Employee_ID%22%3E]]EMP100234[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3C%2Fwd%3AID%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3C%2Fwd%3AWorker_Reference%3E]]
        
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3C!--%202.%20Ng%C3%A0y%20c%C3%B3%20hi%E1%BB%87u%20l%E1%BB%B1c%20(Effective%20Date)%20--%3E]]
        [[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3Cwd%3AEffective_Date%3E]]2026-08-01[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3C%2Fwd%3AEffective_Date%3E]]
        
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3C!--%203.%20L%C3%BD%20do%20thay%20%C4%91%E1%BB%95i%20(Promotion%2C%20Demotion%2C%20Lateral%20Transfer...)%20--%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3Cwd%3AReason_Reference%3E]]
          [[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3Cwd%3AID%20wd%3Atype%3D%22General_Event_Subcategory_ID%22%3E]]PROMOTION_LATERAL[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3C%2Fwd%3AID%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3C%2Fwd%3AReason_Reference%3E]]
        
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3C!--%204.%20V%E1%BB%8B%20tr%C3%AD%2FCh%E1%BB%A9c%20danh%20m%E1%BB%9Bi%20--%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3Cwd%3APosition_Reference%3E]]
          [[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3Cwd%3AID%20wd%3Atype%3D%22Position_ID%22%3E]]P-09823[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3C%2Fwd%3AID%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3C%2Fwd%3APosition_Reference%3E]]
        
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3C!--%205.%20Ph%C3%A2n%20b%E1%BB%95%20T%E1%BB%95%20ch%E1%BB%A9c%20%26%20Cost%20Center%20m%E1%BB%9Bi%20--%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3Cwd%3AOrganization_Assignments_Data%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%20%20%3Cwd%3ACost_Center_Assignment_Data%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%20%20%20%20%3Cwd%3ACost_Center_Reference%3E]]
              [[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3Cwd%3AID%20wd%3Atype%3D%22Cost_Center_ID%22%3E]]CC-3001[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:inline-html:%3C%2Fwd%3AID%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%20%20%20%20%3C%2Fwd%3ACost_Center_Reference%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%20%20%3C%2Fwd%3ACost_Center_Assignment_Data%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%20%20%3C%2Fwd%3AOrganization_Assignments_Data%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%20%20%3C%2Fwd%3AChange_Job_Data%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%20%20%3C%2Fwd%3ASubmit_Change_Job_Request%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%20%20%3C%2Fenv%3ABody%3E]]
[[ORCA_RICH_MD:a0d0860471ee3e83bbd02157a1e87472:block-html:%3C%2Fenv%3AEnvelope%3E]]
```

---

## 3. API Outbound: Trích Xuất Dữ Liệu Thay Đổi (Data Change Job)

Khi cần đồng bộ dữ liệu thay đổi công việc từ Workday sang các hệ thống khác (ví dụ: SAP, ERP, Payroll), có 4 phương thức chính:

1. **Transaction Log Filter (`Get_Workers` SOAP)**:
 Sử dụng `Transaction_Log_Criteria_Data` với khoảng thời gian `Updated_From` và `Updated_Through`. Phương thức này chỉ trả về các bản ghi Worker có sự thay đổi trong khoảng thời gian chỉ định mà không phải quét toàn bộ tenant.
2. **PECI (Payroll Effective Change Interface)**:
 Chuẩn chuyên dụng cho tích hợp lương. PECI tự động gom nhóm các thay đổi liên quan đến công việc và đãi ngộ theo từng kỳ lương (Pay Period).
3. **WQL (Workday Query Language)**:
 Sử dụng truy vấn dạng SQL qua REST endpoint:
  ```sql
   SELECT worker, effectiveDate, position, costCenter 
   FROM workerJobChanges 
   WHERE effectiveDate >= '2026-07-01'
  ```
4. **RaaS (Report-as-a-Service)**:
 Tạo Custom Report trong Workday lọc theo `Job Change Event` và xuất bản dưới dạng Web Service endpoint (XML / JSON / CSV).

---

## 4. Các Lưu Ý Tối Quan Trọng Khi Triển Khai (Best Practices &amp; Pitfalls)

### Security &amp; Phân Quyền ISU

- **Integration System User (ISU)**: Mỗi hệ thống tích hợp phải có 1 tài khoản ISU riêng biệt.
- **Domain Security Policies**: ISU phải được phân quyền `Get` và `Put` đối với các Domain Policy liên quan đến **Staffing** và **Worker Data**.
- **Kích hoạt quyền**: Sau khi sửa đổi phân quyền cho ISU, bắt buộc phải chạy tác vụ `**Activate Pending Security Policy Changes**` trong Workday thì thay đổi mới có hiệu lực.

### Handling Effective Dating

- Mọi giao dịch trong Workday đều gắn liền với `Effective_Date`.
- Khi gọi API, nếu không truyền ngày hiệu lực, Workday sẽ tự động lấy ngày hiện tại. Điều này có thể dẫn đến việc ghi đè sai dữ liệu lịch sử hoặc dữ liệu tương lai.

### Rate Limits &amp; Performance

- Hạn chế tần suất gọi API ở mức **~10 requests/second** trên mỗi tenant để tránh lỗi HTTP `429 Rate Limit Exceeded`.
- Không sử dụng JSON RaaS cho các tập dữ liệu quá 50,000 dòng vì JSON RaaS không hỗ trợ phân trang natively (sử dụng XML RaaS hoặc WQL cho tập dữ liệu lớn).

---

## 5. Tham Khảo Nguồn Tài Liệu Chính Thức

- **Workday WWS Directory v45.2**: [https://community.workday.com/sites/default/files/file-hosting/productionapi/index.html](https://community.workday.com/sites/default/files/file-hosting/productionapi/index.html)
- **Workday SOAP API Reference**: [https://community-content.workday.com/en-us/public/products/platform-and-product-extensions/soap-api-reference.html](https://community-content.workday.com/en-us/public/products/platform-and-product-extensions/soap-api-reference.html)

