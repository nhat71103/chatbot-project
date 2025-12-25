from db import init_db, get_session, User, Knowledge
from auth import hash_password

def run():
    print("🔧 Initializing database...")
    init_db()

    with get_session() as db:
        # ===== ADMIN =====
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            print("✅ Created admin user")

        # ===== SAMPLE KNOWLEDGE =====
        if db.query(Knowledge).count() == 0:
            db.add_all([
                Knowledge(
                    title="Giới thiệu Chatbot",
                    content="Chatbot này hỗ trợ trả lời câu hỏi CNTT."
                ),
                Knowledge(
                    title="Cách sử dụng",
                    content="Bạn có thể hỏi tự nhiên bằng tiếng Việt."
                )
            ])
            print("✅ Added sample knowledge")

        db.commit()

    print("🎉 Database ready!")

if __name__ == "__main__":
    run()
