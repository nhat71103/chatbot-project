import re
from typing import List, Set
from sqlalchemy.orm import Session
from db import Knowledge, get_session


# ======================
# TEXT PROCESSING
# ======================

def normalize_text(text: str) -> str:
    return text.lower().strip()


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_À-ỹ]+", normalize_text(text))


STOPWORDS = {
    "là", "và", "các", "một", "những", "khi", "để",
    "trong", "với", "thì", "có", "không", "gì", "nên",
    "bị", "cho", "về", "ở"
}


# ======================
# INTENT DETECTION
# ======================

def detect_intents(tokens: List[str]) -> Set[str]:
    intents = set()

    for w in tokens:
        if w in {"login", "đăng", "nhập"}:
            intents.add("login_issue")
        if w in {"báo", "cáo", "report"}:
            intents.add("report")
        if w in {"lỗi", "sai", "lệch"}:
            intents.add("report_error")
        if w in {"chậm", "lag", "treo"}:
            intents.add("performance")

    return intents


# ======================
# SCORING
# ======================

def score_knowledge(tokens: List[str], doc: Knowledge, intents: Set[str]) -> int:
    score = 0

    title = normalize_text(doc.title or "")
    content = normalize_text(doc.content or "")
    keywords = normalize_text(doc.keywords or "")
    intent = normalize_text(doc.intent or "")

    # keyword / title / content
    for w in tokens:
        if w in keywords:
            score += 5
        if w in title:
            score += 3
        if w in content:
            score += 2

    # intent match (ưu tiên cao)
    if intent and intent in intents:
        score += 8

    return score


# ======================
# RAG CHATBOT
# ======================

class RAGChatbot:

    def answer(self, question: str) -> str:
        question = normalize_text(question)
        if not question:
            return "Bạn hãy nhập câu hỏi cụ thể hơn nhé."

        tokens = [
            t for t in tokenize(question)
            if t not in STOPWORDS and len(t) > 2
        ]

        if not tokens:
            return "Bạn có thể hỏi rõ hơn về vấn đề báo cáo web không?"

        intents = detect_intents(tokens)

        best_score = 0
        best_answer: str | None = None

        # 🔒 LẤY DATA TRONG SESSION
        with get_session() as db:  # type: Session
            docs = db.query(Knowledge).all()

            for doc in docs:
                score = score_knowledge(tokens, doc, intents)
                if score > best_score:
                    best_score = score
                    best_answer = doc.content  # ⭐ COPY TEXT

        # ❌ Không đủ tin cậy → hỏi lại
        if not best_answer or best_score < 8:
            return (
                "Mình chưa xác định rõ vấn đề bạn đang gặp.\n"
                "💡 Bạn đang hỏi về **lỗi, báo cáo hay hiệu năng** của hệ thống?"
            )

        # ✅ CHỈ RETURN STRING
        return best_answer.strip()
