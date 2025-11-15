import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { getAllVideos, type ProcessedVideo, type ContentPiece } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';

export const ContentLibrary: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [videos, setVideos] = useState<ProcessedVideo[]>([]);
  const [filteredContent, setFilteredContent] = useState<Array<{ video: ProcessedVideo; content: ContentPiece }>>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [contentTypeFilter, setContentTypeFilter] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    filterContent();
  }, [videos, searchQuery, contentTypeFilter, searchParams]);

  const loadData = async () => {
    try {
      const data = await getAllVideos();
      setVideos(data.videos);
    } catch (error) {
      console.error('Failed to load videos:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterContent = () => {
    let allContent: Array<{ video: ProcessedVideo; content: ContentPiece }> = [];
    
    videos.forEach(video => {
      video.content_pieces.forEach(content => {
        allContent.push({ video, content });
      });
    });

    // Filter by video ID from URL params
    const videoIdParam = searchParams.get('video');
    if (videoIdParam) {
      allContent = allContent.filter(item => item.video.youtube_video_id === videoIdParam);
    }

    // Filter by content type
    if (contentTypeFilter !== 'all') {
      allContent = allContent.filter(item => item.content.content_type === contentTypeFilter);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      allContent = allContent.filter(item => 
        item.content.title.toLowerCase().includes(query) ||
        item.content.content_id.toLowerCase().includes(query) ||
        item.video.title.toLowerCase().includes(query)
      );
    }

    setFilteredContent(allContent);
  };

  const copyContent = (content: ContentPiece) => {
    let text = '';
    if (content.content_type === 'reel') {
      text = `${content.title}\n\n${content.hook || ''}\n\n${content.script || ''}\n\n${content.caption || ''}`;
    } else if (content.content_type === 'carousel') {
      text = `${content.title}\n\n${content.caption || ''}\n\nSlides:\n${content.slides?.map((s, i) => `${i + 1}. ${s.heading}\n${s.content}`).join('\n\n')}`;
    } else if (content.content_type === 'tweet') {
      text = content.tweets?.join('\n\n') || '';
    }
    
    navigator.clipboard.writeText(text);
    alert('Content copied to clipboard!');
  };

  const contentTypeCounts = {
    all: filteredContent.length,
    reel: filteredContent.filter(item => item.content.content_type === 'reel').length,
    carousel: filteredContent.filter(item => item.content.content_type === 'carousel').length,
    tweet: filteredContent.filter(item => item.content.content_type === 'tweet').length,
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
          <h2 className="text-4xl font-bold mb-2">Content Library</h2>
          <p className="text-muted-foreground">All your generated content in one place</p>
        </div>

        {/* Toolbar */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
              {/* Search */}
              <div className="flex-1 w-full sm:w-auto">
                <Input
                  placeholder="Search content..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="h-10"
                />
              </div>

              {/* Filters */}
              <select
                value={contentTypeFilter}
                onChange={(e) => setContentTypeFilter(e.target.value)}
                className="h-10 px-4 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="all">All Types ({contentTypeCounts.all})</option>
                <option value="reel">Reels ({contentTypeCounts.reel})</option>
                <option value="carousel">Carousels ({contentTypeCounts.carousel})</option>
                <option value="tweet">Tweets ({contentTypeCounts.tweet})</option>
              </select>

              {/* View Toggle */}
              <div className="flex gap-2">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'secondary'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                >
                  Grid
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'secondary'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                >
                  List
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Count */}
        <div className="mb-4">
          <p className="text-muted-foreground">
            {filteredContent.length} content {filteredContent.length === 1 ? 'piece' : 'pieces'}
          </p>
        </div>

        {/* Content Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : filteredContent.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <div className="text-6xl mb-4">📭</div>
              <h3 className="text-xl font-semibold mb-2">No content found</h3>
              <p className="text-muted-foreground mb-6">
                {searchQuery || contentTypeFilter !== 'all' 
                  ? 'Try adjusting your filters or search query'
                  : 'Process your first video to get started'}
              </p>
              {!searchQuery && contentTypeFilter === 'all' && (
                <Button onClick={() => navigate('/process-video')}>Process Video</Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
            : 'flex flex-col gap-4'
          }>
            {filteredContent.map(({ video, content }, idx) => (
              <Card key={`${content.content_id}-${idx}`} hover>
                <div className={viewMode === 'grid' ? '' : 'flex gap-4'}>
                  {/* Thumbnail */}
                  <div className={viewMode === 'grid' 
                    ? 'aspect-video bg-muted rounded-t-lg flex items-center justify-center overflow-hidden'
                    : 'w-32 aspect-video bg-muted rounded-l-lg flex items-center justify-center overflow-hidden flex-shrink-0'
                  }>
                    {video.thumbnail_url ? (
                      <img src={video.thumbnail_url} alt={content.title} className="w-full h-full object-cover" />
                    ) : (
                      <div className="text-4xl">
                        {content.content_type === 'reel' ? '🎬' : content.content_type === 'carousel' ? '🎨' : '🐦'}
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <CardContent className={viewMode === 'grid' ? 'p-4' : 'p-4 flex-1'}>
                    <div className="mb-2">
                      <Badge variant={content.content_type as any}>{content.content_type}</Badge>
                    </div>
                    <h4 className="font-semibold mb-1 line-clamp-2">{content.title}</h4>
                    <p className="text-sm text-muted-foreground mb-1 line-clamp-1">{video.title}</p>
                    <p className="text-xs text-muted-foreground font-mono mb-3">{content.content_id}</p>
                    <div className="flex gap-2">
                      <Button size="sm" variant="ghost" onClick={() => copyContent(content)} className="flex-1">
                        Copy
                      </Button>
                      <Button size="sm" variant="secondary" onClick={() => {/* Preview modal */}} className="flex-1">
                        Preview
                      </Button>
                    </div>
                  </CardContent>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
