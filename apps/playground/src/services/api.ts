/**
 * OpenVTO API Service
 * 
 * Service for communicating with the OpenVTO backend API.
 */

import * as FileSystem from 'expo-file-system/legacy';
import type { ClothingCategory, ClothingItem } from '../types';

// API Configuration
let apiConfig = {
  baseUrl: 'http://localhost:8000',
  apiKey: 'openvto-dev', // Default dev API key - set same in API's .env as API_KEY=openvto-dev
};

/**
 * Configure the API service
 */
export function configureAPI(config: { baseUrl?: string; apiKey?: string }) {
  apiConfig = { ...apiConfig, ...config };
}

/**
 * Get the current API base URL
 */
export function getAPIBaseUrl(): string {
  return apiConfig.baseUrl;
}

// ============================================================================
// Assets API
// ============================================================================

interface ClothingCategoriesResponse {
  categories: string[];
}

interface ClothingItemsResponse {
  category: string;
  indices: number[];
  views: string[];
}

/**
 * Get list of available clothing categories
 */
export async function getClothingCategories(): Promise<string[]> {
  const response = await fetch(`${apiConfig.baseUrl}/assets/clothes/categories`);
  if (!response.ok) {
    throw new Error(`Failed to fetch categories: ${response.statusText}`);
  }
  const data: ClothingCategoriesResponse = await response.json();
  return data.categories;
}

/**
 * Get items in a clothing category
 */
