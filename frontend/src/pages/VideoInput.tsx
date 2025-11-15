import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getVideoInfo, processVideo, getStylePresets, type StylePreset } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Input } from '../components/ui/Input';

export const VideoInput: React.FC = () => {
  const navigate = useNavigate();
  const [videoUrl, setVideoUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [videoInfo, setVideoInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const [stylePreset, setStylePreset] = useState('professional_business');
  const [presets, setPresets] = useState<Record<string, StylePreset>>({});

  useEffect(() => {
    loadPresets();
  }, []);

  const loadPresets = async () => {
    try {
      const data = await getStylePresets();
      setPresets(data.presets);
    } catch (error) {
      console.error('Failed to load presets:', error);
    }
  };

  const extractVideoId = (url: string): string | null => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
      /^([a-zA-Z0-9_-]{11})$/
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return match[1];
    }
    return null;
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setVideoUrl(url);
    setError('');
    
    const id = extractVideoId(url);
    if (id) {
      setVideoId(id);
    } else if (url) {
      setError('Please enter a valid YouTube URL');
    }
  };

  const handleFetchVideo = async () => {
    if (!videoId) return;
    
    setLoading(true);
    setError('');
    
    try {
      const info = await getVideoInfo(videoId);
      setVideoInfo(info);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch video information');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!videoId) return;
    
    setProcessing(true);
    setError('');
    
    try {
      await processVideo({
        video_id: videoId,
        style_preset: stylePreset,
        force_regenerate: false,
      });
      
      // Navigate to results
      navigate(`/library?video=${videoId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process video');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-20 bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Content Repurposer</h1>
          <Button variant="ghost" onClick={() => navigate('/')}>
            ← Back to Dashboard
          </Button>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h2 className="text-4xl font-bold mb-2">Process New Video</h2>
          <p className="text-muted-foreground">Transform YouTube videos into engaging social media content</p>
        </div>

        {/* Step 1: Video Input */}
        <Card className="mb-6">
          <CardHeader>
            <div className="bg-primary/5 border border-primary/20 rounded px-4 py-3 mb-6">
              <h3 className="text-lg font-semibold text-primary">Step 1: Video Input</h3>
            </div>
            
            <Input
              label="YouTube URL"
              value={videoUrl}
              onChange={handleUrlChange}
              placeholder="https://youtube.com/watch?v=..."
              error={error}
              helperText="Enter the URL of the video you want to process"
              required
            />

            {videoId && !videoInfo && (
              <div className="mt-4">
                <Button onClick={handleFetchVideo} loading={loading} disabled={loading}>
                  Fetch Video Info
                </Button>
              </div>
            )}
          </CardHeader>
        </Card>

        {/* Video Preview */}
        {videoInfo && (
          <Card className="mb-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <CardHeader>
              <h3 className="text-lg font-semibold mb-4">Video Preview</h3>
              <div className="flex gap-4">
                <img
                  src={`https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`}
                  alt={videoInfo.title}
                  className="w-48 aspect-video object-cover rounded-lg"
                />
                <div className="flex-1">
                  <h4 className="font-semibold mb-2">{videoInfo.title}</h4>
                  {videoInfo.channel && (
                    <p className="text-sm text-muted-foreground">Channel: {videoInfo.channel}</p>
                  )}
                  {videoInfo.duration && (
                    <p className="text-sm text-muted-foreground">Duration: {Math.floor(videoInfo.duration / 60)}:{String(videoInfo.duration % 60).padStart(2, '0')}</p>
                  )}
                </div>
              </div>
            </CardHeader>
          </Card>
        )}

        {/* Step 2: Content Style */}
        {videoInfo && (
          <Card className="mb-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <CardHeader>
              <div className="bg-primary/5 border border-primary/20 rounded px-4 py-3 mb-6">
                <h3 className="text-lg font-semibold text-primary">Step 2: Content Style</h3>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-foreground mb-2">
                  Style Preset
                </label>
                <select
                  value={stylePreset}
                  onChange={(e) => setStylePreset(e.target.value)}
                  className="w-full h-12 px-4 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  {Object.entries(presets).map(([key, preset]) => (
                    <option key={key} value={key}>
                      {preset.name}
                    </option>
                  ))}
                </select>
              </div>

              {presets[stylePreset] && (
                <div className="bg-muted rounded p-4 text-sm">
                  <p className="mb-2"><strong>Target Audience:</strong> {presets[stylePreset].target_audience}</p>
                  <p className="mb-2"><strong>Tone:</strong> {presets[stylePreset].tone}</p>
                  <p><strong>Language:</strong> {presets[stylePreset].language}</p>
                </div>
              )}
            </CardHeader>
          </Card>
        )}

        {/* Generate Button */}
        {videoInfo && (
          <div className="text-center">
            <Button
              size="lg"
              onClick={handleGenerate}
              loading={processing}
              disabled={processing}
              className="w-full sm:w-auto"
            >
              {processing ? 'Generating Content...' : 'Generate Content'}
            </Button>
          </div>
        )}

        {/* Processing Status */}
        {processing && (
          <Card className="mt-6">
            <CardContent className="p-6">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
                <h3 className="text-lg font-semibold mb-2">Processing Your Video</h3>
                <p className="text-muted-foreground">
                  This may take a few minutes. We're generating amazing content for you...
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
