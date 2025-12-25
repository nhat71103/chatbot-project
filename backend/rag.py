import re
from typing import List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
import urllib.parse

from sqlalchemy.orm import Session

from db import Knowledge, get_session


def tokenize(text: str) -> List[str]:
    """Tách từ đơn giản, bỏ ký tự đặc biệt và chuyển về lowercase."""
    text = text.lower()
    # Tách theo chữ cái và số, bỏ dấu câu
    return re.findall(r"[a-zA-Z0-9_À-ỹ]+", text)


def expand_keywords(tokens: List[str]) -> List[str]:
    """
    Mở rộng từ khóa với các từ đồng nghĩa/liên quan để tìm kiếm linh hoạt hơn.
    """
    synonyms = {
        "giỏi": ["tốt", "xuất sắc", "thành thạo", "giỏi giang"],
        "lợi thế": ["ưu điểm", "có ích", "hữu ích", "tốt", "có lợi"],
        "ảnh hưởng": ["tác động", "ảnh hưởng", "liên quan"],
        "cần thiết": ["quan trọng", "cần", "cần có", "cần dùng"],
        "không": ["không", "chưa", "thiếu"],
        "có": ["có", "sở hữu", "được"],
        "học": ["học", "nghiên cứu", "tìm hiểu"],
        "toán": ["toán học", "toán", "math"],
        "cntt": ["công nghệ thông tin", "cntt", "it", "tin học"],
    }
    
    expanded = set(tokens)
    for token in tokens:
        if token in synonyms:
            expanded.update(synonyms[token])
    return list(expanded)


def score_text(query_tokens: List[str], text: str) -> int:
    """
    Tính điểm similarity cải thiện giữa query và một đoạn text:
    - Mở rộng từ khóa với từ đồng nghĩa
    - +3 điểm nếu từ trùng chính xác
    - +2 điểm nếu từ đồng nghĩa trùng
    - +1 điểm nếu từ con nằm trong từ lớn hơn
    Bỏ qua stopwords rất phổ biến.
    """
    if not text:
        return 0

    stopwords = {"là", "và", "các", "một", "những", "khi", "để", "trong", "với", "thì", "có", "không", "gì"}
    text_lower = text.lower()
    score = 0
    
    # Mở rộng từ khóa với từ đồng nghĩa
    expanded_tokens = expand_keywords(query_tokens)

    for w in expanded_tokens:
        if w in stopwords and w not in query_tokens:  # Chỉ bỏ stopwords không có trong query gốc
            continue
        
        # Khớp chính xác theo từ
        if re.search(rf"\b{re.escape(w)}\b", text_lower):
            # Từ gốc trong query được điểm cao hơn
            if w in query_tokens:
                score += 3
            else:
                score += 2  # Từ đồng nghĩa
        elif w in text_lower:
            score += 1

    return score


def search_wikipedia(query: str, lang: str = "vi") -> Optional[str]:
    """
    Tìm kiếm thông tin từ Wikipedia API.
    Trả về đoạn text đầu tiên của bài viết phù hợp nhất.
    """
    try:
        # URL encode query
        query_encoded = urllib.parse.quote(query.replace(" ", "_"))
        
        # Thử tìm kiếm bài viết trực tiếp
        search_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{query_encoded}"
        response = requests.get(search_url, timeout=5, headers={"User-Agent": "Chatbot/1.0"})
        
        if response.status_code == 200:
            data = response.json()
            extract = data.get("extract", "")
            if extract:
                # Giới hạn độ dài để không quá dài
                if len(extract) > 600:
                    extract = extract[:600] + "..."
                return extract
        
        # Nếu không tìm thấy, thử tìm kiếm bằng API search
        search_api_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/search/{urllib.parse.quote(query)}"
        response = requests.get(search_api_url, params={"limit": 1}, timeout=5, headers={"User-Agent": "Chatbot/1.0"})
        
        if response.status_code == 200:
            results = response.json()
            pages = results.get("pages", [])
            if pages:
                page_title = pages[0].get("title", "")
                if page_title:
                    # Thử lại với title chính xác
                    title_encoded = urllib.parse.quote(page_title.replace(" ", "_"))
                    summary_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title_encoded}"
                    response2 = requests.get(summary_url, timeout=5, headers={"User-Agent": "Chatbot/1.0"})
                    if response2.status_code == 200:
                        data = response2.json()
                        extract = data.get("extract", "")
                        if extract:
                            if len(extract) > 600:
                                extract = extract[:600] + "..."
                            return extract
        
        # Nếu không tìm thấy tiếng Việt, thử tiếng Anh
        if lang == "vi":
            return search_wikipedia(query, lang="en")
        
        return None
    except Exception as e:
        # Nếu có lỗi, thử tiếng Anh nếu đang ở tiếng Việt
        if lang == "vi":
            try:
                return search_wikipedia(query, lang="en")
            except:
                return None
        return None


