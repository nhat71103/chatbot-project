from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional
import jwt as pyjwt
from passlib.context import CryptContext

from db import User, get_session

# ================= JWT CONFIG =================
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 ngày

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter(prefix="/auth", tags=["auth"])

# ================= PASSWORD =================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# ================= MODELS =================
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ================= JWT =================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        return pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(401, "Token đã hết hạn")
    except pyjwt.JWTError:
        raise HTTPException(401, "Token không hợp lệ")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = verify_token(token)
    username = payload.get("sub")

    if not username:
        raise HTTPException(401)

    with get_session() as db:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(401)
        if not user.is_active:
            raise HTTPException(403, "Tài khoản đã bị khóa")
        return user


# ================= ROUTES =================
@router.post("/register", response_model=UserOut)
def register(data: UserRegister):
    with get_session() as db:
        if db.query(User).filter(User.username == data.username).first():
            raise HTTPException(400, "Username đã tồn tại")

        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(400, "Email đã tồn tại")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            is_active=True,
            is_admin=False,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat(),
        )


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    with get_session() as db:
        user = db.query(User).filter(User.username == form.username).first()

        if not user or not verify_password(form.password, user.hashed_password):
            raise HTTPException(401, "Sai tài khoản hoặc mật khẩu")

        if not user.is_active:
            raise HTTPException(403, "Tài khoản đã bị khóa")

        token = create_access_token({"sub": user.username})

        return Token(
            access_token=token,
            token_type="bearer",
            user=UserOut(
                id=user.id,
                username=user.username,
                email=user.email,
                created_at=user.created_at.isoformat(),
            ),
        )


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at.isoformat(),
    )
