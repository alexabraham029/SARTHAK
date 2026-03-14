import React from 'react';
import { Book } from 'lucide-react';
import { useTheme } from './Layout';

const SourceCard = ({ source }) => {
  const { theme } = useTheme();
  const dark = theme === 'dark';

  return (
    <div className={`p-3.5 rounded-xl transition-all duration-200 cursor-default
      ${dark
        ? 'glass-card-sm glass-card-hover border-l-2 border-l-amber-400/30'
        : 'glass-card-sm-light glass-card-hover-light border-l-2 border-l-amber-400'
      }`}
    >
      <div className="flex items-start gap-2.5">
        <Book className={`w-4 h-4 mt-0.5 flex-shrink-0 ${dark ? 'text-amber-400' : 'text-amber-600'}`} />
        <div className="flex-1 min-w-0">
          <div className={`text-xs font-bold ${dark ? 'text-white/85' : 'text-gray-900'}`}>
            {source.law} Section {source.section}
          </div>
          <div className={`text-[11px] mt-1 ${dark ? 'text-white/45' : 'text-gray-500'}`}>
            {source.title}
          </div>
          {source.score && (
            <div className="mt-2 flex items-center gap-2">
              <div className={`h-1 rounded-full flex-1 ${dark ? 'bg-white/10' : 'bg-gray-200'}`}>
                <div
                  className="h-full rounded-full bg-gradient-to-r from-amber-400 to-amber-500"
                  style={{ width: `${(source.score * 100)}%` }}
                />
              </div>
              <span className={`text-[10px] ${dark ? 'text-white/30' : 'text-gray-400'}`}>
                {(source.score * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const SourcesPanel = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="grid gap-2.5">
      {sources.map((source, index) => (
        <SourceCard key={index} source={source} />
      ))}
    </div>
  );
};

export default SourcesPanel;
