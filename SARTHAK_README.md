# SARTHAK 🇮🇳⚖️

**AI-Powered Indian Legal Assistant** - Your intelligent companion for Indian law research and legal query resolution.

SARTHAK combines the power of OpenAI's GPT-4, Pinecone vector database, and comprehensive Indian legal datasets to provide accurate, contextual answers about Indian laws, case precedents, and legal documents.

---

## 🌟 Features

### 1️⃣ **Legal Chat (Multi-Turn Q&A)**
- Conversational AI assistant for Indian law queries
- Maintains chat history for contextual follow-ups
- Retrieval-Augmented Generation (RAG) for accurate answers
- Cites specific law sections and acts

### 2️⃣ **Semantic Search**
- Natural language search across all Indian laws
- Find relevant sections without knowing exact keywords
- Filter by specific acts (IPC, CrPC, CPC, etc.)
- Ranked results by relevance

### 3️⃣ **Case Law Summarizer**
- Get structured summaries of landmark cases
- Includes facts, judgment, legal issues, and significance
- Multi-turn conversations about specific cases

### 4️⃣ **Case Similarity Search**
- Find cases similar to your situation
- Compare your case with legal precedents
- Filter by court level
- AI-generated comparative analysis

### 5️⃣ **Legal Document Explainer**
- Upload PDF, DOCX, or TXT documents
- Ask questions about specific clauses
- Get plain-language explanations
- Multi-turn document analysis

---

## 📦 Tech Stack

- **Backend**: FastAPI (Python)
- **LLM**: OpenAI GPT-4 Turbo
- **Vector DB**: Pinecone
- **Embeddings**: OpenAI text-embedding-3-small
- **Data**: 8 major Indian Acts + Landmark Cases

---

## 🗂️ Project Structure

```
Indian-Law-Penal-Code-Json/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py          # Configuration management
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py         # Pydantic models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py            # Feature 1: Legal Chat
│   │   │   ├── search.py          # Feature 2: Semantic Search
│   │   │   ├── cases.py           # Features 3 & 4: Cases
│   │   │   └── documents.py       # Feature 5: Document Explainer
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── session_manager.py # Session & history management
│   │   │   ├── pinecone_service.py# Vector DB operations
│   │   │   └── llm_service.py     # OpenAI LLM interactions
│   │   ├── __init__.py
│   │   └── main.py                # FastAPI application
│   ├── .env.example               # Environment variables template
│   └── requirements.txt           # Python dependencies
├── scripts/
│   ├── standardize_laws.py        # Data standardization
│   └── ingest_to_pinecone.py      # Data ingestion pipeline
├── data/
│   ├── raw/                       # Original JSON files
│   ├── processed/                 # Standardized JSONs
│   └── cases/
│       └── landmark_cases.json    # Curated case dataset
├── ipc.json                       # Indian Penal Code
├── crpc.json                      # Code of Criminal Procedure
├── cpc.json                       # Code of Civil Procedure
├── iea.json                       # Indian Evidence Act
├── mva.json                       # Motor Vehicles Act
├── nia.json                       # Negotiable Instruments Act
├── ida.json                       # Indian Divorce Act
├── hma.json                       # Hindu Marriage Act
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key
- Pinecone account (free tier works)

### Step 1: Clone & Setup

```bash
cd Indian-Law-Penal-Code-Json
```

### Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY=your_openai_key
# - PINECONE_API_KEY=your_pinecone_key
# - PINECONE_ENVIRONMENT=your_pinecone_environment (e.g., us-east-1)
```

### Step 4: Standardize Data

```bash
# Navigate to project root
cd ..

# Run data standardization
python scripts/standardize_laws.py
```

This will:
- Convert all law JSONs to unified format
- Add unique IDs to each section
- Create `data/processed/all_laws_combined.json`

### Step 5: Ingest to Pinecone

```bash
python scripts/ingest_to_pinecone.py
```

This will:
- Initialize Pinecone index
- Generate embeddings for all law sections
- Upload to Pinecone (takes 5-10 minutes)
- Ingest landmark case laws

### Step 6: Start the API Server

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 📚 API Usage Examples

### 1. Legal Chat

```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "message": "What is Section 420 IPC?",
    "include_history": true
  }'
```

### 2. Semantic Search

```bash
curl -X POST "http://localhost:8000/api/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "theft and punishment",
    "top_k": 5,
    "law_filter": ["IPC"]
  }'
```

### 3. Case Summarizer

```bash
curl -X POST "http://localhost:8000/api/cases/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "case_query": "Kesavananda Bharati"
  }'
```

### 4. Case Similarity

```bash
curl -X POST "http://localhost:8000/api/cases/similar" \
  -H "Content-Type: application/json" \
  -d '{
    "case_description": "Property dispute between family members",
    "top_k": 3
  }'
```

### 5. Document Upload & Query

