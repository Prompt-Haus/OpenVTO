import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import React, { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { usePlaygroundStore } from '../../src/store';

const BACKGROUNDS = [
  { id: 'white', label: 'White', color: '#FFFFFF' },
  { id: 'gray', label: 'Gray', color: '#F3F4F6' },
  { id: 'black', label: 'Black', color: '#000000' },
  { id: 'studio', label: 'Studio', color: '#1F2937' },
];

const PERSPECTIVES = [
  { id: 'front', label: 'Front' },
  { id: 'back', label: 'Back' },
  { id: 'side', label: 'Side' },
  { id: '3/4', label: '3/4' },
];

const STATES = [
  { id: 'base', label: 'Base (Underwear)' },
  { id: 'clothed', label: 'Clothed' },
];

interface ChipProps {
  label: string;
  selected: boolean;
  onPress: () => void;
  color?: string;
}

const Chip = ({ label, selected, onPress, color }: ChipProps) => (
  <TouchableOpacity
    onPress={onPress}
    style={[styles.chip, selected && styles.chipSelected]}
    activeOpacity={0.7}
  >
    {color && (
      <View style={[styles.colorDot, { backgroundColor: color }]} />
    )}
    <Text style={[styles.chipText, selected && styles.chipTextSelected]}>{label}</Text>
  </TouchableOpacity>
);

export default function AvatarScreen() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [background, setBackground] = useState('white');
  const [perspective, setPerspective] = useState('front');
  const [avatarState, setAvatarState] = useState('base');
  
  const { 
    avatars,
    selectedAvatarId,
    selectAvatar,
    addAvatar,
    updateAvatarStatus,
    removeAvatar,
    addPhoto,
  } = usePlaygroundStore();

  const processImage = async (uri: string, width: number, height: number, source: 'camera' | 'gallery') => {
    addPhoto(uri, source, width, height);
    
    setIsProcessing(true);
    const avatarId = addAvatar({
      name: `Avatar ${avatars.length + 1}`,
      sourcePhotoId: '',
      perspective: perspective as any,
      state: avatarState as any,
      backgroundType: background as any,
      imageUri: uri,
      status: 'pending',
    });
    
    setTimeout(() => updateAvatarStatus(avatarId, 'processing'), 300);
    setTimeout(() => {
      updateAvatarStatus(avatarId, 'completed', uri);
      selectAvatar(avatarId);
      setIsProcessing(false);
    }, 1500);
  };

  const pickFromGallery = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission Required', 'Please grant access to your photo library.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 1,
      allowsEditing: true,
      aspect: [3, 4],
    });

    if (!result.canceled && result.assets[0]) {
      const asset = result.assets[0];
      await processImage(asset.uri, asset.width ?? 600, asset.height ?? 800, 'gallery');
    }
  };

  const takePhoto = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission Required', 'Please grant access to your camera.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ['images'],
      quality: 1,
      allowsEditing: true,
      aspect: [3, 4],
    });

    if (!result.canceled && result.assets[0]) {
      const asset = result.assets[0];
      await processImage(asset.uri, asset.width ?? 600, asset.height ?? 800, 'camera');
    }
  };

  const handleDeleteAvatar = (id: string) => {
    Alert.alert('Delete Avatar', 'Remove this avatar?', [
      { text: 'Cancel', style: 'cancel' },
      { 
        text: 'Delete', 
        style: 'destructive', 
        onPress: () => {
          removeAvatar(id);
          if (selectedAvatarId === id) {
            const remaining = avatars.filter(a => a.id !== id);
            if (remaining.length > 0) selectAvatar(remaining[0].id);
          }
        }
      },
    ]);
  };

  const completedAvatars = avatars.filter(a => a.status === 'completed');

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Avatar</Text>
          <Text style={styles.subtitle}>Create avatars from your photos</Text>
        </View>

        {/* Upload Actions */}
        <View style={styles.uploadSection}>
          <TouchableOpacity 
            style={styles.uploadButton} 
            onPress={takePhoto}
            disabled={isProcessing}
            activeOpacity={0.7}
          >
            <Ionicons name="camera" size={24} color="#000" />
            <Text style={styles.uploadButtonText}>Camera</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.uploadButton} 
            onPress={pickFromGallery}
            disabled={isProcessing}
            activeOpacity={0.7}
          >
            <Ionicons name="images" size={24} color="#000" />
            <Text style={styles.uploadButtonText}>Gallery</Text>
          </TouchableOpacity>
        </View>

        {isProcessing && (
          <View style={styles.processingContainer}>
            <ActivityIndicator size="small" color="#000" />
            <Text style={styles.processingText}>Creating avatar...</Text>
          </View>
        )}

        {/* Generation Options */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Generation Options</Text>
          
          <View style={styles.optionGroup}>
            <Text style={styles.optionLabel}>Background</Text>
            <View style={styles.chipRow}>
              {BACKGROUNDS.map(b => (
                <Chip
                  key={b.id}
                  label={b.label}
                  color={b.color}
                  selected={background === b.id}
                  onPress={() => setBackground(b.id)}
                />
              ))}
            </View>
          </View>

          <View style={styles.optionGroup}>
            <Text style={styles.optionLabel}>Perspective</Text>
            <View style={styles.chipRow}>
              {PERSPECTIVES.map(p => (
                <Chip
                  key={p.id}
                  label={p.label}
                  selected={perspective === p.id}
                  onPress={() => setPerspective(p.id)}
                />
              ))}
            </View>
          </View>

          <View style={styles.optionGroup}>
            <Text style={styles.optionLabel}>Avatar State</Text>
            <View style={styles.chipRow}>
              {STATES.map(s => (
                <Chip
                  key={s.id}
                  label={s.label}
                  selected={avatarState === s.id}
                  onPress={() => setAvatarState(s.id)}
                />
              ))}
            </View>
          </View>
        </View>

        {/* Your Avatars */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your Avatars ({completedAvatars.length})</Text>
          
          {completedAvatars.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="person-outline" size={36} color="#D1D5DB" />
              <Text style={styles.emptyText}>No avatars yet</Text>
              <Text style={styles.emptySubtext}>Take or choose a photo above</Text>
            </View>
          ) : (
            <View style={styles.avatarGrid}>
              {completedAvatars.map(avatar => (
                <TouchableOpacity
                  key={avatar.id}
                  style={[styles.avatarCard, selectedAvatarId === avatar.id && styles.avatarCardSelected]}
                  onPress={() => selectAvatar(avatar.id)}
                  onLongPress={() => handleDeleteAvatar(avatar.id)}
                  activeOpacity={0.8}
                >
                  <Image source={{ uri: avatar.imageUri }} style={styles.avatarImage} resizeMode="cover" />
                  {selectedAvatarId === avatar.id && (
                    <View style={styles.selectedIndicator}>
                      <Ionicons name="checkmark-circle" size={22} color="#000" />
                    </View>
                  )}
                  <View style={styles.avatarMeta}>
                    <Text style={styles.avatarMetaText}>{avatar.perspective}</Text>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          )}
          
          {completedAvatars.length > 0 && (
            <Text style={styles.hintText}>Tap to select • Long press to delete</Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  content: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '600',
    color: '#000',
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  uploadSection: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    gap: 12,
  },
  uploadButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    paddingVertical: 16,
    gap: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  uploadButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#000',
  },
  processingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    gap: 8,
  },
  processingText: {
    color: '#6B7280',
    fontSize: 13,
  },
  section: {
    paddingHorizontal: 20,
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 12,
  },
  optionGroup: {
    marginBottom: 16,
  },
  optionLabel: {
    fontSize: 13,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 8,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
    gap: 6,
  },
  chipSelected: {
    backgroundColor: '#000',
  },
  chipText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#6B7280',
  },
  chipTextSelected: {
    color: '#FFF',
  },
  colorDot: {
    width: 14,
    height: 14,
    borderRadius: 7,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
  },
  emptyText: {
    color: '#6B7280',
    fontSize: 15,
    fontWeight: '500',
    marginTop: 12,
  },
  emptySubtext: {
    color: '#9CA3AF',
    fontSize: 13,
    marginTop: 4,
  },
  avatarGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  avatarCard: {
    width: '31%',
    aspectRatio: 3/4,
    borderRadius: 10,
    overflow: 'hidden',
    backgroundColor: '#F3F4F6',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  avatarCardSelected: {
    borderColor: '#000',
  },
  avatarImage: {
    width: '100%',
    height: '100%',
  },
  selectedIndicator: {
    position: 'absolute',
    top: 6,
    right: 6,
    backgroundColor: '#FFF',
    borderRadius: 11,
  },
  avatarMeta: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingVertical: 4,
    paddingHorizontal: 6,
  },
  avatarMetaText: {
    color: '#FFF',
    fontSize: 10,
    fontWeight: '500',
    textTransform: 'uppercase',
  },
  hintText: {
    color: '#9CA3AF',
    fontSize: 11,
    textAlign: 'center',
    marginTop: 12,
  },
});
