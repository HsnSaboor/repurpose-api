"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ProcessVideoResponse, ContentPiece, editContent, EditContentRequest } from '@/lib/api';
import { Edit3, Copy, Download, Eye, History, Instagram, Twitter, FileImage, Sparkles, Save, X, ExternalLink, Youtube, Play } from 'lucide-react';
import EditHistory from './edit-history';
import { EditHistoryEntry } from '@/lib/edit-history-store';
import ExportDialog from './export-dialog';
import { useContentEditHistory } from '@/lib/edit-history-store';

interface ContentViewerProps {
  content: ProcessVideoResponse | null;
  onContentUpdated: (updatedContent: ProcessVideoResponse) => void;
}

interface EditModalProps {
  contentPiece: ContentPiece;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedContent: ContentPiece) => void;
  videoId: string;
}

function EditModal({ contentPiece, isOpen, onClose, onSave, videoId }: EditModalProps) {
  const [editPrompt, setEditPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleEdit = async () => {
    if (!editPrompt.trim()) {
      setError('Please enter edit instructions');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const request: EditContentRequest = {
        video_id: videoId,
        content_piece_id: contentPiece.content_id,
        edit_prompt: editPrompt,
        content_type: contentPiece.content_type
      };

      const result = await editContent(request);
      
      if (result.success && result.edited_content) {
        onSave(result.edited_content);
        setEditPrompt('');
        onClose();
      } else {
        setError(result.error_message || 'Edit failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to edit content');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Edit3 className="h-5 w-5" />
            Edit Content Piece
          </DialogTitle>
          <DialogDescription>
            Describe how you'd like to modify this {contentPiece.content_type} content
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Current Content Preview:</label>
            <div className="mt-2 p-3 bg-muted rounded-lg text-sm">
              {contentPiece.content_type === 'reel' && (
                <div>
                  <strong>Hook:</strong> {contentPiece.hook}<br />
                  <strong>Script:</strong> {contentPiece.script_body?.substring(0, 100)}...
                </div>
              )}
              {contentPiece.content_type === 'tweet' && (
                <div>{contentPiece.tweet_text}</div>
              )}
              {contentPiece.content_type === 'image_carousel' && (
                <div>
                  <strong>Title:</strong> {contentPiece.title}<br />
                  <strong>Slides:</strong> {contentPiece.slides?.length || 0} slides
                </div>
              )}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium">Edit Instructions:</label>
            <Textarea
              value={editPrompt}
              onChange={(e) => setEditPrompt(e.target.value)}
              placeholder="E.g., 'Make it more engaging and add emojis', 'Change the tone to be more professional', 'Make it shorter and punchier'"
              className="mt-2 min-h-[100px]"
            />
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleEdit} disabled={isLoading || !editPrompt.trim()}>
            {isLoading ? 'Processing...' : 'Apply Changes'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function ContentPieceCard({ contentPiece, onEdit, onCopy, onExport, onViewHistory }: {
  contentPiece: ContentPiece;
  onEdit: () => void;
  onCopy: () => void;
  onExport: () => void;
  onViewHistory: () => void;
}) {
  const getIcon = () => {
    switch (contentPiece.content_type) {
      case 'reel':
        return <Instagram className="h-4 w-4" />;
      case 'tweet':
        return <Twitter className="h-4 w-4" />;
      case 'image_carousel':
        return <FileImage className="h-4 w-4" />;
      default:
        return <Sparkles className="h-4 w-4" />;
    }
  };

  const getTypeLabel = () => {
    switch (contentPiece.content_type) {
      case 'reel':
        return 'Instagram Reel';
      case 'tweet':
        return 'Twitter Thread';
      case 'image_carousel':
        return 'Carousel Post';
      default:
        return 'Content';
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getIcon()}
            <Badge variant="secondary">{getTypeLabel()}</Badge>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="sm" onClick={onEdit}>
              <Edit3 className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onViewHistory}>
              <History className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onCopy}>
              <Copy className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onExport}>
              <Download className="h-3 w-3" />
            </Button>
          </div>
        </div>
        <CardTitle className="text-lg">{contentPiece.title}</CardTitle>
      </CardHeader>
      
      <CardContent>
        {contentPiece.content_type === 'reel' && (
          <div className="space-y-3">
            <div>
              <strong className="text-sm">Hook:</strong>
              <p className="text-sm text-muted-foreground mt-1">{contentPiece.hook}</p>
            </div>
            <div>
              <strong className="text-sm">Script:</strong>
              <p className="text-sm text-muted-foreground mt-1 line-clamp-3">{contentPiece.script_body}</p>
            </div>
            {contentPiece.visual_suggestions && (
              <div>
                <strong className="text-sm">Visual Suggestions:</strong>
                <p className="text-sm text-muted-foreground mt-1">{contentPiece.visual_suggestions}</p>
              </div>
            )}
          </div>
        )}

        {contentPiece.content_type === 'tweet' && (
          <div className="space-y-3">
            <div>
              <strong className="text-sm">Tweet Text:</strong>
              <p className="text-sm text-muted-foreground mt-1">{contentPiece.tweet_text}</p>
            </div>
            {contentPiece.thread_continuation && contentPiece.thread_continuation.length > 0 && (
              <div>
                <strong className="text-sm">Thread ({contentPiece.thread_continuation.length} tweets):</strong>
                <div className="mt-1 space-y-2">
                  {contentPiece.thread_continuation.slice(0, 2).map((tweet, index) => (
                    <p key={index} className="text-sm text-muted-foreground p-2 bg-muted rounded">
                      {index + 2}. {tweet}
                    </p>
                  ))}
                  {contentPiece.thread_continuation.length > 2 && (
                    <p className="text-xs text-muted-foreground">
                      +{contentPiece.thread_continuation.length - 2} more tweets...
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {contentPiece.content_type === 'image_carousel' && (
          <div className="space-y-3">
            {contentPiece.caption && (
              <div>
                <strong className="text-sm">Caption:</strong>
                <p className="text-sm text-muted-foreground mt-1">{contentPiece.caption}</p>
              </div>
            )}
            <div>
              <strong className="text-sm">Slides ({contentPiece.slides?.length || 0}):</strong>
              <div className="mt-1 space-y-2">
                {contentPiece.slides?.slice(0, 3).map((slide, index) => (
                  <div key={index} className="p-2 bg-muted rounded text-sm">
                    <strong>Slide {slide.slide_number}:</strong> {slide.step_heading}
                    <p className="text-muted-foreground">{slide.text.substring(0, 80)}...</p>
                  </div>
                ))}
                {(contentPiece.slides?.length || 0) > 3 && (
                  <p className="text-xs text-muted-foreground">
                    +{(contentPiece.slides?.length || 0) - 3} more slides...
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {contentPiece.hashtags && contentPiece.hashtags.length > 0 && (
          <div className="mt-3 pt-3 border-t">
            <strong className="text-sm">Hashtags:</strong>
            <div className="flex flex-wrap gap-1 mt-1">
              {contentPiece.hashtags.slice(0, 5).map((tag, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  #{tag}
                </Badge>
              ))}
              {contentPiece.hashtags.length > 5 && (
                <Badge variant="outline" className="text-xs">
                  +{contentPiece.hashtags.length - 5} more
                </Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function ContentViewer({ content, onContentUpdated }: ContentViewerProps) {
  const [editingPiece, setEditingPiece] = useState<ContentPiece | null>(null);
  const [viewingHistoryPiece, setViewingHistoryPiece] = useState<ContentPiece | null>(null);
  const [exportingPiece, setExportingPiece] = useState<ContentPiece | null>(null);
  const [showBulkExport, setShowBulkExport] = useState(false);
  const [currentContent, setCurrentContent] = useState<ProcessVideoResponse | null>(content);

  useEffect(() => {
    setCurrentContent(content);
  }, [content]);

  if (!currentContent) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card className="text-center py-12">
          <CardContent>
            <Eye className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No Content Yet</h3>
            <p className="text-muted-foreground">
              Process a YouTube video above to generate content pieces
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleEditContent = (contentPiece: ContentPiece) => {
    setEditingPiece(contentPiece);
  };

  const handleViewHistory = (contentPiece: ContentPiece) => {
    setViewingHistoryPiece(contentPiece);
  };

  const handleRestoreFromHistory = (historyEntry: EditHistoryEntry) => {
    if (!currentContent.content_pieces) return;

    const restoredContent = historyEntry.contentAfter;
    const updatedPieces = currentContent.content_pieces.map(piece =>
      piece.content_id === restoredContent.content_id ? restoredContent : piece
    );

    const updatedResponse = {
      ...currentContent,
      content_pieces: updatedPieces
    };

    setCurrentContent(updatedResponse);
    onContentUpdated(updatedResponse);
    setViewingHistoryPiece(null);
  };

  const handleSaveEdit = (updatedContent: ContentPiece) => {
    if (!currentContent.content_pieces) return;

    const updatedPieces = currentContent.content_pieces.map(piece =>
      piece.content_id === updatedContent.content_id ? updatedContent : piece
    );

    const updatedResponse = {
      ...currentContent,
      content_pieces: updatedPieces
    };

    setCurrentContent(updatedResponse);
    onContentUpdated(updatedResponse);
  };

  const handleCopyContent = async (contentPiece: ContentPiece) => {
    let textToCopy = '';
    
    switch (contentPiece.content_type) {
      case 'reel':
        textToCopy = `Hook: ${contentPiece.hook}\n\nScript:\n${contentPiece.script_body}`;
        break;
      case 'tweet':
        textToCopy = contentPiece.tweet_text || '';
        if (contentPiece.thread_continuation) {
          textToCopy += '\n\nThread:\n' + contentPiece.thread_continuation.join('\n\n');
        }
        break;
      case 'image_carousel':
        textToCopy = `${contentPiece.title}\n\n${contentPiece.caption}\n\nSlides:\n`;
        contentPiece.slides?.forEach(slide => {
          textToCopy += `${slide.slide_number}. ${slide.step_heading}\n${slide.text}\n\n`;
        });
        break;
    }

    if (contentPiece.hashtags) {
      textToCopy += '\n\nHashtags: ' + contentPiece.hashtags.map(tag => `#${tag}`).join(' ');
    }

    try {
      await navigator.clipboard.writeText(textToCopy);
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy content:', err);
    }
  };

  const handleExportContent = (contentPiece: ContentPiece) => {
    setExportingPiece(contentPiece);
  };

  const contentPiecesByType = {
    reel: currentContent.content_pieces?.filter(p => p.content_type === 'reel') || [],
    tweet: currentContent.content_pieces?.filter(p => p.content_type === 'tweet') || [],
    image_carousel: currentContent.content_pieces?.filter(p => p.content_type === 'image_carousel') || []
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Video Information with Thumbnail */}
      <Card className="overflow-hidden">
        <CardContent className="p-0">
          <div className="flex flex-col md:flex-row">
            {/* Thumbnail Section */}
            <div className="md:w-80 aspect-video bg-gray-100 dark:bg-gray-800 relative">
              {currentContent.thumbnail_url ? (
                <>
                  <img
                    src={currentContent.thumbnail_url}
                    alt={currentContent.title || 'Video thumbnail'}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = `https://img.youtube.com/vi/${currentContent.youtube_video_id}/maxresdefault.jpg`;
                    }}
                  />
                  <div className="absolute inset-0 bg-black/20" />
                  <div className="absolute top-4 left-4">
                    <Badge className="bg-red-600 hover:bg-red-700">
                      <Youtube className="h-3 w-3 mr-1" />
                      YouTube
                    </Badge>
                  </div>
                  <div className="absolute bottom-4 right-4">
                    <Button
                      size="sm"
                      variant="secondary"
                      className="bg-white/90 hover:bg-white"
                      onClick={() => {
                        const url = currentContent.video_url || `https://youtube.com/watch?v=${currentContent.youtube_video_id}`;
                        window.open(url, '_blank');
                      }}
                    >
                      <Play className="h-4 w-4 mr-1" />
                      Watch
                    </Button>
                  </div>
                </>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center text-gray-400">
                    <Youtube className="h-12 w-12 mx-auto mb-2" />
                    <p className="text-sm">No thumbnail available</p>
                  </div>
                </div>
              )}
            </div>
            
            {/* Content Info Section */}
            <div className="flex-1 p-6">
              <div className="space-y-4">
                <div>
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <Youtube className="h-4 w-4" />
                    <span>Video ID: {currentContent.youtube_video_id}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={() => {
                        const url = `https://youtube.com/watch?v=${currentContent.youtube_video_id}`;
                        window.open(url, '_blank');
                      }}
                    >
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                  </div>
                  
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white leading-tight">
                    {currentContent.title || 'Untitled Video'}
                  </h1>
                </div>
                
                <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-300">
                  <div className="flex items-center gap-1">
                    <Sparkles className="h-4 w-4" />
                    <span>{currentContent.content_pieces?.length || 0} content pieces generated</span>
                  </div>
                  
                  {currentContent.status && (
                    <Badge variant={currentContent.status === 'completed' ? 'default' : 'secondary'}>
                      {currentContent.status}
                    </Badge>
                  )}
                </div>
                
                <div className="flex items-center gap-2">
                  {currentContent.content_pieces && currentContent.content_pieces.length > 0 && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowBulkExport(true)}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Export All Content
                    </Button>
                  )}
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      const url = currentContent.video_url || `https://youtube.com/watch?v=${currentContent.youtube_video_id}`;
                      window.open(url, '_blank');
                    }}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View Original
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Content Tabs */}
      <Tabs defaultValue="all" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">All ({currentContent.content_pieces?.length || 0})</TabsTrigger>
          <TabsTrigger value="reels">
            <Instagram className="h-4 w-4 mr-1" />
            Reels ({contentPiecesByType.reel.length})
          </TabsTrigger>
          <TabsTrigger value="tweets">
            <Twitter className="h-4 w-4 mr-1" />
            Tweets ({contentPiecesByType.tweet.length})
          </TabsTrigger>
          <TabsTrigger value="carousels">
            <FileImage className="h-4 w-4 mr-1" />
            Carousels ({contentPiecesByType.image_carousel.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {currentContent.content_pieces?.map((piece) => (
              <ContentPieceCard
                key={piece.content_id}
                contentPiece={piece}
                onEdit={() => handleEditContent(piece)}
                onViewHistory={() => handleViewHistory(piece)}
                onCopy={() => handleCopyContent(piece)}
                onExport={() => handleExportContent(piece)}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="reels">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {contentPiecesByType.reel.map((piece) => (
              <ContentPieceCard
                key={piece.content_id}
                contentPiece={piece}
                onEdit={() => handleEditContent(piece)}
                onViewHistory={() => handleViewHistory(piece)}
                onCopy={() => handleCopyContent(piece)}
                onExport={() => handleExportContent(piece)}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="tweets">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {contentPiecesByType.tweet.map((piece) => (
              <ContentPieceCard
                key={piece.content_id}
                contentPiece={piece}
                onEdit={() => handleEditContent(piece)}
                onViewHistory={() => handleViewHistory(piece)}
                onCopy={() => handleCopyContent(piece)}
                onExport={() => handleExportContent(piece)}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="carousels">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {contentPiecesByType.image_carousel.map((piece) => (
              <ContentPieceCard
                key={piece.content_id}
                contentPiece={piece}
                onEdit={() => handleEditContent(piece)}
                onViewHistory={() => handleViewHistory(piece)}
                onCopy={() => handleCopyContent(piece)}
                onExport={() => handleExportContent(piece)}
              />
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Edit Modal */}
      {editingPiece && (
        <EditModal
          contentPiece={editingPiece}
          isOpen={!!editingPiece}
          onClose={() => setEditingPiece(null)}
          onSave={handleSaveEdit}
          videoId={currentContent.youtube_video_id}
        />
      )}

      {/* Edit History Modal */}
      {viewingHistoryPiece && (
        <EditHistory
          contentPiece={viewingHistoryPiece}
          editHistory={[]}
          onRestore={handleRestoreFromHistory}
          isOpen={!!viewingHistoryPiece}
          onClose={() => setViewingHistoryPiece(null)}
        />
      )}

      {/* Single Export Dialog */}
      {exportingPiece && (
        <ExportDialog
          contentPieces={[exportingPiece]}
          singlePiece={exportingPiece}
          isOpen={!!exportingPiece}
          onClose={() => setExportingPiece(null)}
        />
      )}

      {/* Bulk Export Dialog */}
      <ExportDialog
        contentPieces={currentContent?.content_pieces || []}
        isOpen={showBulkExport}
        onClose={() => setShowBulkExport(false)}
      />
    </div>
  );
}