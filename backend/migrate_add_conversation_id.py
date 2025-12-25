"""
Script migration để thêm cột conversation_id vào bảng chat_history
Chạy script này một lần để cập nhật database
"""
import os
import sys
import pyodbc

# Fix encoding cho Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Thông tin kết nối SQL Server
SERVER = "DESKTOP-JBUKRLP\\MSSQLSERVER01"
DATABASE = "ChatbotDB"

def migrate():
    try:
        # Kết nối với Windows Authentication
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Kiểm tra xem cột conversation_id đã tồn tại chưa
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'chat_history' AND COLUMN_NAME = 'conversation_id'
        """)
        
        if cursor.fetchone():
            print("[OK] Cot conversation_id da ton tai. Khong can migrate.")
        else:
            # Thêm cột conversation_id
            print("[...] Dang them cot conversation_id...")
            cursor.execute("""
                ALTER TABLE chat_history 
                ADD conversation_id INT NULL
            """)
            
            # Tạo index để tăng tốc truy vấn
            print("[...] Dang tao index...")
            try:
                cursor.execute("""
                    CREATE INDEX IX_chat_history_conversation_id 
                    ON chat_history(conversation_id)
                """)
            except Exception as idx_err:
                # Index có thể đã tồn tại
                print(f"[WARN] Khong the tao index (co the da ton tai): {idx_err}")
            
            conn.commit()
            print("[OK] Migration thanh cong! Da them cot conversation_id va index.")
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Loi migration: {e}")
        print("\nNeu loi, ban co the chay SQL thu cong trong SSMS:")
        print("ALTER TABLE chat_history ADD conversation_id INT NULL;")
        print("CREATE INDEX IX_chat_history_conversation_id ON chat_history(conversation_id);")

if __name__ == "__main__":
    print("=" * 50)
    print("Migration: Them conversation_id vao chat_history")
    print("=" * 50)
    migrate()

