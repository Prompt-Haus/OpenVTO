import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import {
  Alert,
  Image,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { usePlaygroundStore } from '../../src/store';
import { sampleClothingItems } from '../../src/data/mock-data';

// Animation presets
const ANIMATION_TYPES = [
  { id: 'single', label: 'Single Frame', icon: 'image-outline' },
  { id: 'loop', label: 'Loop (A→B→A)', icon: 'repeat-outline' },
  { id: 'keyframes', label: 'Keyframes', icon: 'film-outline' },
];

interface SectionProps {
  title: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
}

const Section = ({ title, children, defaultExpanded = false }: SectionProps) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  
  return (
    <View style={styles.section}>
      <TouchableOpacity 
        style={styles.sectionHeader} 
        onPress={() => setExpanded(!expanded)}
        activeOpacity={0.7}
      >
        <Text style={styles.sectionTitle}>{title}</Text>
        <Ionicons 
          name={expanded ? 'chevron-up' : 'chevron-down'} 
          size={20} 
          color="#9CA3AF" 
        />
      </TouchableOpacity>
      {expanded && <View style={styles.sectionContent}>{children}</View>}
    </View>
  );
};

export default function SettingsScreen() {
  const [highQuality, setHighQuality] = useState(true);
  const [autoSave, setAutoSave] = useState(true);
  const [selectedAnimationType, setSelectedAnimationType] = useState('single');
  
  const { 
    avatars, 
    tryOnResults, 
    clothingItems,
    addClothingItem,
    clearAll 
  } = usePlaygroundStore();

  const completedAvatars = avatars.filter(a => a.status === 'completed');
  const completedTryOns = tryOnResults.filter(t => t.status === 'completed');

  const handleLoadSampleData = () => {
    Alert.alert(
      'Load Sample Data',
      'This will add sample clothing items to your collection.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Load', 
          onPress: () => {
            sampleClothingItems.forEach(item => {
              addClothingItem({
                name: item.name,
                category: item.category,
                frontImageUri: item.frontImageUri,
                parameters: item.parameters,
                tags: item.tags,
              });
            });
            Alert.alert('Done', 'Sample data loaded successfully!');
          }
        },
      ]
    );
  };

  const handleClearAll = () => {
    Alert.alert(
      'Clear All Data',
      'This will delete all avatars, try-on results, and clothing items. This cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Clear All', style: 'destructive', onPress: clearAll },
      ]
    );
  };

  const handleClearStorage = async () => {
    Alert.alert(
      'Clear AsyncStorage',
      'This will clear all persisted data (history, local clothing). App state will reset on next launch.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Clear Storage', 
          style: 'destructive', 
          onPress: async () => {
            try {
              await AsyncStorage.clear();
              clearAll();
              Alert.alert('Done', 'AsyncStorage cleared. Restart the app for full effect.');
            } catch {
              Alert.alert('Error', 'Failed to clear storage');
            }
          }
        },
      ]
    );
  };

  const handleExport = () => {
    Alert.alert('Export', 'Export functionality would save all generated content to your device. (Mock)');
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Settings</Text>
        </View>

        {/* Collection Section */}
        <Section title="Collection" defaultExpanded={true}>
          <View style={styles.statsRow}>
            <View style={styles.statBox}>
              <Text style={styles.statNumber}>{completedAvatars.length}</Text>
              <Text style={styles.statLabel}>Avatars</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statNumber}>{completedTryOns.length}</Text>
              <Text style={styles.statLabel}>Try-Ons</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statNumber}>{clothingItems.length}</Text>
              <Text style={styles.statLabel}>Clothes</Text>
            </View>
          </View>

          {/* Preview Grid */}
          {(completedAvatars.length > 0 || completedTryOns.length > 0) && (
            <View style={styles.previewSection}>
              <Text style={styles.previewLabel}>Recent</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <View style={styles.previewRow}>
                  {completedAvatars.slice(0, 4).map(avatar => (
                    <View key={avatar.id} style={styles.previewItem}>
                      <Image source={{ uri: avatar.imageUri }} style={styles.previewImage} />
                      <Text style={styles.previewItemLabel}>Avatar</Text>
                    </View>
                  ))}
                  {completedTryOns.slice(0, 4).map(tryon => (
                    <View key={tryon.id} style={styles.previewItem}>
                      <Image source={{ uri: tryon.imageUri }} style={styles.previewImage} />
                      <Text style={styles.previewItemLabel}>Try-On</Text>
                    </View>
                  ))}
                </View>
              </ScrollView>
            </View>
          )}

          <TouchableOpacity style={styles.actionButton} onPress={handleExport}>
            <Ionicons name="download-outline" size={18} color="#000" />
            <Text style={styles.actionButtonText}>Export All</Text>
          </TouchableOpacity>
        </Section>

        {/* Animation Section */}
        <Section title="Animation">
          <Text style={styles.optionLabel}>Animation Type</Text>
          <View style={styles.animationTypes}>
            {ANIMATION_TYPES.map(type => (
              <TouchableOpacity
                key={type.id}
                style={[
                  styles.animationTypeCard,
                  selectedAnimationType === type.id && styles.animationTypeCardSelected
                ]}
                onPress={() => setSelectedAnimationType(type.id)}
                activeOpacity={0.7}
              >
                <Ionicons 
                  name={type.icon as any} 
                  size={24} 
                  color={selectedAnimationType === type.id ? '#000' : '#9CA3AF'} 
                />
                <Text style={[
                  styles.animationTypeLabel,
                  selectedAnimationType === type.id && styles.animationTypeLabelSelected
                ]}>
                  {type.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          
          <View style={styles.infoBox}>
            <Ionicons name="information-circle-outline" size={16} color="#6B7280" />
            <Text style={styles.infoText}>
              {selectedAnimationType === 'single' && 'Generate a single static frame from your avatar.'}
              {selectedAnimationType === 'loop' && 'Create a smooth loop animation between two poses.'}
              {selectedAnimationType === 'keyframes' && 'Define multiple keyframes for complex animations.'}
            </Text>
          </View>
        </Section>

        {/* Generation Settings */}
        <Section title="Generation">
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>High Quality Output</Text>
              <Text style={styles.settingDescription}>Higher resolution, longer processing</Text>
            </View>
            <Switch
              value={highQuality}
              onValueChange={setHighQuality}
              trackColor={{ false: '#E5E7EB', true: '#000' }}
              thumbColor="#fff"
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Auto-save Results</Text>
              <Text style={styles.settingDescription}>Save generated images automatically</Text>
            </View>
            <Switch
              value={autoSave}
              onValueChange={setAutoSave}
              trackColor={{ false: '#E5E7EB', true: '#000' }}
              thumbColor="#fff"
            />
          </View>
        </Section>

        {/* Data Management */}
        <Section title="Data">
          <TouchableOpacity style={styles.actionButton} onPress={handleLoadSampleData}>
            <Ionicons name="cloud-download-outline" size={18} color="#000" />
            <Text style={styles.actionButtonText}>Load Sample Data</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={[styles.actionButton, styles.dangerButton]} onPress={handleClearAll}>
            <Ionicons name="trash-outline" size={18} color="#DC2626" />
            <Text style={[styles.actionButtonText, styles.dangerText]}>Clear All Data</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={[styles.actionButton, styles.dangerButton]} onPress={handleClearStorage}>
            <Ionicons name="server-outline" size={18} color="#DC2626" />
            <Text style={[styles.actionButtonText, styles.dangerText]}>Clear AsyncStorage</Text>
          </TouchableOpacity>
        </Section>

        {/* About */}
        <Section title="About">
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Version</Text>
            <Text style={styles.aboutValue}>1.0.0</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>Environment</Text>
            <Text style={styles.aboutValue}>Playground (Mock)</Text>
          </View>
          <View style={styles.aboutRow}>
            <Text style={styles.aboutLabel}>AI Engine</Text>
            <Text style={styles.aboutValue}>Not Connected</Text>
          </View>
        </Section>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>VTO Playground</Text>
          <Text style={styles.footerSubtext}>Virtual Try-On Technology Demo</Text>
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
    paddingBottom: 8,
  },
  title: {
    fontSize: 28,
    fontWeight: '600',
    color: '#000',
    letterSpacing: -0.5,
  },
  section: {
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  sectionContent: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#F9FAFB',
    borderRadius: 10,
    padding: 16,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: '600',
    color: '#000',
  },
  statLabel: {
    fontSize: 11,
    color: '#6B7280',
    marginTop: 4,
    textTransform: 'uppercase',
  },
  previewSection: {
    marginBottom: 16,
  },
  previewLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#6B7280',
    marginBottom: 8,
  },
  previewRow: {
    flexDirection: 'row',
    gap: 8,
  },
  previewItem: {
    alignItems: 'center',
  },
  previewImage: {
    width: 60,
    height: 80,
    borderRadius: 6,
    backgroundColor: '#F3F4F6',
  },
  previewItemLabel: {
    fontSize: 9,
    color: '#9CA3AF',
    marginTop: 4,
    textTransform: 'uppercase',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F3F4F6',
    paddingVertical: 12,
    borderRadius: 10,
    gap: 8,
    marginTop: 8,
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#000',
  },
  dangerButton: {
    backgroundColor: '#FEF2F2',
  },
  dangerText: {
    color: '#DC2626',
  },
  optionLabel: {
    fontSize: 13,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 12,
  },
  animationTypes: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 16,
  },
  animationTypeCard: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 16,
    borderRadius: 10,
    backgroundColor: '#F9FAFB',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  animationTypeCardSelected: {
    borderColor: '#000',
    backgroundColor: '#FFF',
  },
  animationTypeLabel: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 8,
    textAlign: 'center',
  },
  animationTypeLabelSelected: {
    color: '#000',
    fontWeight: '500',
  },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#F9FAFB',
    padding: 12,
    borderRadius: 8,
    gap: 8,
  },
  infoText: {
    flex: 1,
    fontSize: 12,
    color: '#6B7280',
    lineHeight: 18,
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F9FAFB',
    padding: 14,
    borderRadius: 10,
    marginBottom: 8,
  },
  settingInfo: {
    flex: 1,
    marginRight: 12,
  },
  settingLabel: {
    fontSize: 14,
    color: '#000',
    fontWeight: '500',
  },
  settingDescription: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  aboutRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  aboutLabel: {
    fontSize: 14,
    color: '#6B7280',
  },
  aboutValue: {
    fontSize: 14,
    color: '#000',
    fontWeight: '500',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 32,
    paddingHorizontal: 20,
  },
  footerText: {
    fontSize: 13,
    color: '#9CA3AF',
    fontWeight: '500',
  },
  footerSubtext: {
    fontSize: 11,
    color: '#D1D5DB',
    marginTop: 4,
  },
});
