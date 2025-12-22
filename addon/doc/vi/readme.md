### CloudVision

tiện ích bổ sung này cho phép bạn nhận mô tả hình ảnh bằng cách sử dụng trí tuệ nhân tạo.

Tiện ích hoạt động thông qua Google Chrome OCR, PiccyBot và Mathpix dành cho các công thức và phương trình toán học.

Trước đây có hỗ trợ Microsoft và Be My Eyes, nhưng Microsoft đã chặn quyền truy cập, còn Be My Eyes đã bắt đầu thực hiện các biện pháp bảo vệ để ngăn chặn việc sử dụng API không chính thức.

Cài đặt của tiện ích nằm trong NVDA menu, parameters, CloudVision Settings.

Các phím tắt:

* NVDA+CTRL+I - Nhận mô tả của navigator object (đối tượng điều hướng) hoặc file jpg/png nếu nó đang được chọn trong Windows Explorer. Nếu nhấn nhanh hai lần kết quả sẽ hiển thị trong trình xem ảo (virtual viewer), bạn có thể đọc bằng các phím mũi tên, chọn, sao chép, v.v;
* NVDA+ALT+F - Nhận dạng toàn màn hình;
* NVDA+ALT+W - Nhận dạng cửa sổ đang hoạt động;
* NVDA+ALT+C - Nhận dạng hình ảnh từ bộ nhớ tạm;
* NVDA+ALT+A - Đặt câu hỏi cho bot về hình ảnh được nhận dạng gần nhất;
* Phân tích đối tượng với Mathpix (dành cho công thức toán học) - Tổ hợp phím này chưa được gán, bạn có thể tự gán trong mục Các cử chỉ nhập liệu (Input gestures);
* Sao chép kết quả nhận dạng gần nhất vào bộ nhớ tạm - Tổ hợp phím này chưa được gán, bạn có thể tự gán trong mục Các cử chỉ nhập liệu (Input gestures);
* NVDA+ALT+P - Chuyển đổi các gợi ý (prompts) (ngắn gọn, chi tiết hoặc tùy chỉnh của riêng bạn).

## Tích hợp Mathpix

Để sử dụng Mathpix cho việc nhận dạng các công thức và phương trình toán học:

1. Lấy mã API từ trang web [mathpix.com](https://mathpix.com)
2. Nhập mã API của bạn vào hộp thoại cài đặt CloudVision
3. Bật tùy chọn Sử dụng Mathpix để nhận dạng công thức toán học

Bạn có thể sử dụng Mathpix theo hai cách:

* Khi được kích hoạt trong phần cài đặt, Mathpix sẽ được sử dụng song song với các dịch vụ nhận dạng khác trong quá trình nhận dạng tiêu chuẩn (NVDA+CTRL+I)
* Bạn có thể gán phím tắt cho lệnh Analyze object with Mathpix trong hộp thoại Cử chỉ nhập liệu (Input gestures) của NVDA để sử dụng trực tiếp Mathpix
