/**
 * Mock Data for VTO Playground
 * 
 * Sample data for testing UI without AI engine.
 * These are placeholder URLs - replace with actual sample images.
 */

import type { ClothingCategory, AvatarPerspective, BackgroundType } from '../types';

// Sample clothing items
export const sampleClothingItems = [
  {
    name: 'White T-Shirt',
    category: 'top' as ClothingCategory,
    frontImageUri: 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400',
    parameters: { fit: 'regular' as const },
    tags: ['casual', 'basic', 'white'],
  },
  {
    name: 'Black Jeans',
    category: 'bottom' as ClothingCategory,
    frontImageUri: 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400',
    parameters: { fit: 'regular' as const },
    tags: ['casual', 'denim', 'black'],
  },
  {
    name: 'Blue Dress',
    category: 'dress' as ClothingCategory,
    frontImageUri: 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400',
    parameters: { fit: 'regular' as const },
    tags: ['elegant', 'blue'],
  },
  {
    name: 'Leather Jacket',
    category: 'outerwear' as ClothingCategory,
    frontImageUri: 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400',
    parameters: { fit: 'regular' as const },
    tags: ['leather', 'black', 'casual'],
  },
  {
    name: 'Sneakers',
    category: 'shoes' as ClothingCategory,
    frontImageUri: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400',
    parameters: {},
    tags: ['casual', 'sport', 'white'],
  },
];

// Sample outfit sets
export const sampleOutfitSets = [
  {
    name: 'Casual Day',
    description: 'Perfect for a relaxed day out',
    itemIndices: [0, 1, 4], // White T-Shirt, Black Jeans, Sneakers
  },
  {
    name: 'Night Out',
    description: 'Elegant evening look',
    itemIndices: [2, 4], // Blue Dress, Sneakers
  },
  {
    name: 'Street Style',
    description: 'Urban casual look',
    itemIndices: [0, 1, 3, 4], // T-Shirt, Jeans, Jacket, Sneakers
  },
];

// Sample avatar configurations
export const sampleAvatarConfigs = [
  {
    name: 'Front View - Base',
    perspective: 'front' as AvatarPerspective,
    state: 'base' as const,
    backgroundType: 'white' as BackgroundType,
  },
  {
    name: 'Front View - Studio',
    perspective: 'front' as AvatarPerspective,
    state: 'base' as const,
    backgroundType: 'studio' as BackgroundType,
  },
  {
    name: 'Back View',
    perspective: 'back' as AvatarPerspective,
    state: 'base' as const,
    backgroundType: 'white' as BackgroundType,
  },
  {
    name: '3/4 View',
    perspective: 'three_quarter' as AvatarPerspective,
    state: 'base' as const,
    backgroundType: 'transparent' as BackgroundType,
  },
];

// Sample animation presets
export const sampleAnimationPresets = [
  {
    name: '360 Spin',
    type: 'loop' as const,
    duration: 3,
    fps: 30,
    loop: true,
  },
  {
    name: 'Quick Turn',
    type: 'single_frame' as const,
    duration: 1,
    fps: 24,
    loop: false,
  },
  {
    name: 'Smooth Rotation',
    type: 'keyframe_sequence' as const,
    duration: 5,
    fps: 60,
    loop: true,
  },
];

// Placeholder image for development
export const PLACEHOLDER_IMAGE = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400';

// Helper function to load sample data into store
export function getSampleData() {
  return {
    clothingItems: sampleClothingItems,
    outfitSets: sampleOutfitSets,
    avatarConfigs: sampleAvatarConfigs,
    animationPresets: sampleAnimationPresets,
  };
}
