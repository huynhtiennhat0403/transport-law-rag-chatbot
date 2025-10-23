"""
RAG Service - Orchestrate retrieval and generation
"""
from typing import Dict, List, Tuple
from app.core.chromadb_client import get_collection
from app.core.embedding_model import get_embedding_model
from app.services.llm_service import llm_service
from app.models.schemas import Source

class RAGService:
    def __init__(self):
        """Intialize RAG service"""
        self.collection = get_collection()
        self.embedding_model = get_embedding_model()
        print("✅ RAG Service initialized")
    
    def retrieve(self, query: str, n_results: int = 5) -> Dict:
        """
        Looling for the most related chunks 
        
        Args:
            query: User's question
            n_results: Number of chunks returned
            
        Returns:
            Dict contains documents, metadatas, distances
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
        Format chunks into context for LLM
        
        Args:
            results: Results from ChromaDB
            
        Returns:
            Formated string context 
        """
        contexts = []
        
        for i, (doc, metadata) in enumerate(zip(
            results['documents'][0], 
            results['metadatas'][0]
        ), 1):
            ref = metadata.get('full_reference', 'N/A')
            contexts.append(f"[Trích dẫn {i}] {ref}\nNội dung: {doc}")
        
        return "\n\n".join(contexts)
    
    def extract_sources(self, results: Dict) -> List[Source]:
        """
        Extract information from retrieval results
        
        Args:
            results: Results from ChromaDB
            
        Returns:
            List of Source objects
        """
        sources = []
        
        for doc, metadata, distance in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            source = Source(
                reference=metadata.get('full_reference', 'N/A'),
                content=doc[:200] + "..." if len(doc) > 200 else doc,
                relevance_score=round(1 - distance, 4)  # Convert distance to similarity
            )
            sources.append(source)
        
        return sources
    
    def query(
        self, 
        question: str, 
        n_results: int = 5,
        show_sources: bool = True,
        model: str = None
    ) -> Tuple[str, List[Source]]:
        """
        Query end-to-end: Retrieve → Generate
        
        Args:
            question: User's question
            n_results: Number of chunks to retrieve
            show_sources: If to extract source documents
            model: Groq model to use (optional)
            
        Returns:
            Tuple (answer, sources)
        """
        # Step 1: Retrieve relevant chunks
        results = self.retrieve(question, n_results)
        
        # Step 2: Format context
        context = self.format_context(results)
        
        # Step 3: Generate answer
        answer = llm_service.generate_answer(question, context, model)
        
        # Step 4: Extract sources (if needed)
        sources = self.extract_sources(results) if show_sources else []
        
        return answer, sources

# Singleton instance
rag_service = RAGService()