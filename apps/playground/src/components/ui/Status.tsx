import React from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import type { GenerationStatus } from '../../types';

interface StatusBadgeProps {
  status: GenerationStatus;
  size?: 'sm' | 'md';
}

const statusConfig: Record<
  GenerationStatus,
  { label: string; color: string; bgColor: string; icon?: keyof typeof Ionicons.glyphMap }
> = {
  idle: { label: 'Ready', color: '#737373', bgColor: '#e5e5e5', icon: 'ellipse-outline' },
  pending: { label: 'Queued', color: '#737373', bgColor: '#e5e5e5', icon: 'time-outline' },
  processing: { label: 'Processing', color: '#000', bgColor: '#d4d4d4' },
  completed: { label: 'Done', color: '#fff', bgColor: '#000000', icon: 'checkmark' },
  failed: { label: 'Failed', color: '#dc2626', bgColor: '#fecaca', icon: 'alert-circle' },
};

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const config = statusConfig[status];
  const isProcessing = status === 'processing';
  const isCompleted = status === 'completed';

  const iconSize = size === 'sm' ? 10 : 12;

  return (
    <View
      style={[
        styles.badge,
        size === 'sm' ? styles.badgeSm : styles.badgeMd,
        { backgroundColor: config.bgColor },
      ]}
    >
      {isProcessing ? (
        <ActivityIndicator size="small" color={config.color} style={styles.badgeIcon} />
      ) : config.icon ? (
        <Ionicons
          name={config.icon}
          size={iconSize}
          color={config.color}
          style={styles.badgeIcon}
        />
      ) : null}
      <Text
        style={[
          styles.badgeText,
          size === 'sm' ? styles.badgeTextSm : styles.badgeTextMd,
          { color: config.color },
        ]}
      >
        {config.label}
      </Text>
    </View>
  );
}

// Loading overlay
interface LoadingOverlayProps {
  visible: boolean;
  message?: string;
}

export function LoadingOverlay({ visible, message }: LoadingOverlayProps) {
  if (!visible) return null;

  return (
    <View style={styles.overlay}>
      <ActivityIndicator size="large" color="#000" />
      {message && <Text style={styles.overlayText}>{message}</Text>}
    </View>
  );
}

// Progress indicator
interface ProgressBarProps {
  progress: number; // 0-100
  label?: string;
}

export function ProgressBar({ progress, label }: ProgressBarProps) {
  const clampedProgress = Math.min(100, Math.max(0, progress));

  return (
    <View style={styles.progressContainer}>
      {label && (
        <View style={styles.progressHeader}>
          <Text style={styles.progressLabel}>{label}</Text>
          <Text style={styles.progressPercent}>{Math.round(clampedProgress)}%</Text>
        </View>
      )}
      <View style={styles.progressTrack}>
        <View style={[styles.progressFill, { width: `${clampedProgress}%` }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  // Status Badge
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  badgeSm: {
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  badgeMd: {
    paddingHorizontal: 12,
    paddingVertical: 4,
  },
  badgeIcon: {
    marginRight: 4,
  },
  badgeText: {
    fontWeight: '500',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  badgeTextSm: {
    fontSize: 10,
  },
  badgeTextMd: {
    fontSize: 12,
  },

  // Loading Overlay
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255,255,255,0.95)',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 50,
  },
  overlayText: {
    marginTop: 16,
    fontSize: 14,
    color: '#404040',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },

  // Progress Bar
  progressContainer: {
    width: '100%',
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  progressLabel: {
    fontSize: 12,
    color: '#525252',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  progressPercent: {
    fontSize: 12,
    color: '#525252',
  },
  progressTrack: {
    height: 4,
    backgroundColor: '#e5e5e5',
    width: '100%',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#000000',
  },
});
