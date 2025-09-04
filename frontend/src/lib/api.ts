// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002';

// Types
export interface CustomContentStyle {
  target_audience: string;
  call_to_action: string;
  content_goal: string;
  language: string;
  tone: string;
  additional_instructions?: string;
}

// Enhanced transcript types
export interface TranscriptPreferences {
  prefer_manual?: boolean;
  require_english?: boolean;
  enable_translation?: boolean;
  fallback_languages?: string[];
  preserve_formatting?: boolean;
}

export interface TranscriptMetadata {
  language_code: string;
  language: string;
  is_generated: boolean;
  is_translated: boolean;
  priority: string;
  translation_source_language?: string;
  confidence_score: number;
  processing_notes: string[];
}

export interface EnhancedTranscriptResponse {
  youtube_video_id: string;
  title?: string;
  transcript: string;
  transcript_metadata?: TranscriptMetadata;
  available_languages: string[];
  status?: string;
}

export interface TranscriptAnalysisResponse {
  youtube_video_id: string;
  available_transcripts: Array<{
    language_code: string;
    language: string;
    is_generated: boolean;
    is_translatable: boolean;
  }>;
  recommended_approach: string;
  processing_notes: string[];
}

export interface ProcessVideoRequest {
  video_id: string;
  force_regenerate?: boolean;
  style_preset?: string;
  custom_style?: CustomContentStyle;
}

export interface ContentPiece {
  content_id: string;
  content_type: 'reel' | 'image_carousel' | 'tweet';
  title: string;
  caption?: string;
  hook?: string;
  script_body?: string;
  tweet_text?: string;
  slides?: Array<{
    slide_number: number;
    step_number: number;
    step_heading: string;
    text: string;
  }>;
  visual_suggestions?: string;
  hashtags?: string[];
  thread_continuation?: string[];
}

export interface ProcessVideoResponse {
  id?: number;
  youtube_video_id: string;
  title?: string;
  transcript?: string;
  status?: string;
  thumbnail_url?: string;
  video_url?: string;
  ideas?: Array<{
    suggested_content_type: string;
    suggested_title: string;
    relevant_transcript_snippet: string;
  }>;
  content_pieces?: ContentPiece[];
}

export interface EditContentRequest {
  video_id: string;
  content_piece_id: string;
  edit_prompt: string;
  content_type: 'reel' | 'image_carousel' | 'tweet';
}

export interface EditContentResponse {
  success: boolean;
  content_piece_id: string;
  original_content?: ContentPiece;
  edited_content?: ContentPiece;
  changes_made?: string[];
  error_message?: string;
}

export interface StylePreset {
  name: string;
  description: string;
  target_audience: string;
  language: string;
  tone: string;
}

// API Error handling
interface ApiErrorDetail {
  loc?: (string | number)[];
  msg: string;
  type: string;
}

interface ApiErrorResponse {
  detail?: string | ApiErrorDetail[];
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetailMessage = `API Error (${response.status}): ${response.statusText}`;
    try {
      const errorData: ApiErrorResponse = await response.json();
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorDetailMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorDetailMessage = errorData.detail.map(err => `${err.loc?.join(' -> ')}: ${err.msg}`).join('; ');
        }
      }
    } catch (e) {
      // Response was not JSON or error parsing JSON
    }
    throw new Error(errorDetailMessage);
  }
  
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

// API Functions
export async function getStylePresets(): Promise<Record<string, StylePreset>> {
  const response = await fetch(`${API_BASE_URL}/content-styles/presets/`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });
  const data = await handleResponse<{presets: Record<string, StylePreset>}>(response);
  return data.presets;
}

export async function processVideo(options: ProcessVideoRequest): Promise<ProcessVideoResponse> {
  const response = await fetch(`${API_BASE_URL}/process-video/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(options),
  });
  return handleResponse<ProcessVideoResponse>(response);
}

export async function editContent(request: EditContentRequest): Promise<EditContentResponse> {
  const response = await fetch(`${API_BASE_URL}/edit-content/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(request),
  });
  return handleResponse<EditContentResponse>(response);
}

export async function transcribeVideo(videoId: string): Promise<{youtube_video_id: string; title?: string; transcript: string; status?: string}> {
  const response = await fetch(`${API_BASE_URL}/transcribe/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({ video_id: videoId }),
  });
  return handleResponse(response);
}

// Enhanced transcript functions
export async function transcribeVideoEnhanced(
  videoId: string, 
  preferences?: TranscriptPreferences
): Promise<EnhancedTranscriptResponse> {
  const requestBody: any = { video_id: videoId };
  if (preferences) {
    requestBody.preferences = preferences;
  }
  
  const response = await fetch(`${API_BASE_URL}/transcribe-enhanced/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });
  return handleResponse<EnhancedTranscriptResponse>(response);
}

export async function analyzeTranscripts(videoId: string): Promise<TranscriptAnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze-transcripts/${videoId}`, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });
  return handleResponse<TranscriptAnalysisResponse>(response);
}

// Helper function to get the best transcript processing approach
export async function getOptimalTranscriptApproach(videoId: string): Promise<{
  approach: string;
  confidence: string;
  notes: string[];
}> {
  try {
    const analysis = await analyzeTranscripts(videoId);
    
    const confidenceMap: Record<string, string> = {
      'manual_english': 'High',
      'auto_english': 'Good', 
      'manual_translated': 'Medium',
      'auto_translated': 'Low'
    };
    
    return {
      approach: analysis.recommended_approach,
      confidence: confidenceMap[analysis.recommended_approach] || 'Unknown',
      notes: analysis.processing_notes
    };
  } catch (error) {
    return {
      approach: 'unknown',
      confidence: 'Unknown',
      notes: [`Analysis failed: ${error}`]
    };
  }
}