def search_web_simple(query: str) -> Optional[str]:
    """
    Tìm kiếm đơn giản trên web bằng cách tìm kiếm từ khóa chính.
    Trả về đoạn text ngắn từ kết quả tìm kiếm.
    """
    try:
        # Lấy từ khóa chính (bỏ stopwords, ưu tiên từ dài hơn)
        tokens = tokenize(query)
        stopwords = {"là", "và", "các", "một", "những", "khi", "để", "trong", "với", "thì", "có", "không", "gì", "không"}
        keywords = [t for t in tokens if t not in stopwords and len(t) > 2]
        
        # Sắp xếp theo độ dài (từ dài hơn = cụ thể hơn)
        keywords.sort(key=len, reverse=True)
        
        if not keywords:
            return None
        
        # Thử tìm trên Wikipedia với từ khóa đầu tiên (quan trọng nhất)
        # Ví dụ: "python là gì" -> tìm "python"
        main_keyword = keywords[0]
        result = search_wikipedia(main_keyword)
        if result:
            return result
        
        # Nếu không tìm thấy, thử với toàn bộ câu hỏi (loại bỏ dấu câu)
        query_clean = re.sub(r'[?.,!]', '', query).strip()
        if query_clean and query_clean != main_keyword:
            result = search_wikipedia(query_clean)
            if result:
                return result
        
        return None
    except Exception:
        return None


