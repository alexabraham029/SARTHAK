"""
Groq LLM Service (FREE)
Handles LLM interactions for chat, summarization, and explanation
Uses Groq's free API with fast inference
"""

from typing import List, Dict, Any, Optional
from groq import Groq
from ..core.config import get_settings
from ..models.schemas import ChatMessage

settings = get_settings()


class LLMService:
    """Service for Groq LLM operations (FREE)"""
    
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
    
    def generate_chat_response(
        self,
        query: str,
        context: List[Dict[str, Any]],
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate chat response with RAG
        
        Args:
            query: User query
            context: Retrieved law sections/cases
            chat_history: Previous chat messages
            
        Returns:
            Generated response
        """
        # Build context string
        context_str = self._format_context(context)
        
        # Build system prompt
        system_prompt = f"""You are Sarthak, an expert AI assistant specializing in Indian law.

Your role:
- Answer questions about Indian laws accurately using ONLY the provided context below
- Cite specific sections, acts, and case laws when relevant
- Maintain a professional, helpful tone

CRITICAL RULES:
1. You MUST ONLY use information from the "Retrieved Legal Context" below
2. If a specific section is NOT in the context below, respond: "I don't have information about [section name] in my current context. Please try searching for related topics."
3. NEVER use your general knowledge or training data to answer legal questions
4. If the context is insufficient, clearly state what's missing

Retrieved Legal Context:
{context_str}

Response Guidelines:
1. Always cite the law and section number (e.g., "IPC Section 420")
2. Explain legal concepts clearly for non-lawyers
3. If asked about a specific case, provide facts, judgment, and legal principles
4. For multi-turn conversations, maintain context from previous exchanges
"""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        # Generate response with Groq
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                top_p=1,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error generating chat response: {str(e)}")
            raise
    
    def summarize_case(self, case_data: Dict[str, Any], chat_history: List[Dict[str, str]] = None) -> str:
        """
        Generate structured case summary
        
        Args:
            case_data: Case information
            chat_history: Previous chat messages
            
        Returns:
            Formatted case summary
        """
        system_prompt = """You are a legal expert providing case law summaries.

Generate a structured summary with:
1. Case Name and Citation
2. Court and Year
3. Facts of the Case
4. Legal Issues
5. Judgment/Ruling
6. Legal Principles Established
7. Significance

Be concise but comprehensive. Use clear headings and bullet points where appropriate."""
        
        case_text = f"""
Case Name: {case_data.get('case_name', 'N/A')}
Court: {case_data.get('court', 'N/A')}
Year: {case_data.get('year', 'N/A')}
Citation: {case_data.get('citation', 'N/A')}
Facts: {case_data.get('facts', 'N/A')}
Judgment: {case_data.get('judgment', 'N/A')}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Summarize this case:\n\n{case_text}"}
        ]
        
        # Add chat history for follow-up questions
        if chat_history:
            # Insert history before the current query
            messages = [messages[0]] + chat_history + [messages[-1]]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                top_p=1,
                stream=False,
                temperature=0.5,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error summarizing case: {str(e)}")
            raise
    
    def explain_document(
        self,
        query: str,
        document_chunks: List[str],
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Explain document content based on query
        
        Args:
            query: User query about document
            document_chunks: Relevant document chunks
            chat_history: Previous chat messages
            
        Returns:
            Explanation of document content
        """
        chunks_text = "\n\n---\n\n".join(document_chunks)
        
        system_prompt = f"""You are a legal document expert. Analyze and explain legal documents clearly.

Document Content:
{chunks_text}

Guidelines:
- Explain clauses and terms in simple language
- Identify key obligations, rights, and conditions
- Highlight any ambiguous or concerning language
- Reference specific sections when explaining
- Answer follow-up questions based on previous context
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            messages.extend(chat_history)
        
        messages.append({"role": "user", "content": query})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                top_p=1,
                stream=False,
                temperature=0.6,
                max_tokens=1200
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error explaining document: {str(e)}")
            raise
    
    def generate_case_comparison(
        self,
        user_case: str,
        similar_cases: List[Dict[str, Any]]
    ) -> str:
        """
        Generate comparison between user case and similar cases
        
        Args:
            user_case: User's case description
            similar_cases: List of similar cases from database
            
        Returns:
            Comparative analysis
        """
        cases_text = "\n\n".join([
            f"**{i+1}. {case.get('case_name')}**\n"
            f"Court: {case.get('court')}\n"
            f"Facts: {case.get('facts', 'N/A')}\n"
            f"Judgment: {case.get('judgment', '')[:300]}..."
            for i, case in enumerate(similar_cases)
        ])
        
        prompt = f"""Analyze this user's case and compare it with similar cases:

User's Case:
{user_case}

Similar Cases:
{cases_text}

Provide:
1. How the user's case relates to the similar cases
2. Key legal principles applicable
3. Potential outcomes based on precedents
4. Important distinctions or similarities
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert legal analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500,
                top_p=1,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error generating case comparison: {str(e)}")
            raise
    
    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format retrieved context for prompt"""
        if not context:
            return "No relevant context found."
        
        formatted = []
        for i, item in enumerate(context, 1):
            metadata = item.get('metadata', {})
            
            if metadata.get('type') == 'law_section':
                formatted.append(
                    f"{i}. **{metadata.get('law')} Section {metadata.get('section')}**: "
                    f"{metadata.get('title')}\n"
                    f"   {metadata.get('text', '')}\n"
                )
            elif metadata.get('type') == 'case_law':
                formatted.append(
                    f"{i}. **{metadata.get('case_name')}**\n"
                    f"   Court: {metadata.get('court')}\n"
                    f"   {metadata.get('judgment', '')}\n"
                )
        
        return "\n".join(formatted)


# Global LLM service instance
llm_service = LLMService()
