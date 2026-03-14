import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Loader2 } from 'lucide-react';
import SourcesPanel from '../components/SourcesPanel';
import { searchLaws, getAvailableLaws } from '../services/api';
import { useTheme } from '../components/Layout';

const searchSuggestions = [
  "Right to self defense",
  "Dowry prohibition",
  "Cybercrime penalties",
  "Motor vehicle accidents",
  "Property inheritance rights",
  "Bail provisions",
];

const SearchPage = () => {
  const { theme } = useTheme();
  const dark = theme === 'dark';
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (searchText) => {
    const q = searchText || query;
    if (!q.trim()) return;
    setQuery(q);
    setLoading(true);
    setSearched(true);
    try {
      const response = await searchLaws(q);
      setResults(response.results || []);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-4">
      <div className="max-w-4xl mx-auto py-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className={`text-3xl font-bold mb-2 ${dark ? 'text-white' : 'text-gray-900'}`}>Search Laws</h1>
          <p className={`text-sm ${dark ? 'text-white/40' : 'text-gray-500'}`}>
            Search across Indian Penal Code, CrPC, CPC, and more using AI-powered semantic search
          </p>
        </motion.div>

        {/* Search Bar */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className={`p-1.5 rounded-2xl mb-6 ${dark ? 'glass-card' : 'glass-card-light'}`}
        >
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className={`absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 ${dark ? 'text-white/30' : 'text-gray-400'}`} />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search for laws, sections, or legal topics..."
                className={`w-full pl-12 pr-4 py-4 text-sm rounded-xl ${dark ? 'glass-input' : 'glass-input-light'} border-0`}
              />
            </div>
            <button
              onClick={() => handleSearch()}
              disabled={!query.trim() || loading}
              className="px-8 py-4 btn-glow rounded-xl flex items-center gap-2 text-sm font-semibold"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              Search
            </button>
          </div>
        </motion.div>

        {/* Suggestions (before search) */}
        {!searched && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <p className={`text-xs font-medium mb-3 ${dark ? 'text-white/30' : 'text-gray-400'}`}>
              POPULAR SEARCHES
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {searchSuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSearch(suggestion)}
                  className="prompt-card text-left text-xs"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Results */}
        {searched && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div className="text-center">
                  <Loader2 className={`w-8 h-8 animate-spin mx-auto mb-3 ${dark ? 'text-amber-400' : 'text-amber-500'}`} />
                  <p className={`text-sm ${dark ? 'text-white/40' : 'text-gray-500'}`}>Searching through legal databases...</p>
                </div>
              </div>
            ) : results.length > 0 ? (
              <>
                <div className="flex items-center justify-between mb-4">
                  <p className={`text-sm font-medium ${dark ? 'text-white/50' : 'text-gray-600'}`}>
                    Found <span className={dark ? 'text-amber-400' : 'text-amber-600'}>{results.length}</span> results
                  </p>
                </div>
                <div className="grid gap-3">
                  {results.map((result, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={`p-5 rounded-2xl transition-all duration-300
                        ${dark ? 'glass-card glass-card-hover' : 'glass-card-light glass-card-hover-light'}`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`px-2.5 py-1 rounded-lg text-xs font-bold shrink-0
                          ${dark ? 'bg-amber-400/15 text-amber-400' : 'bg-amber-100 text-amber-700'}`}>
                          {result.law}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className={`text-sm font-semibold mb-1 ${dark ? 'text-white' : 'text-gray-900'}`}>
                            Section {result.section}
                          </div>
                          <div className={`text-xs mb-2 ${dark ? 'text-white/60' : 'text-gray-600'}`}>
                            {result.title}
                          </div>
                          {result.score && (
                            <div className="flex items-center gap-2">
                              <div className={`h-1.5 rounded-full flex-1 max-w-[120px] ${dark ? 'bg-white/10' : 'bg-gray-200'}`}>
                                <div
                                  className="h-full rounded-full bg-gradient-to-r from-amber-400 to-amber-500"
                                  style={{ width: `${(result.score * 100)}%` }}
                                />
                              </div>
                              <span className={`text-[10px] ${dark ? 'text-white/35' : 'text-gray-400'}`}>
                                {(result.score * 100).toFixed(0)}% match
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-20">
                <Search className={`w-12 h-12 mx-auto mb-3 ${dark ? 'text-white/15' : 'text-gray-300'}`} />
                <p className={`text-sm ${dark ? 'text-white/40' : 'text-gray-500'}`}>No results found. Try a different search term.</p>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