```bash
# Upload
curl -X POST "http://localhost:8000/api/documents/upload?session_id=user123" \
  -F "file=@contract.pdf"

# Query
curl -X POST "http://localhost:8000/api/documents/query" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "document_id": "<document_id_from_upload>",
    "query": "What are the termination clauses?"
  }'
```

---

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │
│  (Chat UI)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│           FastAPI Backend                    │
│  ┌─────────────────────────────────────┐   │
│  │  Routers (5 Feature Endpoints)      │   │
│  └─────────┬───────────────────────────┘   │
│            │                                 │
│  ┌─────────▼──────────┐  ┌──────────────┐  │
│  │  Session Manager   │  │  LLM Service │  │
│  │  (Chat History)    │  │  (OpenAI)    │  │
│  └────────────────────┘  └──────────────┘  │
│            │                     │           │
│  ┌─────────▼─────────────────────▼───────┐ │
│  │      Pinecone Service                 │ │
│  │  (Embeddings + Vector Search)         │ │
│  └───────────────────────────────────────┘ │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
       ┌────────────────────┐
       │  Pinecone Vector DB│
       │  ┌──────────────┐  │
       │  │ laws (ns)    │  │
       │  │ cases (ns)   │  │
       │  └──────────────┘  │
       └────────────────────┘
```

### Data Flow (Legal Chat Example)

```
1. User Query → Session Manager (append to history)
                     ↓
2. Query → Pinecone Service → Generate Embedding
                     ↓
3. Embedding → Pinecone DB → Semantic Search
                     ↓
4. Top-K Law Sections Retrieved
                     ↓
5. Retrieved Context + Chat History + Query → LLM Service
                     ↓
6. LLM → Generate Response
                     ↓
7. Response → Session Manager (append to history)
                     ↓
8. Response + Sources → Frontend
```

---

## 📊 Available Datasets

### Laws (8 Acts)
- **IPC** - Indian Penal Code, 1860 (511 sections)
- **CrPC** - Code of Criminal Procedure, 1973 (484 sections)
- **CPC** - Code of Civil Procedure, 1908 (158 sections)
- **IEA** - Indian Evidence Act, 1872 (167 sections)
- **MVA** - Motor Vehicles Act, 1988 (217 sections)
- **NIA** - Negotiable Instruments Act, 1881 (147 sections)
- **IDA** - Indian Divorce Act, 1869 (60 sections)
- **HMA** - Hindu Marriage Act, 1955 (30 sections)

### Landmark Cases (8 Cases)
- Kesavananda Bharati v. State of Kerala (Basic Structure)
- Maneka Gandhi v. Union of India (Article 21)
- Vishaka v. State of Rajasthan (Sexual Harassment)
- Shah Bano Case (Maintenance Rights)
- Indra Sawhney v. Union of India (Mandal Commission)
- Naz Foundation (Section 377)
- Nirbhaya Case (Sexual Assault Laws)
- And more...

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `OPENAI_MODEL` | GPT model to use | `gpt-4-turbo-preview` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `PINECONE_API_KEY` | Pinecone API key | `abc123...` |
| `PINECONE_ENVIRONMENT` | Pinecone region | `us-east-1` |
| `PINECONE_INDEX_NAME` | Index name | `sarthak-laws` |
| `TOP_K_RESULTS` | Results per query | `5` |
| `MAX_HISTORY_LENGTH` | Chat history size | `10` |

---

## 🛠️ Development

### Adding New Law Sections

1. Add JSON file to project root (e.g., `new_act.json`)
2. Update `scripts/standardize_laws.py`:
   - Add to `LAW_METADATA`
   - Create standardizer function
3. Run: `python scripts/standardize_laws.py`
4. Ingest: `python scripts/ingest_to_pinecone.py`

### Adding New Cases

1. Edit `data/cases/landmark_cases.json`
2. Add case with required fields:
   - `id`, `case_name`, `court`, `year`, `citation`, `facts`, `judgment`, `legal_issues`
3. Run: `python scripts/ingest_to_pinecone.py`

---

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### System Stats

```bash
curl http://localhost:8000/stats
```

---

## 📝 API Documentation

Full interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Add more Indian laws
- Expand the case law database
- Improve prompts and responses
- Add new features
- Fix bugs

---

## 📄 License

This project is for educational and research purposes.

---

## 🙏 Acknowledgments

- Original JSON datasets from [civictech-India](https://github.com/civictech-India/Indian-Law-Penal-Code-Json)
- OpenAI for GPT-4 and embeddings
- Pinecone for vector database
- FastAPI framework

---

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

## 🎯 Roadmap

- [ ] Add more Indian laws (Constitution, Family Laws, etc.)
- [ ] Expand case law database (1000+ cases)
- [ ] Add citation network visualization
- [ ] Multi-language support (Hindi, Tamil, etc.)
- [ ] Fine-tune model on Indian legal corpus
- [ ] Add frontend chat interface
- [ ] Deploy on cloud (AWS/Azure/GCP)
- [ ] Add authentication and user management

---

**Built with ❤️ for the Indian Legal Community**
