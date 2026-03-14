import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Scale, MessageSquare, Search, FileText, ArrowRight, Sparkles } from 'lucide-react';
import { useTheme } from '../components/Layout';

const features = [
  {
    icon: MessageSquare,
    title: 'Legal Chat',
    description: 'Ask any legal question and get AI-powered answers with relevant law citations.',
    path: '/chat',
    gradient: 'from-blue-500 to-cyan-500',
    shadowColor: 'shadow-blue-500/20',
  },
  {
    icon: Search,
    title: 'Search Laws',
    description: 'Search across IPC, CrPC, CPC, and more with semantic AI-powered search.',
    path: '/search',
    gradient: 'from-purple-500 to-pink-500',
    shadowColor: 'shadow-purple-500/20',
  },
  {
    icon: FileText,
    title: 'Document Analysis',
    description: 'Upload legal documents (PDF, DOCX, TXT) and ask questions about them.',
    path: '/document',
    gradient: 'from-emerald-500 to-teal-500',
    shadowColor: 'shadow-emerald-500/20',
  },
];

const quickStats = [
  { label: 'Indian Laws', value: '8+' },
  { label: 'AI Powered', value: 'LLM' },
  { label: 'Document Types', value: '3' },
  { label: 'Response Time', value: '<5s' },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.12 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
};

const HomePage = () => {
  const navigate = useNavigate();
  const { theme } = useTheme();
  const dark = theme === 'dark';

  return (
    <div className="h-full overflow-y-auto px-4 sm:px-6 lg:px-8 py-8">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-5xl mx-auto"
      >
        {/* Hero Section */}
        <motion.div variants={itemVariants} className="text-center mb-12 pt-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6 text-xs font-medium tracking-wider uppercase
            glass-card-sm text-amber-400">
            <Sparkles className="w-3.5 h-3.5" />
            AI-Powered Legal Intelligence
          </div>

          <h1 className={`text-4xl sm:text-5xl lg:text-6xl font-extrabold mb-5 leading-tight ${dark ? 'text-white' : 'text-gray-900'}`}>
            Your AI Legal
            <span className="block bg-gradient-to-r from-amber-400 via-amber-500 to-orange-500 bg-clip-text text-transparent">
              Assistant
            </span>
          </h1>

          <p className={`text-lg max-w-2xl mx-auto leading-relaxed ${dark ? 'text-white/50' : 'text-gray-500'}`}>
            Navigate Indian law with confidence. Get instant answers, search through legal codes,
            and analyze documents — all powered by advanced AI.
          </p>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate('/chat')}
            className="mt-8 inline-flex items-center gap-2 px-8 py-4 btn-glow text-base rounded-2xl"
          >
            Start Chatting
            <ArrowRight className="w-5 h-5" />
          </motion.button>
        </motion.div>

        {/* Quick Stats */}
        <motion.div variants={itemVariants} className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-12">
          {quickStats.map((stat) => (
            <div
              key={stat.label}
              className={`text-center py-4 px-3 rounded-2xl ${dark ? 'glass-card-sm' : 'glass-card-sm-light'}`}
            >
              <div className={`text-2xl font-bold ${dark ? 'text-amber-400' : 'text-amber-600'}`}>{stat.value}</div>
              <div className={`text-xs mt-1 ${dark ? 'text-white/40' : 'text-gray-500'}`}>{stat.label}</div>
            </div>
          ))}
        </motion.div>

        {/* Feature Cards */}
        <motion.div variants={itemVariants} className="grid md:grid-cols-3 gap-5 mb-12">
          {features.map((feature) => (
            <motion.div
              key={feature.title}
              whileHover={{ y: -6 }}
              onClick={() => navigate(feature.path)}
              className={`p-6 rounded-2xl cursor-pointer transition-all duration-300 group
                ${dark ? 'glass-card glass-card-hover' : 'glass-card-light glass-card-hover-light'}`}
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 shadow-lg ${feature.shadowColor}`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className={`text-lg font-semibold mb-2 ${dark ? 'text-white' : 'text-gray-900'}`}>{feature.title}</h3>
              <p className={`text-sm leading-relaxed mb-4 ${dark ? 'text-white/45' : 'text-gray-500'}`}>{feature.description}</p>
              <div className={`flex items-center gap-1 text-sm font-medium group-hover:gap-2 transition-all
                ${dark ? 'text-amber-400' : 'text-amber-600'}`}>
                Get Started <ArrowRight className="w-4 h-4" />
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Footer Note */}
        <motion.p variants={itemVariants} className={`text-center text-xs pb-8 ${dark ? 'text-white/25' : 'text-gray-400'}`}>
          Powered by Groq AI & Pinecone Vector Search • Made with ❤️ for Indian Legal Community
        </motion.p>
      </motion.div>
    </div>
  );
};

export default HomePage;
