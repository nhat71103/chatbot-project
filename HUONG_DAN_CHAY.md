# Chatbot CNTT

## 🚀 Cài đặt nhanh

### 1. Clone repo
```bash
git clone https://github.com/USERNAME/chatbot-project.git
cd chatbot-project

2. Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate

3. Cài thư viện
pip install -r requirements.txt

4. Tạo database + admin
python init_data.py

5. Chạy server
uvicorn main:app --reload

🔐 Admin mặc định

Username: admin

Password: admin123