class RAGChatbot:
    """
    Chatbot RAG với khả năng tìm kiếm web:
    - Ưu tiên tìm trong database (kiến thức do admin quản lý)
    - Nếu không tìm thấy, tìm kiếm trên Wikipedia/web
    - Dùng keyword matching nâng cao để tìm document và đoạn phù hợp nhất
    """

    def __init__(self):
        # Dữ liệu KHÔNG còn lấy từ thư mục knowledge nữa.
        # Admin sẽ quản lý trực tiếp trong database (qua SSMS hoặc trang admin).
        pass

    def _search_best_paragraphs(
        self, question: str, max_paragraphs: int = 4, min_score: int = 3
    ) -> Tuple[List[str], List[str]]:
        """
        Tìm các đoạn phù hợp nhất từ nhiều document khác nhau.
        Chỉ lấy đoạn có điểm >= min_score để đảm bảo liên quan thực sự.
        """
        query_tokens = tokenize(question)
        if not query_tokens:
            return [], []

        # Lưu tất cả các đoạn kèm điểm số và tiêu đề document
        candidates = []

        with get_session() as db:  # type: Session
            docs = db.query(Knowledge).all()
            if not docs:
                return [], []

            for doc in docs:
                paragraphs = [
                    p for p in (doc.content or "").split("\n\n") if p.strip()
                ]
                if not paragraphs:
                    continue
                
                # Tính điểm cho từng đoạn
                for para in paragraphs:
                    score = score_text(query_tokens, para)
                    # Chỉ lấy đoạn có điểm >= min_score (liên quan thực sự)
                    if score >= min_score:
                        candidates.append({
                            "score": score,
                            "title": doc.title,
                            "para": para.strip()
                        })

        if not candidates:
            return [], []

        # Sắp xếp theo điểm giảm dần
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Tính điểm cao nhất để làm ngưỡng
        max_score = candidates[0]["score"]
        # Ngưỡng động: chỉ lấy đoạn có điểm >= 60% điểm cao nhất (tăng để chặt chẽ hơn)
        threshold = max(min_score, int(max_score * 0.6))
        
        # Lấy top N đoạn, nhưng đảm bảo có đoạn từ nhiều document khác nhau
        selected_paragraphs = []
        selected_titles = []
        seen_paras = set()
        doc_count = {}  # Đếm số đoạn từ mỗi document
        
        for cand in candidates:
            para_text = cand["para"]
            title = cand["title"]
            score = cand["score"]
            
            # Bỏ qua nếu đã có đoạn này rồi
            if para_text in seen_paras:
                continue
            
            # Chỉ lấy đoạn có điểm >= ngưỡng
            if score < threshold:
                continue
            
            # Giới hạn số đoạn từ mỗi document (tối đa 2 đoạn/document)
            doc_para_count = doc_count.get(title, 0)
            if doc_para_count >= 2:
                # Chỉ lấy thêm nếu điểm rất cao (>= 80% điểm cao nhất)
                if score < max_score * 0.8:
                    continue
            
            selected_paragraphs.append(para_text)
            selected_titles.append(title)
            seen_paras.add(para_text)
            doc_count[title] = doc_count.get(title, 0) + 1
            
            # Dừng khi đã có đủ đoạn
            if len(selected_paragraphs) >= max_paragraphs:
                break

        return selected_titles, selected_paragraphs

    def answer(self, question: str) -> str:
        question = question.strip()
        if not question:
            return "Bạn hãy nhập một câu hỏi cụ thể hơn để mình có thể hỗ trợ nhé."

        # Lấy từ khóa chính từ câu hỏi (bỏ stopwords)
        query_tokens = tokenize(question)
        stopwords = {"là", "và", "các", "một", "những", "khi", "để", "trong", "với", "thì", "có", "không", "gì", "không"}
        main_keywords = [t for t in query_tokens if t not in stopwords and len(t) > 2]
        
        # Bước 1: Tìm trong database trước (tăng ngưỡng điểm để chỉ lấy đoạn thực sự liên quan)
        titles, paragraphs = self._search_best_paragraphs(question, max_paragraphs=4, min_score=3)

        # Bước 2: Kiểm tra xem đoạn có thực sự liên quan không (phải chứa ít nhất 1 từ khóa chính)
        if paragraphs and main_keywords:
            relevant_paragraphs = []
            question_lower = question.lower()
            seen_paras = set()
            
            for para in paragraphs:
                para_stripped = para.strip()
                if not para_stripped or para_stripped in seen_paras:
                    continue
                
                para_lower = para_stripped.lower()
                
                # Kiểm tra xem đoạn có chứa từ khóa chính không
                has_main_keyword = any(kw in para_lower for kw in main_keywords)
                
                # Nếu không có từ khóa chính, bỏ qua (trừ khi điểm rất cao)
                if not has_main_keyword:
                    continue
                
                # Bỏ qua đoạn đầu nếu nó chỉ là tiêu đề giống với câu hỏi
                if len(relevant_paragraphs) == 0 and len(para_stripped) < 50:
                    if "?" in para_stripped or question_lower in para_lower or para_lower in question_lower:
                        if len(paragraphs) > 1:
                            continue
                
                relevant_paragraphs.append(para_stripped)
                seen_paras.add(para_stripped)
            
            if relevant_paragraphs:
                content = "\n\n".join(relevant_paragraphs)
                return content
        
        # Nếu không tìm thấy trong database
        return (
            "Xin lỗi, mình chưa tìm được thông tin phù hợp trong kiến thức hiện có.\n"
            "Bạn có thể thử hỏi lại chi tiết hơn, ví dụ: "
            "“HTML là gì?”, “Cú pháp SELECT trong SQL như thế nào?”, "
            "hoặc “Sự khác nhau giữa let và var trong JavaScript?”.\n\n"
            "💡 Nếu bạn muốn bot trả lời câu hỏi này, hãy thêm thông tin vào database qua trang admin nhé."
        )
