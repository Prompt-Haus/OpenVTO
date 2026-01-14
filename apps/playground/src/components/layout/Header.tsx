import React from 'react';
import { View, Text, TouchableOpacity, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface ScreenHeaderProps {
  title: string;
  subtitle?: string;
  leftAction?: {
    icon: keyof typeof Ionicons.glyphMap;
    onPress: () => void;
  };
  rightAction?: {
    icon: keyof typeof Ionicons.glyphMap;
    onPress: () => void;
    label?: string;
  };
}

export function ScreenHeader({
  title,
  subtitle,
  leftAction,
  rightAction,
}: ScreenHeaderProps) {
  return (
    <View className="bg-white border-b border-border">
      <SafeAreaView>
        <View className="flex-row items-center justify-between px-4 py-3 min-h-[56px]">
          {/* Left action */}
          <View className="w-12">
            {leftAction && (
              <TouchableOpacity
                onPress={leftAction.onPress}
                className="p-2 -ml-2"
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                <Ionicons name={leftAction.icon} size={24} color="#000" />
              </TouchableOpacity>
            )}
          </View>

          {/* Title */}
          <View className="flex-1 items-center">
            <Text className="text-sm font-semibold text-black uppercase tracking-widest">
              {title}
            </Text>
            {subtitle && (
              <Text className="text-xs text-primary-400 mt-0.5">
                {subtitle}
              </Text>
            )}
          </View>

          {/* Right action */}
          <View className="w-12 items-end">
            {rightAction && (
              <TouchableOpacity
                onPress={rightAction.onPress}
                className="p-2 -mr-2 flex-row items-center"
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                {rightAction.label && (
                  <Text className="text-xs font-medium text-black uppercase tracking-wide mr-1">
                    {rightAction.label}
                  </Text>
                )}
                <Ionicons name={rightAction.icon} size={24} color="#000" />
              </TouchableOpacity>
            )}
          </View>
        </View>
      </SafeAreaView>
    </View>
  );
}

// Simple page header without actions
interface PageTitleProps {
  title: string;
  subtitle?: string;
}

export function PageTitle({ title, subtitle }: PageTitleProps) {
  return (
    <View className="px-4 py-6">
      <Text className="text-2xl font-light text-black tracking-tight">
        {title}
      </Text>
      {subtitle && (
        <Text className="text-sm text-primary-400 mt-1">
          {subtitle}
        </Text>
      )}
    </View>
  );
}
