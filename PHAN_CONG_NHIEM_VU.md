# 👥 Phân công Nhiệm vụ cho 3 người

## 📋 Tổng quan dự án

**Web Chatbot CNTT** với các module chính:
- Authentication & Authorization
- Chatbot RAG với Knowledge Base
- Conversation Management
- Admin Panel (Knowledge & User Management)

---

## 🎯 CÁCH PHÂN CHIA (3 người)

### **NGƯỜI 1: Backend - Authentication & User Management**
**Phần trách nhiệm:**
- ✅ Module `auth.py` (Đăng ký, Đăng nhập, JWT)
- ✅ Module `db.py` (Database models, connection)
- ✅ API endpoints: `/auth/*`, `/admin/users/*`
- ✅ Bảo mật: Password hashing (bcrypt), JWT tokens
- ✅ Phân quyền Admin/User

**Có thể trình bày:**
- "Em phụ trách phần Authentication và User Management. Em đã xây dựng hệ thống đăng ký/đăng nhập với JWT, hash mật khẩu bằng bcrypt, và quản lý phân quyền admin/user. Em cũng thiết kế database schema cho bảng users và xây dựng các API endpoints để admin có thể quản lý tài khoản."

**Files liên quan:**
- `backend/auth.py`
- `backend/db.py` (phần User model)
- `backend/main.py` (phần admin/users endpoints)

**Công nghệ sử dụng:**
- FastAPI, PyJWT, Bcrypt, Passlib, SQLAlchemy

---

### **NGƯỜI 2: Backend - Chatbot RAG & Knowledge Base**
**Phần trách nhiệm:**
- ✅ Module `rag.py` (RAG Chatbot logic)
- ✅ API endpoint: `/chat`
- ✅ Keyword matching, similarity scoring
- ✅ Tìm kiếm trong Knowledge Base
- ✅ API endpoints: `/admin/knowledge/*`

**Có thể trình bày:**
- "Em phụ trách phần Chatbot RAG và Knowledge Base. Em đã xây dựng hệ thống chatbot sử dụng RAG (Retrieval-Augmented Generation), với thuật toán keyword matching nâng cao, tính điểm similarity để tìm đoạn phù hợp nhất. Em cũng xây dựng các API để admin quản lý knowledge base."

**Files liên quan:**
- `backend/rag.py`
- `backend/main.py` (phần `/chat` và `/admin/knowledge/*`)
- `backend/db.py` (phần Knowledge model)

**Công nghệ sử dụng:**
- FastAPI, SQLAlchemy, Regex, BeautifulSoup, Requests

---

### **NGƯỜI 3: Frontend - Chat Interface & Conversation Management**
**Phần trách nhiệm:**
- ✅ Trang chat chính (`index.html`, `index.css`, `app.js`)
- ✅ Giao diện chat, sidebar, lịch sử
- ✅ Quản lý conversations (xem, tạo, xóa, ghim)
- ✅ Tìm kiếm conversations
- ✅ Authentication UI (modal đăng nhập/đăng ký)
- ✅ API endpoints: `/chat/conversations/*`

**Có thể trình bày:**
- "Em phụ trách phần Frontend cho trang chat chính. Em đã xây dựng giao diện chat hiện đại với sidebar hiển thị lịch sử, tính năng quản lý conversations (tạo mới, xem lại, xóa, ghim), tìm kiếm conversations, và modal đăng nhập/đăng ký. Em cũng tích hợp với các API backend để lưu và tải lịch sử chat."

**Files liên quan:**
- `frontend/index.html`
- `frontend/index.css`
- `frontend/app.js`
- `backend/main.py` (phần `/chat/conversations/*`)

**Công nghệ sử dụng:**
- HTML5, CSS3, Vanilla JavaScript, Fetch API, LocalStorage

---

## 📊 BẢNG PHÂN CÔNG CHI TIẾT

| Người | Module chính | Files | API Endpoints | Database Tables |
|-------|-------------|-------|---------------|-----------------|
| **Người 1** | Auth & Users | `auth.py`, `db.py` (User), `main.py` (users) | `/auth/*`, `/admin/users/*` | `users` |
| **Người 2** | RAG & Knowledge | `rag.py`, `main.py` (chat, knowledge) | `/chat`, `/admin/knowledge/*` | `knowledge`, `chat_history` |
| **Người 3** | Chat Frontend | `index.html/css/js`, `main.py` (conversations) | `/chat/conversations/*` | `chat_history` |

---

## 🎤 GỢI Ý TRÌNH BÀY

