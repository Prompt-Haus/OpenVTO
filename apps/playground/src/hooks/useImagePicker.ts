import { useCallback } from 'react';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system/legacy';

interface ImagePickerResult {
  uri: string;
  width: number;
  height: number;
  cancelled: boolean;
}

export function useImagePicker() {
  const [permissionStatus, requestPermission] = ImagePicker.useCameraPermissions();

  const pickImage = useCallback(async (source: 'camera' | 'library'): Promise<ImagePickerResult | null> => {
    try {
      // Check permissions
      if (source === 'camera') {
        const { status } = await requestPermission();
        if (status !== 'granted') {
          alert('Sorry, we need camera permissions to make this work!');
          return null;
        }
      }

      let result;
      if (source === 'camera') {
        result = await ImagePicker.launchCameraAsync({
          mediaTypes: ImagePicker.MediaTypeOptions.Images,
          allowsEditing: true,
          aspect: [3, 4],
          quality: 0.8,
        });
      } else {
        result = await ImagePicker.launchImageLibraryAsync({
          mediaTypes: ImagePicker.MediaTypeOptions.Images,
          allowsEditing: true,
          aspect: [3, 4],
          quality: 0.8,
        });
      }

      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0];
        
        // Move to permanent storage if needed
        const fileName = asset.uri.split('/').pop();
        const newPath = `${FileSystem.documentDirectory}${fileName}`;
        
        await FileSystem.copyAsync({
          from: asset.uri,
          to: newPath,
        });

        return {
          uri: newPath,
          width: asset.width,
          height: asset.height,
          cancelled: false,
        };
      }

      return {
        uri: '',
        width: 0,
        height: 0,
        cancelled: true,
      };
    } catch (error) {
      console.error('Error picking image:', error);
      return null;
    }
  }, [requestPermission]);

  return {
    pickImage,
    permissionStatus,
  };
}

export default useImagePicker;

