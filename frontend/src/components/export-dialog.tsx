"use client";

import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ContentPiece } from '@/lib/api';
import { Download, FileText, Image, Share2, Copy, CheckCircle2, FileJson, FileType } from 'lucide-react';

interface ExportDialogProps {
  contentPieces: ContentPiece[];
  isOpen: boolean;
  onClose: () => void;
  singlePiece?: ContentPiece;
}

type ExportFormat = 'txt' | 'json' | 'csv' | 'md' | 'docx' | 'pdf';
type ExportScope = 'single' | 'selected' | 'all';

interface ExportOptions {
  format: ExportFormat;
  scope: ExportScope;
  selectedPieces: string[];
  includeMetadata: boolean;
  includeHashtags: boolean;
  includeTimestamp: boolean;
  customTemplate?: string;
}

const exportFormats = [
  { 
    value: 'txt' as ExportFormat, 
    label: 'Plain Text (.txt)', 
    description: 'Simple text format for easy copying',
    icon: FileText 
  },
  { 
    value: 'json' as ExportFormat, 
    label: 'JSON (.json)', 
    description: 'Structured data format for developers',
    icon: FileJson 
  },
  { 
    value: 'csv' as ExportFormat, 
    label: 'CSV (.csv)', 
    description: 'Spreadsheet format for data analysis',
    icon: FileType 
  },
  { 
    value: 'md' as ExportFormat, 
    label: 'Markdown (.md)', 
    description: 'Formatted text for documentation',
    icon: FileText 
  },
];

