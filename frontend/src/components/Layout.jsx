import React, { createContext, useContext, useState, useEffect } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Scale, MessageSquare, Search, FileText, Home, Sun, Moon, Menu, X } from 'lucide-react';

// Theme context
const ThemeContext = createContext();
export const useTheme = () => useContext(ThemeContext);

const navItems = [
  { to: '/', icon: Home, label: 'Home' },
  { to: '/chat', icon: MessageSquare, label: 'Legal Chat' },
  { to: '/search', icon: Search, label: 'Search Laws' },
  { to: '/document', icon: FileText, label: 'Documents' },
];

const Layout = () => {
  const [theme, setTheme] = useState(() => localStorage.getItem('sarthak-theme') || 'dark');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    localStorage.setItem('sarthak-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');

  const bgClass = theme === 'dark'
    ? 'app-background'
    : 'app-background-light';

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div className={`${bgClass} flex h-screen overflow-hidden`}>
        {/* Desktop Sidebar */}
        <aside className={`hidden md:flex flex-col w-72 ${theme === 'dark' ? 'glass-sidebar' : 'glass-sidebar-light'} z-20`}>
          {/* Logo */}
          <div className="p-6 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
                <Scale className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className={`text-xl font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Sarthak</h1>
                <p className={`text-[11px] font-medium tracking-wider uppercase ${theme === 'dark' ? 'text-white/40' : 'text-gray-500'}`}>
                  AI Legal Assistant
                </p>
              </div>
            </div>
            <div className={`mt-5 ${theme === 'dark' ? 'accent-line' : 'accent-line-light'}`} />
          </div>

          {/* Nav Links */}
          <nav className="flex-1 px-4 space-y-1.5">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 border border-transparent
                  ${isActive
                    ? theme === 'dark'
                      ? 'nav-active text-amber-400'
                      : 'nav-active-light text-amber-700'
                    : theme === 'dark'
                      ? 'text-white/50 hover:text-white/80 hover:bg-white/5'
                      : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/60'
                  }`
                }
              >
                <Icon className="w-5 h-5 nav-icon" />
                {label}
              </NavLink>
            ))}
          </nav>

          {/* Theme Toggle */}
          <div className="p-4">
            <button
              onClick={toggleTheme}
              className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300
                ${theme === 'dark'
                  ? 'btn-glass text-white/60 hover:text-white'
                  : 'btn-glass-light text-gray-500 hover:text-gray-800'
                }`}
            >
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
            </button>
          </div>
        </aside>

        {/* Mobile Header */}
        <div className="md:hidden fixed top-0 left-0 right-0 z-30">
          <div className={`flex items-center justify-between px-4 py-3 ${theme === 'dark' ? 'glass-sidebar' : 'glass-sidebar-light'}`}>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center">
                <Scale className="w-4 h-4 text-white" />
              </div>
              <span className={`font-bold ${theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Sarthak</span>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={toggleTheme} className={`p-2 rounded-lg ${theme === 'dark' ? 'text-white/60' : 'text-gray-500'}`}>
                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
              <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className={`p-2 rounded-lg ${theme === 'dark' ? 'text-white/60' : 'text-gray-500'}`}>
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Mobile Nav Dropdown */}
          <AnimatePresence>
            {mobileMenuOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className={`${theme === 'dark' ? 'glass-sidebar' : 'glass-sidebar-light'} border-t ${theme === 'dark' ? 'border-white/10' : 'border-gray-200'}`}
              >
                <nav className="p-3 space-y-1">
                  {navItems.map(({ to, icon: Icon, label }) => (
                    <NavLink
                      key={to}
                      to={to}
                      end={to === '/'}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all
                        ${isActive
                          ? theme === 'dark' ? 'nav-active text-amber-400' : 'nav-active-light text-amber-700'
                          : theme === 'dark' ? 'text-white/60' : 'text-gray-500'
                        }`
                      }
                    >
                      <Icon className="w-5 h-5" />
                      {label}
                    </NavLink>
                  ))}
                </nav>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Main Content */}
        <main className="flex-1 overflow-hidden relative z-10 pt-14 md:pt-0">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="h-full"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </ThemeContext.Provider>
  );
};

export default Layout;
