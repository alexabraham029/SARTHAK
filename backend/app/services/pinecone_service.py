"""
Pinecone Vector Database Service (FREE TIER)
Handles embeddings, indexing, and semantic search
Uses FREE sentence-transformers for embeddings
"""

from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from ..core.config import get_settings
from ..models.schemas import LawSection, CaseLaw

settings = get_settings()


class PineconeService:
    """Service for Pinecone vector database operations (FREE)"""
    
    def __init__(self):
        """Initialize Pinecone client and embedding model"""
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        
        # Load FREE sentence-transformer model locally
        print(f"[*] Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
        print(f"[OK] Embedding model loaded (dimension: {self.embedding_dimension})")
        
        self.index = None
        
    def initialize_index(self, dimension: int = None):
        """
        Initialize or connect to Pinecone index
        
        Args:
            dimension: Embedding dimension (auto-detected from model if None)
        """
        try:
            # Use model's dimension if not specified
            if dimension is None:
                dimension = self.embedding_dimension
            
            # Check if index exists
            if self.index_name not in self.pc.list_indexes().names():
                print(f"[*] Creating new index: {self.index_name} (dimension: {dimension})")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENVIRONMENT
                    )
                )
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            print(f"[OK] Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            print(f"[ERROR] Error initializing Pinecone: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using FREE sentence-transformers
        
        Args:
            text: Input text
            
        Returns:
            List of embedding values
        """
        try:
            # Generate embedding using local model (FREE)
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"[ERROR] Error generating embedding: {str(e)}")
            raise
    
    def upsert_law_sections(self, sections: List[LawSection], namespace: str = "laws"):
        """
        Upsert law sections to Pinecone
        
        Args:
            sections: List of law sections
            namespace: Pinecone namespace
        """
        if not self.index:
            raise Exception("Index not initialized. Call initialize_index() first.")
        
        vectors = []
        for section in sections:
            # Create combined text for embedding
            combined_text = f"{section.title} {section.text}"
            
            # Generate embedding
            embedding = self.generate_embedding(combined_text)
            
            # Prepare metadata
            metadata = {
                "id": section.id,
                "law": section.law,
                "law_name": section.law_name,
                "section": section.section,
                "title": section.title,
                "text": section.text[:1000],  # Limit text length in metadata
                "type": section.type
            }
            
            if section.chapter:
                metadata["chapter"] = section.chapter
            if section.chapter_title:
                metadata["chapter_title"] = section.chapter_title
            
            vectors.append({
                "id": section.id,
                "values": embedding,
                "metadata": metadata
            })
        
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch, namespace=namespace)
        
        print(f"[OK] Upserted {len(vectors)} law sections to namespace '{namespace}'")
    
    def upsert_cases(self, cases: List[CaseLaw], namespace: str = "cases"):
        """
        Upsert case laws to Pinecone
        
        Args:
            cases: List of case laws
            namespace: Pinecone namespace
        """
        if not self.index:
            raise Exception("Index not initialized. Call initialize_index() first.")
        
        vectors = []
        for case in cases:
            # Create combined text for embedding
            combined_text = f"{case.case_name} {case.facts or ''} {case.judgment}"
            
            # Generate embedding
            embedding = self.generate_embedding(combined_text)
            
            # Prepare metadata
            metadata = {
                "id": case.id,
                "case_name": case.case_name,
                "court": case.court,
                "judgment": case.judgment[:1000],  # Limit text length
                "type": "case_law"
            }
            
            if case.year:
                metadata["year"] = case.year
            if case.citation:
                metadata["citation"] = case.citation
            if case.facts:
                metadata["facts"] = case.facts[:500]
            
            vectors.append({
                "id": case.id,
                "values": embedding,
                "metadata": metadata
            })
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch, namespace=namespace)
        
        print(f"[OK] Upserted {len(vectors)} cases to namespace '{namespace}'")
    
    def search_laws(
        self,
        query: str,
        top_k: int = 5,
        law_filter: Optional[List[str]] = None,
        namespace: str = "laws"
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant law sections
        
        Args:
            query: Search query
            top_k: Number of results
            law_filter: Filter by specific laws
            namespace: Pinecone namespace
            
        Returns:
            List of matching law sections with scores
        """
        if not self.index:
            raise Exception("Index not initialized. Call initialize_index() first.")
        
        # Check if query contains specific section number (e.g., "IPC 302", "Section 420", "CPC Section 132")
        import re
        section_pattern = r'\b(IPC|CrPC|CPC|IEA|MVA|NIA|IDA|HMA)\s+(?:Section\s+)?(\d+[A-Z]?)\b'
        match = re.search(section_pattern, query, re.IGNORECASE)
        
        if match:
            law_abbr = match.group(1).upper()
            section_num = match.group(2)
            
            # Try exact section lookup first
            filter_dict = {
                "law": {"$eq": law_abbr},
                "section": {"$eq": section_num}
            }
            
            results = self.index.query(
                vector=self.generate_embedding(query),
                top_k=top_k,
                include_metadata=True,
                namespace=namespace,
                filter=filter_dict
            )
            
            # If exact match found, return it along with semantic results
            if results.matches:
                print(f"[OK] Found exact match for {law_abbr} Section {section_num}")
                # Also get semantic results for context
                semantic_results = self.index.query(
                    vector=self.generate_embedding(query),
                    top_k=top_k - len(results.matches),
                    include_metadata=True,
                    namespace=namespace,
                    filter={"law": {"$in": law_filter}} if law_filter else None
                )
                # Combine exact match first, then semantic results
                all_matches = list(results.matches) + list(semantic_results.matches)
                results.matches = all_matches[:top_k]
                return results.matches
        
        # Regular semantic search
        query_embedding = self.generate_embedding(query)
        
        # Build filter
        filter_dict = None
        if law_filter:
            filter_dict = {"law": {"$in": law_filter}}
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace,
            filter=filter_dict
        )
        
        return results.matches
    
    def search_cases(
        self,
        query: str,
        top_k: int = 5,
        court_filter: Optional[List[str]] = None,
        namespace: str = "cases"
    ) -> List[Dict[str, Any]]:
        """
        Search for similar cases
        
        Args:
            query: Case description
            top_k: Number of results
            court_filter: Filter by court
            namespace: Pinecone namespace
            
        Returns:
            List of matching cases with scores
        """
        if not self.index:
            raise Exception("Index not initialized. Call initialize_index() first.")
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Build filter
        filter_dict = None
        if court_filter:
            filter_dict = {"court": {"$in": court_filter}}
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace,
            filter=filter_dict
        )
        
        return results.matches
    
    def delete_namespace(self, namespace: str):
        """Delete all vectors in a namespace"""
        if not self.index:
            raise Exception("Index not initialized. Call initialize_index() first.")
        
        self.index.delete(delete_all=True, namespace=namespace)
        print(f"[OK] Deleted all vectors in namespace '{namespace}'")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if not self.index:
            raise Exception("Index not initialized. Call initialize_index() first.")
        
        return self.index.describe_index_stats()


# Global Pinecone service instance
pinecone_service = PineconeService()
