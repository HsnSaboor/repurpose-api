"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Bot, Languages, Globe, AlertCircle, Zap } from 'lucide-react';
import { TranscriptMetadata } from '@/lib/api';

interface TranscriptStatusBadgeProps {
  metadata?: TranscriptMetadata;
  status?: 'analyzing' | 'found' | 'translating' | 'ready' | 'error';
  source?: string;
  confidence?: number;
  compact?: boolean;
}

export function TranscriptStatusBadge({ 
  metadata, 
  status, 
  source, 
  confidence, 
  compact = false 
}: TranscriptStatusBadgeProps) {
  // Extract info from metadata if provided
  const finalStatus = status || (metadata ? 'ready' : 'analyzing');
  const finalSource = source || (metadata ? 
    `${metadata.is_generated ? 'Auto' : 'Manual'} ${metadata.is_translated ? 'Translated' : metadata.language}` 
    : 'Unknown'
  );
  const finalConfidence = confidence || (metadata?.confidence_score ? Math.round(metadata.confidence_score * 100) : undefined);

  const getIcon = () => {
    switch (finalStatus) {
      case 'analyzing':
        return <Bot className=\"h-3 w-3 text-blue-500 animate-pulse\" />;
      case 'found':
        return <CheckCircle className=\"h-3 w-3 text-green-500\" />;
      case 'translating':
        return <Languages className=\"h-3 w-3 text-orange-500 animate-spin\" />;
      case 'ready':
        return <Zap className=\"h-3 w-3 text-green-600\" />;
      case 'error':
        return <AlertCircle className=\"h-3 w-3 text-red-500\" />;
      default:
        return <Globe className=\"h-3 w-3 text-gray-500\" />;
    }
  };

  const getVariant = () => {
    switch (finalStatus) {
      case 'found':
      case 'ready':
        return 'default' as const;
      case 'translating':
        return 'secondary' as const;
      case 'analyzing':
        return 'outline' as const;
      case 'error':
        return 'destructive' as const;
      default:
        return 'outline' as const;
    }
  };

  const getConfidenceColor = (conf?: number) => {
    if (!conf) return 'text-gray-500';
    if (conf >= 90) return 'text-green-600';
    if (conf >= 70) return 'text-blue-600';
    if (conf >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
      >
        <Badge variant={getVariant()} className=\"flex items-center gap-1 text-xs\">
          {getIcon()}
          {finalSource}
          {finalConfidence !== undefined && (
            <span className={getConfidenceColor(finalConfidence)}>
              {finalConfidence}%
            </span>
          )}
        </Badge>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className=\"flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border\"
    >
      <div className=\"flex items-center gap-3\">
        {getIcon()}
        <div>
          <div className=\"text-sm font-medium text-gray-700 dark:text-gray-300\">
            Transcript Status
          </div>
          <div className=\"text-xs text-gray-500 dark:text-gray-400\">
            {finalSource}
          </div>
        </div>
      </div>
      {finalConfidence !== undefined && (
        <div className=\"text-right\">
          <div className={`text-sm font-semibold ${
            getConfidenceColor(finalConfidence)
          }`}>
            {finalConfidence}%
          </div>
          <div className=\"text-xs text-gray-400\">
            Quality
          </div>
        </div>
      )}
    </motion.div>
  );
}

export default TranscriptStatusBadge;