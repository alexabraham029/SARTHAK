import React from 'react';
import { Loader2 } from 'lucide-react';
import { useTheme } from './Layout';

const LoadingSpinner = ({ message = 'Processing...' }) => {
  const { theme } = useTheme();
  const dark = theme === 'dark';

  return (
    <div className={`flex items-center gap-3 p-4 rounded-xl message-enter
      ${dark ? 'glass-card-sm' : 'glass-card-sm-light'}`}
    >
      <div className="relative">
        <Loader2 className={`w-5 h-5 animate-spin ${dark ? 'text-amber-400' : 'text-amber-500'}`} />
        <div className="absolute inset-0 w-5 h-5 rounded-full bg-amber-400/20 animate-ping" />
      </div>
      <span className={`text-sm ${dark ? 'text-white/50' : 'text-gray-500'}`}>{message}</span>
    </div>
  );
};

export default LoadingSpinner;
