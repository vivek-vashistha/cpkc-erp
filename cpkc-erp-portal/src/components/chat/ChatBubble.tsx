'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Send, Bot, User, Loader2, AlertTriangle, X, Minimize2, Maximize2 } from 'lucide-react';
import { chatContextManager } from '@/lib/chatContext';
import { Anomaly } from '@/lib/api';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'text' | 'suggestion' | 'error';
}

interface ChatBubbleProps {
  isOpen: boolean;
  onClose: () => void;
  anomalyContext: Anomaly[];
  onContextChange: (anomalies: Anomaly[]) => void;
}

export default function ChatBubble({ isOpen, onClose, anomalyContext, onContextChange }: ChatBubbleProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && anomalyContext.length > 0) {
      // Initialize chat with context message
      const contextMessage: Message = {
        id: `context_${Date.now()}`,
        content: `I have ${anomalyContext.length} anomaly(ies) in context. ${chatContextManager.getContextSummary()}`,
        sender: 'bot',
        timestamp: new Date(),
        type: 'text'
      };
      
      setMessages([contextMessage]);
    } else if (isOpen && anomalyContext.length === 0) {
      // Initialize with welcome message
      const welcomeMessage: Message = {
        id: `welcome_${Date.now()}`,
        content: 'Hello! I\'m your CPKC ERP assistant. How can I help you today?',
        sender: 'bot',
        timestamp: new Date(),
        type: 'text'
      };
      
      setMessages([welcomeMessage]);
    }
  }, [isOpen, anomalyContext]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate bot response
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: generateBotResponse(inputValue),
        sender: 'bot',
        timestamp: new Date(),
        type: 'text'
      };
      setMessages(prev => [...prev, botResponse]);
      setIsLoading(false);
    }, 1000);
  };

  const generateBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    // If we have anomaly context, provide specific responses
    if (anomalyContext.length > 0) {
      if (input.includes('anomaly') || input.includes('issue') || input.includes('problem') || input.includes('details')) {
        return `Based on the ${anomalyContext.length} anomaly(ies) in context:\n\n${chatContextManager.getDetailedContext()}\n\nI can help you understand these anomalies better, suggest resolution strategies, or answer specific questions about them. What would you like to know?`;
      }
      
      if (input.includes('fix') || input.includes('resolve') || input.includes('solution')) {
        const suggestions = anomalyContext.map(a => `• ${a.type} (${a.waybill_id}): ${a.suggested_fix}`).join('\n');
        return `Here are the suggested fixes for the anomalies in context:\n\n${suggestions}\n\nWould you like me to elaborate on any specific fix or help you implement a solution?`;
      }
      
      if (input.includes('confidence') || input.includes('reliability')) {
        const confidenceInfo = anomalyContext.map(a => `• ${a.type} (${a.waybill_id}): ${(a.confidence * 100).toFixed(0)}% confidence`).join('\n');
        return `Confidence levels for the anomalies in context:\n\n${confidenceInfo}\n\nHigher confidence means the anomaly detection is more certain. Would you like me to explain what this means for each anomaly?`;
      }
      
      if (input.includes('status') || input.includes('state')) {
        const statusInfo = anomalyContext.map(a => `• ${a.type} (${a.waybill_id}): ${a.status}`).join('\n');
        return `Current status of the anomalies in context:\n\n${statusInfo}\n\nYou can change the status using the action buttons in the anomalies table. Would you like me to explain what each status means?`;
      }
    }
    
    if (input.includes('waybill') || input.includes('shipment')) {
      return 'I can help you with waybill information. You can search for waybills by ID, check their status, or view shipment events. Would you like me to show you how to find a specific waybill?';
    }
    
    if (input.includes('anomaly') || input.includes('issue') || input.includes('problem')) {
      return 'I see you\'re asking about anomalies. You can view all anomalies in the Anomalies section, filter by status, and resolve issues. Would you like me to help you check for new anomalies?';
    }
    
    if (input.includes('contract') || input.includes('pricing')) {
      return 'For contract and pricing information, you can view all contracts, match contracts to waybills, and see pricing details. The Contracts section has all this information.';
    }
    
    if (input.includes('asset') || input.includes('car') || input.includes('equipment')) {
      return 'Asset management is available in the Assets section. You can view all assets, check their status, and manage assignments. What specific asset information do you need?';
    }
    
    if (input.includes('operation') || input.includes('loading') || input.includes('offloading')) {
      return 'Operations tracking is available in the Operations section. You can log new operations, view operation history, and track loading/offloading activities.';
    }
    
    if (input.includes('help') || input.includes('how')) {
      return 'I can help you with:\n• Waybill tracking and management\n• Contract information and pricing\n• Asset management\n• Operations logging\n• Anomaly detection and resolution\n• Audit trail information\n\nWhat would you like to know more about?';
    }
    
    return 'I understand you\'re looking for help. I can assist you with waybill management, contract information, asset tracking, operations, and anomaly resolution. Could you be more specific about what you need help with?';
  };

  const clearAnomalyContext = () => {
    chatContextManager.clearContext();
    onContextChange([]);
    
    // Add a message about context being cleared
    const clearMessage: Message = {
      id: `clear_${Date.now()}`,
      content: 'Anomaly context has been cleared. I\'m now ready to help with general ERP questions.',
      sender: 'bot',
      timestamp: new Date(),
      type: 'text'
    };
    
    setMessages(prev => [...prev, clearMessage]);
  };

  const quickActions = anomalyContext.length > 0 ? [
    { label: 'Anomaly Details', action: 'Show me detailed information about these anomalies' },
    { label: 'Suggested Fixes', action: 'What are the suggested fixes for these anomalies?' },
    { label: 'Confidence Levels', action: 'Explain the confidence levels of these anomalies' },
    { label: 'Status Information', action: 'What do the different statuses mean for these anomalies?' },
    { label: 'Resolution Help', action: 'Help me resolve these anomalies' },
  ] : [
    { label: 'Check Waybill Status', action: 'Show me how to check waybill status' },
    { label: 'View Anomalies', action: 'Show me the latest anomalies' },
    { label: 'Asset Information', action: 'Help me find asset information' },
    { label: 'Contract Details', action: 'Show me contract information' },
  ];

  const handleQuickAction = (action: string) => {
    setInputValue(action);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <Card className={`w-96 shadow-2xl border-2 transition-all duration-300 ${
        isMinimized ? 'h-16' : 'h-[500px]'
      }`}>
        <CardHeader className="pb-3 border-b">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <Bot className="h-5 w-5" />
              CPKC Assistant
              {anomalyContext.length > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {anomalyContext.length} anomaly{anomalyContext.length !== 1 ? 'ies' : ''}
                </Badge>
              )}
            </CardTitle>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsMinimized(!isMinimized)}
                className="h-6 w-6 p-0"
              >
                {isMinimized ? <Maximize2 className="h-3 w-3" /> : <Minimize2 className="h-3 w-3" />}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="h-6 w-6 p-0"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </CardHeader>

        {!isMinimized && (
          <>
            {/* Anomaly Context Display */}
            {anomalyContext.length > 0 && (
              <div className="p-3 border-b bg-blue-50">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">
                      Context ({anomalyContext.length} anomaly{anomalyContext.length !== 1 ? 'ies' : ''})
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearAnomalyContext}
                    className="h-6 text-blue-600 hover:text-blue-700"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
                <div className="space-y-1 max-h-20 overflow-y-auto">
                  {anomalyContext.map((anomaly) => (
                    <div key={anomaly.id} className="flex items-center justify-between p-1 bg-white rounded text-xs">
                      <div className="flex items-center gap-2">
                        <Badge variant="destructive" className="text-xs px-1 py-0">
                          {anomaly.type}
                        </Badge>
                        <span className="font-medium">{anomaly.waybill_id}</span>
                        <span className="text-gray-500">Car: {anomaly.car_id}</span>
                      </div>
                      <Badge variant="outline" className="text-xs px-1 py-0">
                        {anomaly.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <CardContent className="flex-1 flex flex-col p-0 h-[350px]">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-3 space-y-3">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                        message.sender === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        {message.sender === 'bot' && (
                          <Bot className="h-3 w-3 mt-0.5 flex-shrink-0" />
                        )}
                        {message.sender === 'user' && (
                          <User className="h-3 w-3 mt-0.5 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          <p className="whitespace-pre-wrap">{message.content}</p>
                          <p className="text-xs opacity-70 mt-1">
                            {message.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg px-3 py-2 flex items-center gap-2">
                      <Bot className="h-3 w-3" />
                      <Loader2 className="h-3 w-3 animate-spin" />
                      <span className="text-xs text-gray-600">Typing...</span>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Quick Actions */}
              <div className="p-2 border-t bg-gray-50">
                <div className="flex flex-wrap gap-1">
                  {quickActions.slice(0, 3).map((action, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      className="text-xs h-6 px-2"
                      onClick={() => handleQuickAction(action.action)}
                    >
                      {action.label}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Input */}
              <div className="border-t p-3">
                <div className="flex gap-2">
                  <Input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Ask me anything..."
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    disabled={isLoading}
                    className="text-sm"
                  />
                  <Button 
                    onClick={handleSendMessage} 
                    disabled={!inputValue.trim() || isLoading}
                    size="sm"
                  >
                    <Send className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </>
        )}
      </Card>
    </div>
  );
}
