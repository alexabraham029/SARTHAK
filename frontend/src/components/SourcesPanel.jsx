import React from 'react';
import { Book, ExternalLink } from 'lucide-react';

const SourceCard = ({ source }) => {
  return (
    <div className="border border-gray-200 rounded-lg p-3 bg-white hover:shadow-md transition-shadow">
      <div className="flex items-start gap-2">
        <Book className="w-4 h-4 text-orange-500 mt-1 flex-shrink-0" />
        <div className="flex-1">
          <div className="text-sm font-semibold text-gray-900">
            {source.law} Section {source.section}
          </div>
          <div className="text-xs text-gray-600 mt-1">
            {source.title}
          </div>
          {source.score && (
            <div className="text-xs text-gray-500 mt-2">
              Relevance: {(source.score * 100).toFixed(1)}%
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const SourcesPanel = ({ sources }) => {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 pt-3 border-t border-gray-200">
      <div className="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-1">
        <ExternalLink className="w-3 h-3" />
        Sources ({sources.length})
      </div>
      <div className="grid gap-2">
        {sources.map((source, index) => (
          <SourceCard key={index} source={source} />
        ))}
      </div>
    </div>
  );
};

export default SourcesPanel;
