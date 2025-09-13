import axios from 'axios';
import { CacheManager, CACHE_KEYS, CACHE_TTL } from './cache';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/proxy';

// Types based on the OpenAPI specs
export interface Waybill {
  waybill_id: string;
  customer_id: string;
  contract_id: string;
  origin_location: string;
  destination_location: string;
  commodity: string;
  weight_tons: number;
  created_ts: string;
  current_status: string;
  last_event_ts: string;
}

export interface Contract {
  contract_id: string;
  customer_id: string;
  origin_location: string;
  destination_location: string;
  commodity: string;
  base_rate_per_ton: number;
  fuel_surcharge_pct: number;
  valid_from: string;
  valid_to: string;
}

export interface Asset {
  asset_id: string;
  asset_type: string;
  model: string;
  in_service_date: string;
  current_status: string;
}

export interface Operation {
  id: string;
  timestamp: string;
  type: 'loading' | 'offloading';
  waybillId: string;
  carId: string;
  location: string;
  crewMember: string;
  override: boolean;
  signature?: string;
}

export interface SuggestedFixAction {
  name: string;
  args: Array<{ key: string; value: string }>;
  rationale: string;
}

export interface SuggestedFix {
  actions: SuggestedFixAction[];
}

export interface Anomaly {
  id: string;
  waybill_id: string;
  car_id: string;
  csn_id: string;
  type: string;
  confidence: number;
  suggested_fix: string | SuggestedFix;
  status: 'NEW' | 'RESOLVED' | 'IGNORED';
  created_ts: string;
  updated_ts: string;
  details?: string;
  needs_confirmation?: boolean;
  // RPA Integration fields
  rpa_status?: 'PENDING' | 'SUBMITTED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  rpa_submission_ts?: string;
  rpa_completion_ts?: string;
  rpa_error_message?: string;
  rpa_workflow_id?: string;
  rpa_retry_count?: number;
  auto_fix_eligible?: boolean;
  human_confirmed?: boolean;
  rpa_actions?: RPAAction[];
}

export interface RPAAction {
  id: string;
  action_type: 'INSERT_EVENT' | 'REORDER_EVENTS' | 'SET_CARID' | 'SET_CSNID' | 'CORRECT_EVENT_TS' | 'REVIEW_TERMINAL_STATE';
  event_type?: string;
  ts_hint?: string;
  value?: string;
  event_ids?: string[];
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  error_message?: string;
  executed_ts?: string;
}

export interface AuditEntry {
  audit_id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  detail: string;
  timestamp: string;
  actor: string;
}

export interface PagedResponse<T> {
  items: T[];
  nextPageToken?: string;
  total: number;
}

class ApiService {
  private baseURL: string;
  private apiKey: string;

  constructor() {
    this.baseURL = API_BASE_URL;
    this.apiKey = process.env.NEXT_PUBLIC_API_KEY || '';
  }

