"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import StreamingVideoProcessor from '@/components/streaming-video-processor';
import ContentViewer from '@/components/content-viewer';
import RecentVideos from '@/components/recent-videos';
import NotificationSystem from '@/components/notification-system';
import { ProcessVideoResponse } from '@/lib/api';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAppStore, useNotifications } from '@/lib/app-store';

export default function Home() {
  const { selectedTab, setSelectedTab, currentVideo, setCurrentVideo, initializeDatabaseSync, stopDatabaseSync, recentVideos } = useAppStore();
  const { showSuccess } = useNotifications();
  const [generatedContent, setGeneratedContent] = useState<ProcessVideoResponse | null>(currentVideo);

  // Initialize database sync on component mount
  useEffect(() => {
    initializeDatabaseSync();
    
    return () => {
      stopDatabaseSync();
    };
  }, [initializeDatabaseSync, stopDatabaseSync]);

  // Sync with global state
  useEffect(() => {
    if (currentVideo) {
      setGeneratedContent(currentVideo);
    }
  }, [currentVideo]);

  const handleContentGenerated = (content: ProcessVideoResponse) => {
    setGeneratedContent(content);
    setCurrentVideo(content);
    setSelectedTab('view'); // Auto-switch to view tab after generation
    showSuccess('Content Generated!', `Successfully created ${content.content_pieces?.length || 0} content pieces`);
  };

  const handleContentUpdated = (updatedContent: ProcessVideoResponse) => {
    setGeneratedContent(updatedContent);
    setCurrentVideo(updatedContent);
    showSuccess('Content Updated', 'Your changes have been saved');
  };

  const handleVideoSelect = (video: ProcessVideoResponse) => {
    setGeneratedContent(video);
    setCurrentVideo(video);
    setSelectedTab('view');
    showSuccess('Video Loaded', `Loaded "${video.title}" with ${video.content_pieces?.length || 0} content pieces`);
  };

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-blue-900 dark:to-indigo-900">
        <div className="container mx-auto py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
          <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
            <div className="flex justify-center">
              <TabsList className="grid w-full max-w-md grid-cols-2">
                <TabsTrigger value="process">Process Video</TabsTrigger>
                <TabsTrigger value="view" disabled={!generatedContent}>
                  View Content {generatedContent ? `(${generatedContent.content_pieces?.length || 0})` : ''}
                </TabsTrigger>
              </TabsList>
            </div>

            <AnimatePresence mode="wait">
              <TabsContent value="process" key="process">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="space-y-8">
                    <StreamingVideoProcessor onContentGenerated={handleContentGenerated} />
                    
                    {/* Recent Videos Section */}
                    {recentVideos && recentVideos.length > 0 && (
                      <RecentVideos onVideoSelect={handleVideoSelect} />
                    )}
                  </div>
                </motion.div>
              </TabsContent>

              <TabsContent value="view" key="view">
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                >
                  <ContentViewer 
                    content={generatedContent} 
                    onContentUpdated={handleContentUpdated}
                  />
                </motion.div>
              </TabsContent>
            </AnimatePresence>
          </Tabs>
          </motion.div>
        </div>
      </div>
      
      {/* Global Notification System */}
      <NotificationSystem />
    </>
  );
}
