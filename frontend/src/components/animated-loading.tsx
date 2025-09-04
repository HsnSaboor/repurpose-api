"use client";

import { motion } from 'framer-motion';
import { Loader2, Sparkles, Zap } from 'lucide-react';

interface AnimatedLoadingProps {
  type?: 'spinner' | 'dots' | 'pulse' | 'sparkles';
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
};

const SpinnerLoader = ({ size = 'md' }: { size: string }) => (
  <motion.div
    animate={{ rotate: 360 }}
    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
  >
    <Loader2 className={`${sizeClasses[size as keyof typeof sizeClasses]} text-primary`} />
  </motion.div>
);

const DotsLoader = ({ size = 'md' }: { size: string }) => {
  const dotSize = size === 'sm' ? 'w-1 h-1' : size === 'md' ? 'w-1.5 h-1.5' : 'w-2 h-2';
  
  return (
    <div className="flex space-x-1">
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          animate={{
            y: [0, -8, 0],
            opacity: [0.7, 1, 0.7],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: index * 0.2,
            ease: "easeInOut",
          }}
          className={`${dotSize} bg-primary rounded-full`}
        />
      ))}
    </div>
  );
};

const PulseLoader = ({ size = 'md' }: { size: string }) => (
  <motion.div
    animate={{
      scale: [1, 1.2, 1],
      opacity: [0.7, 1, 0.7],
    }}
    transition={{
      duration: 1.5,
      repeat: Infinity,
      ease: "easeInOut",
    }}
    className={`${sizeClasses[size as keyof typeof sizeClasses]} bg-primary rounded-full`}
  />
);

const SparklesLoader = ({ size = 'md' }: { size: string }) => (
  <div className="relative">
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
      className={`${sizeClasses[size as keyof typeof sizeClasses]} text-primary flex items-center justify-center`}
    >
      <Sparkles className="w-full h-full" />
    </motion.div>
    <motion.div
      animate={{ rotate: -360 }}
      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
      className="absolute inset-0 flex items-center justify-center"
    >
      <Zap className={`${sizeClasses[size as keyof typeof sizeClasses]} text-purple-500 opacity-60`} />
    </motion.div>
  </div>
);

export default function AnimatedLoading({ 
  type = 'spinner', 
  size = 'md', 
  message, 
  className = '' 
}: AnimatedLoadingProps) {
  const renderLoader = () => {
    switch (type) {
      case 'dots':
        return <DotsLoader size={size} />;
      case 'pulse':
        return <PulseLoader size={size} />;
      case 'sparkles':
        return <SparklesLoader size={size} />;
      default:
        return <SpinnerLoader size={size} />;
    }
  };

  return (
    <div className={`flex flex-col items-center justify-center space-y-3 ${className}`}>
      {renderLoader()}
      {message && (
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-sm text-muted-foreground text-center"
        >
          {message}
        </motion.p>
      )}
    </div>
  );
}

// Specialized loading component for content generation
export function ContentGenerationLoader({ message = "Generating amazing content..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        className="relative"
      >
        <div className="w-16 h-16 border-4 border-primary/20 rounded-full" />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 w-16 h-16 border-4 border-primary border-t-transparent rounded-full"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="absolute inset-2 w-12 h-12 border-4 border-purple-500/30 rounded-full"
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <Sparkles className="w-6 h-6 text-primary" />
        </div>
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="text-center space-y-2"
      >
        <h3 className="text-lg font-semibold">Creating Content</h3>
        <motion.p
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="text-muted-foreground"
        >
          {message}
        </motion.p>
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="flex space-x-1"
      >
        {["🎬", "✨", "📝", "🚀"].map((emoji, index) => (
          <motion.span
            key={index}
            animate={{
              y: [0, -5, 0],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: index * 0.3,
              ease: "easeInOut",
            }}
            className="text-lg"
          >
            {emoji}
          </motion.span>
        ))}
      </motion.div>
    </div>
  );
}