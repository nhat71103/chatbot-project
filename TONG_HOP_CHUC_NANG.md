# 📊 Tổng hợp Chức năng và Công nghệ Web Chatbot

## 🎯 CÁC CHỨC NĂNG CHÍNH

### 1. **Chatbot RAG (Retrieval-Augmented Generation)**
- ✅ Chat với người dùng về CNTT
- ✅ Tìm kiếm thông tin trong database kiến thức (do admin quản lý)
- ✅ Sử dụng keyword matching nâng cao để tìm đoạn phù hợp nhất
- ✅ Hỗ trợ tìm kiếm từ đồng nghĩa
- ✅ Tự động loại bỏ stopwords
- ✅ Tính điểm similarity để chọn đoạn tốt nhất

### 2. **Quản lý Hội thoại (Conversations)**
- ✅ Tạo cuộc hội thoại mới
- ✅ Lưu lịch sử chat theo từng cuộc hội thoại
- ✅ Xem lại các cuộc hội thoại cũ
- ✅ Tìm kiếm cuộc hội thoại
- ✅ Xóa cuộc hội thoại
- ✅ Ghim/Bỏ ghim cuộc hội thoại (hiển thị lên đầu)
- ✅ Hiển thị số tin nhắn và thời gian cuối cùng

### 3. **Xác thực Người dùng (Authentication)**
- ✅ Đăng ký tài khoản mới
- ✅ Đăng nhập/Đăng xuất
- ✅ JWT Token (hết hạn sau 30 ngày)
- ✅ Bảo mật mật khẩu với bcrypt
- ✅ Phân quyền Admin/User
- ✅ Khóa/Mở khóa tài khoản

### 4. **Trang Admin - Quản lý Kiến thức**
- ✅ Xem danh sách kiến thức
- ✅ Thêm kiến thức mới
- ✅ Sửa kiến thức
- ✅ Xóa kiến thức
- ✅ Giao diện tabbed (tabs) hiện đại

### 5. **Trang Admin - Quản lý Tài khoản**
- ✅ Xem danh sách tất cả tài khoản
- ✅ Sửa thông tin tài khoản (email, quyền admin, trạng thái)
- ✅ Đổi mật khẩu cho user
- ✅ Xóa tài khoản (không phải admin)
- ✅ Hiển thị badge Admin/Hoạt động/Đã khóa

### 6. **Giao diện Người dùng**
- ✅ Giao diện chat hiện đại, dark theme
- ✅ Sidebar với menu và lịch sử chat
- ✅ Responsive design
- ✅ Modal đăng nhập/đăng ký
- ✅ Tìm kiếm cuộc hội thoại
- ✅ Nhấn Enter để gửi tin nhắn/đăng nhập

### 7. **Tính năng Bổ sung**
- ✅ Lưu lịch sử chat vào database
- ✅ Tự động load lịch sử khi reload trang
- ✅ Retry mechanism khi backend chưa sẵn sàng
- ✅ Error handling tốt
- ✅ Loading states

---

## 🛠️ CÔNG NGHỆ SỬ DỤNG

### **Backend (Python)**
- **FastAPI** - Web framework hiện đại, nhanh
- **Uvicorn** - ASGI server để chạy FastAPI
- **SQLAlchemy** - ORM để làm việc với database
- **PyODBC** - Driver để kết nối SQL Server
- **PyJWT** - Tạo và xác thực JWT tokens
- **Passlib + Bcrypt** - Hash và verify mật khẩu
- **Requests** - HTTP client để tìm kiếm web
- **BeautifulSoup4** - Parse HTML từ web
- **Pydantic** - Data validation

### **Frontend**
- **HTML5** - Cấu trúc trang web
- **CSS3** - Styling (vanilla CSS, không dùng framework)
- **JavaScript (Vanilla)** - Logic xử lý, không dùng framework
- **Fetch API** - Gọi API từ frontend
- **LocalStorage** - Lưu JWT token

### **Database**
- **Microsoft SQL Server (MSSQL)** - Database chính
- **ODBC Driver 17 for SQL Server** - Driver kết nối

