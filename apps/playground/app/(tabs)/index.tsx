import { Ionicons } from '@expo/vector-icons';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Dimensions,
  FlatList,
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Alert,
  ScrollView,
  Modal
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Video from 'react-native-video';
import Animated, { 
  useAnimatedStyle, 
  useSharedValue, 
  withSpring,
  withRepeat,
  withTiming,
  withSequence,
  Easing,
  interpolate
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import * as FileSystem from 'expo-file-system/legacy';
import { 
  configureAPI, 
  getClothingCategories, 
  getClothingItems, 
  getClothingImageUrl,
  getAvatarImageUrl,
  generateAvatar,
  generateTryOn,
  generateVideoLoop,
  imageUriToBase64,
  base64ToDataUri
} from '../../src/services/api';
import { usePlaygroundStore, type HistoryItem } from '../../src/store/playground';
import { useImagePicker } from '../../src/hooks/useImagePicker';
import type { ClothingCategory } from '../../src/types';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');
const PADDING = 20;
const SNAP_TOP = SCREEN_HEIGHT * 0.4;
const SNAP_BOTTOM = SCREEN_HEIGHT - 180; // More visible when collapsed

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Default avatar from API
const DEFAULT_AVATAR = { id: 'default-1', image: getAvatarImageUrl(1), isDefault: true };

interface AvatarItem {
  id: string;
  image: string; // base64 data URI or URL
  isDefault?: boolean;
  isGenerating?: boolean;
}

interface DisplayItem {
  id: string;
  image: string;
  backImage?: string;
  category: string;
  isLocal?: boolean;
}

const GALLERY_GAP = 8;
const GALLERY_SIZE = (SCREEN_WIDTH - PADDING * 2 - GALLERY_GAP * 3) / 4;

// Generation Steps
const GENERATION_STEPS = [
  { text: 'Preparing avatar' },
  { text: 'Analyzing outfit' },
  { text: 'AI styling' },
  { text: 'Finishing' },
];

// Animated Loading Component - Clean White Theme
const GeneratingAnimation = ({ mode }: { mode: 'image' | 'video' }) => {
  const rotation = useSharedValue(0);
  const pulse = useSharedValue(1);
  const [currentStep, setCurrentStep] = React.useState(0);

  React.useEffect(() => {
    // Smooth rotation for the ring
    rotation.value = withRepeat(
      withTiming(360, { duration: 2500, easing: Easing.linear }),
      -1,
      false
    );

    // Gentle pulse for center icon
    pulse.value = withRepeat(
      withSequence(
        withTiming(1.08, { duration: 800, easing: Easing.inOut(Easing.ease) }),
        withTiming(1, { duration: 800, easing: Easing.inOut(Easing.ease) })
      ),
      -1,
      false
    );

    // Step progression
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => (prev + 1) % GENERATION_STEPS.length);
    }, 2000);

    return () => clearInterval(stepInterval);
  }, []);

  const animatedPulse = useAnimatedStyle(() => ({
    transform: [{ scale: pulse.value }],
  }));

  const animatedRotation = useAnimatedStyle(() => ({
    transform: [{ rotate: `${rotation.value}deg` }],
  }));

  return (
    <View style={loadingStyles.container}>
      {/* Spinning ring */}
      <Animated.View style={[loadingStyles.spinnerRing, animatedRotation]}>
        <View style={loadingStyles.spinnerDot} />
      </Animated.View>
      
      {/* Center icon */}
      <Animated.View style={[loadingStyles.centerBox, animatedPulse]}>
        <Ionicons 
          name={mode === 'video' ? 'videocam' : 'sparkles'} 
          size={28} 
          color="#000" 
        />
      </Animated.View>

      {/* Step indicator */}
      <View style={loadingStyles.stepBox}>
        <Text style={loadingStyles.stepText}>{GENERATION_STEPS[currentStep].text}</Text>
        <View style={loadingStyles.dotsRow}>
          {GENERATION_STEPS.map((_, i) => (
            <View 
              key={i} 
              style={[
                loadingStyles.dot, 
                i === currentStep && loadingStyles.dotActive
              ]} 
            />
          ))}
        </View>
      </View>

      {/* Mode badge */}
      <View style={loadingStyles.modeBadge}>
        <Ionicons 
          name={mode === 'video' ? 'videocam-outline' : 'image-outline'} 
          size={14} 
          color="#666" 
        />
        <Text style={loadingStyles.modeText}>
          {mode === 'video' ? 'Video' : 'Photo'}
        </Text>
      </View>
    </View>
  );
};

const loadingStyles = StyleSheet.create({
  container: {
    flex: 1,
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  spinnerRing: {
    position: 'absolute',
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 3,
    borderColor: '#f0f0f0',
    borderTopColor: '#000',
    justifyContent: 'flex-start',
    alignItems: 'center',
  },
  spinnerDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#000',
    marginTop: -5,
  },
  centerBox: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#e0e0e0',
  },
  stepBox: {
    position: 'absolute',
    bottom: 140,
    alignItems: 'center',
  },
  stepText: {
    color: '#000',
    fontSize: 18,
    fontWeight: '600',
  },
  dotsRow: {
    flexDirection: 'row',
    marginTop: 16,
    gap: 8,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#e0e0e0',
  },
  dotActive: {
    backgroundColor: '#000',
    width: 24,
  },
  modeBadge: {
    position: 'absolute',
    top: 80,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 14,
    paddingVertical: 8,
    backgroundColor: '#f5f5f5',
    borderRadius: 20,
  },
  modeText: {
    color: '#666',
    fontSize: 13,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
});

