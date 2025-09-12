// Cache utility for localStorage management
export interface CacheItem<T> {
  data: T;
  timestamp: number;
  expiry: number;
}

export class CacheManager {
  private static readonly CACHE_PREFIX = 'cpkc_cache_';
  private static readonly DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes in milliseconds

  /**
   * Store data in localStorage with timestamp and expiry
   */
  static set<T>(key: string, data: T, ttl: number = this.DEFAULT_TTL): void {
    try {
      const cacheItem: CacheItem<T> = {
        data,
        timestamp: Date.now(),
        expiry: Date.now() + ttl
      };
      
      const cacheKey = this.CACHE_PREFIX + key;
      localStorage.setItem(cacheKey, JSON.stringify(cacheItem));
      console.log(`Cache set for key: ${key}, expires in ${ttl}ms`);
    } catch (error) {
      console.error('Failed to set cache:', error);
    }
  }

  /**
   * Retrieve data from localStorage, checking expiry
   */
  static get<T>(key: string): T | null {
    try {
      const cacheKey = this.CACHE_PREFIX + key;
      const cached = localStorage.getItem(cacheKey);
      
      if (!cached) {
        console.log(`Cache miss for key: ${key}`);
        return null;
      }

      const cacheItem: CacheItem<T> = JSON.parse(cached);
      
      // Check if cache has expired
      if (Date.now() > cacheItem.expiry) {
        console.log(`Cache expired for key: ${key}`);
        this.remove(key);
        return null;
      }

      console.log(`Cache hit for key: ${key}, age: ${Date.now() - cacheItem.timestamp}ms`);
      return cacheItem.data;
    } catch (error) {
      console.error('Failed to get cache:', error);
      return null;
    }
  }

  /**
   * Remove specific cache entry
   */
  static remove(key: string): void {
    try {
      const cacheKey = this.CACHE_PREFIX + key;
      localStorage.removeItem(cacheKey);
      console.log(`Cache removed for key: ${key}`);
    } catch (error) {
      console.error('Failed to remove cache:', error);
    }
  }

  /**
   * Clear all cache entries
   */
  static clear(): void {
    try {
      const keys = Object.keys(localStorage);
      const cacheKeys = keys.filter(key => key.startsWith(this.CACHE_PREFIX));
      
      cacheKeys.forEach(key => {
        localStorage.removeItem(key);
      });
      
      console.log(`Cleared ${cacheKeys.length} cache entries`);
    } catch (error) {
      console.error('Failed to clear cache:', error);
    }
  }

  /**
   * Get cache info (size, keys, etc.)
   */
  static getInfo(): { size: number; keys: string[]; entries: Array<{ key: string; age: number; expires: boolean }> } {
    try {
      const keys = Object.keys(localStorage);
      const cacheKeys = keys.filter(key => key.startsWith(this.CACHE_PREFIX));
      
      const entries = cacheKeys.map(key => {
        const cached = localStorage.getItem(key);
        if (cached) {
          const cacheItem = JSON.parse(cached);
          const age = Date.now() - cacheItem.timestamp;
          const expires = Date.now() > cacheItem.expiry;
          return {
            key: key.replace(this.CACHE_PREFIX, ''),
            age,
            expires
          };
        }
        return null;
      }).filter(Boolean);

      return {
        size: cacheKeys.length,
        keys: cacheKeys.map(key => key.replace(this.CACHE_PREFIX, '')),
        entries: entries as Array<{ key: string; age: number; expires: boolean }>
      };
    } catch (error) {
      console.error('Failed to get cache info:', error);
      return { size: 0, keys: [], entries: [] };
    }
  }

  /**
   * Clean up expired cache entries
   */
  static cleanup(): void {
    try {
      const keys = Object.keys(localStorage);
      const cacheKeys = keys.filter(key => key.startsWith(this.CACHE_PREFIX));
      
      let cleaned = 0;
      cacheKeys.forEach(key => {
        const cached = localStorage.getItem(key);
        if (cached) {
          const cacheItem = JSON.parse(cached);
          if (Date.now() > cacheItem.expiry) {
            localStorage.removeItem(key);
            cleaned++;
          }
        }
      });
      
      if (cleaned > 0) {
        console.log(`Cleaned up ${cleaned} expired cache entries`);
      }
    } catch (error) {
      console.error('Failed to cleanup cache:', error);
    }
  }
}

// Cache keys constants
export const CACHE_KEYS = {
  WAYBILLS: 'waybills',
  WAYBILLS_ALL: 'waybills_all',
  WAYBILLS_ACTIVE: 'waybills_active',
  WAYBILLS_COMPLETED: 'waybills_completed',
  WAYBILLS_PENDING: 'waybills_pending',
  CONTRACTS: 'contracts',
  ASSETS: 'assets',
  ANOMALIES: 'anomalies',
} as const;

// Cache TTL constants (in milliseconds)
export const CACHE_TTL = {
  WAYBILLS: 10 * 60 * 1000, // 10 minutes
  CONTRACTS: 30 * 60 * 1000, // 30 minutes
  ASSETS: 60 * 60 * 1000, // 1 hour
  ANOMALIES: 5 * 60 * 1000, // 5 minutes
} as const;