export async function getClothingItems(category: string): Promise<ClothingItemsResponse> {
  const response = await fetch(`${apiConfig.baseUrl}/assets/clothes/${category}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch items for ${category}: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get clothing image URL
 */
export function getClothingImageUrl(
  category: string,
  itemId: number,
  view: 'front' | 'back'
): string {
  return `${apiConfig.baseUrl}/assets/clothes/${category}/${itemId}/${view}`;
}

/**
 * Get person image URL (posture or selfie)
 */
export function getPersonImageUrl(personId: number, kind: 'posture' | 'selfie'): string {
  return `${apiConfig.baseUrl}/assets/people/${personId}/${kind}`;
}

/**
 * Get avatar image URL
 */
export function getAvatarImageUrl(avatarId: number): string {
  return `${apiConfig.baseUrl}/assets/avatars/${avatarId}`;
}

/**
 * Map API category to ClothingCategory type
 */
function mapCategoryToType(category: string): ClothingCategory {
  const categoryMap: Record<string, ClothingCategory> = {
    shirts: 'top',
    jackets: 'outerwear',
    pants: 'bottom',
  };
  return categoryMap[category] || 'top';
}

/**
 * Fetch all clothing items from API and convert to ClothingItem format
 */
export async function fetchAllClothingItems(): Promise<Omit<ClothingItem, 'id' | 'createdAt' | 'updatedAt'>[]> {
  const categories = await getClothingCategories();
  const allItems: Omit<ClothingItem, 'id' | 'createdAt' | 'updatedAt'>[] = [];

  for (const category of categories) {
    const itemsData = await getClothingItems(category);
    
    for (const index of itemsData.indices) {
      const frontUrl = getClothingImageUrl(category, index, 'front');
      const backUrl = itemsData.views.includes('back') 
        ? getClothingImageUrl(category, index, 'back')
        : undefined;

      allItems.push({
        name: `${capitalize(category)} ${index}`,
        category: mapCategoryToType(category),
        frontImageUri: frontUrl,
        backImageUri: backUrl,
        tags: [category],
      });
    }
  }

  return allItems;
}

// ============================================================================
// Generation API (requires API key)
// ============================================================================

interface GenerationHeaders {
  'Content-Type': string;
  'X-API-Key'?: string;
}

function getAuthHeaders(): GenerationHeaders {
  const headers: GenerationHeaders = {
    'Content-Type': 'application/json',
  };
  if (apiConfig.apiKey) {
    headers['X-API-Key'] = apiConfig.apiKey;
  }
  return headers;
}

interface AvatarGenerationRequest {
  selfie_b64: string;
  posture_b64: string;
  background?: string;
  keep_clothes?: boolean;
}

interface AvatarResponse {
  image_b64: string;
  width: number;
  height: number;
  meta?: {
    model: string;
    provider: string;
    latency_ms?: number;
  };
}

/**
 * Generate avatar from selfie and posture images
 * API expects multipart/form-data with file uploads
 */
export async function generateAvatar(request: AvatarGenerationRequest): Promise<AvatarResponse> {
  const formData = new FormData();
  
  // Save images to temp files and add to form
  const selfieUri = await base64ToTempFile(request.selfie_b64, `selfie_${Date.now()}.png`);
  formData.append('selfie', createFileObject(selfieUri, 'selfie.png') as any);
  
  const postureUri = await base64ToTempFile(request.posture_b64, `posture_${Date.now()}.png`);
  formData.append('posture', createFileObject(postureUri, 'posture.png') as any);
  
  // Add form fields
  formData.append('background', request.background ?? 'studio');
  formData.append('keep_clothes', String(request.keep_clothes ?? false));

  // Don't set Content-Type header
  // Use 'api-key' header (FastAPI converts parameter name api_key to api-key)
  const headers: Record<string, string> = {};
  if (apiConfig.apiKey) {
    headers['api-key'] = apiConfig.apiKey;
  }

  const response = await fetch(`${apiConfig.baseUrl}/generate/avatar`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    let errorMessage = 'Avatar generation failed';
    if (Array.isArray(error.detail)) {
      errorMessage = error.detail.map((e: { msg?: string; loc?: string[] }) => 
        `${e.loc?.join('.') || 'field'}: ${e.msg}` || JSON.stringify(e)
      ).join('; ');
    } else if (typeof error.detail === 'string') {
      errorMessage = error.detail;
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

interface TryOnGenerationRequest {
  avatar_b64: string;
  clothes_b64: string[];
  compose?: boolean;
  seed?: number;
}

interface TryOnResponse {
  image_b64: string;
  clothing_composite_b64?: string;
  meta?: {
    model: string;
    provider: string;
    latency_ms?: number;
  };
}

/**
 * Save base64 data to a temporary file and return the file URI
 * This is needed because React Native FormData requires file URIs, not Blobs
 */
async function base64ToTempFile(base64: string, filename: string): Promise<string> {
  // Remove data URI prefix if present
  const base64Data = base64.includes(',') ? base64.split(',')[1] : base64;
  
  if (!base64Data || base64Data.length === 0) {
    throw new Error(`Invalid base64 data for ${filename}`);
  }
  
  // Create temp file path
  const tempDir = FileSystem.cacheDirectory;
  console.log(`[API] Cache directory: ${tempDir}`);
  
  if (!tempDir) {
    throw new Error('Cache directory not available');
  }
  
  // Ensure path ends with /
  const normalizedDir = tempDir.endsWith('/') ? tempDir : `${tempDir}/`;
  const filePath = `${normalizedDir}${filename}`;
  
  console.log(`[API] Saving temp file: ${filename}`);
  console.log(`[API] Full path: ${filePath}`);
  console.log(`[API] Base64 length: ${base64Data.length}`);
  console.log(`[API] Base64 preview: ${base64Data.substring(0, 50)}...`);
  
  // Write base64 data to file
  await FileSystem.writeAsStringAsync(filePath, base64Data, {
    encoding: FileSystem.EncodingType.Base64,
  });
  
  // Verify file was created
  const fileInfo = await FileSystem.getInfoAsync(filePath);
  console.log(`[API] File info:`, JSON.stringify(fileInfo));
  
  if (!fileInfo.exists) {
    throw new Error(`Failed to create temp file: ${filePath}`);
  }
  
  console.log(`[API] Temp file created successfully, size: ${(fileInfo as any).size || 'unknown'}`);
  
  return filePath;
}

/**
 * Create a React Native compatible file object for FormData
 * Ensures URI has proper file:// prefix
 */
function createFileObject(uri: string, name: string, type: string = 'image/png'): any {
  // Ensure URI has file:// prefix for React Native
  let finalUri = uri;
  if (!uri.startsWith('file://') && !uri.startsWith('content://') && !uri.startsWith('http')) {
    finalUri = `file://${uri}`;
  }
  
  const fileObj = {
    uri: finalUri,
    type: type,
    name: name,
  };
  console.log(`[API] File object created:`, JSON.stringify(fileObj));
  return fileObj;
}

