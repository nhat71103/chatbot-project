# 📋 Hướng dẫn chạy Chatbot sau khi cập nhật

## Bước 1: Cập nhật Database

Bạn có **2 cách** để cập nhật database:

### Cách 1: Chạy script tự động (Khuyến nghị)
```bash
cd backend
python migrate_add_conversation_id.py
```

### Cách 2: Chạy SQL thủ công trong SSMS
Mở SQL Server Management Studio và chạy:
```sql
USE ChatbotDB;
GO

-- Thêm cột conversation_id
ALTER TABLE chat_history ADD conversation_id INT NULL;
GO

-- Tạo index để tăng tốc
CREATE INDEX IX_chat_history_conversation_id ON chat_history(conversation_id);
GO
```

## Bước 2: Khởi động Backend

```bash
cd backend
uvicorn main:app --reload
```

Bạn sẽ thấy thông báo:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Bước 3: Mở trình duyệt

Mở trình duyệt và truy cập:
```
http://127.0.0.1:8000
```

## Bước 4: Test tính năng mới

1. **Gửi tin nhắn đầu tiên** → Tự động tạo cuộc hội thoại mới
2. **Gửi thêm vài tin nhắn** → Tất cả sẽ thuộc cùng một cuộc hội thoại
3. **Click nút "+" ở sidebar** → Tạo cuộc hội thoại mới
4. **Click vào một cuộc hội thoại ở sidebar** → Xem lại toàn bộ tin nhắn
5. **Tìm kiếm** → Nhập từ khóa vào ô tìm kiếm để tìm cuộc hội thoại
6. **Xóa cuộc hội thoại** → Click nút "×" để xóa

## ✨ Tính năng mới

- ✅ Mỗi cuộc hội thoại là một đoạn chat riêng biệt
- ✅ Sidebar hiển thị danh sách các cuộc hội thoại (giống ChatGPT)
- ✅ Click vào cuộc hội thoại để xem lại
- ✅ Tạo cuộc hội thoại mới bằng nút "+"
- ✅ Tìm kiếm cuộc hội thoại
- ✅ Xóa từng cuộc hội thoại
- ✅ Tự động giới hạn 50 cuộc hội thoại (xóa các cuộc cũ nhất)

## 🐛 Nếu gặp lỗi

1. **Lỗi kết nối database**: Kiểm tra SQL Server đã chạy chưa
2. **Lỗi migration**: Chạy SQL thủ công trong SSMS
3. **Lỗi frontend**: Kiểm tra backend đã chạy chưa (port 8000)