export default function ExportDialog({ contentPieces, isOpen, onClose, singlePiece }: ExportDialogProps) {
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'txt',
    scope: singlePiece ? 'single' : 'all',
    selectedPieces: singlePiece ? [singlePiece.content_id] : [],
    includeMetadata: true,
    includeHashtags: true,
    includeTimestamp: true,
  });
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  const handlePieceSelection = (contentId: string, checked: boolean) => {
    setExportOptions(prev => ({
      ...prev,
      selectedPieces: checked 
        ? [...prev.selectedPieces, contentId]
        : prev.selectedPieces.filter(id => id !== contentId)
    }));
  };

  const getContentText = (piece: ContentPiece): string => {
    switch (piece.content_type) {
      case 'reel':
        return `Hook: ${piece.hook || ''}\n\nScript:\n${piece.script_body || ''}${
          piece.visual_suggestions ? `\n\nVisual Suggestions:\n${piece.visual_suggestions}` : ''
        }`;
      case 'tweet':
        let tweetContent = piece.tweet_text || '';
        if (piece.thread_continuation && piece.thread_continuation.length > 0) {
          tweetContent += '\n\nThread:\n' + piece.thread_continuation.map((tweet, i) => `${i + 2}. ${tweet}`).join('\n');
        }
        return tweetContent;
      case 'image_carousel':
        return `Title: ${piece.title}\n\nCaption: ${piece.caption || ''}\n\nSlides:\n${
          piece.slides?.map(slide => `Slide ${slide.slide_number}: ${slide.step_heading}\n${slide.text}`).join('\n\n') || ''
        }`;
      default:
        return piece.title || '';
    }
  };

  const formatForExport = (pieces: ContentPiece[]): string => {
    const { format, includeMetadata, includeHashtags, includeTimestamp } = exportOptions;

    switch (format) {
      case 'txt':
        return pieces.map(piece => {
          let content = `=== ${piece.title} ===\n`;
          if (includeMetadata) {
            content += `Type: ${piece.content_type}\n`;
            content += `ID: ${piece.content_id}\n`;
          }
          if (includeTimestamp) {
            content += `Exported: ${new Date().toLocaleString()}\n`;
          }
          content += `\n${getContentText(piece)}\n`;
          if (includeHashtags && piece.hashtags) {
            content += `\nHashtags: ${piece.hashtags.map(tag => `#${tag}`).join(' ')}\n`;
          }
          return content;
        }).join('\n' + '='.repeat(50) + '\n\n');

      case 'json':
        return JSON.stringify(
          pieces.map(piece => ({
            ...(includeMetadata && {
              content_id: piece.content_id,
              content_type: piece.content_type,
              exported_at: includeTimestamp ? new Date().toISOString() : undefined,
            }),
            title: piece.title,
            content: getContentText(piece),
            ...(includeHashtags && piece.hashtags && { hashtags: piece.hashtags }),
          })),
          null,
          2
        );

      case 'csv':
        const headers = ['Title', 'Type', 'Content'];
        if (includeMetadata) headers.push('Content ID');
        if (includeHashtags) headers.push('Hashtags');
        if (includeTimestamp) headers.push('Exported At');
        
        const rows = pieces.map(piece => {
          const row = [
            `"${piece.title.replace(/"/g, '""')}"`,
            piece.content_type,
            `"${getContentText(piece).replace(/"/g, '""')}"`,
          ];
          if (includeMetadata) row.push(piece.content_id);
          if (includeHashtags) row.push(piece.hashtags ? piece.hashtags.join(', ') : '');
          if (includeTimestamp) row.push(new Date().toISOString());
          return row.join(',');
        });
        
        return [headers.join(','), ...rows].join('\n');

      case 'md':
        return pieces.map(piece => {
          let content = `# ${piece.title}\n\n`;
          if (includeMetadata) {
            content += `**Type:** ${piece.content_type}  \n`;
            content += `**ID:** ${piece.content_id}  \n`;
          }
          if (includeTimestamp) {
            content += `**Exported:** ${new Date().toLocaleString()}  \n`;
          }
          content += `\n${getContentText(piece)}\n\n`;
          if (includeHashtags && piece.hashtags) {
            content += `**Hashtags:** ${piece.hashtags.map(tag => `#${tag}`).join(' ')}\n\n`;
          }
          return content;
        }).join('---\n\n');

      default:
        return '';
    }
  };

  const getPiecesToExport = (): ContentPiece[] => {
    switch (exportOptions.scope) {
      case 'single':
        return singlePiece ? [singlePiece] : [];
      case 'selected':
        return contentPieces.filter(piece => exportOptions.selectedPieces.includes(piece.content_id));
      case 'all':
        return contentPieces;
      default:
        return [];
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const pieces = getPiecesToExport();
      const content = formatForExport(pieces);
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `content-export-${Date.now()}.${exportOptions.format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      setExportSuccess(true);
      setTimeout(() => {
        setExportSuccess(false);
        onClose();
      }, 2000);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleCopyToClipboard = async () => {
    try {
      const pieces = getPiecesToExport();
      const content = formatForExport(pieces);
      await navigator.clipboard.writeText(content);
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 2000);
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  const selectedPieces = getPiecesToExport();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Export Content
          </DialogTitle>
          <DialogDescription>
            Export your content pieces in various formats for different use cases
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Format Selection */}
          <div>
            <h3 className="text-lg font-medium mb-3">Export Format</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {exportFormats.map((format) => (
                <Card 
                  key={format.value}
                  className={`cursor-pointer transition-colors ${
                    exportOptions.format === format.value ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'
                  }`}
                  onClick={() => setExportOptions(prev => ({ ...prev, format: format.value }))}
                >
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <format.icon className="h-4 w-4" />
                      {format.label}
                    </CardTitle>
                    <CardDescription className="text-xs">
                      {format.description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>

          {/* Scope Selection */}
          {!singlePiece && (
            <div>
              <h3 className="text-lg font-medium mb-3">Export Scope</h3>
              <Select
                value={exportOptions.scope}
                onValueChange={(value: ExportScope) => 
                  setExportOptions(prev => ({ ...prev, scope: value, selectedPieces: value === 'all' ? [] : prev.selectedPieces }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Content Pieces ({contentPieces.length})</SelectItem>
                  <SelectItem value="selected">Selected Pieces Only</SelectItem>
                </SelectContent>
              </Select>

              {exportOptions.scope === 'selected' && (
                <div className="mt-3 space-y-2">
                  <p className="text-sm text-muted-foreground">Select content pieces to export:</p>
                  <div className="max-h-40 overflow-y-auto space-y-2">
                    {contentPieces.map((piece) => (
                      <div key={piece.content_id} className="flex items-center space-x-2">
                        <Checkbox
                          id={piece.content_id}
                          checked={exportOptions.selectedPieces.includes(piece.content_id)}
                          onCheckedChange={(checked: boolean) => handlePieceSelection(piece.content_id, checked)}
                        />
                        <label htmlFor={piece.content_id} className="text-sm flex items-center gap-2">
                          <Badge variant="outline">{piece.content_type}</Badge>
                          {piece.title}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Export Options */}
          <div>
            <h3 className="text-lg font-medium mb-3">Export Options</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="includeMetadata"
                  checked={exportOptions.includeMetadata}
                  onCheckedChange={(checked: boolean) => 
                    setExportOptions(prev => ({ ...prev, includeMetadata: checked }))
                  }
                />
                <label htmlFor="includeMetadata" className="text-sm">Include metadata (IDs, types)</label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="includeHashtags"
                  checked={exportOptions.includeHashtags}
                  onCheckedChange={(checked: boolean) => 
                    setExportOptions(prev => ({ ...prev, includeHashtags: checked }))
                  }
                />
                <label htmlFor="includeHashtags" className="text-sm">Include hashtags</label>
              </div>
              
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="includeTimestamp"
                  checked={exportOptions.includeTimestamp}
                  onCheckedChange={(checked: boolean) => 
                    setExportOptions(prev => ({ ...prev, includeTimestamp: checked }))
                  }
                />
                <label htmlFor="includeTimestamp" className="text-sm">Include export timestamp</label>
              </div>
            </div>
          </div>

          {/* Preview */}
          <div>
            <h3 className="text-lg font-medium mb-3">Preview</h3>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">
                  Export Preview ({selectedPieces.length} piece{selectedPieces.length !== 1 ? 's' : ''})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="max-h-40 overflow-y-auto">
                  <pre className="text-xs text-muted-foreground whitespace-pre-wrap">
                    {selectedPieces.length > 0 ? formatForExport(selectedPieces.slice(0, 1)) + 
                     (selectedPieces.length > 1 ? '\n\n... and more' : '') : 'No content selected'}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Success Alert */}
          {exportSuccess && (
            <Alert>
              <CheckCircle2 className="h-4 w-4" />
              <AlertDescription>
                Content exported successfully!
              </AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="outline" onClick={handleCopyToClipboard} disabled={selectedPieces.length === 0}>
            <Copy className="h-4 w-4 mr-2" />
            Copy to Clipboard
          </Button>
          <Button onClick={handleExport} disabled={isExporting || selectedPieces.length === 0}>
            <Download className="h-4 w-4 mr-2" />
            {isExporting ? 'Exporting...' : 'Download'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}