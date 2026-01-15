// AI Engine exports (mock/local generation)
export { default as AIEngine } from './ai-engine';
export {
  configureAIEngine,
  isAIEngineConfigured,
  generateAnimation,
  generate,
} from './ai-engine';

// API exports (remote API calls)
export { default as API } from './api';
export {
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
} from './api';
