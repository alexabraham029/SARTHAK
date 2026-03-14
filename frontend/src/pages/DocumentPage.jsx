import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { FileText, Upload, Send, Trash2, File, CheckCircle, Mic, MicOff } from 'lucide-react';
import ChatMessage from '../components/ChatMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { uploadDocument, queryDocument, generateSessionId } from '../services/api';
import { useTheme } from '../components/Layout';

const DocumentPage = () => {
  const { theme } = useTheme();
  const dark = theme === 'dark';
  const [sessionId] = useState(() => generateSessionId());
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [typingMessage, setTypingMessage] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, typingMessage]);

  // Voice recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-IN';
      recognition.onresult = (event) => {
        const transcript = Array.from(event.results).map(r => r[0].transcript).join('');
        setInput(transcript);
      };
      recognition.onend = () => setIsListening(false);
      recognition.onerror = () => setIsListening(false);
      recognitionRef.current = recognition;
    }
  }, []);

  const toggleVoice = () => {
    if (!recognitionRef.current) return;
    if (isListening) recognitionRef.current.stop();
    else { recognitionRef.current.start(); setIsListening(true); }
  };

  // Typewriter
  const typeMessage = useCallback((fullText, onComplete) => {
    let index = 0;
    setTypingMessage('');
    const interval = setInterval(() => {
      if (index < fullText.length) {
        setTypingMessage(fullText.slice(0, index + 1));
        index++;
      } else {
        clearInterval(interval);
        setTypingMessage(null);
        onComplete(fullText);
      }
    }, 12);
    return () => clearInterval(interval);
  }, []);

  const handleFileUpload = async (file) => {
    if (!file) return;
    setUploading(true);
    try {
      const response = await uploadDocument(sessionId, file);
      setUploadedDoc(response);
      setMessages([{
        role: 'assistant',
        content: `Document "${response.filename}" uploaded successfully! You can now ask questions about it.`
      }]);
    } catch (error) {
      console.error('Upload error:', error);
      setMessages([{
        role: 'assistant',
        content: 'Failed to upload document. Please try again.'
      }]);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!input.trim() || loading || !uploadedDoc) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await queryDocument(sessionId, uploadedDoc.document_id, userMessage);
      setLoading(false);
      typeMessage(response.answer, (fullText) => {
        setMessages(prev => [...prev, { role: 'assistant', content: fullText }]);
      });
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    }
  };

  const resetDocument = () => {
    setUploadedDoc(null);
    setMessages([]);
    setTypingMessage(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Upload View
  if (!uploadedDoc) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-lg w-full"
        >
          <div className="text-center mb-8">
            <h1 className={`text-3xl font-bold mb-2 ${dark ? 'text-white' : 'text-gray-900'}`}>Document Analysis</h1>
            <p className={`text-sm ${dark ? 'text-white/40' : 'text-gray-500'}`}>
              Upload a legal document and ask AI-powered questions about it
            </p>
          </div>

          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => !uploading && fileInputRef.current?.click()}
            className={`drop-zone rounded-2xl p-12 text-center cursor-pointer
              ${dragOver ? 'drag-over' : ''}
              ${dark ? 'glass-card' : 'glass-card-light'}`}
          >
            <input
              ref={fileInputRef}
              type="file"
              onChange={(e) => handleFileUpload(e.target.files[0])}
              accept=".pdf,.docx,.txt"
              className="hidden"
            />

            {uploading ? (
              <div>
                <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center ${dark ? 'bg-white/5' : 'bg-gray-100'}`}>
                  <div className="w-8 h-8 border-3 border-amber-400 border-t-transparent rounded-full animate-spin" />
                </div>
                <p className={`text-sm font-medium ${dark ? 'text-white/60' : 'text-gray-600'}`}>Processing document...</p>
              </div>
            ) : (
              <div>
                <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center ${dark ? 'bg-amber-400/10' : 'bg-amber-50'}`}>
                  <Upload className={`w-8 h-8 ${dark ? 'text-amber-400' : 'text-amber-600'}`} />
                </div>
                <p className={`text-base font-semibold mb-1 ${dark ? 'text-white' : 'text-gray-900'}`}>
                  Drop your document here
                </p>
                <p className={`text-sm mb-4 ${dark ? 'text-white/35' : 'text-gray-400'}`}>
                  or click to browse files
                </p>
                <div className="flex items-center justify-center gap-3">
                  {['PDF', 'DOCX', 'TXT'].map(type => (
                    <span key={type} className={`px-3 py-1 rounded-lg text-xs font-medium
                      ${dark ? 'bg-white/5 text-white/40' : 'bg-gray-100 text-gray-500'}`}>
                      {type}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    );
  }

  // Chat with Document View
  return (
    <div className="h-full flex flex-col p-4">
      <div className={`flex-1 flex flex-col rounded-2xl overflow-hidden ${dark ? 'glass-card' : 'glass-card-light'}`}>
        {/* Header */}
        <div className={`flex items-center justify-between px-5 py-4 border-b ${dark ? 'border-white/8' : 'border-gray-200'}`}>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className={`text-base font-semibold ${dark ? 'text-white' : 'text-gray-900'}`}>Document Chat</h2>
              <div className="flex items-center gap-1.5">
                <CheckCircle className="w-3 h-3 text-emerald-400" />
                <p className={`text-[11px] ${dark ? 'text-emerald-400/70' : 'text-emerald-600'}`}>
                  {uploadedDoc.filename}
                </p>
              </div>
            </div>
          </div>
          <button
            onClick={resetDocument}
            className={`p-2 rounded-lg transition-colors ${dark ? 'text-white/40 hover:text-white/70 hover:bg-white/5' : 'text-gray-400 hover:text-gray-700 hover:bg-gray-100'}`}
            title="Upload a different document"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((msg, index) => (
            <ChatMessage key={index} message={msg.content} isUser={msg.role === 'user'} />
          ))}
          {loading && <LoadingSpinner message="Analyzing document..." />}
          {typingMessage !== null && !loading && (
            <ChatMessage message={typingMessage} isUser={false} isTyping={true} />
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className={`px-4 py-4 border-t ${dark ? 'border-white/8' : 'border-gray-200'}`}>
          <form onSubmit={handleSendMessage} className="flex gap-2">
            {recognitionRef.current && (
              <button
                type="button"
                onClick={toggleVoice}
                className={`p-3 rounded-xl transition-all ${
                  isListening
                    ? 'bg-red-500/20 text-red-400 voice-pulse'
                    : dark ? 'btn-glass text-white/50' : 'btn-glass-light text-gray-400'
                }`}
              >
                {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
            )}
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your document..."
              className={`flex-1 px-4 py-3 text-sm ${dark ? 'glass-input' : 'glass-input-light'}`}
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-5 py-3 btn-glow rounded-xl flex items-center gap-2 text-sm font-semibold"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default DocumentPage;
