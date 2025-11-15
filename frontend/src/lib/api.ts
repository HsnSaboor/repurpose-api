import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface VideoInfo {
  video_id: string;
  title: string;
  channel?: string;
  duration?: number;
  thumbnail?: string;
  view_count?: number;
}

export interface ContentIdea {
  content_type: string;
  title: string;
  target_audience: string;
  key_message: string;
  hook_strategy: string;
}

export interface ContentPiece {
  content_id: string;
  content_type: 'reel' | 'carousel' | 'tweet';
  title: string;
  hook?: string;
  script?: string;
  caption?: string;
  slides?: Array<{ heading: string; content: string }>;
  tweets?: string[];
  hashtags?: string[];
  call_to_action?: string;
}

export interface ProcessedVideo {
  id: number;
  youtube_video_id: string;
  title: string;
  transcript: string;
  status: string;
  thumbnail_url?: string;
  video_url?: string;
  created_at?: string;
  ideas: ContentIdea[];
  content_pieces: ContentPiece[];
}

export interface StylePreset {
  name: string;
  description: string;
  target_audience: string;
  call_to_action: string;
  content_goal: string;
  language: string;
  tone: string;
  additional_instructions?: string;
}

// API functions
export const getVideoInfo = async (videoId: string): Promise<VideoInfo> => {
  const response = await api.get(`/video-info?video_id=${videoId}`);
  return response.data;
};

export const processVideo = async (data: {
  video_id: string;
  style_preset?: string;
  force_regenerate?: boolean;
}): Promise<ProcessedVideo> => {
  const response = await api.post('/process-video/', data);
  return response.data;
};

export const getAllVideos = async (): Promise<{ videos: ProcessedVideo[]; total: number }> => {
  const response = await api.get('/videos/');
  return response.data;
};

export const getStylePresets = async (): Promise<{ presets: Record<string, StylePreset> }> => {
  const response = await api.get('/content-styles/presets/');
  return response.data;
};

export const getStylePreset = async (presetName: string): Promise<StylePreset> => {
  const response = await api.get(`/content-styles/presets/${presetName}`);
  return response.data;
};

export const editContent = async (data: {
  video_id: string;
  content_piece_id: string;
  content_type: string;
  edit_prompt: string;
}) => {
  const response = await api.post('/edit-content/', data);
  return response.data;
};
