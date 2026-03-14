import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ message = 'Processing...' }) => {
  return (
    <div className="flex items-center gap-2 p-4 bg-gray-50 rounded-lg fade-in">
      <Loader2 className="w-5 h-5 text-orange-500 animate-spin" />
      <span className="text-sm text-gray-600">{message}</span>
    </div>
  );
};

export default LoadingSpinner;
