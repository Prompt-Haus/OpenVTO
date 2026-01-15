import React from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function PreviewModal() {
  const params = useLocalSearchParams<{ uri?: string; type?: string; title?: string }>();

  const handleClose = () => {
    router.back();
  };

  const handleShare = () => {
    // Implement share functionality
  };

  const handleSave = () => {
    // Implement save functionality
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <SafeAreaView edges={['top']}>
        <View style={styles.header}>
          <TouchableOpacity onPress={handleClose} style={styles.closeButton}>
            <Ionicons name="close" size={28} color="white" />
          </TouchableOpacity>
          <Text style={styles.title}>{params.title || 'Preview'}</Text>
          <TouchableOpacity onPress={handleShare} style={styles.shareButton}>
            <Ionicons name="share-outline" size={24} color="white" />
          </TouchableOpacity>
        </View>
      </SafeAreaView>

      {/* Content */}
      <View style={styles.content}>
        {params.uri ? (
          <Image source={{ uri: params.uri }} style={styles.image} resizeMode="contain" />
        ) : (
          <View style={styles.placeholder}>
            <Ionicons name="image-outline" size={64} color="#525252" />
            <Text style={styles.placeholderText}>No preview available</Text>
          </View>
        )}
      </View>

      {/* Actions */}
      <SafeAreaView edges={['bottom']}>
        <View style={styles.actions}>
          <TouchableOpacity onPress={handleShare} style={styles.actionOutline}>
            <Ionicons name="share-outline" size={20} color="white" />
            <Text style={styles.actionOutlineText}>Share</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={handleSave} style={styles.actionPrimary}>
            <Ionicons name="download-outline" size={20} color="black" />
            <Text style={styles.actionPrimaryText}>Save</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  closeButton: {
    padding: 8,
    marginLeft: -8,
  },
  title: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  shareButton: {
    padding: 8,
    marginRight: -8,
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16,
  },
  image: {
    width: '100%',
    aspectRatio: 3 / 4,
  },
  placeholder: {
    alignItems: 'center',
  },
  placeholderText: {
    color: '#737373',
    marginTop: 16,
  },
  actions: {
    paddingHorizontal: 16,
    paddingVertical: 16,
    flexDirection: 'row',
    gap: 12,
  },
  actionOutline: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderWidth: 1,
    borderColor: '#ffffff',
  },
  actionOutlineText: {
    marginLeft: 8,
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  actionPrimary: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    backgroundColor: '#ffffff',
  },
  actionPrimaryText: {
    marginLeft: 8,
    color: '#000000',
    fontSize: 14,
    fontWeight: '500',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
});
