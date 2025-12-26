from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

import auth
from auth import router as auth_router, verify_token
from db import Knowledge, get_session, init_db, User, ChatHistory
from rag import RAGChatbot
from sqlalchemy import func, case

app = FastAPI()

# ===== AUTH =====
app.include_router(auth_router)

# ===== FRONTEND =====
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== DB =====
init_db()
bot = RAGChatbot()

# =======================
# HELPERS
# =======================

def get_current_user(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    username = payload.get("sub")

    with get_session() as db:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None

        # ✅ TRẢ DICT – KHÔNG TRẢ ORM
        return {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "is_active": user.is_active
        }


def require_admin(authorization: str | None):
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(401, "Chưa đăng nhập")
    if not user["is_admin"]:
        raise HTTPException(403, "Không có quyền admin")
    if not user["is_active"]:
        raise HTTPException(403, "Tài khoản bị khóa")
    return user

# =======================
# CHAT
# =======================

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


@app.post("/chat")
def chat(req: ChatRequest, authorization: str | None = Header(default=None)):
    answer = bot.answer(req.message)
    user = get_current_user(authorization)

    if not user or not user["is_active"]:
        return {"answer": answer, "guest": True}

    with get_session() as db:
        conv_id = req.conversation_id
        if conv_id is None:
            max_id = db.query(func.max(ChatHistory.conversation_id)).scalar()
            conv_id = (max_id or 0) + 1

        db.add(ChatHistory(
            conversation_id=conv_id,
            question=req.message,
            answer=answer,
            user_id=user["id"]
        ))
        db.commit()

    return {"answer": answer, "conversation_id": conv_id, "guest": False}

# =======================
# CONVERSATIONS
# =======================

@app.get("/chat/conversations")
def conversations(authorization: str | None = Header(default=None)):
    user = get_current_user(authorization)
    if not user:
        return []

    with get_session() as db:
        pinned = func.max(case((ChatHistory.is_pinned == True, 1), else_=0))
        rows = (
            db.query(
                ChatHistory.conversation_id,
                func.min(ChatHistory.question),
                func.max(ChatHistory.created_at),
                func.count(),
                pinned
            )
            .filter(ChatHistory.user_id == user["id"])
            .group_by(ChatHistory.conversation_id)
            .order_by(pinned.desc(), func.max(ChatHistory.created_at).desc())
            .all()
        )

        return [
            {
                "id": r[0],
                "title": (r[1][:50] + "...") if r[1] else "Cuộc hội thoại",
                "last_message_at": r[2].isoformat(),
                "message_count": r[3],
                "is_pinned": bool(r[4])
            }
            for r in rows
        ]

# =======================
# PIN
# =======================

@app.post("/chat/conversations/{cid}/pin")
def pin(cid: int, authorization: str | None = Header(default=None)):
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(401)

    with get_session() as db:
        result = db.query(ChatHistory).filter(
            ChatHistory.conversation_id == cid,
            ChatHistory.user_id == user["id"]
        ).update({"is_pinned": True})
        
        if result == 0:
            raise HTTPException(404, "Conversation not found")
        
        db.commit()

    return {"ok": True}


@app.post("/chat/conversations/{cid}/unpin")
def unpin(cid: int, authorization: str | None = Header(default=None)):
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(401)

    with get_session() as db:
        result = db.query(ChatHistory).filter(
            ChatHistory.conversation_id == cid,
            ChatHistory.user_id == user["id"]
        ).update({"is_pinned": False})
        
        if result == 0:
            raise HTTPException(404, "Conversation not found")
        
        db.commit()

    return {"ok": True}

# =======================
# GET MESSAGES FOR CONVERSATION
# =======================

@app.get("/chat/conversations/{cid}/messages")
def get_conversation_messages(cid: int, authorization: str | None = Header(default=None)):
    try:
        user = get_current_user(authorization)
        if not user:
            raise HTTPException(401, "Chưa đăng nhập")
        
        with get_session() as db:
            messages = db.query(ChatHistory).filter(
                ChatHistory.conversation_id == cid,
                ChatHistory.user_id == user["id"]
            ).order_by(ChatHistory.created_at.asc()).all()
            
            if not messages:
                raise HTTPException(404, "Conversation not found")
            
            result = []
            for m in messages:
                try:
                    created_at_str = ""
                    if m.created_at:
                        try:
                            created_at_str = m.created_at.isoformat()
                        except:
                            created_at_str = str(m.created_at)
                    
                    result.append({
                        "question": str(m.question) if m.question else "",
                        "answer": str(m.answer) if m.answer else "",
                        "created_at": created_at_str
                    })
                except Exception:
                    continue
            
            return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Lỗi server: {str(e)}")

# =======================
# DELETE CONVERSATION
# =======================

@app.delete("/chat/conversations/{cid}")
def delete_conversation(cid: int, authorization: str | None = Header(default=None)):
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(401, "Chưa đăng nhập")
    
    with get_session() as db:
        # Xóa tất cả messages trong conversation này của user
        result = db.query(ChatHistory).filter(
            ChatHistory.conversation_id == cid,
            ChatHistory.user_id == user["id"]
        ).delete()
        
        if result == 0:
            raise HTTPException(404, "Conversation not found")
        
        db.commit()
    
    return {"ok": True}

# =======================
# ADMIN – USERS
# =======================

@app.get("/admin/users")
def admin_users(authorization: str | None = Header(default=None)):
    require_admin(authorization)

    with get_session() as db:
        users = db.query(User).all()
        return [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "is_admin": u.is_admin,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat()
            }
            for u in users
        ]


