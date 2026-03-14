import React, { useState, useRef, useEffect } from 'react';
import { Scale, Send, Trash2, MessageSquare, Search, FileText, Upload } from 'lucide-react';
import ChatMessage from './components/ChatMessage';
import SourcesPanel from './components/SourcesPanel';
import LoadingSpinner from './components/LoadingSpinner';
import { sendChatMessage, searchLaws, generateSessionId, uploadDocument, queryDocument } from './services/api';

function App() {
  const [sessionId, setSessionId] = useState(() => generateSessionId());
  const [chatMessages, setChatMessages] = useState([]);
  const [documentMessages, setDocumentMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  // Get current tab's messages
  const messages = activeTab === 'document' ? documentMessages : chatMessages;
  const setMessages = activeTab === 'document' ? setDocumentMessages : setChatMessages;

  // Clear chat messages when switching to chat tab
  const handleTabChange = (tab) => {
    if (tab === 'chat') {
      setChatMessages([]);
      setSources([]);
    }
    setActiveTab(tab);
    setInput(''); // Clear input when switching tabs
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, activeTab]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      if (activeTab === 'chat') {
        const response = await sendChatMessage(sessionId, userMessage);
        setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);
        setSources(response.sources || []);
      } else if (activeTab === 'document' && uploadedDoc) {
        console.log('Querying document - Session:', sessionId, 'Doc ID:', uploadedDoc.document_id);
        const response = await queryDocument(sessionId, uploadedDoc.document_id, userMessage);
        setMessages(prev => [...prev, { role: 'assistant', content: response.answer }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const response = await searchLaws(searchQuery);
      setSearchResults(response.results || []);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    try {
      const response = await uploadDocument(sessionId, file);
      setUploadedDoc(response);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Document "${response.filename}" uploaded successfully! You can now ask questions about it.`
      }]);
    } catch (error) {
      console.error('Upload error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Failed to upload document. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    const newSessionId = generateSessionId();
    console.log('Clearing chat - Old session:', sessionId, 'New session:', newSessionId);
    setChatMessages([]);
    setDocumentMessages([]);
    setSources([]);
    setSearchResults([]);
    setUploadedDoc(null);
    setSessionId(newSessionId); // Generate new session ID to clear backend session
    if (fileInputRef.current) {
      fileInputRef.current.value = ''; // Reset file input
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-orange-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center shadow-lg">
                <Scale className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                  Sarthak
                </h1>
                <p className="text-xs text-gray-500">AI Legal Assistant</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={clearChat}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Clear chat"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-4">
            <button
              onClick={() => handleTabChange('chat')}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'chat'
                  ? 'border-orange-500 text-orange-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
            >
              <MessageSquare className="w-4 h-4" />
              Legal Chat
            </button>
            <button
              onClick={() => handleTabChange('search')}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'search'
                  ? 'border-orange-500 text-orange-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
            >
              <Search className="w-4 h-4" />
              Search Laws
            </button>
            <button
              onClick={() => handleTabChange('document')}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'document'
                  ? 'border-orange-500 text-orange-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
            >
              <FileText className="w-4 h-4" />
              Document Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <div className="max-w-7xl mx-auto h-full flex flex-col lg:flex-row gap-4 p-4">
          {/* Chat Area */}
          <div className="flex-1 flex flex-col bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center max-w-md">
                    <Scale className="w-16 h-16 text-orange-500 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      Welcome to Sarthak
                    </h2>
                    <p className="text-gray-600">
                      Your AI-powered Indian legal assistant. Ask questions about Indian laws, search for specific sections, or analyze documents.
                    </p>
                    <div className="mt-6 grid gap-2 text-sm text-left">
                      <div className="p-3 bg-gray-50 rounded-lg">
                        💬 <strong>Chat:</strong> Ask any legal question
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        🔍 <strong>Search:</strong> Find relevant law sections
                      </div>
                      <div className="p-3 bg-gray-50 rounded-lg">
                        📄 <strong>Documents:</strong> Upload and analyze legal docs
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg, index) => (
                    <ChatMessage
                      key={index}
                      message={msg.content}
                      isUser={msg.role === 'user'}
                    />
                  ))}
                  {loading && <LoadingSpinner message="Thinking..." />}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-200 p-4 bg-gray-50">
              {activeTab === 'document' && !uploadedDoc && (
                <div className="mb-3">
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileUpload}
                    accept=".pdf,.docx,.txt"
                    className="hidden"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    <Upload className="w-4 h-4" />
                    Upload Document (PDF, DOCX, TXT)
                  </button>
                  <p className="text-xs text-center text-gray-500 mt-2">
                    Please upload a document to analyze
                  </p>
                </div>
              )}
              {activeTab === 'document' && uploadedDoc && (
                <div className="mb-3 p-2 bg-blue-50 rounded border border-blue-200">
                  <p className="text-xs text-blue-700">
                    📄 Analyzing: <strong>{uploadedDoc.filename}</strong>
                  </p>
                </div>
              )}
              <form onSubmit={handleSendMessage} className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={
                    activeTab === 'chat'
                      ? 'Ask a legal question...'
                      : activeTab === 'document'
                        ? 'Ask about your document...'
                        : 'Enter your query...'
                  }
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  disabled={loading || (activeTab === 'document' && !uploadedDoc)}
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim() || (activeTab === 'document' && !uploadedDoc)}
                  className="px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg hover:from-orange-600 hover:to-orange-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg"
                >
                  <Send className="w-4 h-4" />
                  Send
                </button>
              </form>
            </div>
          </div>

          {/* Sidebar */}
          {sources.length > 0 && activeTab === 'chat' && (
            <div className="lg:w-96 bg-white rounded-lg shadow-lg p-4 overflow-y-auto">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Legal Sources</h3>
              <SourcesPanel sources={sources} />
            </div>
          )}

          {/* Search Results */}
          {activeTab === 'search' && (
            <div className="lg:w-96 bg-white rounded-lg shadow-lg p-4 overflow-y-auto">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Search Laws</h3>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Search for laws..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  />
                  <button
                    onClick={handleSearch}
                    className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                  >
                    <Search className="w-4 h-4" />
                  </button>
                </div>
              </div>
              {searchResults.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">
                    Results ({searchResults.length})
                  </h4>
                  <SourcesPanel sources={searchResults} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