/**
 * Generate try-on result
 * API expects multipart/form-data with file uploads
 */
export async function generateTryOn(request: TryOnGenerationRequest): Promise<TryOnResponse> {
  console.log('[API] generateTryOn called');
  console.log('[API] Avatar base64 length:', request.avatar_b64?.length || 0);
  console.log('[API] Clothes count:', request.clothes_b64?.length || 0);
  
  // Validate input
  if (!request.avatar_b64 || request.avatar_b64.length === 0) {
    throw new Error('Avatar image is required');
  }
  if (!request.clothes_b64 || request.clothes_b64.length === 0) {
    throw new Error('At least one clothing item is required');
  }
  
  const formData = new FormData();
  
  try {
    // Save avatar to temp file and add to form
    console.log('[API] Processing avatar...');
    const avatarUri = await base64ToTempFile(request.avatar_b64, `avatar_${Date.now()}.png`);
    const avatarFile = createFileObject(avatarUri, 'avatar.png', 'image/png');
    formData.append('avatar', avatarFile as any);
    console.log('[API] Avatar added to FormData');
    
    // Save each clothing item to temp file and add to form
    console.log('[API] Processing', request.clothes_b64.length, 'clothing items...');
    for (let index = 0; index < request.clothes_b64.length; index++) {
      console.log(`[API] Processing cloth ${index}, base64 length: ${request.clothes_b64[index]?.length || 0}`);
      const clothUri = await base64ToTempFile(request.clothes_b64[index], `cloth_${index}_${Date.now()}.png`);
      const clothFile = createFileObject(clothUri, `cloth_${index}.png`, 'image/png');
      formData.append('clothes', clothFile as any);
      console.log(`[API] Cloth ${index} added to FormData`);
    }
    
    // Add form fields
    formData.append('compose', String(request.compose ?? true));
    if (request.seed !== undefined) {
      formData.append('seed', String(request.seed));
    }
    console.log('[API] Form fields added');

  } catch (fileError) {
    console.error('[API] Error preparing files:', fileError);
    throw new Error(`Failed to prepare files: ${fileError instanceof Error ? fileError.message : 'Unknown error'}`);
  }

  // Don't set Content-Type header - RN will set it with boundary for multipart
  // Use 'api-key' header (FastAPI converts parameter name api_key to api-key)
  const headers: Record<string, string> = {};
  if (apiConfig.apiKey) {
    headers['api-key'] = apiConfig.apiKey;
  }

  console.log('[API] Sending request to:', `${apiConfig.baseUrl}/generate/tryon`);
  console.log('[API] Headers:', JSON.stringify(headers));

  const response = await fetch(`${apiConfig.baseUrl}/generate/tryon`, {
    method: 'POST',
    headers,
    body: formData,
  });

  console.log('[API] Response status:', response.status);

  if (!response.ok) {
    const errorBody = await response.text();
    console.error('[API] Error response body:', errorBody);
    
    let error;
    try {
      error = JSON.parse(errorBody);
    } catch {
      throw new Error(`Server error: ${response.status} ${response.statusText}`);
    }
    
    // Handle FastAPI validation errors (array of objects)
    let errorMessage = 'Try-on generation failed';
    if (Array.isArray(error.detail)) {
      errorMessage = error.detail.map((e: { msg?: string; loc?: string[]; type?: string }) => {
        const location = e.loc?.join('.') || 'unknown';
        const message = e.msg || 'unknown error';
        return `${location}: ${message}`;
      }).join('; ');
    } else if (typeof error.detail === 'string') {
      errorMessage = error.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }
    throw new Error(errorMessage);
  }

  console.log('[API] Success!');
  return response.json();
}