class UserUpdate(BaseModel):
    email: str | None = None
    is_admin: bool | None = None
    is_active: bool | None = None


@app.put("/admin/users/{uid}")
def update_user(uid: int, payload: UserUpdate, authorization: str | None = Header(default=None)):
    require_admin(authorization)

    with get_session() as db:
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            raise HTTPException(404, "User not found")

        for k, v in payload.model_dump(exclude_none=True).items():
            setattr(user, k, v)
        
        db.commit()
        return {"ok": True}


class PasswordChange(BaseModel):
    new_password: str


@app.post("/admin/users/{uid}/password")
def change_password(uid: int, payload: PasswordChange, authorization: str | None = Header(default=None)):
    require_admin(authorization)

    with get_session() as db:
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            raise HTTPException(404, "User not found")

        user.hashed_password = auth.hash_password(payload.new_password)
        db.commit()
        return {"ok": True}


@app.delete("/admin/users/{uid}")
def delete_user(uid: int, authorization: str | None = Header(default=None)):
    require_admin(authorization)

    with get_session() as db:
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            raise HTTPException(404)

        db.delete(user)
        return {"ok": True}

# =======================
# ADMIN – KNOWLEDGE
# =======================

class KnowledgeCreate(BaseModel):
    title: str
    content: str
    keywords: str | None = None

class KnowledgeUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    keywords: str | None = None

@app.get("/admin/knowledge")
def get_knowledge(authorization: str | None = Header(default=None)):
    require_admin(authorization)
    with get_session() as db:
        items = db.query(Knowledge).all()
        return [
            {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "keywords": item.keywords
            }
            for item in items
        ]


@app.post("/admin/knowledge")
def create_knowledge(payload: KnowledgeCreate, authorization: str | None = Header(default=None)):
    require_admin(authorization)
    with get_session() as db:
        item = Knowledge(
            title=payload.title,
            content=payload.content,
            keywords=payload.keywords
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return {
            "id": item.id,
            "title": item.title,
            "content": item.content
        }

@app.put("/admin/knowledge/{kid}")
def update_knowledge(kid: int, payload: KnowledgeUpdate, authorization: str | None = Header(default=None)):
    require_admin(authorization)
    with get_session() as db:
        item = db.query(Knowledge).filter(Knowledge.id == kid).first()
        if not item:
            raise HTTPException(404, "Knowledge not found")
        
        if payload.title is not None:
            item.title = payload.title
        if payload.keywords is not None:
            item.keywords = payload.keywords
        
        db.commit()
        db.refresh(item)
        return {
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "keywords": item.keywords
        }


@app.delete("/admin/knowledge/{kid}")
def delete_knowledge(kid: int, authorization: str | None = Header(default=None)):
    require_admin(authorization)
    with get_session() as db:
        item = db.query(Knowledge).filter(Knowledge.id == kid).first()
        if not item:
            raise HTTPException(404, "Knowledge not found")
        
        db.delete(item)
        db.commit()
        return {"ok": True}

# =======================
# FRONTEND
# =======================

@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/admin-page")
def admin_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))

# =======================
# CREATE ADMIN ENDPOINT (Tạm thời - xóa sau khi tạo xong admin user)
# =======================

@app.get("/create-admin")
def create_admin_endpoint(username: str = "admin", password: str = "admin123", email: str = "admin@example.com"):
    """Endpoint tạm thời để tạo admin user - XÓA SAU KHI TẠO XONG"""
    try:
        import bcrypt
        
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        with get_session() as db:
            user = db.query(User).filter(User.username == username).first()
            
            if user:
                user.is_admin = True
                user.is_active = True
                user.hashed_password = hashed_password
                if email:
                    user.email = email
                db.commit()
                db.refresh(user)
                return {
                    "success": True, 
                    "message": f"Đã cập nhật user '{username}' thành admin"
                }
            else:
                user = User(
                    username=username,
                    email=email,
                    hashed_password=hashed_password,
                    is_admin=True,
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                return {
                    "success": True, 
                    "message": f"Đã tạo admin user '{username}' thành công"
                }
    except Exception as e:
        return {"success": False, "error": str(e)}


if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
