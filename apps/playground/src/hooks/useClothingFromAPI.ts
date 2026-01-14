/**
 * Hook to load clothing items from the OpenVTO API
 */

import { useCallback, useState } from 'react';
import { usePlaygroundStore } from '../store/playground';
import { fetchAllClothingItems, configureAPI } from '../services/api';

interface UseClothingFromAPIOptions {
  apiBaseUrl?: string;
}

interface UseClothingFromAPIReturn {
  loadClothing: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
  itemsLoaded: number;
}

export function useClothingFromAPI(
  options: UseClothingFromAPIOptions = {}
): UseClothingFromAPIReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [itemsLoaded, setItemsLoaded] = useState(0);
  
  const addClothingItem = usePlaygroundStore((state) => state.addClothingItem);

  const loadClothing = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setItemsLoaded(0);

    try {
      // Configure API if baseUrl provided
      if (options.apiBaseUrl) {
        configureAPI({ baseUrl: options.apiBaseUrl });
      }

      // Fetch all items from API
      const items = await fetchAllClothingItems();

      // Add each item to store
      for (const item of items) {
        addClothingItem(item);
      }

      setItemsLoaded(items.length);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load clothing';
      setError(message);
      console.error('[useClothingFromAPI] Error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [options.apiBaseUrl, addClothingItem]);

  return {
    loadClothing,
    isLoading,
    error,
    itemsLoaded,
  };
}

export default useClothingFromAPI;

