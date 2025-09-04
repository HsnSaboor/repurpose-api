import { ProcessVideoResponse } from './api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002';

export interface DatabaseVideo {
  id: number;
  youtube_video_id: string;
  title: string | null;
  transcript: string | null;
  status: string | null;
  thumbnail_url: string;
  video_url: string;
  created_at: string | null;
  ideas: any[];
  content_pieces: any[];
}

export interface DatabaseResponse {
  videos: DatabaseVideo[];
  total: number;
}

// Fetch all videos from database
export async function fetchAllVideos(): Promise<DatabaseResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/videos/`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch videos from database:', error);
    throw error;
  }
}

// Convert database video to ProcessVideoResponse format
export function convertDbVideoToProcessVideoResponse(dbVideo: DatabaseVideo): ProcessVideoResponse {
  return {
    id: dbVideo.id,
    youtube_video_id: dbVideo.youtube_video_id,
    title: dbVideo.title || undefined,
    transcript: dbVideo.transcript || undefined,
    status: dbVideo.status || undefined,
    thumbnail_url: dbVideo.thumbnail_url,
    video_url: dbVideo.video_url,
    ideas: dbVideo.ideas,
    content_pieces: dbVideo.content_pieces,
  };
}

// Real-time video processing with streaming
export function processVideoWithStreaming(
  videoId: string,
  options: {
    forceRegenerate?: boolean;
    stylePreset?: string;
    customStyle?: any;
  } = {},
  onProgress: (data: {
    status: string;
    message?: string;
    progress: number;
    data?: ProcessVideoResponse;
  }) => void
): () => void {
  const controller = new AbortController();

  const startStreaming = async () => {
    try {
      const requestBody = {
        video_id: videoId,
        force_regenerate: options.forceRegenerate || false,
        ...(options.stylePreset && { style_preset: options.stylePreset }),
        ...(options.customStyle && { custom_style: options.customStyle }),
      };

      const response = await fetch(`${API_BASE_URL}/process-video-stream/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Failed to get response reader');
      }

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onProgress(data);
            } catch (error) {
              console.error('Error parsing streaming data:', error);
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Streaming cancelled');
      } else {
        console.error('Streaming error:', error);
        onProgress({
          status: 'error',
          message: error instanceof Error ? error.message : 'Unknown error',
          progress: 0,
        });
      }
    }
  };

  startStreaming();

  // Return cleanup function
  return () => {
    controller.abort();
  };
}

// Database sync service for real-time updates
export class DatabaseSyncService {
  private syncInterval: NodeJS.Timeout | null = null;
  private lastSync: number = 0;
  private listeners: ((videos: DatabaseVideo[]) => void)[] = [];

  constructor(private intervalMs = 5000) {}

  start() {
    this.sync(); // Initial sync
    this.syncInterval = setInterval(() => {
      this.sync();
    }, this.intervalMs);
  }

  stop() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  addListener(callback: (videos: DatabaseVideo[]) => void) {
    this.listeners.push(callback);
  }

  removeListener(callback: (videos: DatabaseVideo[]) => void) {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  private async sync() {
    try {
      const result = await fetchAllVideos();
      this.lastSync = Date.now();
      
      // Notify all listeners
      this.listeners.forEach(listener => {
        try {
          listener(result.videos);
        } catch (error) {
          console.error('Error in sync listener:', error);
        }
      });
    } catch (error) {
      console.error('Database sync failed:', error);
    }
  }

  getLastSyncTime() {
    return this.lastSync;
  }
}

// Singleton instance
export const databaseSync = new DatabaseSyncService();