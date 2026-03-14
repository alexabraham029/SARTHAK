import React from 'react';
import { MessageSquare, User, Scale } from 'lucide-react';

const ChatMessage = ({ message, isUser }) => {
  return (
    <div className={`flex gap-3 p-4 ${isUser ? 'bg-blue-50' : 'bg-white'} rounded-lg fade-in`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'bg-blue-500' : 'bg-orange-500'
        }`}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Scale className="w-5 h-5 text-white" />
        )}
      </div>
      <div className="flex-1">
        <div className="text-sm font-medium text-gray-900 mb-1">
          {isUser ? 'You' : 'Sarthak'}
        </div>
        <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
          {message}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
