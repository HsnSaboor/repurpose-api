"use client";

import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Upload, Play, Square, AlertCircle, CheckCircle, Youtube, Globe, Bot, Languages, Zap } from 'lucide-react';
import { ProcessVideoResponse, processVideo, StylePreset, getStylePresets, transcribeVideoEnhanced, analyzeTranscripts, TranscriptMetadata } from '@/lib/api';
import { processVideoWithStreaming } from '@/lib/database-service';
import { useAppStore, useNotifications } from '@/lib/app-store';
import AnimatedLoading from './animated-loading';
import TranscriptStatusBadge from './transcript-status-badge';

interface StreamingVideoProcessorProps {
  onContentGenerated: (content: ProcessVideoResponse) => void;
}

interface ProgressState {
  status: string;
  message?: string;
  progress: number;
  isComplete: boolean;
  isError: boolean;
  transcriptStatus?: {
    type: 'analyzing' | 'found' | 'translating' | 'ready' | 'error';
    metadata?: TranscriptMetadata;
    source?: string;
    confidence?: number;
  };
}

export default function StreamingVideoProcessor({ onContentGenerated }: StreamingVideoProcessorProps) {
  const [videoUrl, setVideoUrl] = useState('');
  const [selectedStyle, setSelectedStyle] = useState<string>('none');
  const [forceRegenerate, setForceRegenerate] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [stylePresets, setStylePresets] = useState<Record<string, StylePreset>>({});
  const [progressState, setProgressState] = useState<ProgressState>({
    status: 'idle',
    progress: 0,
    isComplete: false,
    isError: false,
    transcriptStatus: undefined,
  });
  const [streamedContent, setStreamedContent] = useState<ProcessVideoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [transcriptPreview, setTranscriptPreview] = useState<{
    available: boolean;
    analysis?: any;
    loading: boolean;
  }>({ available: false, loading: false });
  
  const { addRecentVideo } = useAppStore();
  const { showSuccess, showError } = useNotifications();
  const cancelStreamingRef = useRef<(() => void) | null>(null);

  // Preview transcript analysis when URL changes
  useEffect(() => {
    const checkTranscripts = async () => {
      if (!videoUrl.trim()) {
        setTranscriptPreview({ available: false, loading: false });
        return;
      }
      
      const videoId = getVideoIdFromUrl(videoUrl.trim());
      if (!videoId) {
        setTranscriptPreview({ available: false, loading: false });
        return;
      }
      
      setTranscriptPreview({ available: false, loading: true });
      
      try {
        const analysis = await analyzeTranscripts(videoId);
        setTranscriptPreview({
          available: true,
          analysis,
          loading: false
        });
      } catch (error) {
        setTranscriptPreview({ available: false, loading: false });
      }
    };
    
    // Debounce the analysis call
    const timeoutId = setTimeout(checkTranscripts, 1000);
    return () => clearTimeout(timeoutId);
  }, [videoUrl]);

  // Load style presets on component mount
  useEffect(() => {
    const loadStylePresets = async () => {
      try {
        const presets = await getStylePresets();
        setStylePresets(presets);
      } catch (error) {
        console.error('Failed to load style presets:', error);
      }
    };
    
    loadStylePresets();
  }, []);

  const getVideoIdFromUrl = (url: string): string | null => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
      /^([a-zA-Z0-9_-]{11})$/
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return match[1];
    }
    return null;
  };

  const getProgressMessage = (status: string): string => {
    const messages: Record<string, string> = {
      'starting': 'Initializing video processing...',
      'searching': 'Searching video from YouTube...',
      'transcribing': 'Analyzing available transcripts...',
      'transcript_ready': 'English transcript ready for processing',
      'analyzing': 'Analyzing content for key themes...',
      'generating_ideas': 'Creating content ideas...',
      'creating_content': 'Generating final content pieces...',
      'saving': 'Saving content to database...',
      'complete': 'Processing complete!',
      'error': 'An error occurred during processing',
    };
    return messages[status] || status;
  };

  const getTranscriptStatusInfo = (status: string, message?: string) => {
    // Enhanced transcript status detection
    if (status === 'transcribing' || message?.toLowerCase().includes('transcript')) {
      if (message?.includes('manual English')) {
        return {
          type: 'found' as const,
          source: 'Manual English',
          confidence: 100
        };
      } else if (message?.includes('auto-generated English')) {
        return {
          type: 'found' as const,
          source: 'Auto-generated English', 
          confidence: 80
        };
      } else if (message?.includes('translating') || message?.includes('translated')) {
        return {
          type: 'translating' as const,
          source: 'Translation in progress',
          confidence: 70
        };
      } else if (message?.includes('ready')) {
        return {
          type: 'ready' as const,
          source: 'English transcript ready',
          confidence: 90
        };
      } else {
        return {
          type: 'analyzing' as const,
          source: 'Analyzing transcripts',
          confidence: 50
        };
      }
    }
    return undefined;
  };

  const getTranscriptIcon = (transcriptStatus?: ProgressState['transcriptStatus']) => {
    if (!transcriptStatus) return null;
    
    switch (transcriptStatus.type) {
      case 'analyzing':
        return <Bot className="h-4 w-4 text-blue-500 animate-pulse" />;
      case 'found':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'translating':
        return <Languages className="h-4 w-4 text-orange-500 animate-spin" />;
      case 'ready':
        return <Zap className="h-4 w-4 text-green-600" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Globe className="h-4 w-4 text-gray-500" />;
    }
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-gray-500';
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 70) return 'text-blue-600';
    if (confidence >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  const getProgressValue = (status: string): number => {
    const progressMap: Record<string, number> = {
      'starting': 5,
      'searching': 20,
      'transcribing': 40,
      'analyzing': 60,
      'generating_ideas': 75,
      'creating_content': 90,
      'saving': 95,
      'complete': 100,
      'error': 0,
    };
    return progressMap[status] || 0;
  };

  const analyzeTranscriptsBefore = async (videoId: string) => {
    try {
      setProgressState(prev => ({
        ...prev,
        transcriptStatus: {
          type: 'analyzing',
          source: 'Analyzing available transcripts...',
          confidence: 0
        }
      }));

      const analysis = await analyzeTranscripts(videoId);
      
      // Update progress with transcript analysis results
      const confidenceMap: Record<string, number> = {
        'manual_english': 100,
        'auto_english': 80,
        'manual_translated': 70,
        'auto_translated': 50
      };
      
      const confidence = confidenceMap[analysis.recommended_approach] || 50;
      const sourceMap: Record<string, string> = {
        'manual_english': 'Manual English (Optimal)',
        'auto_english': 'Auto-generated English (Good)',
        'manual_translated': 'Manual + Translation (Medium)',
        'auto_translated': 'Auto-generated + Translation (Basic)'
      };
      
      setProgressState(prev => ({
        ...prev,
        transcriptStatus: {
          type: 'found',
          source: sourceMap[analysis.recommended_approach] || 'Available',
          confidence
        }
      }));
      
      return analysis;
    } catch (error) {
      console.error('Transcript analysis failed:', error);
      setProgressState(prev => ({
        ...prev,
        transcriptStatus: {
          type: 'error',
          source: 'Analysis failed',
          confidence: 0
        }
      }));
      return null;
    }
  };

  const handleProcess = async () => {
    if (!videoUrl.trim()) {
      setError('Please enter a YouTube URL or video ID');
      return;
    }

    const videoId = getVideoIdFromUrl(videoUrl.trim());
    if (!videoId) {
      setError('Invalid YouTube URL or video ID format');
      return;
    }

    // Reset state
    setError(null);
    setIsProcessing(true);
    setStreamedContent(null);
    setProgressState({
      status: 'starting',
      progress: 5,
      isComplete: false,
      isError: false,
      transcriptStatus: undefined,
    });

    try {
      // First, analyze available transcripts
      await analyzeTranscriptsBefore(videoId);
      
      // Start streaming process
      const cleanup = processVideoWithStreaming(
        videoId,
        {
          forceRegenerate,
          stylePreset: selectedStyle !== 'none' ? selectedStyle : undefined,
        },
        (progressData) => {
          const progress = progressData.progress || getProgressValue(progressData.status);
          const message = progressData.message || getProgressMessage(progressData.status);
          
          // Detect and update transcript status
          const transcriptStatus = getTranscriptStatusInfo(progressData.status, message) || 
                                 progressState.transcriptStatus;
          
          setProgressState({
            status: progressData.status,
            message,
            progress,
            isComplete: progressData.status === 'complete',
            isError: progressData.status === 'error',
            transcriptStatus,
          });

          // If we received the final data
          if (progressData.data && progressData.status === 'complete') {
            setStreamedContent(progressData.data);
            onContentGenerated(progressData.data);
            addRecentVideo(videoUrl);
            showSuccess('Video Processed!', `Successfully processed video and generated ${progressData.data.content_pieces?.length || 0} content pieces`);
          }

          // Handle errors
          if (progressData.status === 'error') {
            setError(progressData.message || 'Processing failed');
            showError('Processing Failed', progressData.message || 'An unknown error occurred');
          }
        }
      );

      cancelStreamingRef.current = cleanup;

    } catch (err) {
      console.error('Processing error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      showError('Processing Error', err instanceof Error ? err.message : 'An unexpected error occurred');
      setProgressState(prev => ({
        ...prev,
        status: 'error',
        isError: true,
      }));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCancel = () => {
    if (cancelStreamingRef.current) {
      cancelStreamingRef.current();
      cancelStreamingRef.current = null;
    }
    
    setIsProcessing(false);
    setProgressState({
      status: 'cancelled',
      progress: 0,
      isComplete: false,
      isError: false,
    });
    showError('Processing Cancelled', 'Video processing was cancelled by user');
  };

  const isValidUrl = videoUrl.trim() && getVideoIdFromUrl(videoUrl.trim());

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-4xl mx-auto space-y-6"
    >
      <Card className="shadow-lg border-0 bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900 dark:text-white flex items-center justify-center gap-2">
            <Youtube className="h-6 w-6 text-red-500" />
            YouTube Content Repurposer
          </CardTitle>
          <CardDescription className="text-gray-600 dark:text-gray-300">
            Transform YouTube videos into engaging content with real-time processing
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* URL Input */}
          <div className="space-y-2">
            <Label htmlFor="video-url" className="text-sm font-medium">
              YouTube URL or Video ID
            </Label>
            <div className="flex gap-2">
              <Input
                id="video-url"
                type="text"
                placeholder="https://youtube.com/watch?v=... or video ID"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                className="flex-1"
                disabled={isProcessing}
              />
              <Button
                onClick={handleProcess}
                disabled={!isValidUrl || isProcessing}
                className="px-6"
              >
                {isProcessing ? (
                  <>
                    <Square className="h-4 w-4 mr-2" />
                    Cancel
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Process
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Transcript Preview */}
          {(transcriptPreview.available || transcriptPreview.loading) && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ duration: 0.3 }}
              className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg"
            >
              <div className="flex items-center gap-2 mb-2">
                <Globe className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                  Transcript Analysis
                </span>
              </div>
              
              {transcriptPreview.loading ? (
                <div className="flex items-center gap-2 text-sm text-blue-600">
                  <AnimatedLoading size="sm" />
                  Analyzing available transcripts...
                </div>
              ) : transcriptPreview.analysis ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-blue-700 dark:text-blue-300">
                      Recommended approach: <strong>
                        {transcriptPreview.analysis.recommended_approach.replace('_', ' ')}
                      </strong>
                    </span>
                    <div className="flex items-center gap-1">
                      {transcriptPreview.analysis.recommended_approach === 'manual_english' && (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      )}
                      {transcriptPreview.analysis.recommended_approach === 'auto_english' && (
                        <Bot className="h-4 w-4 text-blue-500" />
                      )}
                      {transcriptPreview.analysis.recommended_approach.includes('translated') && (
                        <Languages className="h-4 w-4 text-orange-500" />
                      )}
                    </div>
                  </div>
                  
                  <div className="text-xs text-blue-600 dark:text-blue-400">
                    Available: {transcriptPreview.analysis.available_transcripts?.map(
                      (t: any) => `${t.language} (${t.is_generated ? 'auto' : 'manual'})`
                    ).join(', ')}
                  </div>
                  
                  {transcriptPreview.analysis.processing_notes?.length > 0 && (
                    <div className="text-xs text-blue-500 dark:text-blue-400">
                      {transcriptPreview.analysis.processing_notes[0]}
                    </div>
                  )}
                </div>
              ) : null}
            </motion.div>
          )}

          {/* Processing Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="style-select" className="text-sm font-medium">
                Content Style
              </Label>
              <Select value={selectedStyle} onValueChange={setSelectedStyle} disabled={isProcessing}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a style..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Default Style</SelectItem>
                  {Object.entries(stylePresets).map(([key, preset]) => (
                    <SelectItem key={key} value={key}>
                      {preset.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2 flex items-end">
              <div className="flex items-center space-x-2">
                <Switch
                  id="force-regenerate"
                  checked={forceRegenerate}
                  onCheckedChange={setForceRegenerate}
                  disabled={isProcessing}
                />
                <Label htmlFor="force-regenerate" className="text-sm">
                  Force Regenerate
                </Label>
              </div>
            </div>
          </div>

          {/* Progress Section */}
          {isProcessing && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              <Separator />
              
              <div className="space-y-3">
                {/* Main progress */}
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {progressState.message || getProgressMessage(progressState.status)}
                  </span>
                  <span className="text-sm text-gray-500">
                    {Math.round(progressState.progress)}%
                  </span>
                </div>
                
                <Progress 
                  value={progressState.progress} 
                  className="h-2"
                />
                
                {/* Transcript Status Indicator */}
                {progressState.transcriptStatus && (
                  <TranscriptStatusBadge
                    status={progressState.transcriptStatus.type}
                    source={progressState.transcriptStatus.source}
                    confidence={progressState.transcriptStatus.confidence}
                  />
                )}
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    {progressState.isError ? (
                      <>
                        <AlertCircle className="h-4 w-4 text-red-500" />
                        Processing failed
                      </>
                    ) : progressState.isComplete ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        Processing complete
                      </>
                    ) : (
                      <>
                        <AnimatedLoading size="sm" />
                        Processing...
                      </>
                    )}
                  </div>
                  
                  {isProcessing && !progressState.isComplete && !progressState.isError && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCancel}
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* Error Display */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            </motion.div>
          )}

          {/* Success Display */}
          {streamedContent && progressState.isComplete && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Alert className="border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800 dark:text-green-200">
                  Successfully processed "{streamedContent.title}" and generated {streamedContent.content_pieces?.length || 0} content pieces!
                </AlertDescription>
              </Alert>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}