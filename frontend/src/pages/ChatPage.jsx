import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Scale, Send, Trash2, Mic, MicOff, Download, Globe } from 'lucide-react';
import ChatMessage from '../components/ChatMessage';
import SourcesPanel from '../components/SourcesPanel';
import LoadingSpinner from '../components/LoadingSpinner';
import { sendChatMessage, generateSessionId } from '../services/api';
import { useTheme } from '../components/Layout';

const quickPrompts = [
  "What is Section 302 of IPC?",
  "Explain the right to bail in India",
  "What are the grounds for divorce under Hindu Marriage Act?",
  "Define sedition under Indian law",
];

const ChatPage = () => {
  const { theme } = useTheme();
  const dark = theme === 'dark';
  const [sessionId, setSessionId] = useState(() => generateSessionId());
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState([]);
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [typingMessage, setTypingMessage] = useState(null);
  const [speechSupported, setSpeechSupported] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, typingMessage]);

  // Voice recognition setup
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-IN';

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        setInput(transcript);
      };

      recognition.onend = () => setIsListening(false);
      recognition.onerror = (e) => {
        console.warn('Speech recognition error:', e.error);
        setIsListening(false);
      };
      recognitionRef.current = recognition;
      setSpeechSupported(true);
    }
  }, []);

  const toggleVoice = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        // Already started — abort and restart
        recognitionRef.current.stop();
        setTimeout(() => {
          recognitionRef.current.start();
          setIsListening(true);
        }, 100);
      }
    }
  };

  // Typewriter effect
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

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await sendChatMessage(sessionId, userMessage, webSearchEnabled);
      setLoading(false);
      setSources(response.sources || []);
      typeMessage(response.message, (fullText) => {
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

  const clearChat = () => {
    setSessionId(generateSessionId());
    setMessages([]);
    setSources([]);
    setTypingMessage(null);
  };

  const exportChat = () => {
    const text = messages.map(m => `${m.role === 'user' ? 'You' : 'Sarthak'}: ${m.content}`).join('\n\n---\n\n');
    const blob = new Blob([`SARTHAK — Legal Chat Export\n${'='.repeat(40)}\n\n${text}`], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sarthak-chat-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePromptClick = (prompt) => {
    setInput(prompt);
  };

  return (
    <div className="h-full flex flex-col lg:flex-row gap-4 p-4">
      {/* Chat Panel */}
      <div className={`flex-1 flex flex-col rounded-2xl overflow-hidden ${dark ? 'glass-card' : 'glass-card-light'}`}>
        {/* Header */}
        <div className={`flex items-center justify-between px-5 py-4 border-b ${dark ? 'border-white/8' : 'border-gray-200'}`}>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className={`text-base font-semibold ${dark ? 'text-white' : 'text-gray-900'}`}>Legal Chat</h2>
              <p className={`text-[11px] ${dark ? 'text-white/35' : 'text-gray-400'}`}>Ask any question about Indian law</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setWebSearchEnabled((prev) => !prev)}
              className={`px-2.5 py-2 rounded-lg text-xs font-medium transition-colors border ${
                webSearchEnabled
                  ? dark
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                    : 'bg-amber-100 text-amber-700 border-amber-300'
                  : dark
                    ? 'text-white/45 border-white/10 hover:bg-white/5'
                    : 'text-gray-500 border-gray-200 hover:bg-gray-100'
              }`}
              title="Toggle web search"
            >
              <span className="inline-flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5" />
                Web
              </span>
            </button>
            {messages.length > 0 && (
              <button onClick={exportChat} className={`p-2 rounded-lg transition-colors ${dark ? 'text-white/40 hover:text-white/70 hover:bg-white/5' : 'text-gray-400 hover:text-gray-700 hover:bg-gray-100'}`} title="Export chat">
                <Download className="w-4 h-4" />
              </button>
            )}
            <button onClick={clearChat} className={`p-2 rounded-lg transition-colors ${dark ? 'text-white/40 hover:text-white/70 hover:bg-white/5' : 'text-gray-400 hover:text-gray-700 hover:bg-gray-100'}`} title="Clear chat">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 && !typingMessage ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md px-4">
                <div className="w-16 h-16 mx-auto mb-5 rounded-2xl bg-gradient-to-br from-amber-400/20 to-amber-600/20 flex items-center justify-center">
                  <Scale className={`w-8 h-8 ${dark ? 'text-amber-400' : 'text-amber-600'}`} />
                </div>
                <h2 className={`text-xl font-bold mb-2 ${dark ? 'text-white' : 'text-gray-900'}`}>
                  How can I help you?
                </h2>
                <p className={`text-sm mb-6 ${dark ? 'text-white/40' : 'text-gray-500'}`}>
                  Ask any question about Indian law — IPC, CrPC, CPC, and more.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {quickPrompts.map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => handlePromptClick(prompt)}
                      className="prompt-card text-left text-xs"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, index) => (
                <ChatMessage key={index} message={msg.content} isUser={msg.role === 'user'} />
              ))}
              {loading && <LoadingSpinner message={webSearchEnabled ? "Searching web + analyzing legal context..." : "Analyzing legal context..."} />}
              {typingMessage !== null && !loading && (
                <ChatMessage message={typingMessage} isUser={false} isTyping={true} />
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className={`px-4 py-4 border-t ${dark ? 'border-white/8' : 'border-gray-200'}`}>
          <form onSubmit={handleSendMessage} className="flex gap-2">
            {speechSupported && (
              <button
                type="button"
                onClick={toggleVoice}
                className={`p-3 rounded-xl transition-all ${
                  isListening
                    ? 'bg-red-500/20 text-red-400 voice-pulse'
                    : dark ? 'btn-glass text-white/50' : 'btn-glass-light text-gray-400'
                }`}
                title={isListening ? 'Stop recording' : 'Voice input'}
              >
                {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
            )}
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a legal question..."
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

      {/* Sources Sidebar */}
      {sources.length > 0 && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className={`lg:w-80 xl:w-96 rounded-2xl p-5 overflow-y-auto ${dark ? 'glass-card' : 'glass-card-light'}`}
        >
          <h3 className={`text-base font-semibold mb-4 ${dark ? 'text-white' : 'text-gray-900'}`}>Legal Sources</h3>
          <SourcesPanel sources={sources} />
        </motion.div>
      )}
    </div>
  );
};

export default ChatPage;