  private async makeRequest<T>(path: string, params: Record<string, any> = {}): Promise<T> {
    const url = new URL(this.baseURL, window.location.origin);
    url.searchParams.append('path', path);
    
    if (this.apiKey) {
      url.searchParams.append('key', this.apiKey);
    }

    // Add query parameters
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    });

    console.log('API Request URL:', url.toString());

    const response = await axios.get(url.toString());

    console.log('API Response:', response.data);
    return response.data;
  }

  private async makePostRequest<T>(path: string, data: any): Promise<T> {
    const url = new URL(this.baseURL, window.location.origin);
    url.searchParams.append('path', path);
    
    if (this.apiKey) {
      url.searchParams.append('key', this.apiKey);
    }

    const response = await axios.post(url.toString(), data, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return response.data;
  }

  private async makePatchRequest<T>(path: string, data: any): Promise<T> {
    const url = new URL(this.baseURL, window.location.origin);
    url.searchParams.append('path', path);
    
    if (this.apiKey) {
      url.searchParams.append('key', this.apiKey);
    }

    const response = await axios.patch(url.toString(), data, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return response.data;
  }

  // Waybills
  async getWaybills(params: {
    id?: string;
    customer_id?: string;
    status?: string;
    origin?: string;
    dest?: string;
    commodity?: string;
    since?: string;
    limit?: number;
    pageToken?: string;
  } = {}): Promise<PagedResponse<Waybill>> {
    // Create cache key based on parameters
    const cacheKey = this.createCacheKey('waybills', params);
    
    // Try to get from cache first
    const cachedData = CacheManager.get<PagedResponse<Waybill>>(cacheKey);
    if (cachedData) {
      console.log('Returning waybills from cache');
      return cachedData as PagedResponse<Waybill>;
    }

    // If not in cache, fetch from API
    console.log('Fetching waybills from API');
    const data = await this.makeRequest<PagedResponse<Waybill>>('waybills', params);
    
    // Store in cache
    CacheManager.set(cacheKey, data, CACHE_TTL.WAYBILLS);
    
    return data;
  }

  // Helper method to create cache keys
  private createCacheKey(baseKey: string, params: Record<string, any>): string {
    const sortedParams = Object.keys(params)
      .filter(key => params[key] !== undefined && params[key] !== null)
      .sort()
      .map(key => `${key}:${params[key]}`)
      .join('|');
    
    return sortedParams ? `${baseKey}_${sortedParams}` : baseKey;
  }

  // Contracts
  async getContracts(params: {
    customer_id?: string;
    origin?: string;
    dest?: string;
    commodity?: string;
    valid_on?: string;
    limit?: number;
    pageToken?: string;
  } = {}): Promise<PagedResponse<Contract>> {
    const cacheKey = this.createCacheKey('contracts', params);
    
    const cachedData = CacheManager.get<PagedResponse<Contract>>(cacheKey);
    if (cachedData) {
      console.log('Returning contracts from cache');
      return cachedData as PagedResponse<Contract>;
    }

    console.log('Fetching contracts from API');
    const data = await this.makeRequest<PagedResponse<Contract>>('contracts', params);
    
    CacheManager.set(cacheKey, data, CACHE_TTL.CONTRACTS);
    
    return data;
  }

  async matchContract(waybillId: string): Promise<{
    choice: string | null;
    confidence: number;
    reason: string;
    alternatives: Array<{ contract_id: string; reason: string }>;
  }> {
    return this.makeRequest('contract/match', { waybill_id: waybillId });
  }

  // Assets
  async getAssets(params: {
    id?: string;
    asset_type?: string;
    model?: string;
    current_status?: string;
    limit?: number;
    pageToken?: string;
  } = {}): Promise<PagedResponse<Asset> | { item: Asset }> {
    return this.makeRequest('assets', params);
  }

  // Operations
  async logOperation(operation: {
    type: 'loading' | 'offloading';
    waybillId: string;
    carId: string;
    location?: string;
    crewMember?: string;
    override?: boolean;
    signature?: string;
  }): Promise<{ ok: boolean; operation: Operation }> {
    return this.makePostRequest('operations', operation);
  }

  // Anomalies
  async getAnomalies(params: {
    status?: 'NEW' | 'RESOLVED' | 'IGNORED';
    waybill_id?: string;
    id?: string;
    limit?: number;
    pageToken?: string;
  } = {}): Promise<PagedResponse<Anomaly>> {
    return this.makeRequest('anomalies', params);
  }

  async updateAnomalyStatus(id: string, status: 'NEW' | 'RESOLVED' | 'IGNORED'): Promise<{ ok: boolean; anomaly: Anomaly }> {
    return this.makePatchRequest('anomalies', { id, status });
  }

  // Audit
  async createAuditEntry(entry: {
    entity_type: string;
    entity_id: string;
    action: string;
    detail?: string;
    actor?: string;
  }): Promise<{ ok: boolean; audit: AuditEntry }> {
    return this.makePostRequest('audit', entry);
  }

  // LangGraph Analysis
  async analyzeWaybill(waybillId: string): Promise<{
    anomalies: Anomaly[];
    version: string;
    generated_at: string;
  }> {
    return this.makePostRequest('langgraph/analyze', { waybill_id: waybillId });
  }

  // Local Anomaly Check API
  async checkAnomalies(waybillIds: string): Promise<{
    waybill_id: string;
    result: string;
  }> {
    const agentUrl = process.env.NEXT_PUBLIC_AGENT_URL || 'http://localhost:8080';
    const response = await axios.post(`${agentUrl}/api/anomalies`, {
      waybill_id: waybillIds,
      thread_id: `thread_${Date.now()}`
    }, {
      params: {
        status: 'NEW'
      }
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ ok: boolean; ts: string }> {
    return this.makeRequest('ping');
  }

  // File-based Storage for Anomalies
  async saveAnomaliesToFile(anomalies: Anomaly[]): Promise<boolean> {
    try {
      const response = await axios.post('/api/anomalies', { anomalies });
      console.log('Anomalies saved to file:', anomalies.length, 'items');
      return response.data.success;
    } catch (error) {
      console.error('Failed to save anomalies to file:', error);
      return false;
    }
  }

  async loadAnomaliesFromFile(): Promise<Anomaly[]> {
    try {
      const response = await axios.get('/api/anomalies');
      console.log('Anomalies loaded from file:', response.data.items.length, 'items');
      return response.data.items;
    } catch (error) {
      console.error('Failed to load anomalies from file:', error);
      return [];
    }
  }

  async deleteAnomalyFromFile(anomalyId: string): Promise<boolean> {
    try {
      const response = await axios.delete(`/api/anomalies?id=${anomalyId}`);
      console.log('Anomaly deleted from file:', anomalyId);
      return response.data.success;
    } catch (error) {
      console.error('Failed to delete anomaly from file:', error);
      return false;
    }
  }

  async updateAnomalyInFile(anomalyId: string, updates: Partial<Anomaly>): Promise<boolean> {
    try {
      const response = await axios.patch(`/api/anomalies?id=${anomalyId}`, updates);
      console.log('Anomaly updated in file:', anomalyId);
      return response.data.success;
    } catch (error) {
      console.error('Failed to update anomaly in file:', error);
      return false;
    }
  }

  async clearAllAnomaliesFromFile(): Promise<boolean> {
    try {
      const response = await axios.delete('/api/anomalies');
      console.log('All anomalies cleared from file');
      return response.data.success;
    } catch (error) {
      console.error('Failed to clear all anomalies from file:', error);
      return false;
    }
  }

  // RPA Integration Methods
  async submitToRPA(anomalyIds: string[], autoFix: boolean = false): Promise<{
    success: boolean;
    submitted_count: number;
    workflow_ids: string[];
    errors?: string[];
  }> {
    try {
      const response = await axios.post('/api/rpa/submit', {
        anomaly_ids: anomalyIds,
        auto_fix: autoFix,
        timestamp: new Date().toISOString()
      });
      console.log('Anomalies submitted to RPA:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to submit anomalies to RPA:', error);
      return {
        success: false,
        submitted_count: 0,
        workflow_ids: [],
        errors: [error instanceof Error ? error.message : 'Unknown error']
      };
    }
  }

  async getRPAStatus(workflowId: string): Promise<{
    workflow_id: string;
    status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
    progress: number;
    current_action?: string;
    error_message?: string;
    completed_actions: number;
    total_actions: number;
    estimated_completion?: string;
  }> {
    try {
      const response = await axios.get(`/api/rpa/status/${workflowId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get RPA status:', error);
      throw error;
    }
  }

  async cancelRPAWorkflow(workflowId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await axios.post(`/api/rpa/cancel/${workflowId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to cancel RPA workflow:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  async retryRPAWorkflow(workflowId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await axios.post(`/api/rpa/retry/${workflowId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to retry RPA workflow:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  async getRPAWorkflowHistory(anomalyId: string): Promise<{
    anomaly_id: string;
    workflows: Array<{
      workflow_id: string;
      status: string;
      submitted_ts: string;
      completed_ts?: string;
      actions: RPAAction[];
    }>;
  }> {
    try {
      const response = await axios.get(`/api/rpa/history/${anomalyId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get RPA workflow history:', error);
      return {
        anomaly_id: anomalyId,
        workflows: []
      };
    }
  }

  // Cache management methods
  invalidateWaybillCache(): void {
    const keys = Object.keys(localStorage);
    const waybillKeys = keys.filter(key => key.includes('waybills'));
    waybillKeys.forEach(key => CacheManager.remove(key.replace('cpkc_cache_', '')));
    console.log('Waybill cache invalidated');
  }

  invalidateContractCache(): void {
    const keys = Object.keys(localStorage);
    const contractKeys = keys.filter(key => key.includes('contracts'));
    contractKeys.forEach(key => CacheManager.remove(key.replace('cpkc_cache_', '')));
    console.log('Contract cache invalidated');
  }

  invalidateAssetCache(): void {
    const keys = Object.keys(localStorage);
    const assetKeys = keys.filter(key => key.includes('assets'));
    assetKeys.forEach(key => CacheManager.remove(key.replace('cpkc_cache_', '')));
    console.log('Asset cache invalidated');
  }

  invalidateAnomalyCache(): void {
    const keys = Object.keys(localStorage);
    const anomalyKeys = keys.filter(key => key.includes('anomalies'));
    anomalyKeys.forEach(key => CacheManager.remove(key.replace('cpkc_cache_', '')));
    console.log('Anomaly cache invalidated');
  }

  clearAllCache(): void {
    CacheManager.clear();
    console.log('All cache cleared');
  }

  getCacheInfo() {
    return CacheManager.getInfo();
  }

  cleanupExpiredCache(): void {
    CacheManager.cleanup();
  }
}

export const apiService = new ApiService();
