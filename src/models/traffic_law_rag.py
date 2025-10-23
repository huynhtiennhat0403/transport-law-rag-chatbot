"""
RAG System cho Luật Giao Thông Việt Nam
Sử dụng: ChromaDB + BGE-M3 + Groq (Llama 3.1)
"""

import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
import os
from typing import List, Dict, Tuple
from pathlib import Path
class TrafficLawRAG:
    def __init__(
        self, 
        chromadb_path: str,
        collection_name: str = "law_traffic_vietnam",
        api_key: str = None
    ):
        """
        Khởi tạo RAG system
        
        Args:
            chromadb_path: Đường dẫn đến ChromaDB
            collection_name: Tên collection
            api_key: Groq API key (hoặc set biến môi trường GROQ_API_KEY)
        """
        print("🚀 Đang khởi tạo Traffic Law RAG System...")
        
        # 1. Load ChromaDB
        print("📂 Đang load ChromaDB...")
        self.client = chromadb.PersistentClient(path=chromadb_path)
        self.collection = self.client.get_collection(name = collection_name)
        print(f"   ✓ Đã load collection '{collection_name}'")
        
        # 2. Load Embedding Model
        print("🔄 Đang load embedding model (BAAI/bge-m3)...")
        self.embedding_model = SentenceTransformer('BAAI/bge-m3')
        print("   ✓ Đã load embedding model")
        
        # 3. Initialize Groq Client
        print("🤖 Đang kết nối Groq API...")
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key is None:
                raise ValueError(
                    "Vui lòng cung cấp GROQ_API_KEY!\n"
                    "Cách 1: TrafficLawRAG(api_key='gsk_...')\n"
                    "Cách 2: Set biến môi trường GROQ_API_KEY"
                )
        
        self.llm_client = Groq(api_key=api_key)
        print("   ✓ Đã kết nối Groq API")
        
        print("\n✅ Khởi tạo thành công! Sẵn sàng trả lời câu hỏi.\n")
    
    def retrieve(self, query: str, n_results: int = 5) -> Dict:
        """
        Tìm kiếm các chunks liên quan nhất
        
        Args:
            query: Câu hỏi người dùng
            n_results: Số lượng chunks trả về
            
        Returns:
            Dict chứa documents, metadatas, distances
        """
        # Encode query
        query_embedding = self.embedding_model.encode(
            query, 
            normalize_embeddings=True
        )
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        
        return results
    
    def format_context(self, results: Dict) -> str:
        """
        Format các chunks thành context cho LLM
        
        Args:
            results: Kết quả từ ChromaDB
            
        Returns:
            String context đã được format
        """
        contexts = []
        
        for i, (doc, metadata) in enumerate(zip(
            results['documents'][0], 
            results['metadatas'][0]
        ), 1):
            ref = metadata.get('full_reference', 'N/A')
            contexts.append(f"[Trích dẫn {i}] {ref}\nNội dung: {doc}")
        
        return "\n\n".join(contexts)
    
    def generate_answer(self, query: str, context: str, model: str = "llama-3.1-70b-versatile") -> str:
        """
        Tạo câu trả lời từ LLM
        
        Args:
            query: Câu hỏi người dùng
            context: Context từ retrieved chunks
            model: Model Groq (mặc định: llama-3.1-70b-versatile)
                   Các option khác: mixtral-8x7b-32768, llama-3.1-8b-instant
            
        Returns:
            Câu trả lời từ LLM
        """
        
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
            response = self.llm_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Giảm để tăng tính chính xác
                max_tokens=1500,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"❌ Lỗi khi gọi Groq API: {str(e)}"
    
    def query(
        self, 
        question: str, 
        n_results: int = 5, 
        show_sources: bool = True,
        model: str = "llama-3.3-70b-versatile"
    ) -> Tuple[str, Dict]:
        """
        Truy vấn end-to-end: Retrieve → Generate
        
        Args:
            question: Câu hỏi người dùng
            n_results: Số chunks retrieve
            show_sources: Có hiển thị nguồn trích dẫn không
            model: Model Groq sử dụng
            
        Returns:
            Tuple (answer, retrieval_results)
        """
        
        print("="*80)
        print(f"❓ CÂU HỎI: {question}")
        print("="*80)
        
        # Step 1: Retrieve
        print("\n🔍 Đang tìm kiếm quy định liên quan...")
        results = self.retrieve(question, n_results)
        print(f"   ✓ Tìm thấy {len(results['documents'][0])} quy định liên quan")
        
        # Step 2: Format context
        context = self.format_context(results)
        
        # Step 3: Generate answer
        print("🤖 Đang tạo câu trả lời...\n")
        answer = self.generate_answer(question, context, model)
        
        # Display answer
        print("="*80)
        print("💡 TRẢ LỜI:")
        print("="*80)
        print(answer)
        print()
        
        # Display sources
        if show_sources:
            print("="*80)
            print("📚 NGUỒN TRÍCH DẪN:")
            print("="*80)
            for i, (metadata, distance) in enumerate(zip(
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                ref = metadata.get('full_reference', 'N/A')
                score = 1 - distance  # Convert distance to similarity score
                print(f"[{i}] {ref} (độ liên quan: {score:.2%})")
            print()
        
        return answer, results
    
    def batch_query(self, questions: List[str], **kwargs):
        """
        Truy vấn nhiều câu hỏi
        
        Args:
            questions: List các câu hỏi
            **kwargs: Các tham số cho query()
        """
        for i, q in enumerate(questions, 1):
            print(f"\n\n{'='*80}")
            print(f"CÂU HỎI {i}/{len(questions)}")
            print(f"{'='*80}")
            
            self.query(q, **kwargs)
            
            if i < len(questions):
                print("\n" + "─"*80)


# ============================================
# DEMO USAGE
# ============================================

def main():
    """Demo script"""

    PROJECT_ROOT = Path(__file__).parent.parent.parent

    CHROMADB_PATH = PROJECT_ROOT / "data" / "law_chroma_db"

    rag = TrafficLawRAG(chromadb_path=CHROMADB_PATH.as_posix())
    
    # Test với nhiều câu hỏi
    test_questions = [
        "Điều kiện để được lái xe ô tô là gì?",
        "Người đi xe máy có bắt buộc đội mũ bảo hiểm không?",
        "Tốc độ tối đa trong khu dân cư là bao nhiêu?",
        "Uống rượu bia có được lái xe không?",
        "Xe ô tô có bắt buộc phải thắt dây an toàn không?"
    ]
    
    # Chạy batch query
    rag.batch_query(
        test_questions,
        n_results=5,
        show_sources=True,
        model = "llama-3.3-70b-versatile"
    )
    
    print("\n" + "="*80)
    print("✅ HOÀN THÀNH DEMO!")
    print("="*80)
    
    # Interactive mode
    print("\n💬 Chế độ tương tác (gõ 'quit' để thoát):\n")
    while True:
        question = input("❓ Câu hỏi của bạn: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Tạm biệt!")
            break
        
        if not question:
            continue
        
        rag.query(question, show_sources=True)
        print()


if __name__ == "__main__":
    main()