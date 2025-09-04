"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Clock, Play, FileText, Image, ExternalLink } from 'lucide-react';
import { ProcessVideoResponse } from '@/lib/api';
import { useAppStore } from '@/lib/app-store';
import { formatDistanceToNow } from 'date-fns';

interface RecentVideosProps {
  onVideoSelect: (video: ProcessVideoResponse) => void;
}

export default function RecentVideos({ onVideoSelect }: RecentVideosProps) {
  const { recentVideos } = useAppStore();

  if (!recentVideos || recentVideos.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card className="shadow-sm border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-4">
              <Clock className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No Recent Videos
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-sm">
              Process your first video to see it appear here. Recent videos will be automatically saved and synced.
            </p>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="space-y-4"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          Recent Videos
        </h2>
        <Badge variant="secondary" className="text-xs">
          {recentVideos.length} videos
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {recentVideos.map((video, index) => (
          <motion.div
            key={video.id || video.youtube_video_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Card 
              className="group hover:shadow-lg transition-all duration-300 cursor-pointer border-0 bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm hover:bg-white/90 dark:hover:bg-gray-800/90"
              onClick={() => onVideoSelect(video)}
            >
              <CardContent className="p-0">
                {/* Thumbnail Section */}
                <div className="relative aspect-video overflow-hidden rounded-t-lg bg-gray-100 dark:bg-gray-800">
                  {video.thumbnail_url ? (
                    <>
                      <img
                        src={video.thumbnail_url}
                        alt={video.title || 'Video thumbnail'}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.src = `https://img.youtube.com/vi/${video.youtube_video_id}/maxresdefault.jpg`;
                        }}
                      />
                      <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors duration-300" />
                      <div className="absolute top-2 right-2">
                        <Badge variant="secondary" className="text-xs">
                          <FileText className="h-3 w-3 mr-1" />
                          {video.content_pieces?.length || 0}
                        </Badge>
                      </div>
                      <div className="absolute bottom-2 right-2">
                        <Button
                          size="sm"
                          variant="secondary"
                          className="h-8 w-8 p-0 bg-white/90 hover:bg-white"
                          onClick={(e) => {
                            e.stopPropagation();
                            window.open(video.video_url || `https://youtube.com/watch?v=${video.youtube_video_id}`, '_blank');
                          }}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      </div>
                    </>
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Image className="h-12 w-12 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* Content Section */}
                <div className="p-4 space-y-3">
                  <div>
                    <h3 className="font-semibold text-sm line-clamp-2 text-gray-900 dark:text-white group-hover:text-primary transition-colors">
                      {video.title || `Video ${video.youtube_video_id}`}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      ID: {video.youtube_video_id}
                    </p>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <div className="flex items-center gap-3">
                      <span className="flex items-center gap-1">
                        <FileText className="h-3 w-3" />
                        {video.content_pieces?.length || 0} pieces
                      </span>
                      {video.status && (
                        <Badge 
                          variant={video.status === 'completed' ? 'default' : 'secondary'}
                          className="text-xs px-2 py-0"
                        >
                          {video.status}
                        </Badge>
                      )}
                    </div>
                  </div>

                  <Separator />

                  {/* Action Button */}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start h-8 text-xs group-hover:bg-primary/10"
                    onClick={(e) => {
                      e.stopPropagation();
                      onVideoSelect(video);
                    }}
                  >
                    <Play className="h-3 w-3 mr-2" />
                    View Content
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}