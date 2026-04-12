Nhiệm vụ

So sánh: Thread vs Asyncio vs Selectors

|Tiêu chí|Thread|Asyncio|Selectors|
|-|-|-|-|
|Cơ chế|Mỗi client tạo 1 thread|1 thread + event loop + coroutine|Event-driven, 1 thread, quản lý nhiều socket|
|Sử dụng RAM|Cao|Trung bình|Thấp|
|CPU|Trung bình|Thấp|Thấp|
|Độ phức tạp code|Dễ hiểu, code tuyến tính|Cần async/await, code rõ ràng|Cần quản lý selector, code hơi “thuần”|
|Hiệu năng với nhiều client|Kém khi nhiều client (IO-bound)|Tốt với nhiều client|Tốt, nhẹ nhất, ít overhead|
|Ưu điểm|Code dễ viết, dễ debug|Dễ phát triển, event-driven|Nhẹ nhất, tiêu thụ tài nguyên thấp|
|Nhược điểm|Tốn RAM, mỗi thread có overhead|Cần học async/await|Code khó viết hơn asyncio, quản lý event thủ công|



•	Test:

o	5 client

o	20 client

\# Kết quả test



\## 5 client



\- Sử dụng `multi\_test.py` spawn 5 client → tất cả gửi tin nhắn “hello” thành công.  

\- Server log nhận tin nhắn ổn định, CPU và RAM ở mức trung bình.  



\## 20 client



\- Sử dụng `multi\_test.py` spawn 20 client → tất cả gửi tin nhắn “hello” thành công.  

\- Server log nhận 20 tin nhắn → CPU và RAM tăng nhưng vẫn thấp với Selectors.  

\- Output terminal:



PS D:\\Download\\UDM10-TCP-CHAT-main (4)> cd UDM10-TCP-CHAT-MAIn

PS D:\\Download\\UDM10-TCP-CHAT-main (4)\\UDM10-TCP-CHAT-MAIn> cd code

PS D:\\Download\\UDM10-TCP-CHAT-main (4)\\UDM10-TCP-CHAT-MAIn\\code> python multi\_test.py

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

b'hello'

PS D:\\Download\\UDM10-TCP-CHAT-main (4)\\UDM10-TCP-CHAT-MAIn\\code>











