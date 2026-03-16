import React from 'react';
import { Book, Scale } from 'lucide-react';
import { useTheme } from './Layout';

const SourceCard = ({ source }) => {
  const { theme } = useTheme();
  const dark = theme === 'dark';
  const isCaseSource = source.type === 'case_law' || source.type === 'sc_judgment';
  const Icon = isCaseSource ? Scale : Book;
  const scorePercentage = source.score ? Math.min(source.score * 100, 100) : null;

  return (
    <div className={`p-3.5 rounded-xl transition-all duration-200 cursor-default
      ${dark
        ? 'glass-card-sm glass-card-hover border-l-2 border-l-amber-400/30'
        : 'glass-card-sm-light glass-card-hover-light border-l-2 border-l-amber-400'
      }`}
    >
      <div className="flex items-start gap-2.5">
        <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${dark ? 'text-amber-400' : 'text-amber-600'}`} />
        <div className="flex-1 min-w-0">
          <div className={`text-xs font-bold ${dark ? 'text-white/85' : 'text-gray-900'}`}>
            {isCaseSource
              ? source.case_name || 'Case Law'
              : `${source.law} Section ${source.section}`}
          </div>
          <div className={`text-[11px] mt-1 ${dark ? 'text-white/45' : 'text-gray-500'}`}>
            {isCaseSource
              ? [source.court, source.year].filter(Boolean).join(' • ') || source.citation || 'Judgment source'
              : source.title}
          </div>
          {isCaseSource && source.citation && (
            <div className={`text-[11px] mt-2 ${dark ? 'text-white/45' : 'text-gray-500'}`}>
              {source.citation}
            </div>
          )}
          {isCaseSource && (source.facts || source.judgment) && (
            <div className={`text-[11px] mt-2 line-clamp-4 ${dark ? 'text-white/55' : 'text-gray-600'}`}>
              {source.facts || source.judgment}
            </div>
          )}
          {source.score && (
            <div className="mt-2 flex items-center gap-2">
              <div className={`h-1 rounded-full flex-1 ${dark ? 'bg-white/10' : 'bg-gray-200'}`}>
                <div
                  className="h-full rounded-full bg-gradient-to-r from-amber-400 to-amber-500"
                  style={{ width: `${scorePercentage}%` }}
                />
              </div>
              <span className={`text-[10px] ${dark ? 'text-white/30' : 'text-gray-400'}`}>
                {scorePercentage.toFixed(0)}%
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
