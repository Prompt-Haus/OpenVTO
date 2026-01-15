import React from 'react';
import { View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// Tab selector component
interface TabOption {
  key: string;
  label: string;
  icon?: keyof typeof Ionicons.glyphMap;
}

interface TabSelectorProps {
  options: TabOption[];
  selected: string;
  onSelect: (key: string) => void;
  variant?: 'pills' | 'underline';
}

export function TabSelector({
  options,
  selected,
  onSelect,
  variant = 'pills',
}: TabSelectorProps) {
  if (variant === 'underline') {
    return (
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.underlineContainer}
      >
        <View style={styles.underlineRow}>
          {options.map((option) => (
            <TouchableOpacity
              key={option.key}
              onPress={() => onSelect(option.key)}
              style={[
                styles.underlineTab,
                selected === option.key && styles.underlineTabSelected,
              ]}
            >
              {option.icon && (
                <Ionicons
                  name={option.icon}
                  size={16}
                  color={selected === option.key ? '#000' : '#a3a3a3'}
                  style={styles.tabIcon}
                />
              )}
              <Text
                style={[
                  styles.tabText,
                  selected === option.key ? styles.tabTextSelected : styles.tabTextInactive,
                ]}
              >
                {option.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.pillsContainer}
    >
      <View style={styles.pillsRow}>
        {options.map((option) => (
          <TouchableOpacity
            key={option.key}
            onPress={() => onSelect(option.key)}
            style={[
              styles.pillTab,
              selected === option.key ? styles.pillTabSelected : styles.pillTabDefault,
            ]}
          >
            {option.icon && (
              <Ionicons
                name={option.icon}
                size={14}
                color={selected === option.key ? '#fff' : '#737373'}
                style={styles.tabIcon}
              />
            )}
            <Text
              style={[
                styles.tabText,
                selected === option.key ? styles.pillTextSelected : styles.pillTextDefault,
              ]}
            >
              {option.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

// Chip component for tags/filters
interface ChipProps {
  label: string;
  selected?: boolean;
  onPress?: () => void;
  onRemove?: () => void;
  size?: 'sm' | 'md';
}

export function Chip({
  label,
  selected = false,
  onPress,
  onRemove,
  size = 'md',
}: ChipProps) {
  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.7}
      style={[
        styles.chip,
        size === 'sm' ? styles.chipSm : styles.chipMd,
        selected ? styles.chipSelected : styles.chipDefault,
      ]}
    >
      <Text
        style={[
          size === 'sm' ? styles.chipTextSm : styles.chipTextMd,
          selected ? styles.chipTextSelected : styles.chipTextDefault,
        ]}
      >
        {label}
      </Text>
      {onRemove && (
        <TouchableOpacity onPress={onRemove} style={styles.chipRemove}>
          <Ionicons name="close" size={12} color={selected ? '#fff' : '#737373'} />
        </TouchableOpacity>
      )}
    </TouchableOpacity>
  );
}

// Radio option group
interface RadioOption {
  key: string;
  label: string;
  description?: string;
}

interface RadioGroupProps {
  options: RadioOption[];
  selected: string;
  onSelect: (key: string) => void;
  label?: string;
}

export function RadioGroup({
  options,
  selected,
  onSelect,
  label,
}: RadioGroupProps) {
  return (
    <View>
      {label && <Text style={styles.radioLabel}>{label}</Text>}
      <View style={styles.radioGroup}>
        {options.map((option) => (
          <TouchableOpacity
            key={option.key}
            onPress={() => onSelect(option.key)}
            style={[
              styles.radioOption,
              selected === option.key ? styles.radioOptionSelected : styles.radioOptionDefault,
            ]}
          >
            <View
              style={[
                styles.radioCircle,
                selected === option.key ? styles.radioCircleSelected : styles.radioCircleDefault,
              ]}
            >
              {selected === option.key && <View style={styles.radioCircleInner} />}
            </View>
            <View style={styles.radioContent}>
              <Text
                style={[
                  styles.radioOptionText,
                  selected === option.key ? styles.radioTextSelected : styles.radioTextDefault,
                ]}
              >
                {option.label}
              </Text>
              {option.description && (
                <Text
                  style={[
                    styles.radioDescription,
                    selected === option.key
                      ? styles.radioDescriptionSelected
                      : styles.radioDescriptionDefault,
                  ]}
                >
                  {option.description}
                </Text>
              )}
            </View>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  // Tab Selector - Underline
  underlineContainer: {
    borderBottomWidth: 1,
    borderBottomColor: '#e5e5e5',
  },
  underlineRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
  },
  underlineTab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginRight: 8,
  },
  underlineTabSelected: {
    borderBottomWidth: 2,
    borderBottomColor: '#000000',
  },
  tabIcon: {
    marginRight: 6,
  },
  tabText: {
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    fontWeight: '500',
  },
  tabTextSelected: {
    color: '#000000',
  },
  tabTextInactive: {
    color: '#737373',
  },

  // Tab Selector - Pills
  pillsContainer: {
    paddingHorizontal: 16,
  },
  pillsRow: {
    flexDirection: 'row',
    gap: 8,
  },
  pillTab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  pillTabSelected: {
    backgroundColor: '#000000',
  },
  pillTabDefault: {
    backgroundColor: '#f5f5f5',
  },
  pillTextSelected: {
    color: '#ffffff',
  },
  pillTextDefault: {
    color: '#525252',
  },

  // Chip
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  chipSm: {
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  chipMd: {
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  chipSelected: {
    backgroundColor: '#000000',
  },
  chipDefault: {
    backgroundColor: '#f5f5f5',
    borderWidth: 1,
    borderColor: '#e5e5e5',
  },
  chipTextSm: {
    fontSize: 10,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    fontWeight: '500',
  },
  chipTextMd: {
    fontSize: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    fontWeight: '500',
  },
  chipTextSelected: {
    color: '#ffffff',
  },
  chipTextDefault: {
    color: '#404040',
  },
  chipRemove: {
    marginLeft: 8,
  },

  // Radio Group
  radioLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#525252',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 12,
  },
  radioGroup: {
    gap: 8,
  },
  radioOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
  },
  radioOptionSelected: {
    backgroundColor: '#000000',
  },
  radioOptionDefault: {
    backgroundColor: '#f5f5f5',
  },
  radioCircle: {
    width: 16,
    height: 16,
    borderRadius: 8,
    borderWidth: 2,
    marginRight: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  radioCircleSelected: {
    borderColor: '#ffffff',
  },
  radioCircleDefault: {
    borderColor: '#a3a3a3',
  },
  radioCircleInner: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ffffff',
  },
  radioContent: {
    flex: 1,
  },
  radioOptionText: {
    fontSize: 14,
    fontWeight: '500',
  },
  radioTextSelected: {
    color: '#ffffff',
  },
  radioTextDefault: {
    color: '#000000',
  },
  radioDescription: {
    fontSize: 12,
    marginTop: 2,
  },
  radioDescriptionSelected: {
    color: 'rgba(255,255,255,0.7)',
  },
  radioDescriptionDefault: {
    color: '#737373',
  },
});
