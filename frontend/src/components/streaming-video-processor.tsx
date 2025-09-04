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
import { Upload, Play, Square, AlertCircle, CheckCircle, Youtube } from 'lucide-react';
import { ProcessVideoResponse, processVideo, StylePreset, getStylePresets } from '@/lib/api';
import { processVideoWithStreaming } from '@/lib/database-service';
import { useAppStore, useNotifications } from '@/lib/app-store';
import AnimatedLoading from './animated-loading';

interface StreamingVideoProcessorProps {
  onContentGenerated: (content: ProcessVideoResponse) => void;
}

interface ProgressState {
  status: string;
  message?: string;
  progress: number;
  isComplete: boolean;
  isError: boolean;
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
  });
  const [streamedContent, setStreamedContent] = useState<ProcessVideoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const { addRecentVideo } = useAppStore();
  const { showSuccess, showError } = useNotifications();
  const cancelStreamingRef = useRef<(() => void) | null>(null);

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
      'transcribing': 'Generating transcript...',
      'analyzing': 'Analyzing content for key themes...',
      'generating_ideas': 'Creating content ideas...',
      'creating_content': 'Generating final content pieces...',
      'saving': 'Saving content to database...',
      'complete': 'Processing complete!',
      'error': 'An error occurred during processing',
    };
    return messages[status] || status;
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
    });

    try {
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
          
          setProgressState({
            status: progressData.status,
            message,
            progress,
            isComplete: progressData.status === 'complete',
            isError: progressData.status === 'error',
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