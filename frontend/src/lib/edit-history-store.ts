import { create } from 'zustand';
import { ContentPiece } from '@/lib/api';

export interface EditHistoryEntry {
  id: string;
  timestamp: Date;
  description: string;
  contentBefore: ContentPiece;
  contentAfter: ContentPiece;
  changeType: 'manual_edit' | 'ai_edit' | 'style_change' | 'creation';
  prompt?: string;
}

interface EditHistoryStore {
  // History entries by content piece ID
  historyByContentId: Record<string, EditHistoryEntry[]>;
  
  // Actions
  addHistoryEntry: (contentId: string, entry: Omit<EditHistoryEntry, 'id' | 'timestamp'>) => void;
  getHistoryForContent: (contentId: string) => EditHistoryEntry[];
  clearHistory: (contentId: string) => void;
  clearAllHistory: () => void;
}

export const useEditHistoryStore = create<EditHistoryStore>((set, get) => ({
  historyByContentId: {},

  addHistoryEntry: (contentId: string, entry) => {
    const newEntry: EditHistoryEntry = {
      ...entry,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    };

    set((state) => ({
      historyByContentId: {
        ...state.historyByContentId,
        [contentId]: [
          newEntry,
          ...(state.historyByContentId[contentId] || []),
        ].slice(0, 50), // Keep only last 50 entries
      },
    }));
  },

  getHistoryForContent: (contentId: string) => {
    return get().historyByContentId[contentId] || [];
  },

  clearHistory: (contentId: string) => {
    set((state) => {
      const newHistoryByContentId = { ...state.historyByContentId };
      delete newHistoryByContentId[contentId];
      return { historyByContentId: newHistoryByContentId };
    });
  },

  clearAllHistory: () => {
    set({ historyByContentId: {} });
  },
}));

// Helper hook for managing edit history of a specific content piece
export const useContentEditHistory = (contentPiece: ContentPiece) => {
  const { historyByContentId, addHistoryEntry, getHistoryForContent, clearHistory } = useEditHistoryStore();
  
  const history = getHistoryForContent(contentPiece.content_id);

  const recordEdit = (
    contentAfter: ContentPiece,
    changeType: EditHistoryEntry['changeType'],
    description: string,
    prompt?: string
  ) => {
    addHistoryEntry(contentPiece.content_id, {
      description,
      contentBefore: contentPiece,
      contentAfter,
      changeType,
      prompt,
    });
  };

  const recordCreation = () => {
    addHistoryEntry(contentPiece.content_id, {
      description: 'Content piece created',
      contentBefore: contentPiece, // Same as after for creation
      contentAfter: contentPiece,
      changeType: 'creation',
    });
  };

  const recordAIEdit = (contentAfter: ContentPiece, prompt: string) => {
    recordEdit(contentAfter, 'ai_edit', 'AI-assisted edit', prompt);
  };

  const recordManualEdit = (contentAfter: ContentPiece, description: string = 'Manual edit') => {
    recordEdit(contentAfter, 'manual_edit', description);
  };

  const recordStyleChange = (contentAfter: ContentPiece, newStyle: string) => {
    recordEdit(contentAfter, 'style_change', `Style changed to ${newStyle}`);
  };

  return {
    history,
    recordEdit,
    recordCreation,
    recordAIEdit,
    recordManualEdit,
    recordStyleChange,
    clearHistory: () => clearHistory(contentPiece.content_id),
  };
};