interface VideoLoopRequest {
  image_b64: string;
  mode?: '360' | 'idle';
  seconds?: number;
  seed?: number;
}

interface VideoLoopResponse {
  video_b64: string;
  first_frame_b64: string;
  duration_seconds: number;
  width: number;
  height: number;
  mode: string;
  meta?: {
    model: string;
    provider: string;
    latency_ms?: number;
  };
}

/**
 * Generate video loop from image
 * API expects multipart/form-data with file upload
 */
export async function generateVideoLoop(request: VideoLoopRequest): Promise<VideoLoopResponse> {
  const formData = new FormData();
  
  // Save image to temp file and add to form
  const imageUri = await base64ToTempFile(request.image_b64, `image_${Date.now()}.png`);
  formData.append('image', createFileObject(imageUri, 'image.png') as any);
  
  // Add form fields
  formData.append('mode', request.mode ?? '360');
  formData.append('seconds', String(request.seconds ?? 4.0));
  if (request.seed !== undefined) {
    formData.append('seed', String(request.seed));
  }

  // Don't set Content-Type header
  // Use 'api-key' header
  const headers: Record<string, string> = {};
  if (apiConfig.apiKey) {
    headers['api-key'] = apiConfig.apiKey;
  }

  const response = await fetch(`${apiConfig.baseUrl}/generate/videoloop`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    let errorMessage = 'Video loop generation failed';
    if (Array.isArray(error.detail)) {
      errorMessage = error.detail.map((e: { msg?: string }) => e.msg || JSON.stringify(e)).join('; ');
    } else if (typeof error.detail === 'string') {
      errorMessage = error.detail;
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

// ============================================================================
// Utilities
// ============================================================================

function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Convert image URI to base64
 * Handles: local file URIs, remote URLs, and data URIs
 */
export async function imageUriToBase64(uri: string): Promise<string> {
  // If it's already a data URI, extract the base64 part
  if (uri.startsWith('data:')) {
    const base64Part = uri.split(',')[1];
    return base64Part || uri;
  }
  
  // For local files, use FileSystem directly
  if (uri.startsWith('file://') || uri.startsWith('/')) {
    const base64 = await FileSystem.readAsStringAsync(uri, {
      encoding: FileSystem.EncodingType.Base64,
    });
    return base64;
  }
  
  // For remote URLs, download first then convert
  try {
    const tempFile = `${FileSystem.cacheDirectory}temp_${Date.now()}.png`;
    const downloadResult = await FileSystem.downloadAsync(uri, tempFile);
    
    if (downloadResult.status !== 200) {
      throw new Error(`Failed to download image: ${downloadResult.status}`);
    }
    
    const base64 = await FileSystem.readAsStringAsync(downloadResult.uri, {
      encoding: FileSystem.EncodingType.Base64,
    });
    
    // Clean up temp file
    await FileSystem.deleteAsync(downloadResult.uri, { idempotent: true });
    
    return base64;
  } catch (error) {
    console.error('Error converting URI to base64:', error);
    throw new Error(`Failed to convert image: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Convert base64 to data URI
 */
export function base64ToDataUri(base64: string, mimeType = 'image/png'): string {
  return `data:${mimeType};base64,${base64}`;
}

export default {
  configureAPI,
  getAPIBaseUrl,
  getClothingCategories,
  getClothingItems,
  getClothingImageUrl,
  getPersonImageUrl,
  getAvatarImageUrl,
  fetchAllClothingItems,
  generateAvatar,
  generateTryOn,
  generateVideoLoop,
  imageUriToBase64,
  base64ToDataUri,
};

