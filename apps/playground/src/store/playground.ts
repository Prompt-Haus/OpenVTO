import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type {
  UserPhoto,
  ClothingItem,
  ClothingSet,
  Avatar,
  TryOnResult,
  AnimationResult,
  GenerationStatus,
  ImageSource,
} from '../types';

// History item type
export interface HistoryItem {
  id: string;
  type: 'image' | 'video';
  uri: string;
  thumbnail?: string; // First frame for videos
  timestamp: number;
}

// Simple unique ID generator (no crypto dependency)
const generateId = (): string => {
  return `${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 11)}`;
};

// Store state interface
interface PlaygroundState {
  // Photos
  photos: UserPhoto[];
  selectedPhotoId: string | null;
  
  // Clothing
  clothingItems: ClothingItem[];
  clothingSets: ClothingSet[];
  selectedClothingIds: string[];
  
  // Avatars
  avatars: Avatar[];
  selectedAvatarId: string | null;
  
  // Try-on results
  tryOnResults: TryOnResult[];
  selectedTryOnId: string | null;
  
  // Animations
  animations: AnimationResult[];
  selectedAnimationId: string | null;
  
  // Generation History (persisted)
  generationHistory: HistoryItem[];
  
  // UI State
  isLoading: boolean;
  currentTab: string;
}

// Store actions interface
interface PlaygroundActions {
  // Photo actions
  addPhoto: (uri: string, source: ImageSource, width: number, height: number) => string;
  removePhoto: (id: string) => void;
  selectPhoto: (id: string | null) => void;
  
  // Clothing actions
  addClothingItem: (item: Omit<ClothingItem, 'id' | 'createdAt' | 'updatedAt'>) => string;
  updateClothingItem: (id: string, updates: Partial<ClothingItem>) => void;
  removeClothingItem: (id: string) => void;
  selectClothingItem: (id: string) => void;
  deselectClothingItem: (id: string) => void;
  clearClothingSelection: () => void;
  
  // Clothing set actions
  createClothingSet: (name: string, itemIds: string[]) => string;
  removeClothingSet: (id: string) => void;
  
  // Avatar actions
  addAvatar: (avatar: Omit<Avatar, 'id' | 'createdAt' | 'updatedAt'>) => string;
  updateAvatarStatus: (id: string, status: GenerationStatus, imageUri?: string, error?: string) => void;
  removeAvatar: (id: string) => void;
  selectAvatar: (id: string | null) => void;
  
  // Try-on actions
  addTryOnResult: (result: Omit<TryOnResult, 'id' | 'createdAt' | 'updatedAt'>) => string;
  updateTryOnStatus: (id: string, status: GenerationStatus, imageUri?: string, error?: string) => void;
  removeTryOnResult: (id: string) => void;
  selectTryOn: (id: string | null) => void;
  
  // Animation actions
  addAnimation: (animation: Omit<AnimationResult, 'id' | 'createdAt' | 'updatedAt'>) => string;
  updateAnimationStatus: (id: string, status: GenerationStatus, videoUri?: string, error?: string) => void;
  removeAnimation: (id: string) => void;
  selectAnimation: (id: string | null) => void;
  
  // UI actions
  setLoading: (loading: boolean) => void;
  setCurrentTab: (tab: string) => void;
  
  // History actions
  addToHistory: (item: Omit<HistoryItem, 'id' | 'timestamp'>) => string;
  removeFromHistory: (id: string) => void;
  clearHistory: () => void;
  
  // Bulk actions
  clearAll: () => void;
}

type PlaygroundStore = PlaygroundState & PlaygroundActions;

const initialState: PlaygroundState = {
  photos: [],
  selectedPhotoId: null,
  clothingItems: [],
  clothingSets: [],
  selectedClothingIds: [],
  avatars: [],
  selectedAvatarId: null,
  tryOnResults: [],
  selectedTryOnId: null,
  animations: [],
  selectedAnimationId: null,
  generationHistory: [],
  isLoading: false,
  currentTab: 'photos',
};

