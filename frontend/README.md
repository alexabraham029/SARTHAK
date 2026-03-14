# KanoonGPT Frontend

Modern React frontend for KanoonGPT - AI Legal Assistant for Indian Law.

## Features

✅ **Legal Chat** - Conversational AI interface
✅ **Semantic Search** - Search Indian laws by meaning
✅ **Document Analysis** - Upload and analyze legal documents
✅ **Modern UI** - Clean, responsive design with Tailwind CSS
✅ **Real-time** - Instant responses with loading states

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will run at **http://localhost:3000**

### 3. Make sure Backend is Running

The backend should be running at **http://localhost:8000**

```bash
cd backend
uvicorn app.main:app --reload
```

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool (fast!)
- **Tailwind CSS** - Styling
- **Axios** - API calls
- **Lucide React** - Icons

## Build for Production

```bash
npm run build
```

Output will be in `dist/` folder.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatMessage.jsx      # Chat message component
│   │   ├── SourcesPanel.jsx     # Sources display
│   │   └── LoadingSpinner.jsx   # Loading indicator
│   ├── services/
│   │   └── api.js               # API integration
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── index.html
├── package.json
└── vite.config.js
```

## Usage

1. **Legal Chat**: Ask any question about Indian laws
2. **Search**: Use the search tab to find specific law sections
3. **Documents**: Upload PDF/DOCX files and ask questions about them

## API Endpoints Used

- `POST /api/chat/` - Send chat messages
- `POST /api/search/` - Search laws
- `POST /api/documents/upload` - Upload documents
- `POST /api/documents/query` - Query documents

---

**Happy Legal Research! ⚖️**
