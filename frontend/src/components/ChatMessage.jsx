import React from 'react';
import { User, Scale } from 'lucide-react';
import { useTheme } from './Layout';

const ChatMessage = ({ message, isUser, isTyping = false }) => {
  const { theme } = useTheme();
  const dark = theme === 'dark';

  return (
    <div className={`flex gap-3 p-4 rounded-xl message-enter ${
      isUser
        ? dark ? 'bg-amber-400/5 border border-amber-400/10' : 'bg-amber-50 border border-amber-100'
        : dark ? 'glass-card-sm' : 'glass-card-sm-light'
    }`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
        isUser
          ? 'bg-gradient-to-br from-blue-400 to-blue-600'
          : 'bg-gradient-to-br from-amber-400 to-amber-600'
      }`}>
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Scale className="w-4 h-4 text-white" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className={`text-xs font-semibold mb-1.5 ${
          isUser
            ? dark ? 'text-blue-400' : 'text-blue-600'
            : dark ? 'text-amber-400' : 'text-amber-600'
        }`}>
          {isUser ? 'You' : 'Sarthak'}
        </div>
        <div className={`text-sm whitespace-pre-wrap leading-relaxed ${
          dark ? 'text-white/75' : 'text-gray-700'
        } ${isTyping ? 'typewriter-cursor' : ''}`}>
          {message}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
