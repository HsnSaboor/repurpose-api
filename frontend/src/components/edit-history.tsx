"use client";

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { History, RotateCcw, Clock, User, FileText, Eye, ArrowRight } from 'lucide-react';
import { ContentPiece } from '@/lib/api';

interface EditHistoryEntry {
  id: string;
  timestamp: Date;
  description: string;
  contentBefore: ContentPiece;
  contentAfter: ContentPiece;
  changeType: 'manual_edit' | 'ai_edit' | 'style_change' | 'creation';
  prompt?: string;
}

interface EditHistoryProps {
  contentPiece: ContentPiece;
  editHistory: EditHistoryEntry[];
  onRestore: (historyEntry: EditHistoryEntry) => void;
  isOpen: boolean;
  onClose: () => void;
}

interface HistoryTimelineProps {
  entries: EditHistoryEntry[];
  onViewDiff: (entry: EditHistoryEntry) => void;
  onRestore: (entry: EditHistoryEntry) => void;
  selectedEntry?: EditHistoryEntry | null;
}

interface DiffViewProps {
  before: ContentPiece;
  after: ContentPiece;
  changeType: string;
  prompt?: string;
}

function DiffView({ before, after, changeType, prompt }: DiffViewProps) {
  const getContentText = (content: ContentPiece): string => {
    switch (content.content_type) {
      case 'reel':
        return `Hook: ${content.hook || ''}\n\nScript: ${content.script_body || ''}`;
      case 'tweet':
        return content.tweet_text || '';
      case 'image_carousel':
        return `Title: ${content.title}\n\nCaption: ${content.caption || ''}\n\nSlides:\n${
          content.slides?.map(slide => `${slide.slide_number}. ${slide.step_heading}\n${slide.text}`).join('\n\n') || ''
        }`;
      default:
        return content.title || '';
    }
  };

  const beforeText = getContentText(before);
  const afterText = getContentText(after);

  // Simple diff highlighting (in a real app, you'd use a proper diff library)
  const highlightChanges = (text: string, isAfter: boolean) => {
    if (beforeText === afterText) return text;
    
    const lines = text.split('\n');
    const otherLines = (isAfter ? beforeText : afterText).split('\n');
    
    return lines.map((line, index) => {
      const isChanged = line !== (otherLines[index] || '');
      return (
        <div
          key={index}
          className={`${
            isChanged
              ? isAfter
                ? 'bg-green-100 dark:bg-green-900/30 border-l-4 border-green-500'
                : 'bg-red-100 dark:bg-red-900/30 border-l-4 border-red-500'
              : ''
          } px-2 py-1`}
        >
          {line || ' '}
        </div>
      );
    });
  };

  return (
    <div className="space-y-4">
      {prompt && (
        <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
          <p className="text-sm font-medium text-blue-900 dark:text-blue-100">Edit Prompt:</p>
          <p className="text-sm text-blue-800 dark:text-blue-200 mt-1">{prompt}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
            <span className="w-3 h-3 bg-red-500 rounded-full"></span>
            Before Changes
          </h4>
          <Card>
            <CardContent className="p-3">
              <div className="font-mono text-xs space-y-0">
                {highlightChanges(beforeText, false)}
              </div>
            </CardContent>
          </Card>
        </div>

        <div>
          <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
            <span className="w-3 h-3 bg-green-500 rounded-full"></span>
            After Changes
          </h4>
          <Card>
            <CardContent className="p-3">
              <div className="font-mono text-xs space-y-0">
                {highlightChanges(afterText, true)}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function HistoryTimeline({ entries, onViewDiff, onRestore, selectedEntry }: HistoryTimelineProps) {
  const getChangeIcon = (changeType: string) => {
    switch (changeType) {
      case 'creation':
        return <FileText className="h-4 w-4" />;
      case 'ai_edit':
        return <User className="h-4 w-4" />;
      case 'manual_edit':
        return <FileText className="h-4 w-4" />;
      case 'style_change':
        return <FileText className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getChangeColor = (changeType: string) => {
    switch (changeType) {
      case 'creation':
        return 'bg-blue-500';
      case 'ai_edit':
        return 'bg-purple-500';
      case 'manual_edit':
        return 'bg-green-500';
      case 'style_change':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <ScrollArea className="h-96">
      <div className="space-y-4 p-1">
        {entries.map((entry, index) => (
          <div key={entry.id} className="relative">
            {/* Timeline line */}
            {index < entries.length - 1 && (
              <div className="absolute left-4 top-8 w-px h-8 bg-gray-200 dark:bg-gray-700" />
            )}
            
            <div className={`flex items-start gap-3 p-3 rounded-lg border ${
              selectedEntry?.id === entry.id ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-200' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}>
              {/* Timeline dot */}
              <div className={`w-8 h-8 rounded-full ${getChangeColor(entry.changeType)} flex items-center justify-center text-white flex-shrink-0`}>
                {getChangeIcon(entry.changeType)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm font-medium">{entry.description}</p>
                  <time className="text-xs text-muted-foreground">
                    {entry.timestamp.toLocaleTimeString()}
                  </time>
                </div>
                
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="text-xs">
                    {entry.changeType.replace('_', ' ')}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {entry.timestamp.toLocaleDateString()}
                  </span>
                </div>

                {entry.prompt && (
                  <p className="text-xs text-muted-foreground mb-2 italic">
                    "{entry.prompt.substring(0, 100)}..."
                  </p>
                )}

                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onViewDiff(entry)}
                    className="h-7 px-2 text-xs"
                  >
                    <Eye className="h-3 w-3 mr-1" />
                    View Changes
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onRestore(entry)}
                    className="h-7 px-2 text-xs"
                  >
                    <RotateCcw className="h-3 w-3 mr-1" />
                    Restore
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}

export default function EditHistory({ contentPiece, editHistory, onRestore, isOpen, onClose }: EditHistoryProps) {
  const [selectedEntry, setSelectedEntry] = useState<EditHistoryEntry | null>(null);
  const [showDiff, setShowDiff] = useState(false);

  const handleViewDiff = (entry: EditHistoryEntry) => {
    setSelectedEntry(entry);
    setShowDiff(true);
  };

  const handleRestore = (entry: EditHistoryEntry) => {
    onRestore(entry);
    onClose();
  };

  const handleCloseDiff = () => {
    setShowDiff(false);
    setSelectedEntry(null);
  };

  return (
    <>
      {/* Main History Dialog */}
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              Edit History - {contentPiece.title}
            </DialogTitle>
            <DialogDescription>
              View and restore previous versions of this content piece
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {editHistory.length > 0 ? (
              <HistoryTimeline
                entries={editHistory}
                onViewDiff={handleViewDiff}
                onRestore={handleRestore}
                selectedEntry={selectedEntry}
              />
            ) : (
              <div className="text-center py-8">
                <History className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No Edit History</h3>
                <p className="text-muted-foreground">
                  This content piece hasn't been edited yet.
                </p>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Diff View Dialog */}
      {selectedEntry && (
        <Dialog open={showDiff} onOpenChange={handleCloseDiff}>
          <DialogContent className="max-w-6xl max-h-[80vh]">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <ArrowRight className="h-5 w-5" />
                Changes Made - {selectedEntry.description}
              </DialogTitle>
              <DialogDescription>
                Compare the before and after versions of the content
              </DialogDescription>
            </DialogHeader>

            <ScrollArea className="max-h-96">
              <DiffView
                before={selectedEntry.contentBefore}
                after={selectedEntry.contentAfter}
                changeType={selectedEntry.changeType}
                prompt={selectedEntry.prompt}
              />
            </ScrollArea>

            <DialogFooter>
              <Button variant="outline" onClick={handleCloseDiff}>
                Close
              </Button>
              <Button onClick={() => handleRestore(selectedEntry)}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Restore This Version
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}