// Helper component for clothing item
const ClothingItemView = ({ 
  item, 
  isSelected, 
  onPress,
  onLongPress
}: { 
  item: DisplayItem; 
  isSelected: boolean; 
  onPress: () => void;
  onLongPress: () => void;
}) => {
  const hasBack = !!item.backImage;

  return (
    <TouchableOpacity
      style={[styles.clothesItem, isSelected && styles.clothesActive]}
      onPress={onPress}
      onLongPress={onLongPress}
      delayLongPress={300}
    >
      <Image 
        source={{ uri: item.image }} 
        style={styles.clothesImage} 
      />
      {isSelected && <View style={styles.check}><Ionicons name="checkmark" size={14} color="#fff" /></View>}
      {item.isLocal && <View style={styles.localBadge}><Ionicons name="person" size={8} color="#fff" /></View>}
      {hasBack && (
        <View style={styles.flipBadge}>
          <Ionicons name="repeat" size={10} color="#fff" />
        </View>
      )}
    </TouchableOpacity>
  );
};

export default function TryOnScreen() {
  const insets = useSafeAreaInsets();
  
  // Selection State (single selection per category)
  const [selectedShirt, setSelectedShirt] = useState<string | null>(null);
  const [selectedTrousers, setSelectedTrousers] = useState<string | null>(null);
  const [selectedJacket, setSelectedJacket] = useState<string | null>(null);
  const [selectedAvatarId, setSelectedAvatarId] = useState<string>('default-1');
  
  // Avatar State
  const [avatars, setAvatars] = useState<AvatarItem[]>([DEFAULT_AVATAR]);
  const [showAvatarModal, setShowAvatarModal] = useState(false);
  const [avatarSelfie, setAvatarSelfie] = useState<string | null>(null);
  const [avatarPosture, setAvatarPosture] = useState<string | null>(null);
  const [isCreatingAvatar, setIsCreatingAvatar] = useState(false);
  
  // Preview Modal State
  const [previewItem, setPreviewItem] = useState<DisplayItem | null>(null);
  const [previewShowBack, setPreviewShowBack] = useState(false);
  
  // Generation State
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationMode, setGenerationMode] = useState<'image' | 'video'>('image');
  const [resultUri, setResultUri] = useState<string | null>(null);
  const [resultType, setResultType] = useState<'image' | 'video'>('image');
  
  // Data State
  const [shirts, setShirts] = useState<DisplayItem[]>([]);
  const [trousers, setTrousers] = useState<DisplayItem[]>([]);
  const [jackets, setJackets] = useState<DisplayItem[]>([]);
  const [isLoadingClothes, setIsLoadingClothes] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  
  // Animation
  const translateY = useSharedValue(SNAP_TOP);

  // Local clothing hook
  const { pickImage } = useImagePicker();
  const { addClothingItem, removeClothingItem, clothingItems: storedClothingItems, generationHistory, addToHistory } = usePlaygroundStore();

  // Load initial data
  useEffect(() => {
    configureAPI({ baseUrl: API_BASE_URL });
    loadClothingFromAPI();
  }, []);

  // Load stored local clothing items
  useEffect(() => {
    if (storedClothingItems && storedClothingItems.length > 0) {
      const localItems = storedClothingItems.filter(item => item.isLocal);
      
      localItems.forEach(item => {
        const displayItem: DisplayItem = {
          id: item.id,
          image: item.frontImageUri,
          backImage: item.backImageUri,
          category: item.category,
          isLocal: true,
        };
        
        if (item.category === 'shirts') {
          setShirts(prev => {
            if (prev.some(i => i.id === item.id)) return prev;
            return [displayItem, ...prev];
          });
        } else if (item.category === 'pants') {
          setTrousers(prev => {
            if (prev.some(i => i.id === item.id)) return prev;
            return [displayItem, ...prev];
          });
        } else if (item.category === 'jackets') {
          setJackets(prev => {
            if (prev.some(i => i.id === item.id)) return prev;
            return [displayItem, ...prev];
          });
        }
      });
    }
  }, [storedClothingItems]);

  const loadClothingFromAPI = async () => {
    setIsLoadingClothes(true);
    setLoadError(null);
    try {
      const categories = await getClothingCategories();
      for (const category of categories) {
        const itemsData = await getClothingItems(category);
        const items: DisplayItem[] = itemsData.indices.map(index => ({
          id: `${category}-${index}`,
          image: getClothingImageUrl(category, index, 'front'),
          backImage: itemsData.views.includes('back') 
            ? getClothingImageUrl(category, index, 'back') 
            : undefined,
          category,
        }));
        
        if (category === 'shirts') setShirts(prev => [...prev.filter(i => i.isLocal), ...items]);
        else if (category === 'pants') setTrousers(prev => [...prev.filter(i => i.isLocal), ...items]);
        else if (category === 'jackets') setJackets(prev => [...prev.filter(i => i.isLocal), ...items]);
      }
    } catch (error) {
      console.error('Failed to load clothing:', error);
      setLoadError(error instanceof Error ? error.message : 'Failed to load');
    } finally {
      setIsLoadingClothes(false);
    }
  };

  const handleAddLocalItem = async (category: string) => {
    Alert.alert('Add Item', 'Choose source', [
      { text: 'Camera', onPress: () => pickAndAddItem(category, 'camera') },
      { text: 'Gallery', onPress: () => pickAndAddItem(category, 'library') },
      { text: 'Cancel', style: 'cancel' }
    ]);
  };

  const pickAndAddItem = async (category: string, source: 'camera' | 'library') => {
    // 1. Pick Front Image
    const frontResult = await pickImage(source);
    if (!frontResult || frontResult.cancelled) return;

    // 2. Ask for Back Image
    Alert.alert(
      'Add Back View?',
      'Do you want to add a back view image for this item?',
      [
        { 
          text: 'No, skip', 
          onPress: () => saveItem(category, frontResult.uri) 
        },
        { 
          text: 'Yes, add back', 
          onPress: async () => {
            // Slight delay to allow modal to close
            setTimeout(async () => {
              const backResult = await pickImage(source);
              if (backResult && !backResult.cancelled) {
                saveItem(category, frontResult.uri, backResult.uri);
              } else {
                // If cancelled back image, just save front
                saveItem(category, frontResult.uri);
              }
            }, 500);
          } 
        }
      ]
    );
  };

  const saveItem = (category: string, frontUri: string, backUri?: string) => {
    const newItem: DisplayItem = {
      id: `local-${Date.now()}`,
      image: frontUri,
      backImage: backUri,
      category,
      isLocal: true,
    };
    
    addClothingItem({
      name: `My ${category}`,
      category: category as ClothingCategory,
      frontImageUri: frontUri,
      backImageUri: backUri,
      isLocal: true,
    });

    if (category === 'shirts') {
      setShirts(prev => [newItem, ...prev]);
      setSelectedShirt(newItem.id);
    } else if (category === 'pants') {
      setTrousers(prev => [newItem, ...prev]);
      setSelectedTrousers(newItem.id);
    } else if (category === 'jackets') {
      setJackets(prev => [newItem, ...prev]);
      setSelectedJacket(newItem.id);
    }
  };

  const canGenerate = selectedShirt !== null || selectedTrousers !== null || selectedJacket !== null;

  const handleDeleteLocalItem = (item: DisplayItem) => {
    Alert.alert(
      'Delete Item',
      'Are you sure you want to delete this item?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            // Remove from store (AsyncStorage) - this persists the deletion
            removeClothingItem(item.id);
            
            // Remove from local display list
            if (item.category === 'shirts') {
              setShirts(prev => prev.filter(i => i.id !== item.id));
              if (selectedShirt === item.id) setSelectedShirt(null);
            } else if (item.category === 'pants') {
              setTrousers(prev => prev.filter(i => i.id !== item.id));
              if (selectedTrousers === item.id) setSelectedTrousers(null);
            } else if (item.category === 'jackets') {
              setJackets(prev => prev.filter(i => i.id !== item.id));
              if (selectedJacket === item.id) setSelectedJacket(null);
            }
            // Close preview modal
            setPreviewItem(null);
            setPreviewShowBack(false);
          }
        }
      ]
    );
  };

  // Avatar creation functions
  const handleStartAvatarCreation = () => {
    setAvatarSelfie(null);
    setAvatarPosture(null);
    setShowAvatarModal(true);
  };

  const handlePickAvatarImage = async (type: 'selfie' | 'posture') => {
    Alert.alert('Choose Source', '', [
      { 
        text: 'Camera', 
        onPress: async () => {
          const result = await pickImage('camera');
          if (result && !result.cancelled) {
            if (type === 'selfie') setAvatarSelfie(result.uri);
            else setAvatarPosture(result.uri);
          }
        }
      },
      { 
        text: 'Gallery', 
        onPress: async () => {
          const result = await pickImage('library');
          if (result && !result.cancelled) {
            if (type === 'selfie') setAvatarSelfie(result.uri);
            else setAvatarPosture(result.uri);
          }
        }
      },
      { text: 'Cancel', style: 'cancel' }
    ]);
  };

  const handleCreateAvatar = async () => {
    if (!avatarSelfie || !avatarPosture) {
      Alert.alert('Missing Images', 'Please add both selfie and posture images.');
      return;
    }

    setIsCreatingAvatar(true);
    try {
      const selfieB64 = await imageUriToBase64(avatarSelfie);
      const postureB64 = await imageUriToBase64(avatarPosture);

      const result = await generateAvatar({
        selfie_b64: selfieB64,
        posture_b64: postureB64,
        background: 'studio',
        keep_clothes: false,
      });

      const newAvatar: AvatarItem = {
        id: `avatar-${Date.now()}`,
        image: base64ToDataUri(result.image_b64, 'image/png'),
      };

      setAvatars(prev => [...prev, newAvatar]);
      setSelectedAvatarId(newAvatar.id);
      setShowAvatarModal(false);
      setAvatarSelfie(null);
      setAvatarPosture(null);
      
      Alert.alert('Success', 'Avatar created successfully!');
    } catch (error) {
      console.error('Avatar creation failed:', error);
      Alert.alert('Error', error instanceof Error ? error.message : 'Failed to create avatar');
    } finally {
      setIsCreatingAvatar(false);
    }
  };

  const handleDeleteAvatar = (avatarId: string) => {
    const avatar = avatars.find(a => a.id === avatarId);
    if (avatar?.isDefault) {
      Alert.alert('Cannot Delete', 'Default avatar cannot be deleted.');
      return;
    }

    Alert.alert('Delete Avatar', 'Are you sure?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: () => {
          setAvatars(prev => prev.filter(a => a.id !== avatarId));
          if (selectedAvatarId === avatarId) {
            setSelectedAvatarId('default-1');
          }
        }
      }
    ]);
  };

  const handleGenerate = async () => {
    if (!canGenerate || isGenerating) return;
    
    setIsGenerating(true);
    translateY.value = withSpring(SNAP_BOTTOM); // Collapse sheet during generation
    
    try {
      // 1. Get Avatar Image
      const selectedAvatar = avatars.find(a => a.id === selectedAvatarId);
      if (!selectedAvatar) {
        throw new Error('No avatar selected');
      }
      console.log('[Generate] Avatar URI:', selectedAvatar.image);
      const avatarB64 = await imageUriToBase64(selectedAvatar.image);
      console.log('[Generate] Avatar B64 length:', avatarB64?.length || 0);

      // 2. Get Clothing Images
      const selectedItems = [
        shirts.find(i => i.id === selectedShirt),
        trousers.find(i => i.id === selectedTrousers),
        jackets.find(i => i.id === selectedJacket),
      ].filter((item): item is DisplayItem => item !== undefined);
      
      console.log('[Generate] Selected items:', selectedItems.length);
      selectedItems.forEach((item, i) => console.log(`[Generate] Item ${i}: ${item.image.substring(0, 50)}...`));
      
      const clothesB64 = await Promise.all(
        selectedItems.map(async (item, index) => {
          console.log(`[Generate] Converting cloth ${index}...`);
          const b64 = await imageUriToBase64(item.image);
          console.log(`[Generate] Cloth ${index} B64 length:`, b64?.length || 0);
          return b64;
        })
      );

      console.log('[Generate] All clothes converted, calling API...');
      
      // 3. Generate Try-On
      const tryOnResult = await generateTryOn({
        avatar_b64: avatarB64,
        clothes_b64: clothesB64,
      });

      let finalUri = base64ToDataUri(tryOnResult.image_b64, 'image/png');
      let finalType: 'image' | 'video' = 'image';

      // 4. If Video Mode, generate video loop
      let videoThumbnail: string | undefined;
      if (generationMode === 'video') {
        const videoResult = await generateVideoLoop({
          image_b64: tryOnResult.image_b64,
          mode: '360',
        });
        
        // Save first frame as thumbnail
        if (videoResult.first_frame_b64) {
          videoThumbnail = base64ToDataUri(videoResult.first_frame_b64, 'image/png');
        }
        
        // Save video to temp file (react-native-video needs file:// URI)
        const videoFileName = `vto_video_${Date.now()}.mp4`;
        const videoFilePath = `${FileSystem.cacheDirectory}${videoFileName}`;
        
        // Remove data URI prefix if present
        const base64Data = videoResult.video_b64.includes(',') 
          ? videoResult.video_b64.split(',')[1] 
          : videoResult.video_b64;
          
        await FileSystem.writeAsStringAsync(videoFilePath, base64Data, {
          encoding: FileSystem.EncodingType.Base64,
        });
        
        // Verify file exists
        const fileInfo = await FileSystem.getInfoAsync(videoFilePath);
        console.log('[Video] Saved to:', videoFilePath, 'exists:', fileInfo.exists, 'size:', fileInfo.size);
        
        if (!fileInfo.exists || fileInfo.size === 0) {
          throw new Error('Video file was not saved correctly');
        }
        
        finalUri = videoFilePath;
        finalType = 'video';
      }

      // 5. Update State
      setResultUri(finalUri);
      setResultType(finalType);
      
      // Add to persisted history
      addToHistory({
        type: finalType,
        uri: finalUri,
        thumbnail: videoThumbnail,
      });

      // Collapse sheet to show result
      translateY.value = withSpring(SNAP_BOTTOM);

    } catch (error) {
      console.error('Generation failed:', error);
      Alert.alert('Error', 'Failed to generate result. Please try again.');
      translateY.value = withSpring(SNAP_TOP); // Show sheet on error
    } finally {
      setIsGenerating(false);
    }
  };

  // Gesture Handler (new API for Reanimated v3+)
  const startY = useSharedValue(0);
  const panGesture = Gesture.Pan()
    .onStart(() => {
      startY.value = translateY.value;
    })
    .onUpdate((event) => {
      let nextY = startY.value + event.translationY;
      if (nextY < SNAP_TOP - 50) nextY = SNAP_TOP - 50;
      if (nextY > SNAP_BOTTOM + 50) nextY = SNAP_BOTTOM + 50;
      translateY.value = nextY;
    })
    .onEnd((event) => {
      if (event.velocityY > 500 || translateY.value > (SNAP_TOP + SNAP_BOTTOM) / 2) {
        translateY.value = withSpring(SNAP_BOTTOM);
      } else {
        translateY.value = withSpring(SNAP_TOP);
      }
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
  }));

  const toggleSheet = () => {
    translateY.value = withSpring(translateY.value > (SNAP_TOP + SNAP_BOTTOM) / 2 ? SNAP_TOP : SNAP_BOTTOM);
  };

  return (
    <View style={styles.container}>
      {/* Result Display */}
      <TouchableOpacity 
        style={styles.resultContainer} 
        activeOpacity={1} 
        onPress={toggleSheet}
      >
        {isGenerating ? (
          <GeneratingAnimation mode={generationMode} />
        ) : resultUri ? (
          resultType === 'video' ? (
            <Video
              source={
                resultUri === 'LOCAL_MOCK_VIDEO' 
                  ? require('../../assets/_mocks_/result.mov')
                  : { uri: resultUri }
              }
              style={{ width: SCREEN_WIDTH, height: SCREEN_HEIGHT }}
              resizeMode="cover"
              repeat={true}
              paused={false}
              muted={true}
              onError={(e: any) => {
                console.log('[Video] Error:', JSON.stringify(e.error || e));
              }}
              onLoad={() => console.log('[Video] Loaded successfully')}
            />
          ) : (
            <Image 
              source={{ uri: resultUri }} 
              style={{ width: SCREEN_WIDTH, height: SCREEN_HEIGHT }} 
              resizeMode="cover" 
            />
          )
        ) : (
          <Image 
            source={{ uri: avatars.find(a => a.id === selectedAvatarId)?.image || DEFAULT_AVATAR.image }} 
            style={{ width: SCREEN_WIDTH, height: SCREEN_HEIGHT }} 
            resizeMode="cover" 
          />
        )}
      </TouchableOpacity>

      {/* Bottom Sheet */}
      <Animated.View style={[styles.bottomSheet, animatedStyle]}>
        <GestureDetector gesture={panGesture}>
          <Animated.View>
            <TouchableOpacity style={styles.handleContainer} activeOpacity={0.8} onPress={toggleSheet}>
              <View style={styles.handle} />
            </TouchableOpacity>
          </Animated.View>
        </GestureDetector>
        
        <ScrollView
          style={styles.bottomSheetContent}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          bounces={true}
        >
            {/* History Section */}
            <Text style={styles.title}>History</Text>
            <View style={styles.galleryRow}>
              {/* New Generation Button (Active State) */}
              <TouchableOpacity
                style={[styles.galleryItem, !resultUri && styles.galleryItemActive]}
                onPress={() => { setResultUri(null); translateY.value = withSpring(SNAP_TOP); }}
              >
                <View style={styles.newGenIcon}>
                  <Ionicons name="add" size={32} color="#000" />
                </View>
                <Text style={styles.newGenText}>New</Text>
              </TouchableOpacity>

              {generationHistory.map(item => (
                <TouchableOpacity
                  key={item.id}
                  style={[styles.galleryItem, resultUri === item.uri && styles.galleryItemActive]}
                  onPress={async () => { 
                    let uri = item.uri;
                    
                    // If it's a video with data URI, convert to file first
                    if (item.type === 'video' && uri.startsWith('data:')) {
                      const base64Data = uri.split(',')[1];
                      const videoFilePath = `${FileSystem.cacheDirectory}history_video_${item.id}.mp4`;
                      await FileSystem.writeAsStringAsync(videoFilePath, base64Data, {
                        encoding: FileSystem.EncodingType.Base64,
                      });
                      uri = videoFilePath;
                    }
                    
                    setResultUri(uri); 
                    setResultType(item.type); 
                  }}
                >
                  {item.type === 'video' ? (
                    item.thumbnail ? (
                      <>
                        <Image source={{ uri: item.thumbnail }} style={styles.galleryImage} resizeMode="cover" />
                        <View style={styles.playOverlay}>
                          <Ionicons name="play-circle" size={24} color="#fff" />
                        </View>
                      </>
                    ) : (
                      <View style={styles.videoThumbnail}>
                        <Ionicons name="videocam" size={28} color="#fff" />
                        <Text style={styles.videoThumbnailText}>Video</Text>
                      </View>
                    )
                  ) : (
                    <Image source={{ uri: item.uri }} style={styles.galleryImage} resizeMode="cover" />
                  )}
                </TouchableOpacity>
              ))}
            </View>

            {/* Avatar Selection */}
            <View style={styles.sectionHeader}>
              <Text style={styles.label}>Model</Text>
              <TouchableOpacity onPress={handleStartAvatarCreation}>
                <Ionicons name="add-circle-outline" size={24} color="#000" />
              </TouchableOpacity>
            </View>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.avatarScrollView}>
              <View style={styles.avatarRow}>
                {avatars.map(avatar => (
                  <TouchableOpacity
                    key={avatar.id}
                    style={[styles.avatarItem, selectedAvatarId === avatar.id && styles.avatarActive]}
                    onPress={() => setSelectedAvatarId(avatar.id)}
                    onLongPress={() => !avatar.isDefault && handleDeleteAvatar(avatar.id)}
                    delayLongPress={300}
                  >
                    <Image source={{ uri: avatar.image }} style={styles.avatarImage} />
                    {selectedAvatarId === avatar.id && (
                      <View style={styles.avatarCheck}>
                        <Ionicons name="checkmark" size={12} color="#fff" />
                      </View>
                    )}
                    {avatar.isDefault && (
                      <View style={styles.defaultBadge}>
                        <Ionicons name="star" size={8} color="#fff" />
                      </View>
                    )}
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>

            {/* Clothes Selection */}
            {isLoadingClothes ? (
              <ActivityIndicator style={{ margin: 20 }} />
            ) : (
              <>
                <View style={styles.sectionHeader}>
                  <Text style={styles.label}>Shirts</Text>
                  <TouchableOpacity onPress={() => handleAddLocalItem('shirts')}>
                    <Ionicons name="add-circle-outline" size={24} color="#000" />
                  </TouchableOpacity>
                </View>
                <FlatList
                  data={shirts}
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  keyExtractor={item => item.id}
                  style={styles.clothesList}
                  contentContainerStyle={styles.clothesScrollContent}
                  renderItem={({ item }) => (
                    <ClothingItemView
                      item={item}
                      isSelected={selectedShirt === item.id}
                      onPress={() => setSelectedShirt(prev => prev === item.id ? null : item.id)}
                      onLongPress={() => setPreviewItem(item)}
                    />
                  )}
                />

                <View style={styles.sectionHeader}>
                  <Text style={styles.label}>Pants</Text>
                  <TouchableOpacity onPress={() => handleAddLocalItem('pants')}>
                    <Ionicons name="add-circle-outline" size={24} color="#000" />
                  </TouchableOpacity>
                </View>
                <FlatList
                  data={trousers}
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  keyExtractor={item => item.id}
                  style={styles.clothesList}
                  contentContainerStyle={styles.clothesScrollContent}
                  renderItem={({ item }) => (
                    <ClothingItemView
                      item={item}
                      isSelected={selectedTrousers === item.id}
                      onPress={() => setSelectedTrousers(prev => prev === item.id ? null : item.id)}
                      onLongPress={() => setPreviewItem(item)}
                    />
                  )}
                />
                
                <View style={styles.sectionHeader}>
                  <Text style={styles.label}>Jackets</Text>
                  <TouchableOpacity onPress={() => handleAddLocalItem('jackets')}>
                    <Ionicons name="add-circle-outline" size={24} color="#000" />
                  </TouchableOpacity>
                </View>
                <FlatList
                  data={jackets}
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  keyExtractor={item => item.id}
                  style={styles.clothesList}
                  contentContainerStyle={styles.clothesScrollContent}
                  renderItem={({ item }) => (
                    <ClothingItemView
                      item={item}
                      isSelected={selectedJacket === item.id}
                      onPress={() => setSelectedJacket(prev => prev === item.id ? null : item.id)}
                      onLongPress={() => setPreviewItem(item)}
                    />
                  )}
                />
              </>
            )}

            {/* Generation Controls */}
            <View style={styles.controls}>
              <View style={styles.modeSwitch}>
                <TouchableOpacity 
                  style={[styles.modeBtn, generationMode === 'image' && styles.modeBtnActive]}
                  onPress={() => setGenerationMode('image')}
                >
                  <Ionicons name="image-outline" size={20} color={generationMode === 'image' ? '#fff' : '#000'} />
                  <Text style={[styles.modeText, generationMode === 'image' && styles.modeTextActive]}>Photo</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                  style={[styles.modeBtn, generationMode === 'video' && styles.modeBtnActive]}
                  onPress={() => setGenerationMode('video')}
                >
                  <Ionicons name="videocam-outline" size={20} color={generationMode === 'video' ? '#fff' : '#000'} />
                  <Text style={[styles.modeText, generationMode === 'video' && styles.modeTextActive]}>Video</Text>
                </TouchableOpacity>
              </View>

              <TouchableOpacity
                style={[styles.btn, (!canGenerate || isGenerating) && styles.btnDisabled]}
                onPress={handleGenerate}
                disabled={!canGenerate || isGenerating}
              >
                <Ionicons name="sparkles" size={18} color={canGenerate ? '#fff' : '#bbb'} />
                <Text style={[styles.btnText, (!canGenerate || isGenerating) && styles.btnTextDisabled]}>
                  {isGenerating ? 'Generating...' : `Generate ${generationMode === 'video' ? 'Video' : 'Photo'}`}
                </Text>
              </TouchableOpacity>
            </View>
          </ScrollView>
        </Animated.View>

      {/* Clothing Preview Modal */}
      <Modal
        visible={previewItem !== null}
        transparent
        animationType="fade"
        onRequestClose={() => setPreviewItem(null)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {/* Close Button */}
            <TouchableOpacity 
              style={styles.modalClose} 
              onPress={() => { setPreviewItem(null); setPreviewShowBack(false); }}
            >
              <Ionicons name="close" size={28} color="#000" />
            </TouchableOpacity>

            {/* Image */}
            <Image
              source={{ 
                uri: previewShowBack && previewItem?.backImage 
                  ? previewItem.backImage 
                  : previewItem?.image 
              }}
              style={styles.modalImage}
              resizeMode="contain"
            />

            {/* Front/Back Toggle */}
            {previewItem?.backImage && (
              <View style={styles.modalToggle}>
                <TouchableOpacity
                  style={[styles.modalToggleBtn, !previewShowBack && styles.modalToggleBtnActive]}
                  onPress={() => setPreviewShowBack(false)}
                >
                  <Text style={[styles.modalToggleText, !previewShowBack && styles.modalToggleTextActive]}>
                    Front
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.modalToggleBtn, previewShowBack && styles.modalToggleBtnActive]}
                  onPress={() => setPreviewShowBack(true)}
                >
                  <Text style={[styles.modalToggleText, previewShowBack && styles.modalToggleTextActive]}>
                    Back
                  </Text>
                </TouchableOpacity>
              </View>
            )}

            {/* Item Info */}
            <View style={styles.modalInfo}>
              <Text style={styles.modalInfoText}>
                {previewItem?.isLocal ? '📱 Local Item' : '☁️ From API'}
              </Text>
              <Text style={styles.modalInfoCategory}>
                {previewItem?.category}
              </Text>
            </View>

            {/* Delete Button (only for local items) */}
            {previewItem?.isLocal && (
              <TouchableOpacity
                style={styles.modalDeleteBtn}
                onPress={() => previewItem && handleDeleteLocalItem(previewItem)}
              >
                <Ionicons name="trash-outline" size={18} color="#fff" />
                <Text style={styles.modalDeleteText}>Delete Item</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      </Modal>

      {/* Avatar Creation Modal */}
      <Modal
        visible={showAvatarModal}
        transparent
        animationType="slide"
        onRequestClose={() => !isCreatingAvatar && setShowAvatarModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.avatarModalContent}>
            {/* Header */}
            <View style={styles.avatarModalHeader}>
              <Text style={styles.avatarModalTitle}>Create Avatar</Text>
              <TouchableOpacity 
                onPress={() => !isCreatingAvatar && setShowAvatarModal(false)}
                disabled={isCreatingAvatar}
              >
                <Ionicons name="close" size={28} color={isCreatingAvatar ? '#ccc' : '#000'} />
              </TouchableOpacity>
            </View>

            <Text style={styles.avatarModalSubtitle}>
              Upload a selfie and a full-body posture photo to generate your avatar
            </Text>

            {/* Image Pickers */}
            <View style={styles.avatarImagePickers}>
              {/* Selfie */}
              <TouchableOpacity 
                style={styles.avatarImagePicker}
                onPress={() => handlePickAvatarImage('selfie')}
                disabled={isCreatingAvatar}
              >
                {avatarSelfie ? (
                  <Image source={{ uri: avatarSelfie }} style={styles.avatarPickerImage} />
                ) : (
                  <View style={styles.avatarPickerPlaceholder}>
                    <Ionicons name="person-circle-outline" size={40} color="#999" />
                    <Text style={styles.avatarPickerLabel}>Selfie</Text>
                  </View>
                )}
                {avatarSelfie && (
                  <View style={styles.avatarPickerCheck}>
                    <Ionicons name="checkmark" size={16} color="#fff" />
                  </View>
                )}
              </TouchableOpacity>

              {/* Posture */}
              <TouchableOpacity 
                style={styles.avatarImagePicker}
                onPress={() => handlePickAvatarImage('posture')}
                disabled={isCreatingAvatar}
              >
                {avatarPosture ? (
                  <Image source={{ uri: avatarPosture }} style={styles.avatarPickerImage} />
                ) : (
                  <View style={styles.avatarPickerPlaceholder}>
                    <Ionicons name="body-outline" size={40} color="#999" />
                    <Text style={styles.avatarPickerLabel}>Full Body</Text>
                  </View>
                )}
                {avatarPosture && (
                  <View style={styles.avatarPickerCheck}>
                    <Ionicons name="checkmark" size={16} color="#fff" />
                  </View>
                )}
              </TouchableOpacity>
            </View>

            {/* Create Button */}
            <TouchableOpacity
              style={[
                styles.avatarCreateBtn,
                (!avatarSelfie || !avatarPosture || isCreatingAvatar) && styles.avatarCreateBtnDisabled
              ]}
              onPress={handleCreateAvatar}
              disabled={!avatarSelfie || !avatarPosture || isCreatingAvatar}
            >
              {isCreatingAvatar ? (
                <>
                  <ActivityIndicator size="small" color="#fff" />
                  <Text style={styles.avatarCreateBtnText}>Creating Avatar...</Text>
                </>
              ) : (
                <>
                  <Ionicons name="sparkles" size={18} color="#fff" />
                  <Text style={styles.avatarCreateBtnText}>Generate Avatar</Text>
                </>
              )}
            </TouchableOpacity>

            <Text style={styles.avatarModalHint}>
              💡 Tip: Use a clear front-facing selfie and a standing full-body photo
            </Text>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  resultContainer: { ...StyleSheet.absoluteFillObject, backgroundColor: '#111', zIndex: 0 },
  videoContainer: { flex: 1, width: '100%', height: '100%', backgroundColor: '#000', justifyContent: 'center', alignItems: 'center' },
  video: { width: SCREEN_WIDTH, height: SCREEN_HEIGHT },
  videoLoader: { position: 'absolute', zIndex: 1 },
  videoBadge: { 
    position: 'absolute', 
    top: 60, 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 6,
    backgroundColor: 'rgba(0,0,0,0.6)', 
    paddingHorizontal: 12, 
    paddingVertical: 6, 
    borderRadius: 16 
  },
  videoBadgeText: { color: '#fff', fontSize: 12, fontWeight: '600' },
  simulatorWarning: {
    position: 'absolute',
    bottom: 200,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: 'rgba(255,150,0,0.9)',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
  },
  simulatorWarningText: { color: '#fff', fontSize: 13, fontWeight: '600' },
  bottomSheet: {
    position: 'absolute', left: 0, right: 0, top: 0, bottom: 0,
    backgroundColor: '#fff',
    borderTopLeftRadius: 28, borderTopRightRadius: 28,
    shadowColor: '#000', shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.25, shadowRadius: 3.84, elevation: 5, zIndex: 10,
  },
  handleContainer: { width: '100%', height: 40, justifyContent: 'center', alignItems: 'center' },
  handle: { width: 40, height: 5, backgroundColor: '#e0e0e0', borderRadius: 3 },
  bottomSheetContent: { flex: 1 },
  scrollContent: { paddingBottom: SNAP_TOP + 50 },
  title: { fontSize: 22, fontWeight: '700', color: '#000', marginBottom: 16, paddingHorizontal: PADDING },
  galleryRow: { flexDirection: 'row', gap: GALLERY_GAP, marginBottom: 20, paddingHorizontal: PADDING },
  galleryItem: {
    width: GALLERY_SIZE, height: GALLERY_SIZE * 1.25, borderRadius: 12, overflow: 'hidden',
    backgroundColor: '#f0f0f0', borderWidth: 2.5, borderColor: 'transparent',
    justifyContent: 'center', alignItems: 'center',
  },
  galleryItemActive: { borderColor: '#000' },
  galleryImage: { width: '100%', height: '100%' },
  playOverlay: {
    ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center', alignItems: 'center',
  },
  videoThumbnail: {
    width: '100%',
    height: '100%',
    backgroundColor: '#333',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 4,
  },
  videoThumbnailText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
  },
  newGenIcon: { marginBottom: 4 },
  newGenText: { fontSize: 12, fontWeight: '600', color: '#000' },
  label: { fontSize: 12, fontWeight: '600', color: '#999', textTransform: 'uppercase', letterSpacing: 0.5, marginTop: 12, marginBottom: 10, paddingHorizontal: PADDING },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 12, marginBottom: 10, paddingHorizontal: PADDING },
  clothesList: { flexGrow: 0, height: 80 },
  clothesScrollContent: { paddingHorizontal: PADDING, gap: 10 },
  clothesItem: { width: 80, height: 80, borderRadius: 12, overflow: 'hidden', backgroundColor: '#f0f0f0', borderWidth: 2.5, borderColor: 'transparent' },
  clothesActive: { borderColor: '#000' },
  clothesImage: { width: '100%', height: '100%' },
  check: { position: 'absolute', top: 5, right: 5, width: 20, height: 20, borderRadius: 10, backgroundColor: '#000', justifyContent: 'center', alignItems: 'center' },
  localBadge: { position: 'absolute', bottom: 5, right: 5, width: 14, height: 14, borderRadius: 7, backgroundColor: '#007AFF', justifyContent: 'center', alignItems: 'center' },
  flipBadge: { position: 'absolute', bottom: 5, left: 5, width: 14, height: 14, borderRadius: 7, backgroundColor: 'rgba(0,0,0,0.6)', justifyContent: 'center', alignItems: 'center' },
  avatarScrollView: { marginBottom: 8 },
  avatarRow: { flexDirection: 'row', paddingHorizontal: PADDING, gap: 10 },
  avatarItem: { width: 70, height: 70, borderRadius: 35, overflow: 'hidden', borderWidth: 3, borderColor: 'transparent', backgroundColor: '#f0f0f0' },
  avatarActive: { borderColor: '#000' },
  avatarImage: { width: '100%', height: '100%' },
  avatarCheck: { position: 'absolute', bottom: 2, right: 2, width: 18, height: 18, borderRadius: 9, backgroundColor: '#000', justifyContent: 'center', alignItems: 'center' },
  defaultBadge: { position: 'absolute', top: 2, right: 2, width: 16, height: 16, borderRadius: 8, backgroundColor: '#FFD700', justifyContent: 'center', alignItems: 'center' },
  controls: { paddingHorizontal: PADDING, marginTop: 20 },
  modeSwitch: { flexDirection: 'row', backgroundColor: '#f0f0f0', borderRadius: 12, padding: 4, marginBottom: 16 },
  modeBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 10, borderRadius: 10, gap: 6 },
  modeBtnActive: { backgroundColor: '#000' },
  modeText: { fontSize: 14, fontWeight: '600', color: '#000' },
  modeTextActive: { color: '#fff' },
  btn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#000', paddingVertical: 16, borderRadius: 14, gap: 8 },
  btnDisabled: { backgroundColor: '#e5e5e5' },
  btnText: { fontSize: 16, fontWeight: '600', color: '#fff' },
  btnTextDisabled: { color: '#bbb' },
  loading: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingStatusText: { color: '#fff', marginTop: 10, fontSize: 16 },
  placeholder: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  placeholderText: { color: '#666', marginTop: 16, fontSize: 16 },
  loadingClothes: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 12, gap: 8 },
  loadingText: { color: '#666', fontSize: 14 },
  errorBox: { backgroundColor: '#fff3cd', padding: 12, marginHorizontal: PADDING, borderRadius: 8, marginBottom: 12 },
  errorText: { color: '#856404', fontSize: 14 },
  retryText: { color: '#0066cc', fontSize: 12, marginTop: 4 },
  emptyText: { color: '#999', fontSize: 14, paddingVertical: 20 },
  // Modal styles
  modalOverlay: { 
    flex: 1, 
    backgroundColor: 'rgba(0,0,0,0.9)', 
    justifyContent: 'center', 
    alignItems: 'center' 
  },
  modalContent: { 
    width: SCREEN_WIDTH - 40, 
    maxHeight: SCREEN_HEIGHT * 0.8,
    backgroundColor: '#fff', 
    borderRadius: 20, 
    padding: 20,
    alignItems: 'center',
  },
  modalClose: { 
    position: 'absolute', 
    top: 12, 
    right: 12, 
    zIndex: 10,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalImage: { 
    width: SCREEN_WIDTH - 80, 
    height: SCREEN_WIDTH - 80, 
    borderRadius: 16,
    backgroundColor: '#f5f5f5',
    marginTop: 20,
  },
  modalToggle: { 
    flexDirection: 'row', 
    backgroundColor: '#f0f0f0', 
    borderRadius: 12, 
    padding: 4, 
    marginTop: 20,
    width: '100%',
  },
  modalToggleBtn: { 
    flex: 1, 
    paddingVertical: 12, 
    borderRadius: 10, 
    alignItems: 'center' 
  },
  modalToggleBtnActive: { 
    backgroundColor: '#000' 
  },
  modalToggleText: { 
    fontSize: 15, 
    fontWeight: '600', 
    color: '#000' 
  },
  modalToggleTextActive: { 
    color: '#fff' 
  },
  modalInfo: { 
    marginTop: 16, 
    alignItems: 'center' 
  },
  modalInfoText: { 
    fontSize: 14, 
    color: '#666' 
  },
  modalInfoCategory: { 
    fontSize: 12, 
    color: '#999', 
    textTransform: 'uppercase', 
    marginTop: 4 
  },
  modalDeleteBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#dc3545',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 10,
    marginTop: 16,
    gap: 8,
  },
  modalDeleteText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
  },
  // Avatar Creation Modal
  avatarModalContent: {
    width: SCREEN_WIDTH - 40,
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 24,
  },
  avatarModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  avatarModalTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#000',
  },
  avatarModalSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 24,
    lineHeight: 20,
  },
  avatarImagePickers: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 24,
  },
  avatarImagePicker: {
    flex: 1,
    aspectRatio: 0.75,
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: '#f5f5f5',
    borderWidth: 2,
    borderColor: '#e0e0e0',
    borderStyle: 'dashed',
  },
  avatarPickerImage: {
    width: '100%',
    height: '100%',
  },
  avatarPickerPlaceholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  avatarPickerLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#999',
  },
  avatarPickerCheck: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#34C759',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarCreateBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#000',
    paddingVertical: 16,
    borderRadius: 14,
    gap: 8,
  },
  avatarCreateBtnDisabled: {
    backgroundColor: '#ccc',
  },
  avatarCreateBtnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  avatarModalHint: {
    fontSize: 13,
    color: '#999',
    textAlign: 'center',
    marginTop: 16,
  },
});
