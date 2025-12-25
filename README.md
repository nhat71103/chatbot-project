# 🤖 Web ChatBot Project

Dự án Web ChatBot gồm:
- Trang chủ cho người dùng chat với bot
- Trang Admin để quản lý kiến thức & tài khoản
- Backend FastAPI
- Frontend HTML / CSS / JavaScript
- Database SQLite (chạy local, dễ dùng cho nhóm)

---

## 📂 Cấu trúc thư mục

Web-ChatBot/
│
├── backend/
│ ├── main.py
│ ├── auth.py
│ ├── rag.py
│ ├── migrate_add_conversation_id.py
│ └── database.db
│
├── static/
│ ├── app.js
│ ├── admin.js
│ ├── index.css
│ └── admin.css
│
├── templates/
│ ├── index.html
│ └── admin.html
│
├── README.md
└── HUONG_DAN_CHAY.md

yaml
Sao chép mã

---

## ⚙️ Yêu cầu môi trường

- Python **3.10 trở lên**
- pip
- Git
- Trình duyệt (Chrome / Edge)

---

## 🚀 Hướng dẫn chạy project (CHI TIẾT)

### 1️⃣ Clone project từ GitHub

```bash
git clone https://github.com/nhat71103/chatbot-project.git
cd Web-ChatBot

2️⃣ Tạo & kích hoạt môi trường ảo (khuyến nghị)

python -m venv venv
venv\Scripts\activate

3️⃣ Cài thư viện backend
Nếu có requirements.txt:

pip install -r requirements.txt
Nếu chưa có:

pip install fastapi uvicorn sqlalchemy passlib[bcrypt] python-jose python-multipart

4️⃣ Chạy backend

cd backend
uvicorn main:app --reload

Khi thấy:
Uvicorn running on http://127.0.0.1:8000
→ Backend chạy thành công ✅

🌐 Đường dẫn sử dụng
🏠 Trang chủ (User Chat)
http://127.0.0.1:8000/

🔐 Trang Admin
http://127.0.0.1:8000/admin-page