### **Kiến trúc**
- **RESTful API** - API design
- **JWT Authentication** - Xác thực stateless
- **RAG (Retrieval-Augmented Generation)** - Chatbot architecture
- **CORS** - Cross-Origin Resource Sharing

---

## 📁 CẤU TRÚC DỰ ÁN

```
Web-ChatBot/
├── backend/
│   ├── main.py          # FastAPI app, routes chính
│   ├── auth.py          # Authentication (login, register, JWT)
│   ├── db.py            # Database models và connection
│   ├── rag.py           # RAG Chatbot logic
│   ├── requirements.txt # Python dependencies
│   └── knowledge.db     # SQLite (không dùng nữa)
│
├── frontend/
│   ├── index.html       # Trang chat chính
│   ├── admin.html       # Trang admin
│   ├── index.css        # CSS cho trang chat
│   ├── admin.css        # CSS cho trang admin
│   ├── app.js           # JavaScript cho trang chat
│   └── admin.js         # JavaScript cho trang admin
│
└── HUONG_DAN_CHAY.md    # Hướng dẫn chạy
```

---

## 🔐 BẢO MẬT

- ✅ Mật khẩu được hash bằng bcrypt (12 rounds)
- ✅ JWT token với secret key
- ✅ Token hết hạn sau 30 ngày
- ✅ Phân quyền Admin/User
- ✅ Kiểm tra tài khoản active trước khi cho phép truy cập
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS được cấu hình

---

## 📊 DATABASE SCHEMA

### **Bảng `users`**
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `hashed_password`
- `is_admin` (Boolean)
- `is_active` (Boolean)
- `created_at` (DateTime)

### **Bảng `knowledge`**
- `id` (Primary Key)
- `title` (Unicode)
- `content` (UnicodeText)

### **Bảng `chat_history`**
- `id` (Primary Key)
- `conversation_id` (Integer, Indexed)
- `question` (UnicodeText)
- `answer` (UnicodeText)
- `created_at` (DateTime)
- `user_id` (Integer, Indexed)
- `is_pinned` (Boolean)

---

## 🚀 API ENDPOINTS

### **Authentication**
- `POST /auth/register` - Đăng ký
- `POST /auth/login` - Đăng nhập
- `GET /auth/me` - Lấy thông tin user hiện tại

### **Chat**
- `POST /chat` - Gửi tin nhắn, nhận câu trả lời

### **Conversations**
- `GET /chat/conversations` - Lấy danh sách cuộc hội thoại
- `GET /chat/conversations/{id}/messages` - Lấy tin nhắn trong cuộc hội thoại
- `POST /chat/conversations/{id}/pin` - Ghim cuộc hội thoại
- `POST /chat/conversations/{id}/unpin` - Bỏ ghim
- `DELETE /chat/conversations/{id}` - Xóa cuộc hội thoại

### **Admin - Knowledge**
- `GET /admin/knowledge` - Lấy danh sách kiến thức
- `POST /admin/knowledge` - Thêm kiến thức mới
- `PUT /admin/knowledge/{id}` - Sửa kiến thức
- `DELETE /admin/knowledge/{id}` - Xóa kiến thức

### **Admin - Users**
- `GET /admin/users` - Lấy danh sách users
- `PUT /admin/users/{id}` - Sửa user
- `POST /admin/users/{id}/password` - Đổi mật khẩu
- `DELETE /admin/users/{id}` - Xóa user

### **Frontend**
- `GET /` - Trang chat chính
- `GET /admin-page` - Trang admin
- `GET /static/*` - Static files (CSS, JS)

### **Utility (Tạm thời)**
- `GET /create-admin` - Tạo admin user (xóa sau khi dùng xong)

---

## 📝 GHI CHÚ

- Web hỗ trợ cả **guest mode** (không đăng nhập) và **user mode** (có đăng nhập)
- Guest mode: Chat được nhưng không lưu lịch sử
- User mode: Chat và lưu lịch sử vào database
- Admin có thể quản lý kiến thức và users qua trang `/admin-page`

