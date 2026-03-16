"""
Pinecone Vector Database Service (FREE TIER)
Handles embeddings, indexing, and semantic search
Uses FREE sentence-transformers for embeddings
"""

from typing import List, Dict, Any, Optional
import re
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
            combined_text = " ".join(filter(None, [
                case.case_name,
                case.petitioner,
                case.respondent,
                case.facts or '',
                case.judgment,
                case.judge,
            ]))
            
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
            if case.judge:
                metadata["judge"] = case.judge[:300]
            if case.petitioner:
                metadata["petitioner"] = case.petitioner[:250]
            if case.respondent:
                metadata["respondent"] = case.respondent[:250]
            
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

        law_aliases = {
            "IPC": "IPC",
            "INDIAN PENAL CODE": "IPC",
            "CRPC": "CRPC",
            "CODE OF CRIMINAL PROCEDURE": "CRPC",
            "CPC": "CPC",
            "CODE OF CIVIL PROCEDURE": "CPC",
            "IEA": "IEA",
            "INDIAN EVIDENCE ACT": "IEA",
            "MVA": "MVA",
            "MOTOR VEHICLES ACT": "MVA",
            "NIA": "NIA",
            "NATIONAL INVESTIGATION AGENCY ACT": "NIA",
            "IDA": "IDA",
            "INDUSTRIAL DISPUTES ACT": "IDA",
            "HMA": "HMA",
            "HINDU MARRIAGE ACT": "HMA",
        }

        law_token_pattern = "|".join(sorted((re.escape(alias) for alias in law_aliases.keys()), key=len, reverse=True))
        section_token_pattern = r"(\d+[A-Za-z]?)"

        patterns = [
            rf"\b({law_token_pattern})\s*(?:section|sec\.?|s\.?)*\s*{section_token_pattern}\b",
            rf"\b(?:section|sec\.?|s\.?)\s*{section_token_pattern}\s*(?:of\s+)?({law_token_pattern})\b",
            rf"\b{section_token_pattern}\s*({law_token_pattern})\b",
        ]

        exact_filters = []
        for pattern in patterns:
            for match in re.finditer(pattern, query, re.IGNORECASE):
                raw_first = match.group(1).upper().strip()
                raw_second = match.group(2).upper().strip()

                if raw_first in law_aliases:
                    law_abbr = law_aliases[raw_first]
                    section_num = raw_second
                else:
                    law_abbr = law_aliases.get(raw_second)
                    section_num = raw_first

                if not law_abbr:
                    continue

                exact_filters.append({
                    "law": {"$eq": law_abbr},
                    "section": {"$eq": section_num.upper()}
                })

        # De-duplicate exact filters while preserving order
        dedup_filters = []
        seen_keys = set()
        for item in exact_filters:
            key = (item["law"]["$eq"], item["section"]["$eq"])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            dedup_filters.append(item)

        query_embedding = self.generate_embedding(query)

        if dedup_filters:
            exact_matches = []
            seen_ids = set()

            for filter_dict in dedup_filters:
                results = self.index.query(
                    vector=query_embedding,
                    top_k=min(3, top_k),
                    include_metadata=True,
                    namespace=namespace,
                    filter=filter_dict
                )

                for match in results.matches:
                    match_id = getattr(match, 'id', None)
                    if not match_id or match_id in seen_ids:
                        continue
                    exact_matches.append(match)
                    seen_ids.add(match_id)

            if exact_matches:
                preview = ", ".join([f"{f['law']['$eq']} Section {f['section']['$eq']}" for f in dedup_filters])
                print(f"[OK] Found exact law-section match(es): {preview}")

                if len(exact_matches) >= top_k:
                    return exact_matches[:top_k]

                exact_laws = list({
                    filter_item["law"]["$eq"]
                    for filter_item in dedup_filters
                })

                semantic_filter = None
                if law_filter and exact_laws:
                    allowed_laws = [law for law in exact_laws if law in law_filter]
                    if allowed_laws:
                        semantic_filter = {"law": {"$in": allowed_laws}}
                    else:
                        semantic_filter = {"law": {"$in": law_filter}}
                elif exact_laws:
                    semantic_filter = {"law": {"$in": exact_laws}}
                elif law_filter:
                    semantic_filter = {"law": {"$in": law_filter}}

                semantic_results = self.index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True,
                    namespace=namespace,
                    filter=semantic_filter
                )

                merged = list(exact_matches)
                exact_ids = {getattr(match, 'id', None) for match in exact_matches}
                for match in semantic_results.matches:
                    match_id = getattr(match, 'id', None)
                    if match_id in exact_ids:
                        continue
                    merged.append(match)
                    if len(merged) >= top_k:
                        break

                return merged[:top_k]
        
        # Regular semantic search
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
