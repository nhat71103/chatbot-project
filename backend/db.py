from __future__ import annotations
from contextlib import contextmanager
from typing import Generator
import os
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    UnicodeText,
    DateTime,
    Boolean,
    create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# =========================
# DATABASE CONFIG
# =========================
SERVER_NAME = "DESKTOP-JBUKRLP\\MSSQLSERVER01"
DATABASE_NAME = "ChatbotDB"

DATABASE_URL = (
    f"mssql+pyodbc://@{SERVER_NAME}/{DATABASE_NAME}"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&Trusted_Connection=yes"
    "&TrustServerCertificate=yes"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =========================
# MODELS
# =========================

class Knowledge(Base):
    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True)
    title = Column(Unicode(255))
    content = Column(UnicodeText(), nullable=False)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, index=True)
    question = Column(UnicodeText(), nullable=False)
    answer = Column(UnicodeText(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, index=True)
    is_pinned = Column(Boolean, default=False, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(Unicode(50), unique=True, index=True)
    email = Column(Unicode(100), unique=True)
    hashed_password = Column(Unicode(255))

    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

# =========================
# INIT DB
# =========================
def init_db():
    Base.metadata.create_all(bind=engine)

# =========================
# SESSION
# =========================
@contextmanager
def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
