import { Anomaly } from './api';

export interface ChatContext {
  anomalies: Anomaly[];
  contextType: 'anomalies' | 'general';
  timestamp: Date;
}

class ChatContextManager {
  private static instance: ChatContextManager;
  private currentContext: ChatContext | null = null;

  private constructor() {}

  static getInstance(): ChatContextManager {
    if (!ChatContextManager.instance) {
      ChatContextManager.instance = new ChatContextManager();
    }
    return ChatContextManager.instance;
  }

  setAnomalyContext(anomalies: Anomaly[]): void {
    this.currentContext = {
      anomalies,
      contextType: 'anomalies',
      timestamp: new Date()
    };
    
    // Store in sessionStorage for persistence across page refreshes
    sessionStorage.setItem('chatContext', JSON.stringify(this.currentContext));
  }

  getCurrentContext(): ChatContext | null {
    if (this.currentContext) {
      return this.currentContext;
    }

    // Try to load from sessionStorage
    try {
      const stored = sessionStorage.getItem('chatContext');
      if (stored) {
        const parsed = JSON.parse(stored);
        this.currentContext = {
          ...parsed,
          timestamp: new Date(parsed.timestamp)
        };
        return this.currentContext;
      }
    } catch (error) {
      console.error('Failed to load chat context from storage:', error);
    }

    return null;
  }

  clearContext(): void {
    this.currentContext = null;
    sessionStorage.removeItem('chatContext');
  }

  addAnomaliesToContext(anomalies: Anomaly[]): void {
    const current = this.getCurrentContext();
    if (current && current.contextType === 'anomalies') {
      // Merge with existing anomalies, avoiding duplicates
      const existingIds = new Set(current.anomalies.map(a => a.id));
      const newAnomalies = anomalies.filter(a => !existingIds.has(a.id));
      
      this.setAnomalyContext([...current.anomalies, ...newAnomalies]);
    } else {
      this.setAnomalyContext(anomalies);
    }
  }

  removeAnomalyFromContext(anomalyId: string): void {
    const current = this.getCurrentContext();
    if (current && current.contextType === 'anomalies') {
      const filteredAnomalies = current.anomalies.filter(a => a.id !== anomalyId);
      if (filteredAnomalies.length > 0) {
        this.setAnomalyContext(filteredAnomalies);
      } else {
        this.clearContext();
      }
    }
  }

  getContextSummary(): string {
    const context = this.getCurrentContext();
    if (!context || context.contextType !== 'anomalies') {
      return '';
    }

    const anomalyCount = context.anomalies.length;
    const waybillIds = [...new Set(context.anomalies.map(a => a.waybill_id))];
    const anomalyTypes = [...new Set(context.anomalies.map(a => a.type))];
    
    return `I have ${anomalyCount} anomaly(ies) in context from waybill(s): ${waybillIds.join(', ')}. Anomaly types: ${anomalyTypes.join(', ')}.`;
  }

  getDetailedContext(): string {
    const context = this.getCurrentContext();
    if (!context || context.contextType !== 'anomalies') {
      return '';
    }

    let details = 'Anomaly Details:\n\n';
    context.anomalies.forEach((anomaly, index) => {
      details += `${index + 1}. Waybill: ${anomaly.waybill_id}\n`;
      details += `   Type: ${anomaly.type}\n`;
      details += `   Car ID: ${anomaly.car_id}\n`;
      details += `   CSN ID: ${anomaly.csn_id}\n`;
      details += `   Status: ${anomaly.status}\n`;
      details += `   Confidence: ${(anomaly.confidence * 100).toFixed(0)}%\n`;
      details += `   Suggested Fix: ${anomaly.suggested_fix}\n`;
      if (anomaly.details) {
        details += `   Details: ${anomaly.details}\n`;
      }
      details += `   Created: ${new Date(anomaly.created_ts).toLocaleString()}\n\n`;
    });

    return details;
  }
}

export const chatContextManager = ChatContextManager.getInstance();
