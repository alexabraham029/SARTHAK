"""
Data Ingestion Script - Load data into Pinecone
Ingests standardized law sections and case laws into vector database
"""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

from backend.app.services.pinecone_service import pinecone_service
from backend.app.models.schemas import LawSection, CaseLaw


def load_law_sections():
    """Load all standardized law sections"""
    processed_dir = Path(__file__).parent.parent / "data" / "processed"
    combined_file = processed_dir / "all_laws_combined.json"
    
    if not combined_file.exists():
        print(f"❌ Combined laws file not found: {combined_file}")
        print("   Please run standardize_laws.py first!")
        return []
    
    print(f"📖 Loading law sections from {combined_file}...")
    
    with open(combined_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert to LawSection objects
    sections = []
    for item in data:
        try:
            section = LawSection(**item)
            sections.append(section)
        except Exception as e:
            print(f"⚠️  Skipping invalid section: {str(e)}")
    
    print(f"✅ Loaded {len(sections)} law sections")
    return sections


def load_case_laws():
    """Load case law dataset"""
    cases_file = Path(__file__).parent.parent / "data" / "cases" / "landmark_cases.json"
    
    if not cases_file.exists():
        print(f"⚠️  Case laws file not found: {cases_file}")
        return []
    
    print(f"📖 Loading case laws from {cases_file}...")
    
    with open(cases_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert to CaseLaw objects
    cases = []
    for item in data:
        try:
            # Remove 'type' field if present (not in CaseLaw model)
            item.pop('type', None)
            case = CaseLaw(**item)
            cases.append(case)
        except Exception as e:
            print(f"⚠️  Skipping invalid case: {str(e)}")
    
    print(f"✅ Loaded {len(cases)} cases")
    return cases


def main():
    """Main ingestion process"""
    print("=" * 70)
    print("KanoonGPT - Data Ingestion to Pinecone")
    print("=" * 70)
    
    # Initialize Pinecone
    print("\n📌 Initializing Pinecone...")
    try:
        pinecone_service.initialize_index()
        print("✅ Pinecone initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Pinecone: {str(e)}")
        print("\nMake sure you have:")
        print("1. Created a .env file from .env.example")
        print("2. Added your Pinecone API key")
        print("3. Set the correct Pinecone environment")
        return
    
    # Load and ingest law sections
    print("\n" + "=" * 70)
    print("STEP 1: Ingesting Law Sections")
    print("=" * 70)
    
    law_sections = load_law_sections()
    if law_sections:
        print(f"\n🔄 Upserting {len(law_sections)} law sections to Pinecone...")
        print("   This may take several minutes...")
        
        try:
            pinecone_service.upsert_law_sections(law_sections, namespace="laws")
            print("✅ Law sections ingested successfully!")
        except Exception as e:
            print(f"❌ Error ingesting law sections: {str(e)}")
    
    # Load and ingest case laws
    print("\n" + "=" * 70)
    print("STEP 2: Ingesting Case Laws")
    print("=" * 70)
    
    case_laws = load_case_laws()
    if case_laws:
        print(f"\n🔄 Upserting {len(case_laws)} cases to Pinecone...")
        
        try:
            pinecone_service.upsert_cases(case_laws, namespace="cases")
            print("✅ Cases ingested successfully!")
        except Exception as e:
            print(f"❌ Error ingesting cases: {str(e)}")
    
    # Show final stats
    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    
    try:
        stats = pinecone_service.get_index_stats()
        print(f"\n📊 Pinecone Index Stats:")
        print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
        print(f"   Namespaces: {stats.get('namespaces', {})}")
    except Exception as e:
        print(f"⚠️  Could not retrieve stats: {str(e)}")
    
    print("\n" + "=" * 70)
    print("✅ Data ingestion complete!")
    print("=" * 70)
    print("\n🚀 You can now start the FastAPI server:")
    print("   cd backend")
    print("   uvicorn app.main:app --reload")
    print("\n📚 API Documentation will be available at:")
    print("   http://localhost:8000/docs")
    print("=" * 70)


if __name__ == "__main__":
    main()