export const usePlaygroundStore = create<PlaygroundStore>()(
  persist(
    (set, get) => ({
  ...initialState,
  
  // Photo actions
  addPhoto: (uri, source, width, height) => {
    const id = generateId();
    const now = new Date();
    const photo: UserPhoto = {
      id,
      uri,
      source,
      width,
      height,
      createdAt: now,
      updatedAt: now,
    };
    set((state) => ({ photos: [...state.photos, photo] }));
    return id;
  },
  
  removePhoto: (id) => {
    set((state) => ({
      photos: state.photos.filter((p) => p.id !== id),
      selectedPhotoId: state.selectedPhotoId === id ? null : state.selectedPhotoId,
    }));
  },
  
  selectPhoto: (id) => {
    set({ selectedPhotoId: id });
  },
  
  // Clothing actions
  addClothingItem: (item) => {
    const id = generateId();
    const now = new Date();
    const clothingItem: ClothingItem = {
      ...item,
      id,
      createdAt: now,
      updatedAt: now,
    };
    set((state) => ({ clothingItems: [...state.clothingItems, clothingItem] }));
    return id;
  },
  
  updateClothingItem: (id, updates) => {
    set((state) => ({
      clothingItems: state.clothingItems.map((item) =>
        item.id === id ? { ...item, ...updates, updatedAt: new Date() } : item
      ),
    }));
  },
  
  removeClothingItem: (id) => {
    set((state) => ({
      clothingItems: state.clothingItems.filter((item) => item.id !== id),
      selectedClothingIds: state.selectedClothingIds.filter((cid) => cid !== id),
    }));
  },
  
  selectClothingItem: (id) => {
    set((state) => ({
      selectedClothingIds: state.selectedClothingIds.includes(id)
        ? state.selectedClothingIds
        : [...state.selectedClothingIds, id],
    }));
  },
  
  deselectClothingItem: (id) => {
    set((state) => ({
      selectedClothingIds: state.selectedClothingIds.filter((cid) => cid !== id),
    }));
  },
  
  clearClothingSelection: () => {
    set({ selectedClothingIds: [] });
  },
  
  // Clothing set actions
  createClothingSet: (name, itemIds) => {
    const id = generateId();
    const now = new Date();
    const clothingSet: ClothingSet = {
      id,
      name,
      items: itemIds,
      createdAt: now,
      updatedAt: now,
    };
    set((state) => ({ clothingSets: [...state.clothingSets, clothingSet] }));
    return id;
  },
  
  removeClothingSet: (id) => {
    set((state) => ({
      clothingSets: state.clothingSets.filter((s) => s.id !== id),
    }));
  },
  
  // Avatar actions
  addAvatar: (avatar) => {
    const id = generateId();
    const now = new Date();
    const newAvatar: Avatar = {
      ...avatar,
      id,
      createdAt: now,
      updatedAt: now,
    };
    set((state) => ({ avatars: [...state.avatars, newAvatar] }));
    return id;
  },
  
  updateAvatarStatus: (id, status, imageUri, error) => {
    set((state) => ({
      avatars: state.avatars.map((avatar) =>
        avatar.id === id
          ? {
              ...avatar,
              status,
              imageUri: imageUri ?? avatar.imageUri,
              errorMessage: error,
              updatedAt: new Date(),
            }
          : avatar
      ),
    }));
  },
  
  removeAvatar: (id) => {
    set((state) => ({
      avatars: state.avatars.filter((a) => a.id !== id),
      selectedAvatarId: state.selectedAvatarId === id ? null : state.selectedAvatarId,
    }));
  },
  
  selectAvatar: (id) => {
    set({ selectedAvatarId: id });
  },
  
  // Try-on actions
  addTryOnResult: (result) => {
    const id = generateId();
    const now = new Date();
    const tryOnResult: TryOnResult = {
      ...result,
      id,
      createdAt: now,
      updatedAt: now,
    };
    set((state) => ({ tryOnResults: [...state.tryOnResults, tryOnResult] }));
    return id;
  },
  
  updateTryOnStatus: (id, status, imageUri, error) => {
    set((state) => ({
      tryOnResults: state.tryOnResults.map((result) =>
        result.id === id
          ? {
              ...result,
              status,
              imageUri: imageUri ?? result.imageUri,
              errorMessage: error,
              updatedAt: new Date(),
            }
          : result
      ),
    }));
  },
  
  removeTryOnResult: (id) => {
    set((state) => ({
      tryOnResults: state.tryOnResults.filter((r) => r.id !== id),
      selectedTryOnId: state.selectedTryOnId === id ? null : state.selectedTryOnId,
    }));
  },
  
  selectTryOn: (id) => {
    set({ selectedTryOnId: id });
  },
  
  // Animation actions
  addAnimation: (animation) => {
    const id = generateId();
    const now = new Date();
    const newAnimation: AnimationResult = {
      ...animation,
      id,
      createdAt: now,
      updatedAt: now,
    };
    set((state) => ({ animations: [...state.animations, newAnimation] }));
    return id;
  },
  
  updateAnimationStatus: (id, status, videoUri, error) => {
    set((state) => ({
      animations: state.animations.map((anim) =>
        anim.id === id
          ? {
              ...anim,
              status,
              videoUri: videoUri ?? anim.videoUri,
              errorMessage: error,
              updatedAt: new Date(),
            }
          : anim
      ),
    }));
  },
  
  removeAnimation: (id) => {
    set((state) => ({
      animations: state.animations.filter((a) => a.id !== id),
      selectedAnimationId: state.selectedAnimationId === id ? null : state.selectedAnimationId,
    }));
  },
  
  selectAnimation: (id) => {
    set({ selectedAnimationId: id });
  },
  
  // UI actions
  setLoading: (loading) => {
    set({ isLoading: loading });
  },
  
  setCurrentTab: (tab) => {
    set({ currentTab: tab });
  },
  
  // History actions
  addToHistory: (item) => {
    const id = generateId();
    const historyItem: HistoryItem = {
      ...item,
      id,
      timestamp: Date.now(),
    };
    set((state) => ({ 
      generationHistory: [historyItem, ...state.generationHistory].slice(0, 50) // Keep last 50
    }));
    return id;
  },
  
  removeFromHistory: (id) => {
    set((state) => ({
      generationHistory: state.generationHistory.filter((h) => h.id !== id),
    }));
  },
  
  clearHistory: () => {
    set({ generationHistory: [] });
  },
  
  // Bulk actions
  clearAll: () => {
    set(initialState);
  },
}),
    {
      name: 'playground-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        // Only persist these fields
        generationHistory: state.generationHistory,
        clothingItems: state.clothingItems.filter(item => item.isLocal), // Only local items
      }),
    }
  )
);

// Selectors
export const selectPhotos = (state: PlaygroundState) => state.photos;
export const selectSelectedPhoto = (state: PlaygroundState) =>
  state.photos.find((p) => p.id === state.selectedPhotoId);
export const selectClothingItems = (state: PlaygroundState) => state.clothingItems;
export const selectSelectedClothing = (state: PlaygroundState) =>
  state.clothingItems.filter((item) => state.selectedClothingIds.includes(item.id));
export const selectAvatars = (state: PlaygroundState) => state.avatars;
export const selectSelectedAvatar = (state: PlaygroundState) =>
  state.avatars.find((a) => a.id === state.selectedAvatarId);
export const selectTryOnResults = (state: PlaygroundState) => state.tryOnResults;
export const selectAnimations = (state: PlaygroundState) => state.animations;
