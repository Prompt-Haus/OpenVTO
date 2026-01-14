import React from 'react';
import { View, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

interface ScreenContainerProps {
  children: React.ReactNode;
  scrollable?: boolean;
  padded?: boolean;
  safeArea?: boolean;
  keyboardAvoiding?: boolean;
}

export function ScreenContainer({
  children,
  scrollable = true,
  padded = false,
  safeArea = true,
  keyboardAvoiding = false,
}: ScreenContainerProps) {
  const content = (
    <View className={`flex-1 bg-white ${padded ? 'px-4' : ''}`}>
      {scrollable ? (
        <ScrollView
          className="flex-1"
          contentContainerStyle={{ flexGrow: 1 }}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {children}
        </ScrollView>
      ) : (
        children
      )}
    </View>
  );

  if (keyboardAvoiding) {
    return (
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        className="flex-1 bg-white"
      >
        {safeArea ? <SafeAreaView className="flex-1">{content}</SafeAreaView> : content}
      </KeyboardAvoidingView>
    );
  }

  if (safeArea) {
    return <SafeAreaView className="flex-1 bg-white">{content}</SafeAreaView>;
  }

  return content;
}

// Grid container for items
interface GridContainerProps {
  children: React.ReactNode;
  columns?: 2 | 3 | 4;
  gap?: 'sm' | 'md' | 'lg';
}

const gapStyles: Record<string, string> = {
  sm: 'gap-1',
  md: 'gap-2',
  lg: 'gap-4',
};

export function GridContainer({
  children,
  columns = 3,
  gap = 'md',
}: GridContainerProps) {
  return (
    <View className={`flex-row flex-wrap px-4 ${gapStyles[gap]}`}>
      {React.Children.map(children, (child) => (
        <View style={{ width: `${100 / columns - (columns > 2 ? 2 : 1)}%` }}>
          {child}
        </View>
      ))}
    </View>
  );
}

// Action bar at bottom
interface ActionBarProps {
  children: React.ReactNode;
}

export function ActionBar({ children }: ActionBarProps) {
  return (
    <View className="border-t border-border bg-white">
      <SafeAreaView edges={['bottom']}>
        <View className="px-4 py-3 flex-row gap-3">
          {children}
        </View>
      </SafeAreaView>
    </View>
  );
}
