"""
Services for interacting with large language models (LLMs).
"""

from app.core.config import settings
from groq import Groq

"""
Service xử lý LLM calls (Groq)
"""
from groq import Groq
from app.core.config import settings

class LLMService:
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        print("   ✓ Groq API client initialized")
    
    def generate_answer(
        self, 
        query: str, 
        context: str, 
        model: str = None
    ) -> str:
        """
        Create answers from LLM model
        
        Args:
            query: User's question
            context: Context documents
            model: Groq model to use (optional)
            
        Returns:
            Answer from LLM model
        """
        if model is None:
            model = settings.DEFAULT_LLM_MODEL
        
        system_prompt = """Bạn là trợ lý AI chuyên tư vấn Luật Giao thông đường bộ Việt Nam.

NHIỆM VỤ:
- Trả lời câu hỏi của người dùng dựa CHÍNH XÁC trên các quy định pháp luật được cung cấp
- Trích dẫn rõ ràng Điều, Khoản, Điểm liên quan
- Giải thích dễ hiểu, có ví dụ cụ thể nếu cần
- Nếu thông tin không đủ hoặc không có trong quy định, hãy nói rõ

ĐỊNH DẠNG TRẢ LỜI:
1. Trả lời trực tiếp câu hỏi
2. Trích dẫn cụ thể: [Điều X, Khoản Y]
3. Giải thích chi tiết nếu cần
4. Lưu ý bổ sung (nếu có)

LƯU Ý:
- KHÔNG bịa đặt thông tin không có trong quy định
- KHÔNG trả lời về các vấn đề ngoài luật giao thông
- Sử dụng ngôn ngữ lịch sự, chuyên nghiệp"""

        user_prompt = f"""CÁC QUY ĐỊNH LIÊN QUAN:

{context}

---

CÂU HỎI CỦA NGƯỜI DÙNG:
{query}

Hãy trả lời câu hỏi dựa trên các quy định trên."""

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                top_p=settings.LLM_TOP_P
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"Error while calling Groq API: {str(e)}")

# Singleton instance
llm_service = LLMService()