### **Người 1 - Authentication & User Management:**
```
"Xin chào, em là [Tên], em phụ trách phần Authentication và User Management.

1. Về Authentication:
   - Em đã xây dựng hệ thống đăng ký/đăng nhập với JWT tokens
   - Mật khẩu được hash bằng bcrypt với 12 rounds để bảo mật
   - Token có thời hạn 30 ngày

2. Về User Management:
   - Thiết kế database schema cho bảng users với các trường: username, email, hashed_password, is_admin, is_active
   - Xây dựng API endpoints để admin quản lý users: xem danh sách, sửa thông tin, đổi mật khẩu, xóa user
   - Phân quyền: Admin có thể quản lý tất cả users, user thường chỉ quản lý được chính mình

3. Công nghệ sử dụng:
   - FastAPI cho REST API
   - PyJWT cho JWT tokens
   - Bcrypt/Passlib cho password hashing
   - SQLAlchemy ORM cho database

Em xin cảm ơn!"
```

### **Người 2 - Chatbot RAG & Knowledge Base:**
```
"Xin chào, em là [Tên], em phụ trách phần Chatbot RAG và Knowledge Base.

1. Về Chatbot RAG:
   - Em đã xây dựng hệ thống chatbot sử dụng RAG (Retrieval-Augmented Generation)
   - Khi user hỏi, hệ thống sẽ tìm kiếm trong knowledge base để tìm đoạn phù hợp nhất
   - Sử dụng thuật toán keyword matching nâng cao với tính điểm similarity

2. Về thuật toán:
   - Tokenize câu hỏi, loại bỏ stopwords
   - Mở rộng từ khóa với từ đồng nghĩa
   - Tính điểm cho từng đoạn: +3 điểm nếu từ trùng chính xác, +2 điểm nếu từ đồng nghĩa
   - Chọn top 4 đoạn có điểm cao nhất từ nhiều documents khác nhau

3. Về Knowledge Base:
   - Xây dựng API CRUD để admin quản lý knowledge
   - Knowledge được lưu trong database với title và content
   - Content được chia thành các đoạn (paragraphs) để tìm kiếm chính xác hơn

4. Công nghệ sử dụng:
   - FastAPI, SQLAlchemy
   - Regex cho text processing
   - BeautifulSoup, Requests (dự phòng cho web search)

Em xin cảm ơn!"
```

### **Người 3 - Chat Frontend:**
```
"Xin chào, em là [Tên], em phụ trách phần Frontend cho trang chat chính.

1. Về giao diện:
   - Xây dựng giao diện chat hiện đại với dark theme
   - Sidebar bên trái hiển thị menu và lịch sử conversations
   - Khu vực chat chính ở giữa với input ở dưới

2. Về Conversation Management:
   - Hiển thị danh sách conversations với thông tin: tiêu đề, số tin nhắn, thời gian
   - Tính năng ghim conversations để hiển thị lên đầu
   - Tìm kiếm conversations theo từ khóa
   - Tạo conversation mới, xóa conversation
   - Click vào conversation để xem lại toàn bộ tin nhắn

3. Về Authentication UI:
   - Modal đăng nhập/đăng ký
   - Lưu JWT token vào localStorage
   - Tự động load lịch sử khi đã đăng nhập
   - Hiển thị hint đăng nhập cho guest users

4. Về UX:
   - Nhấn Enter để gửi tin nhắn/đăng nhập
   - Loading states khi đang tải
   - Error handling và retry mechanism
   - Responsive design

5. Công nghệ sử dụng:
   - HTML5, CSS3, Vanilla JavaScript
   - Fetch API để gọi backend
   - LocalStorage để lưu token

Em xin cảm ơn!"
```

---

## 🔄 LUỒNG HOẠT ĐỘNG

```
User truy cập → Backend (Routing)
    ↓
Đăng nhập → Người 1 (Auth)
    ↓
Chat → Người 2 (RAG) + Người 3 (Frontend)
    ↓
Lưu lịch sử → Người 3 (Conversations)
    ↓
Admin quản lý → Người 1/2 (APIs)
```

---

## 💡 LƯU Ý KHI TRÌNH BÀY

1. **Mỗi người nên:**
   - Giới thiệu phần của mình (2-3 phút)
   - Demo các tính năng chính
   - Giải thích công nghệ sử dụng
   - Trả lời câu hỏi về phần của mình

2. **Thứ tự trình bày gợi ý:**
   - Người 1 (Authentication - Nền tảng)
   - Người 2 (Chatbot - Core feature)
   - Người 3 (Frontend - User experience)

3. **Chuẩn bị:**
   - Demo live trên máy
   - Chuẩn bị slides (nếu cần)
   - Sẵn sàng trả lời câu hỏi về code

---

## ✅ CHECKLIST TRƯỚC KHI TRÌNH BÀY

- [ ] Đã test tất cả tính năng của phần mình
- [ ] Đã chuẩn bị demo
- [ ] Đã đọc và hiểu code của phần mình
- [ ] Đã chuẩn bị giải thích về công nghệ
- [ ] Đã test integration với các phần khác

---

## 🎯 KẾT LUẬN

Với cách phân chia này:
- ✅ Mỗi người có phần rõ ràng, độc lập
- ✅ Có thể trình bày riêng biệt
- ✅ Khối lượng công việc tương đối cân bằng
- ✅ Dễ dàng giải thích và demo

**Chúc các bạn trình bày thành công! 🚀**

