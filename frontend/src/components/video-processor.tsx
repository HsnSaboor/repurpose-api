"use client";

import { useState, useCallback, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { processVideo, getStylePresets, ProcessVideoRequest, ProcessVideoResponse, StylePreset } from '@/lib/api';
import { Upload, Play, AlertCircle, CheckCircle2, Loader2, Youtube } from 'lucide-react';

interface VideoProcessorProps {
  onContentGenerated: (content: ProcessVideoResponse) => void;
}

export default function VideoProcessor({ onContentGenerated }: VideoProcessorProps) {
  const [videoUrl, setVideoUrl] = useState('');
  const [selectedPreset, setSelectedPreset] = useState<string>('none');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [stylePresets, setStylePresets] = useState<Record<string, StylePreset>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load style presets on component mount
  useState(() => {
    const loadPresets = async () => {
      try {
        const presets = await getStylePresets();
        setStylePresets(presets);
      } catch (err) {
        console.error('Failed to load style presets:', err);
      }
    };
    loadPresets();
  });

  const extractVideoId = (url: string): string | null => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
      /^[a-zA-Z0-9_-]{11}$/
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) {
        return match[1] || match[0];
      }
    }
    return null;
  };

  const handleVideoProcess = async () => {
    const videoId = extractVideoId(videoUrl);
    if (!videoId) {
      setError('Please enter a valid YouTube URL or video ID');
      return;
    }

    setIsProcessing(true);
    setError('');
    setProgress(0);
    setStatus('Initializing...');

    try {
      // Simulate progress updates
      const progressSteps = [
        'Fetching video information...',
        'Extracting transcript...',
        'Analyzing content...',
        'Generating content pieces...',
        'Finalizing...'
      ];

      for (let i = 0; i < progressSteps.length; i++) {
        setStatus(progressSteps[i]);
        setProgress(((i + 1) / progressSteps.length) * 80);
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      const options: ProcessVideoRequest = {
        video_id: videoId,
        force_regenerate: false,
      };

      if (selectedPreset && selectedPreset !== 'none') {
        options.style_preset = selectedPreset;
      }

      setStatus('Processing video...');
      setProgress(90);

      const result = await processVideo(options);
      
      setProgress(100);
      setStatus('Complete!');
      
      // Pass the generated content to parent component
      onContentGenerated(result);
      
      // Reset form
      setVideoUrl('');
      setSelectedPreset('none');
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process video');
    } finally {
      setIsProcessing(false);
      setTimeout(() => {
        setProgress(0);
        setStatus('');
      }, 2000);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const text = e.dataTransfer.getData('text');
    if (text) {
      setVideoUrl(text);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          YouTube Content Repurposer
        </h1>
        <p className="text-muted-foreground text-lg">
          Transform YouTube videos into engaging social media content with AI
        </p>
      </div>

      <Card className="bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-blue-900">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Youtube className="h-5 w-5 text-red-500" />
            Video Input
          </CardTitle>
          <CardDescription>
            Enter a YouTube URL or drag and drop a video link here
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Drag and Drop Area */}
          <div
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all ${
              isDragOver 
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-lg font-medium mb-2">Drop YouTube URL here</p>
            <p className="text-sm text-muted-foreground mb-4">
              Or paste a YouTube URL below
            </p>
            
            <div className="flex gap-2 max-w-md mx-auto">
              <Input
                placeholder="https://youtube.com/watch?v=... or video ID"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                className="flex-1"
              />
              <Button
                onClick={handleVideoProcess}
                disabled={!videoUrl || isProcessing}
                className="px-6"
              >
                {isProcessing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          {/* Style Preset Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Content Style (Optional)</label>
            <Select value={selectedPreset} onValueChange={setSelectedPreset}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a content style preset..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">No preset (default style)</SelectItem>
                {Object.entries(stylePresets).map(([key, preset]) => (
                  <SelectItem key={key} value={key}>
                    <div className="flex flex-col items-start">
                      <span className="font-medium">{preset.name}</span>
                      <span className="text-xs text-muted-foreground">{preset.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            {selectedPreset && selectedPreset !== 'none' && stylePresets[selectedPreset] && (
              <div className="flex flex-wrap gap-2 mt-2">
                <Badge variant="secondary">
                  {stylePresets[selectedPreset].language}
                </Badge>
                <Badge variant="outline">
                  {stylePresets[selectedPreset].tone}
                </Badge>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          {isProcessing && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Processing</span>
                <span className="text-sm text-muted-foreground">{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
              {status && (
                <p className="text-sm text-muted-foreground flex items-center gap-2">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  {status}
                </p>
              )}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Success Message */}
          {progress === 100 && !error && (
            <Alert>
              <CheckCircle2 className="h-4 w-4" />
              <AlertTitle>Success!</AlertTitle>
              <AlertDescription>
                Video processed successfully. Content pieces generated and ready for editing.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Quick Examples */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Quick Examples</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="font-medium mb-2">URL Formats:</p>
              <ul className="space-y-1 text-muted-foreground">
                <li>• https://youtube.com/watch?v=dQw4w9WgXcQ</li>
                <li>• https://youtu.be/dQw4w9WgXcQ</li>
                <li>• dQw4w9WgXcQ (video ID only)</li>
              </ul>
            </div>
            <div>
              <p className="font-medium mb-2">Content Types Generated:</p>
              <ul className="space-y-1 text-muted-foreground">
                <li>• Instagram Reels Scripts</li>
                <li>• Twitter Thread Content</li>
                <li>• Carousel Post Slides</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}