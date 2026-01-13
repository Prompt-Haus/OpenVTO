// Core types for the VTO Playground application

export type ImageSource = 'camera' | 'gallery' | 'import';

export type ClothingCategory = 'top' | 'bottom' | 'dress' | 'outerwear' | 'accessories' | 'shoes' | 'full_outfit' | 'shirts' | 'pants' | 'jackets';

export type ClothingSide = 'front' | 'back';

export type AvatarPerspective = 'front' | 'back' | 'side_left' | 'side_right' | 'three_quarter';

export type AvatarState = 'clothed' | 'base'; // base = underwear/base layer

export type AnimationType = 'single_frame' | 'loop' | 'keyframe_sequence';

export type GenerationStatus = 'idle' | 'pending' | 'processing' | 'completed' | 'failed';

// Base entity with common fields
export interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

// Photo uploaded by user (for avatar generation)
export interface UserPhoto extends BaseEntity {
  uri: string;
  source: ImageSource;
  width: number;
  height: number;
  thumbnail?: string;
}

// Clothing item
export interface ClothingItem extends BaseEntity {
  name: string;
  category: ClothingCategory;
  frontImageUri: string;
  backImageUri?: string;
  thumbnail?: string;
  parameters?: ClothingParameters;
  tags?: string[];
  isLocal?: boolean;
}

// Styling parameters for clothing
export interface ClothingParameters {
  fit?: 'tight' | 'regular' | 'loose' | 'oversized';
  length?: 'cropped' | 'regular' | 'long';
  color?: string;
  pattern?: string;
  material?: string;
  customParams?: Record<string, string | number>;
}

// Clothing set (outfit)
export interface ClothingSet extends BaseEntity {
  name: string;
  items: string[]; // ClothingItem IDs
  thumbnail?: string;
}

// Generated avatar
export interface Avatar extends BaseEntity {
  name: string;
  sourcePhotoId: string;
  perspective: AvatarPerspective;
  state: AvatarState;
  backgroundType: BackgroundType;
  imageUri: string;
  thumbnail?: string;
  status: GenerationStatus;
  errorMessage?: string;
}

// Background options for avatar
export type BackgroundType = 'transparent' | 'white' | 'black' | 'studio' | 'custom';

export interface BackgroundConfig {
  type: BackgroundType;
  customUri?: string;
  color?: string;
}

// Try-on generation result
export interface TryOnResult extends BaseEntity {
  avatarId: string;
  clothingItemIds: string[];
  perspective: AvatarPerspective;
  imageUri: string;
  thumbnail?: string;
  status: GenerationStatus;
  errorMessage?: string;
}

// Animation configuration
export interface AnimationConfig {
  type: AnimationType;
  keyframes: AnimationKeyframe[];
  duration: number; // in seconds
  fps: number;
  loop: boolean;
}

export interface AnimationKeyframe {
  frameIndex: number;
  imageUri: string;
  perspective?: AvatarPerspective;
  timestamp: number; // in milliseconds
}

// Animation result
export interface AnimationResult extends BaseEntity {
  name: string;
  sourceType: 'avatar' | 'tryon';
  sourceId: string;
  config: AnimationConfig;
  videoUri?: string;
  gifUri?: string;
  status: GenerationStatus;
  errorMessage?: string;
}

// Collection item (unified view)
export interface CollectionItem {
  id: string;
  type: 'photo' | 'clothing' | 'avatar' | 'tryon' | 'animation';
  data: UserPhoto | ClothingItem | Avatar | TryOnResult | AnimationResult;
  thumbnail: string;
  createdAt: Date;
}

// AI Engine interface (placeholder for future integration)
export interface AIEngineConfig {
  endpoint?: string;
  apiKey?: string;
  modelVersion?: string;
}

export interface AIGenerationRequest {
  type: 'avatar' | 'tryon' | 'animation';
  inputData: Record<string, unknown>;
  config?: Record<string, unknown>;
}

export interface AIGenerationResponse {
  success: boolean;
  resultUri?: string;
  error?: string;
  metadata?: Record<string, unknown>;
}
