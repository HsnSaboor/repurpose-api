import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ProcessVideoResponse, ContentPiece, StylePreset } from './api';
import { DatabaseVideo, databaseSync, convertDbVideoToProcessVideoResponse } from './database-service';

export interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  autoSaveEnabled: boolean;
  notificationsEnabled: boolean;
  defaultExportFormat: 'txt' | 'json' | 'csv' | 'md';
  recentVideoUrls: string[];
  favoriteStylePresets: string[];
}

export interface AppNotification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  timestamp: Date;
}

interface AppStore {
  // Current state
  isLoading: boolean;
  currentVideo: ProcessVideoResponse | null;
  selectedTab: string;
  
  // Database videos
  allVideos: ProcessVideoResponse[];
  recentVideos: ProcessVideoResponse[];
  
  // Settings
  settings: AppSettings;
  
  // Notifications
  notifications: AppNotification[];
  
  // UI State
  sidebarOpen: boolean;
  
  // Actions
  setLoading: (loading: boolean) => void;
  setCurrentVideo: (video: ProcessVideoResponse | null) => void;
  setSelectedTab: (tab: string) => void;
  updateSettings: (settings: Partial<AppSettings>) => void;
  addNotification: (notification: Omit<AppNotification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  setSidebarOpen: (open: boolean) => void;
  
  // Database sync
  updateAllVideos: (videos: DatabaseVideo[]) => void;
  initializeDatabaseSync: () => void;
  stopDatabaseSync: () => void;
  
  // Recent videos
  addRecentVideo: (url: string) => void;
  addFavoritePreset: (presetName: string) => void;
  removeFavoritePreset: (presetName: string) => void;
}

const defaultSettings: AppSettings = {
  theme: 'system',
  autoSaveEnabled: true,
  notificationsEnabled: true,
  defaultExportFormat: 'txt',
  recentVideoUrls: [],
  favoriteStylePresets: [],
};

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Initial state
      isLoading: false,
      currentVideo: null,
      selectedTab: 'process',
      allVideos: [],
      recentVideos: [],
      settings: defaultSettings,
      notifications: [],
      sidebarOpen: false,

      // Actions
      setLoading: (loading) => set({ isLoading: loading }),
      
      setCurrentVideo: (video) => set({ currentVideo: video }),
      
      setSelectedTab: (tab) => set({ selectedTab: tab }),
      
      updateSettings: (newSettings) => 
        set((state) => ({
          settings: { ...state.settings, ...newSettings }
        })),

      addNotification: (notification) => {
        const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const newNotification: AppNotification = {
          ...notification,
          id,
          timestamp: new Date(),
          duration: notification.duration || (notification.type === 'error' ? 8000 : 4000),
        };
        
        set((state) => ({
          notifications: [newNotification, ...state.notifications].slice(0, 10) // Keep only 10 notifications
        }));

        // Auto-remove notification after duration
        if (newNotification.duration && newNotification.duration > 0) {
          setTimeout(() => {
            get().removeNotification(id);
          }, newNotification.duration);
        }
      },

      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id)
        })),

      clearNotifications: () => set({ notifications: [] }),

      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      // Database sync
      updateAllVideos: (videos) => {
        const convertedVideos = videos.map(convertDbVideoToProcessVideoResponse);
        const recentVideos = convertedVideos
          .filter(v => v.content_pieces && v.content_pieces.length > 0)
          .sort((a, b) => (b.id || 0) - (a.id || 0))
          .slice(0, 10);
        
        set({ 
          allVideos: convertedVideos,
          recentVideos: recentVideos
        });
      },

      initializeDatabaseSync: () => {
        const handleDatabaseUpdate = (videos: DatabaseVideo[]) => {
          get().updateAllVideos(videos);
        };
        
        databaseSync.addListener(handleDatabaseUpdate);
        databaseSync.start();
      },

      stopDatabaseSync: () => {
        databaseSync.stop();
      },

      addRecentVideo: (url) =>
        set((state) => ({
          settings: {
            ...state.settings,
            recentVideoUrls: [
              url,
              ...state.settings.recentVideoUrls.filter(u => u !== url)
            ].slice(0, 10) // Keep only 10 recent videos
          }
        })),

      addFavoritePreset: (presetName) =>
        set((state) => ({
          settings: {
            ...state.settings,
            favoriteStylePresets: [
              ...state.settings.favoriteStylePresets.filter(p => p !== presetName),
              presetName
            ]
          }
        })),

      removeFavoritePreset: (presetName) =>
        set((state) => ({
          settings: {
            ...state.settings,
            favoriteStylePresets: state.settings.favoriteStylePresets.filter(p => p !== presetName)
          }
        })),
    }),
    {
      name: 'youtube-repurposer-store',
      partialize: (state) => ({
        settings: state.settings,
        selectedTab: state.selectedTab,
      }),
    }
  )
);

// Notification helper hook
export const useNotifications = () => {
  const { notifications, addNotification, removeNotification, clearNotifications } = useAppStore();

  const showSuccess = (title: string, message?: string) => {
    addNotification({ type: 'success', title, message });
  };

  const showError = (title: string, message?: string) => {
    addNotification({ type: 'error', title, message });
  };

  const showWarning = (title: string, message?: string) => {
    addNotification({ type: 'warning', title, message });
  };

  const showInfo = (title: string, message?: string) => {
    addNotification({ type: 'info', title, message });
  };

  return {
    notifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeNotification,
    clearNotifications,
  };
};