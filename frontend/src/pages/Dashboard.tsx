import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllVideos, type ProcessedVideo } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [videos, setVideos] = useState<ProcessedVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    videosProcessed: 0,
    reelsGenerated: 0,
    carouselsGenerated: 0,
    tweetsGenerated: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await getAllVideos();
      setVideos(data.videos.slice(0, 8));
      
      // Calculate stats
      const reels = data.videos.reduce((sum, v) => sum + v.content_pieces.filter(p => p.content_type === 'reel').length, 0);
      const carousels = data.videos.reduce((sum, v) => sum + v.content_pieces.filter(p => p.content_type === 'carousel').length, 0);
      const tweets = data.videos.reduce((sum, v) => sum + v.content_pieces.filter(p => p.content_type === 'tweet').length, 0);
      
      setStats({
        videosProcessed: data.videos.length,
        reelsGenerated: reels,
        carouselsGenerated: carousels,
        tweetsGenerated: tweets,
      });
    } catch (error) {
      console.error('Failed to load videos:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyContent = (content: any) => {
    const text = content.script || content.caption || content.tweets?.join('\n\n') || '';
    navigator.clipboard.writeText(text);
    alert('Content copied to clipboard!');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-20 bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Content Repurposer</h1>
          <Button onClick={() => navigate('/process-video')} size="default">
            + New Video
          </Button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h2 className="text-4xl font-bold mb-2">Dashboard</h2>
          <p className="text-muted-foreground">Welcome back! Here's what's happening.</p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card hover className="cursor-pointer" onClick={() => navigate('/process-video')}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Process Video</h3>
                  <p className="text-muted-foreground">Transform a YouTube video into social media content</p>
                </div>
                <svg className="w-5 h-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </CardHeader>
          </Card>

          <Card hover className="cursor-pointer" onClick={() => navigate('/library')}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <div className="w-12 h-12 rounded-lg bg-carousel/10 flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-carousel" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Content Library</h3>
                  <p className="text-muted-foreground">Browse all your generated content</p>
                </div>
                <svg className="w-5 h-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </CardHeader>
          </Card>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Videos Processed', value: stats.videosProcessed, icon: '📹' },
            { label: 'Reels Generated', value: stats.reelsGenerated, icon: '🎬' },
            { label: 'Carousels Generated', value: stats.carouselsGenerated, icon: '🎨' },
            { label: 'Tweets Generated', value: stats.tweetsGenerated, icon: '🐦' },
          ].map((stat, i) => (
            <Card key={i}>
              <CardContent className="p-6 text-center">
                <div className="text-3xl mb-2">{stat.icon}</div>
                <div className="text-3xl font-bold mb-1">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Content */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-semibold">Recent Content</h3>
            <Button variant="ghost" onClick={() => navigate('/library')}>
              View All →
            </Button>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : videos.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="text-6xl mb-4">🎬</div>
                <h3 className="text-xl font-semibold mb-2">No content yet</h3>
                <p className="text-muted-foreground mb-6">Process your first video to get started</p>
                <Button onClick={() => navigate('/process-video')}>Process Video</Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {videos.flatMap(video => 
                video.content_pieces.slice(0, 2).map((content, idx) => (
                  <Card key={`${video.id}-${idx}`} hover>
                    <div className="aspect-video bg-muted rounded-t-lg flex items-center justify-center overflow-hidden">
                      {video.thumbnail_url ? (
                        <img src={video.thumbnail_url} alt={content.title} className="w-full h-full object-cover" />
                      ) : (
                        <div className="text-4xl">
                          {content.content_type === 'reel' ? '🎬' : content.content_type === 'carousel' ? '🎨' : '🐦'}
                        </div>
                      )}
                    </div>
                    <CardContent className="p-4">
                      <div className="mb-2">
                        <Badge variant={content.content_type as any}>{content.content_type}</Badge>
                      </div>
                      <h4 className="font-semibold mb-1 line-clamp-2 text-sm">{content.title}</h4>
                      <p className="text-xs text-muted-foreground font-mono mb-3">{content.content_id}</p>
                      <div className="flex gap-2">
                        <Button size="sm" variant="ghost" onClick={() => copyContent(content)} className="flex-1">
                          Copy
                        </Button>
                        <Button size="sm" variant="secondary" onClick={() => navigate(`/library?video=${video.youtube_video_id}`)} className="flex-1">
                          View
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ).slice(0, 8)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
