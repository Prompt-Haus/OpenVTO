import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet, ViewStyle } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface CardProps {
  children: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  style?: ViewStyle;
}

export function Card({
  children,
  variant = 'default',
  padding = 'md',
  style,
}: CardProps) {
  return (
    <View style={[styles.card, styles[`card_${variant}`], styles[`padding_${padding}`], style]}>
      {children}
    </View>
  );
}

// Image Card for displaying photos/clothing/avatars
interface ImageCardProps {
  uri: string;
  onPress?: () => void;
  onDelete?: () => void;
  selected?: boolean;
  label?: string;
  badge?: string;
  aspectRatio?: 'square' | 'portrait' | 'landscape';
  size?: 'sm' | 'md' | 'lg';
}

export function ImageCard({
  uri,
  onPress,
  onDelete,
  selected = false,
  label,
  badge,
  aspectRatio = 'square',
  size = 'md',
}: ImageCardProps) {
  const aspectStyles = {
    square: { aspectRatio: 1 },
    portrait: { aspectRatio: 3 / 4 },
    landscape: { aspectRatio: 4 / 3 },
  };

  const sizeStyles = {
    sm: { width: 80 },
    md: { width: 128 },
    lg: { width: '100%' as const },
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.8}
      style={[
        styles.imageCard,
        sizeStyles[size],
        selected ? styles.imageCardSelected : styles.imageCardDefault,
      ]}
    >
      <View style={[styles.imageContainer, aspectStyles[aspectRatio]]}>
        <Image source={{ uri }} style={styles.image} resizeMode="cover" />

        {/* Selection indicator */}
        {selected && (
          <View style={styles.selectionIndicator}>
            <Ionicons name="checkmark" size={14} color="white" />
          </View>
        )}

        {/* Delete button */}
        {onDelete && (
          <TouchableOpacity onPress={onDelete} style={styles.deleteButton}>
            <Ionicons name="close" size={14} color="black" />
          </TouchableOpacity>
        )}

        {/* Badge */}
        {badge && (
          <View style={styles.badge}>
            <Text style={styles.badgeText}>{badge}</Text>
          </View>
        )}
      </View>

      {/* Label */}
      {label && (
        <View style={styles.labelContainer}>
          <Text style={styles.labelText} numberOfLines={1}>
            {label}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

// Placeholder card for empty states
interface PlaceholderCardProps {
  icon: keyof typeof Ionicons.glyphMap;
  text: string;
  onPress?: () => void;
  aspectRatio?: 'square' | 'portrait' | 'landscape';
  size?: 'sm' | 'md' | 'lg';
}

export function PlaceholderCard({
  icon,
  text,
  onPress,
  aspectRatio = 'square',
  size = 'md',
}: PlaceholderCardProps) {
  const aspectStyles = {
    square: { aspectRatio: 1 },
    portrait: { aspectRatio: 3 / 4 },
    landscape: { aspectRatio: 4 / 3 },
  };

  const sizeStyles = {
    sm: { width: 80 },
    md: { width: 128 },
    lg: { width: '100%' as const },
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.7}
      style={[styles.placeholderCard, sizeStyles[size]]}
    >
      <View style={[styles.placeholderContent, aspectStyles[aspectRatio]]}>
        <Ionicons name={icon} size={24} color="#a3a3a3" />
        <Text style={styles.placeholderText}>{text}</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  // Card styles
  card: {
    backgroundColor: '#ffffff',
  },
  card_default: {},
  card_elevated: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  card_outlined: {
    borderWidth: 1,
    borderColor: '#e5e5e5',
  },
  padding_none: {},
  padding_sm: {
    padding: 8,
  },
  padding_md: {
    padding: 16,
  },
  padding_lg: {
    padding: 24,
  },

  // ImageCard styles
  imageCard: {
    backgroundColor: '#f5f5f5',
    overflow: 'hidden',
  },
  imageCardDefault: {
    borderWidth: 1,
    borderColor: '#e5e5e5',
  },
  imageCardSelected: {
    borderWidth: 2,
    borderColor: '#000000',
  },
  imageContainer: {
    position: 'relative',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  selectionIndicator: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 24,
    height: 24,
    backgroundColor: '#000000',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  deleteButton: {
    position: 'absolute',
    top: 8,
    left: 8,
    width: 24,
    height: 24,
    backgroundColor: 'rgba(255,255,255,0.9)',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  badge: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    backgroundColor: '#000000',
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  badgeText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
    textTransform: 'uppercase',
  },
  labelContainer: {
    padding: 8,
    backgroundColor: '#ffffff',
  },
  labelText: {
    fontSize: 12,
    color: '#525252',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },

  // PlaceholderCard styles
  placeholderCard: {
    borderWidth: 1,
    borderStyle: 'dashed',
    borderColor: '#d4d4d4',
    backgroundColor: '#f5f5f5',
  },
  placeholderContent: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderText: {
    fontSize: 12,
    color: '#737373',
    marginTop: 8,
    textAlign: 'center',
    paddingHorizontal: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
});
