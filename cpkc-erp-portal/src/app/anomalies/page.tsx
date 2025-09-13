'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiService, type Anomaly, type SuggestedFix } from '@/lib/api';
import { formatDate, getStatusColor, isRPAEligible, getRPAEligibilityReason } from '@/lib/utils';
import { chatContextManager } from '@/lib/chatContext';
import { Search, AlertTriangle, CheckCircle, XCircle, Eye, Settings, Trash2, MessageCircle, Bot, Zap, RefreshCw, MoreHorizontal, ChevronDown, ChevronRight } from 'lucide-react';
import ChatBubble from '@/components/chat/ChatBubble';
import { RPAStatus, RPAWorkflowDetails } from '@/components/ui/rpa-status';

// Helper function to format suggested_fix display
const formatSuggestedFix = (suggestedFix: string | SuggestedFix): string => {
  if (typeof suggestedFix === 'string') {
    return suggestedFix;
  }
  
  if (suggestedFix && suggestedFix.actions && suggestedFix.actions.length > 0) {
    return suggestedFix.actions.map(action => action.name).join(', ');
  }
  
  return 'Manual review required';
};

// Helper function to get rationale for tooltip
const getSuggestedFixRationale = (suggestedFix: string | SuggestedFix): string => {
  if (typeof suggestedFix === 'string') {
    return suggestedFix;
  }
  
  if (suggestedFix && suggestedFix.actions && suggestedFix.actions.length > 0) {
    return suggestedFix.actions.map(action => 
      action.rationale ? `${action.name}: ${action.rationale}` : action.name
    ).join('\n');
  }
  
  return 'Manual review required';
};

// Helper function to get suggested fix details for expanded view
const getSuggestedFixDetails = (suggestedFix: string | SuggestedFix) => {
  if (typeof suggestedFix === 'string') {
    return { actions: [{ name: suggestedFix, args: [], rationale: '' }] };
  }
  
  return suggestedFix || { actions: [] };
};

export default function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [waybillId, setWaybillId] = useState('');
  const [checkingAnomalies, setCheckingAnomalies] = useState(false);
  const [duplicateWarning, setDuplicateWarning] = useState('');
  const [selectedAnomalies, setSelectedAnomalies] = useState<Set<string>>(new Set());
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatAnomalyContext, setChatAnomalyContext] = useState<Anomaly[]>([]);
  const [rpaWorkflowDetails, setRpaWorkflowDetails] = useState<Anomaly | null>(null);
  const [isRpaWorkflowDetailsOpen, setIsRpaWorkflowDetailsOpen] = useState(false);
  const [submittingToRPA, setSubmittingToRPA] = useState(false);
  const [rpaStatusUpdates, setRpaStatusUpdates] = useState<Map<string, any>>(new Map());
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [actionMenus, setActionMenus] = useState<Set<string>>(new Set());
  const [activeMenuId, setActiveMenuId] = useState<string | null>(null);
  const [deletingAnomalies, setDeletingAnomalies] = useState<Set<string>>(new Set());
  const [dropdownPosition, setDropdownPosition] = useState<{ [key: string]: { top: number; left: number; position: 'above' | 'below' } }>({});

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        // First try to load from file
        const savedAnomalies = await apiService.loadAnomaliesFromFile();
        if (savedAnomalies.length > 0) {
          setAnomalies(savedAnomalies);
          console.log('Loaded anomalies from file');
        } else {
          // Fallback to API if no saved data
          const data = await apiService.getAnomalies({ limit: 100 });
          setAnomalies(data.items);
          // Save to file
          await apiService.saveAnomaliesToFile(data.items);
        }
      } catch (error) {
        console.error('Failed to fetch anomalies:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnomalies();
  }, []);

  // Close action menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (activeMenuId) {
        // Check if the click is outside any action menu
        const target = event.target as Element;
        const isInsideActionMenu = target.closest('[data-action-menu]');
        const isActionButton = target.closest('[data-anomaly-id]');
        const isBackdrop = target.classList.contains('fixed') && target.classList.contains('inset-0');
        if (!isInsideActionMenu && !isActionButton && !isBackdrop) {
        setActionMenus(new Set());
          setActiveMenuId(null);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [activeMenuId]);

  // Recalculate dropdown position on scroll
  useEffect(() => {
    const handleScroll = () => {
      if (activeMenuId && dropdownPosition[activeMenuId]) {
        const button = document.querySelector(`[data-anomaly-id="${activeMenuId}"]`);
        if (button) {
          const rect = button.getBoundingClientRect();
          const viewportHeight = window.innerHeight;
          const viewportWidth = window.innerWidth;
          const dropdownHeight = 200;
          const dropdownWidth = 192;
          
          // Position dropdown right next to the button
          let top = rect.bottom + 8; // Small gap below button
          let left = rect.right - dropdownWidth; // Align to right edge of button
          let position: 'above' | 'below' = 'below';
          
          // Check if dropdown would go off screen vertically
          if (top + dropdownHeight > viewportHeight - 10) {
            // Position above button if not enough space below
            top = rect.top - dropdownHeight - 8;
            position = 'above';
          }
          
          // Ensure dropdown doesn't go off left edge
          if (left < 10) {
            left = 10;
          }
          
          // Ensure dropdown doesn't go off right edge
          if (left + dropdownWidth > viewportWidth - 10) {
            left = viewportWidth - dropdownWidth - 10;
          }
          
          // If still not enough space, center it horizontally
          if (left < 10) {
            left = Math.max(10, (viewportWidth - dropdownWidth) / 2);
          }
          
          setDropdownPosition(prev => ({ 
            ...prev, 
            [activeMenuId]: { top, left, position }
          }));
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleScroll);
    };
  }, [activeMenuId, dropdownPosition]);

  const filteredAnomalies = anomalies.filter(anomaly => 
    anomaly.waybill_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    anomaly.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    anomaly.car_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleStatusUpdate = async (id: string, status: 'NEW' | 'RESOLVED' | 'IGNORED') => {
    try {
      // Update in file first
      const success = await apiService.updateAnomalyInFile(id, { status });
      if (success) {
        // Update local state
        const updatedAnomalies = anomalies.map(anomaly => 
          anomaly.id === id ? { ...anomaly, status } : anomaly
        );
        setAnomalies(updatedAnomalies);
      }
    } catch (error) {
      console.error('Failed to update anomaly status:', error);
    }
  };

  const handleDeleteAnomaly = async (id: string) => {
    console.log('Delete button clicked for anomaly:', id);
    if (confirm('Are you sure you want to delete this anomaly?')) {
      setDeletingAnomalies(prev => new Set(prev).add(id));
      try {
        console.log('Attempting to delete anomaly from file:', id);
        // Delete from file first
        const success = await apiService.deleteAnomalyFromFile(id);
        console.log('Delete API response:', success);
        if (success) {
          // Update local state
          const updatedAnomalies = anomalies.filter(anomaly => anomaly.id !== id);
          setAnomalies(updatedAnomalies);
          console.log('Anomaly deleted successfully:', id);
          // Clear duplicate warning if it was related to this deletion
          setDuplicateWarning('');
          // Remove from chat context if it exists
          chatContextManager.removeAnomalyFromContext(id);
          // Close the action menu after successful deletion
          setActionMenus(new Set());
          setActiveMenuId(null);
        } else {
          console.error('Delete API returned false');
          alert('Failed to delete anomaly. Please try again.');
        }
      } catch (error) {
        console.error('Failed to delete anomaly:', error);
        alert('Failed to delete anomaly. Please try again.');
      } finally {
        setDeletingAnomalies(prev => {
          const newSet = new Set(prev);
          newSet.delete(id);
          return newSet;
        });
      }
    }
  };

  const handleChatWithAnomaly = (anomaly: Anomaly) => {
    // Set the anomaly context and open chat bubble
    chatContextManager.setAnomalyContext([anomaly]);
    setChatAnomalyContext([anomaly]);
    setIsChatOpen(true);
  };

  const handleChatWithSelectedAnomalies = (anomalies: Anomaly[]) => {
    // Set the anomaly context and open chat bubble
    chatContextManager.setAnomalyContext(anomalies);
    setChatAnomalyContext(anomalies);
    setIsChatOpen(true);
  };

  const handleSelectAnomaly = (anomalyId: string) => {
    setSelectedAnomalies(prev => {
      const newSet = new Set(prev);
      if (newSet.has(anomalyId)) {
        newSet.delete(anomalyId);
      } else {
        newSet.add(anomalyId);
      }
      return newSet;
    });
  };

  const handleSelectAllAnomalies = (anomalies: Anomaly[]) => {
    const allSelected = anomalies.every(anomaly => selectedAnomalies.has(anomaly.id));
    if (allSelected) {
      setSelectedAnomalies(new Set());
    } else {
      setSelectedAnomalies(new Set(anomalies.map(anomaly => anomaly.id)));
    }
  };

  const handleBulkChat = () => {
    const selectedAnomalyObjects = anomalies.filter(anomaly => selectedAnomalies.has(anomaly.id));
    if (selectedAnomalyObjects.length > 0) {
      handleChatWithSelectedAnomalies(selectedAnomalyObjects);
    }
  };

  const handleChatClose = () => {
    setIsChatOpen(false);
    setChatAnomalyContext([]);
  };

  const handleContextChange = (anomalies: Anomaly[]) => {
    setChatAnomalyContext(anomalies);
  };

  const handleSubmitToRPA = async (anomalyIds: string[], autoFix: boolean = false) => {
    setSubmittingToRPA(true);
    try {
      const result = await apiService.submitToRPA(anomalyIds, autoFix);
      if (result.success) {
        // Update anomalies with RPA status
        const updatedAnomalies = anomalies.map(anomaly => {
          if (anomalyIds.includes(anomaly.id)) {
            return {
              ...anomaly,
              rpa_status: 'SUBMITTED' as const,
              rpa_submission_ts: new Date().toISOString(),
              auto_fix_eligible: autoFix,
              human_confirmed: !autoFix
            };
          }
          return anomaly;
        });
        setAnomalies(updatedAnomalies);
        await apiService.saveAnomaliesToFile(updatedAnomalies);
        
        alert(`Successfully submitted ${result.submitted_count} anomalies to RPA`);
      } else {
        alert(`Failed to submit anomalies: ${result.errors?.join(', ')}`);
      }
    } catch (error) {
      console.error('Failed to submit to RPA:', error);
      alert('Failed to submit anomalies to RPA');
    } finally {
      setSubmittingToRPA(false);
    }
  };

  const handleRpaRetry = async (workflowId: string) => {
    try {
      const result = await apiService.retryRPAWorkflow(workflowId);
      if (result.success) {
        alert('RPA workflow retry initiated');
        // Refresh the anomaly data
        const updatedAnomalies = await apiService.loadAnomaliesFromFile();
        setAnomalies(updatedAnomalies);
      } else {
        alert(`Failed to retry RPA workflow: ${result.message}`);
      }
    } catch (error) {
      console.error('Failed to retry RPA workflow:', error);
      alert('Failed to retry RPA workflow');
    }
  };

  const handleRpaCancel = async (workflowId: string) => {
    try {
      const result = await apiService.cancelRPAWorkflow(workflowId);
      if (result.success) {
        alert('RPA workflow cancelled');
        // Refresh the anomaly data
        const updatedAnomalies = await apiService.loadAnomaliesFromFile();
        setAnomalies(updatedAnomalies);
      } else {
        alert(`Failed to cancel RPA workflow: ${result.message}`);
      }
    } catch (error) {
      console.error('Failed to cancel RPA workflow:', error);
      alert('Failed to cancel RPA workflow');
    }
  };

  const handleViewRpaDetails = (anomaly: Anomaly) => {
    setRpaWorkflowDetails(anomaly);
    setIsRpaWorkflowDetailsOpen(true);
  };

  const handleBulkRpaSubmit = async (autoFix: boolean = false) => {
    const selectedAnomalyObjects = anomalies.filter(anomaly => selectedAnomalies.has(anomaly.id));
    const eligibleAnomalies = selectedAnomalyObjects.filter(anomaly => 
      !anomaly.rpa_status && (autoFix ? isRPAEligible(anomaly) : true)
    );
    
    if (eligibleAnomalies.length === 0) {
      alert('No eligible anomalies selected for RPA submission');
      return;
    }

    const anomalyIds = eligibleAnomalies.map(anomaly => anomaly.id);
    await handleSubmitToRPA(anomalyIds, autoFix);
  };

  const toggleRowExpansion = (anomalyId: string) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(anomalyId)) {
        newSet.delete(anomalyId);
      } else {
        newSet.add(anomalyId);
      }
      return newSet;
    });
  };

  const toggleActionMenu = (anomalyId: string) => {
    console.log('Toggle action menu for anomaly:', anomalyId);
    console.log('Current active menu:', activeMenuId);
    
    if (activeMenuId === anomalyId) {
      // Close this menu
      console.log('Closing menu for:', anomalyId);
      setActiveMenuId(null);
      setActionMenus(new Set());
      } else {
      // Open this menu and close others
      console.log('Opening menu for:', anomalyId, 'closing others');
      setActiveMenuId(anomalyId);
      setActionMenus(new Set([anomalyId]));
      
      // Calculate exact position
      const button = document.querySelector(`[data-anomaly-id="${anomalyId}"]`);
      if (button) {
        const rect = button.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        const dropdownHeight = 200; // Approximate dropdown height
        const dropdownWidth = 192; // 48 * 4 (w-48)
        
        // Position dropdown right next to the button
        let top = rect.bottom + 8; // Small gap below button
        let left = rect.right - dropdownWidth; // Align to right edge of button
        let position: 'above' | 'below' = 'below';
        
        // Check if dropdown would go off screen vertically
        if (top + dropdownHeight > viewportHeight - 10) {
          // Position above button if not enough space below
          top = rect.top - dropdownHeight - 8;
          position = 'above';
        }
        
        // Ensure dropdown doesn't go off left edge
        if (left < 10) {
          left = 10;
        }
        
        // Ensure dropdown doesn't go off right edge
        if (left + dropdownWidth > viewportWidth - 10) {
          left = viewportWidth - dropdownWidth - 10;
        }
        
        // If still not enough space, center it horizontally
        if (left < 10) {
          left = Math.max(10, (viewportWidth - dropdownWidth) / 2);
        }
        
        setDropdownPosition(prev => ({ 
          ...prev, 
          [anomalyId]: { top, left, position }
        }));
      }
    }
  };

  const handleQuickAction = (anomalyId: string, action: string) => {
    console.log('Quick action triggered:', action, 'for anomaly:', anomalyId);
    const anomaly = anomalies.find(a => a.id === anomalyId);
    if (!anomaly) {
      console.error('Anomaly not found:', anomalyId);
      return;
    }

    switch (action) {
      case 'accept':
        handleStatusUpdate(anomalyId, 'RESOLVED');
        break;
      case 'reject':
        handleStatusUpdate(anomalyId, 'IGNORED');
        break;
      case 'new':
        handleStatusUpdate(anomalyId, 'NEW');
        break;
      case 'modify':
        console.log('Modify button clicked for anomaly:', anomalyId);
        break;
      case 'escalate':
        alert(`Ticket has been raised for the anomaly ${anomaly.waybill_id}`);
        break;
      case 'chat':
        handleChatWithAnomaly(anomaly);
        break;
      case 'delete':
        console.log('Delete action triggered for anomaly:', anomalyId);
        handleDeleteAnomaly(anomalyId);
        // Don't close menu here - let delete function handle it
        return;
      case 'rpa':
        handleViewRpaDetails(anomaly);
        break;
    }
    // Close all menus for all actions except delete
    setActionMenus(new Set());
    setActiveMenuId(null);
  };

  const checkForDuplicates = (inputValue: string) => {
    if (!inputValue.trim()) {
      setDuplicateWarning('');
      return;
    }

    const waybillIds = inputValue.split(',').map(id => id.trim());
    const existingAnomalies = anomalies.filter(anomaly => 
      waybillIds.includes(anomaly.waybill_id)
    );

    if (existingAnomalies.length > 0) {
      const existingWaybillIds = Array.from(new Set(existingAnomalies.map(a => a.waybill_id)));
      setDuplicateWarning(`⚠️ Anomalies already exist for: ${existingWaybillIds.join(', ')} (${existingAnomalies.length} anomalies)`);
    } else {
      setDuplicateWarning('');
    }
  };

  const handleCheckAnomalies = async () => {
    if (!waybillId.trim()) {
      alert('Please enter a Waybill ID');
      return;
    }

    setCheckingAnomalies(true);
    try {
      console.log('Checking anomalies for waybill(s):', waybillId);
      
      // Parse waybill IDs (handle comma-separated)
      const waybillIds = waybillId.split(',').map(id => id.trim());
      
      // Check if anomalies already exist for these waybill IDs
      const existingAnomalies = anomalies.filter(anomaly => 
        waybillIds.includes(anomaly.waybill_id)
      );
      
      if (existingAnomalies.length > 0) {
        const existingWaybillIds = Array.from(new Set(existingAnomalies.map(a => a.waybill_id)));
        const message = `⚠️ Anomalies Already Exist!\n\n` +
          `Waybill ID(s): ${existingWaybillIds.join(', ')}\n` +
          `Existing anomalies: ${existingAnomalies.length}\n\n` +
          `To run new checks:\n` +
          `1. Delete existing anomalies for these waybill IDs, OR\n` +
          `2. Use different waybill IDs\n\n` +
          `Check the table below to see existing anomalies.`;
        
        alert(message);
        setCheckingAnomalies(false);
        return;
      }
      
      // Call the local anomaly check API only if no existing anomalies
      const result = await apiService.checkAnomalies(waybillId);
      console.log('Anomaly check result:', result);
      
      // Parse the result string to get the anomalies array
      let parsedAnomalies = [];
      try {
        parsedAnomalies = JSON.parse(result.result);
        console.log('Parsed anomalies:', parsedAnomalies);
      } catch (parseError) {
        console.error('Failed to parse anomalies result:', parseError);
        alert('Received response but failed to parse anomalies data.');
        return;
      }
      
      // Add the new anomalies to the existing list
      const newAnomalies = parsedAnomalies.map((anomaly: any) => ({
        id: anomaly.id || `anomaly_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        waybill_id: anomaly.waybill_id,
        car_id: anomaly.car_id,
        csn_id: anomaly.csn_id,
        type: anomaly.type,
        confidence: anomaly.confidence,
        suggested_fix: anomaly.suggested_fix || 'Manual review required',
        status: anomaly.status || 'NEW',
        created_ts: anomaly.created_ts || new Date().toISOString(),
        updated_ts: anomaly.updated_ts || new Date().toISOString(),
        details: anomaly.details || '',
        needs_confirmation: anomaly.needs_confirmation || false,
        // Preserve all RPA-related fields from backend response
        rpa_status: anomaly.rpa_status,
        rpa_submission_ts: anomaly.rpa_submission_ts,
        rpa_completion_ts: anomaly.rpa_completion_ts,
        rpa_error_message: anomaly.rpa_error_message,
        rpa_workflow_id: anomaly.rpa_workflow_id,
        rpa_retry_count: anomaly.rpa_retry_count,
        human_confirmed: anomaly.human_confirmed,
        rpa_actions: anomaly.rpa_actions
      }));
      
      // Add new anomalies to the existing list
      const updatedAnomalies = [...newAnomalies, ...anomalies];
      setAnomalies(updatedAnomalies);
      
      // Save updated anomalies to file
      await apiService.saveAnomaliesToFile(updatedAnomalies);
      
      // Clear the input
      setWaybillId('');
      
      alert(`Anomaly check completed! Found ${parsedAnomalies.length} anomalies for waybill(s): ${result.waybill_id}`);
    } catch (error) {
      console.error('Failed to check anomalies:', error);
      alert('Failed to check anomalies. Please make sure the local API server is running on http://localhost:8080');
    } finally {
      setCheckingAnomalies(false);
    }
  };

  const newAnomalies = filteredAnomalies.filter(a => a.status === 'NEW');
  const resolvedAnomalies = filteredAnomalies.filter(a => a.status === 'RESOLVED');
  const ignoredAnomalies = filteredAnomalies.filter(a => a.status === 'IGNORED');

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 overflow-visible">
      {/* Portal container for dropdowns */}
      <div id="dropdown-portal" className="fixed inset-0 pointer-events-none z-[999999]" style={{ zIndex: 999999 }}>
        {activeMenuId && dropdownPosition[activeMenuId] && (
          <>
            {/* Backdrop */}
            <div 
              className="fixed inset-0 pointer-events-auto"
              style={{ 
                position: 'fixed', 
                top: 0, 
                left: 0, 
                right: 0, 
                bottom: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.01)',
                zIndex: 999998
              }}
              onClick={() => {
                setActionMenus(new Set());
                setActiveMenuId(null);
              }}
            />
            {/* Dropdown */}
            <div 
              className="fixed w-48 bg-white rounded-md shadow-2xl border-2 border-gray-200 pointer-events-auto"
              data-action-menu
              style={{ 
                position: 'fixed',
                top: `${dropdownPosition[activeMenuId]?.top || 0}px`,
                left: `${dropdownPosition[activeMenuId]?.left || 0}px`,
                minWidth: '192px',
                maxHeight: '300px',
                overflowY: 'auto',
                backgroundColor: 'white',
                zIndex: 999999
              }}
            >
              <div className="py-1">
                {(() => {
                  const anomaly = anomalies.find(a => a.id === activeMenuId);
                  if (!anomaly) return null;
                  
                  const isResolved = anomaly.status === 'RESOLVED';
                  const isIgnored = anomaly.status === 'IGNORED';
                  
                  return (
                    <>
                      {/* For NEW anomalies */}
                      {!isResolved && !isIgnored && (
                        <>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'accept')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            Accept
                          </button>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'reject')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <XCircle className="h-4 w-4 text-red-600" />
                            Reject
                          </button>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'modify')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <Settings className="h-4 w-4 text-blue-600" />
                            Modify
                          </button>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'escalate')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <AlertTriangle className="h-4 w-4 text-orange-600" />
                            Escalate
                          </button>
                        </>
                      )}
                      
                      {/* For RESOLVED anomalies */}
                      {isResolved && (
                        <>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'new')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <AlertTriangle className="h-4 w-4 text-orange-600" />
                            Move to New
                          </button>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'reject')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <XCircle className="h-4 w-4 text-red-600" />
                            Reject
                          </button>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'modify')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <Settings className="h-4 w-4 text-blue-600" />
                            Modify
                          </button>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'escalate')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <AlertTriangle className="h-4 w-4 text-orange-600" />
                            Escalate
                          </button>
                        </>
                      )}
                      
                      {/* For IGNORED anomalies */}
                      {isIgnored && (
                        <>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'new')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <AlertTriangle className="h-4 w-4 text-orange-600" />
                            Move to New
                          </button>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'accept')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            Accept
                          </button>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'modify')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <Settings className="h-4 w-4 text-blue-600" />
                            Modify
                          </button>
                          <button
                            onClick={() => handleQuickAction(anomaly.id, 'escalate')}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            <AlertTriangle className="h-4 w-4 text-orange-600" />
                            Escalate
                          </button>
                        </>
                      )}
                      
                      {/* Common buttons for all statuses */}
                      <button
                        onClick={() => handleQuickAction(anomaly.id, 'chat')}
                        className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <MessageCircle className="h-4 w-4 text-blue-600" />
                        Chat about this
                      </button>
                      <button
                        onClick={() => handleQuickAction(anomaly.id, 'rpa')}
                        className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <Bot className="h-4 w-4 text-purple-600" />
                        RPA Details
                      </button>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleQuickAction(anomaly.id, 'delete');
                        }}
                        disabled={deletingAnomalies.has(anomaly.id)}
                        className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {deletingAnomalies.has(anomaly.id) ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                            Deleting...
                          </>
                        ) : (
                          <>
                            <Trash2 className="h-4 w-4" />
                            Delete
                          </>
                        )}
                      </button>
                    </>
                  );
                })()}
              </div>
            </div>
          </>
        )}
      </div>
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Anomalies</h1>
            <p className="text-gray-600 mt-2">Monitor and resolve system anomalies</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search anomalies..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
            <Button 
              variant="outline"
              className="flex items-center gap-2"
              onClick={async () => {
                if (confirm('Are you sure you want to clear all anomalies?')) {
                  try {
                    const success = await apiService.clearAllAnomaliesFromFile();
                    if (success) {
                      setAnomalies([]);
                      setDuplicateWarning('');
                      console.log('All anomalies cleared');
                    }
                  } catch (error) {
                    console.error('Failed to clear all anomalies:', error);
                  }
                }
              }}
            >
              <Trash2 className="h-4 w-4" />
              Clear All
            </Button>
            <Button 
              className="flex items-center gap-2"
              onClick={handleBulkChat}
              disabled={selectedAnomalies.size === 0}
              variant={selectedAnomalies.size > 0 ? "default" : "outline"}
            >
              <MessageCircle className="h-4 w-4" />
              Chat Selected ({selectedAnomalies.size})
            </Button>
            <Button 
              className="flex items-center gap-2"
              onClick={() => handleBulkRpaSubmit(true)}
              disabled={selectedAnomalies.size === 0 || submittingToRPA}
              variant={selectedAnomalies.size > 0 ? "default" : "outline"}
            >
              {submittingToRPA ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Zap className="h-4 w-4" />
              )}
              Auto-Fix ({selectedAnomalies.size})
            </Button>
            <Button 
              className="flex items-center gap-2"
              onClick={() => handleBulkRpaSubmit(false)}
              disabled={selectedAnomalies.size === 0 || submittingToRPA}
              variant="outline"
            >
              {submittingToRPA ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Bot className="h-4 w-4" />
              )}
              Submit to RPA ({selectedAnomalies.size})
            </Button>
          </div>
        </div>
      </div>

      {/* Anomaly Check Section */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Check for Anomalies
          </CardTitle>
          <CardDescription>
            Enter one or more Waybill IDs (comma-separated) to analyze for potential anomalies using AI
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <Input
                placeholder="Enter Waybill ID(s) (e.g., WB3014 or WB3005, WB3019)"
                value={waybillId}
                onChange={(e) => {
                  setWaybillId(e.target.value);
                  checkForDuplicates(e.target.value);
                }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleCheckAnomalies();
                  }
                }}
                disabled={checkingAnomalies}
                className={duplicateWarning ? 'border-yellow-400 bg-yellow-50' : ''}
              />
            </div>
            <Button 
              onClick={handleCheckAnomalies}
              disabled={checkingAnomalies || !waybillId.trim() || duplicateWarning !== ''}
              className="flex items-center gap-2"
            >
              {checkingAnomalies ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Checking...
                </>
              ) : (
                <>
                  <AlertTriangle className="h-4 w-4" />
                  Check Anomalies
                </>
              )}
            </Button>
          </div>
          {duplicateWarning && (
            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-sm text-yellow-800">{duplicateWarning}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              New Anomalies
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{newAnomalies.length}</div>
            <p className="text-xs text-gray-500">Require immediate attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Resolved
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{resolvedAnomalies.length}</div>
            <p className="text-xs text-gray-500">Successfully fixed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Ignored
            </CardTitle>
            <XCircle className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">{ignoredAnomalies.length}</div>
            <p className="text-xs text-gray-500">Marked as false positives</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="new" className="space-y-6 overflow-visible">
        <TabsList>
          <TabsTrigger value="new" className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            New ({newAnomalies.length})
          </TabsTrigger>
          <TabsTrigger value="resolved" className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            Resolved ({resolvedAnomalies.length})
          </TabsTrigger>
          <TabsTrigger value="ignored" className="flex items-center gap-2">
            <XCircle className="h-4 w-4" />
            Ignored ({ignoredAnomalies.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="new">
          <Card>
            <CardHeader>
              <CardTitle>New Anomalies</CardTitle>
              <CardDescription>
                Anomalies that require immediate attention
              </CardDescription>
            </CardHeader>
            <CardContent className="overflow-visible">
              <div className="overflow-visible">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <input
                        type="checkbox"
                        checked={newAnomalies.length > 0 && newAnomalies.every(anomaly => selectedAnomalies.has(anomaly.id))}
                        onChange={() => handleSelectAllAnomalies(newAnomalies)}
                        className="rounded"
                      />
                    </TableHead>
                    <TableHead>Anomaly</TableHead>
                    <TableHead>Fix & Confidence</TableHead>
                    <TableHead>RPA Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="w-12">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {newAnomalies.map((anomaly) => (
                    <>
                      <TableRow key={anomaly.id} className="hover:bg-gray-50 relative">
                        <TableCell>
                          <input
                            type="checkbox"
                            checked={selectedAnomalies.has(anomaly.id)}
                            onChange={() => handleSelectAnomaly(anomaly.id)}
                            className="rounded"
                          />
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <Badge variant="destructive" className="text-xs">
                                {anomaly.type}
                              </Badge>
                              <span className="font-medium text-sm">{anomaly.waybill_id}</span>
                            </div>
                            <div className="text-xs text-gray-600">
                              {anomaly.details || 'No details available'}
                            </div>
                            <div className="flex items-center gap-2 text-xs text-gray-500">
                              <span>Car: {anomaly.car_id}</span>
                              <span>•</span>
                              <span className="font-mono">CSN: {anomaly.csn_id}</span>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-2">
                            <div 
                              className="inline-block"
                              title={getSuggestedFixRationale(anomaly.suggested_fix)}
                            >
                              <Badge variant="outline" className="text-xs cursor-help">
                                {formatSuggestedFix(anomaly.suggested_fix)}
                            </Badge>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="w-16 bg-gray-200 rounded-full h-1.5">
                                <div 
                                  className="bg-red-500 h-1.5 rounded-full" 
                                  style={{ width: `${anomaly.confidence * 100}%` }}
                                ></div>
                              </div>
                              <span className="text-xs text-gray-600">
                                {(anomaly.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <RPAStatus 
                            anomaly={anomaly}
                            onRetry={handleRpaRetry}
                            onCancel={handleRpaCancel}
                            onViewDetails={handleViewRpaDetails}
                          />
                        </TableCell>
                        <TableCell>
                          <span className="text-sm text-gray-600">
                            {formatDate(anomaly.created_ts)}
                          </span>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1 relative z-10">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleActionMenu(anomaly.id)}
                              className="h-8 w-8 p-0"
                              data-anomaly-id={anomaly.id}
                            >
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                      {expandedRows.has(anomaly.id) && (
                        <TableRow>
                          <TableCell colSpan={6} className="bg-gray-50 p-4">
                            <div className="space-y-3">
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <h4 className="font-medium text-sm text-gray-900 mb-2">Anomaly Details</h4>
                                  <div className="space-y-1 text-sm">
                                    <div><span className="font-medium">Type:</span> {anomaly.type}</div>
                                    <div><span className="font-medium">Waybill ID:</span> {anomaly.waybill_id}</div>
                                    <div><span className="font-medium">Car ID:</span> {anomaly.car_id}</div>
                                    <div><span className="font-medium">CSN ID:</span> {anomaly.csn_id}</div>
                                  </div>
                                </div>
                                <div>
                                  <h4 className="font-medium text-sm text-gray-900 mb-2">Suggested Fix</h4>
                                  <div className="space-y-1 text-sm">
                                    <div><span className="font-medium">Actions:</span></div>
                                    {getSuggestedFixDetails(anomaly.suggested_fix).actions.map((action, index) => (
                                      <div key={index} className="ml-4 p-2 bg-gray-50 rounded border-l-2 border-blue-200">
                                        <div className="font-medium text-blue-800">{action.name}</div>
                                        {action.args && action.args.length > 0 && (
                                          <div className="text-xs text-gray-600 mt-1">
                                            <span className="font-medium">Arguments:</span>
                                            {action.args.map((arg, argIndex) => (
                                              <span key={argIndex} className="ml-1">
                                                {arg.key}: {arg.value}
                                                {argIndex < action.args.length - 1 ? ', ' : ''}
                                              </span>
                                            ))}
                                          </div>
                                        )}
                                        {action.rationale && (
                                          <div className="text-xs text-gray-600 mt-1">
                                            <span className="font-medium">Rationale:</span> {action.rationale}
                                          </div>
                                        )}
                                      </div>
                                    ))}
                                    <div><span className="font-medium">Confidence:</span> {(anomaly.confidence * 100).toFixed(0)}%</div>
                                    <div><span className="font-medium">Needs Confirmation:</span> {anomaly.needs_confirmation ? 'Yes' : 'No'}</div>
                                  </div>
                                </div>
                              </div>
                              <div className="pt-2 border-t">
                                <h4 className="font-medium text-sm text-gray-900 mb-2">Description</h4>
                                <p className="text-sm text-gray-600">{anomaly.details || 'No additional details available'}</p>
                              </div>
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </>
                  ))}
                </TableBody>
              </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resolved">
          <Card>
            <CardHeader>
              <CardTitle>Resolved Anomalies</CardTitle>
              <CardDescription>
                Anomalies that have been successfully resolved
              </CardDescription>
            </CardHeader>
            <CardContent className="overflow-visible">
              <div className="overflow-visible">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <input
                        type="checkbox"
                        checked={resolvedAnomalies.length > 0 && resolvedAnomalies.every(anomaly => selectedAnomalies.has(anomaly.id))}
                        onChange={() => handleSelectAllAnomalies(resolvedAnomalies)}
                        className="rounded"
                      />
                    </TableHead>
                    <TableHead>Anomaly</TableHead>
                    <TableHead>Fix & Confidence</TableHead>
                    <TableHead>RPA Status</TableHead>
                    <TableHead>Resolved</TableHead>
                    <TableHead className="w-12">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {resolvedAnomalies.map((anomaly) => (
                    <TableRow key={anomaly.id} className="hover:bg-gray-50 relative">
                      <TableCell>
                        <input
                          type="checkbox"
                          checked={selectedAnomalies.has(anomaly.id)}
                          onChange={() => handleSelectAnomaly(anomaly.id)}
                          className="rounded"
                        />
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge className="bg-green-100 text-green-800 text-xs">
                              {anomaly.type}
                            </Badge>
                            <span className="font-medium text-sm">{anomaly.waybill_id}</span>
                          </div>
                          <div className="text-xs text-gray-600">
                            {anomaly.details || 'No details available'}
                          </div>
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <span>Car: {anomaly.car_id}</span>
                            <span>•</span>
                            <span className="font-mono">CSN: {anomaly.csn_id}</span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-2">
                          <div 
                            className="inline-block"
                            title={getSuggestedFixRationale(anomaly.suggested_fix)}
                          >
                            <Badge variant="outline" className="text-xs cursor-help">
                              {formatSuggestedFix(anomaly.suggested_fix)}
                          </Badge>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-1.5">
                              <div 
                                className="bg-green-500 h-1.5 rounded-full" 
                                style={{ width: `${anomaly.confidence * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-xs text-gray-600">
                              {(anomaly.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <RPAStatus 
                          anomaly={anomaly}
                          onRetry={handleRpaRetry}
                          onCancel={handleRpaCancel}
                          onViewDetails={handleViewRpaDetails}
                        />
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-gray-600">
                          {formatDate(anomaly.updated_ts)}
                        </span>
                      </TableCell>
                      <TableCell>
                          <div className="flex items-center gap-1 relative z-10">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleActionMenu(anomaly.id)}
                            className="h-8 w-8 p-0"
                              data-anomaly-id={anomaly.id}
                          >
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                            {activeMenuId === anomaly.id && (
                              <>
                                {/* Backdrop to prevent interaction with elements behind */}
                                <div 
                                  className="fixed inset-0 z-[999998]"
                                  style={{ 
                                    position: 'fixed', 
                                    top: 0, 
                                    left: 0, 
                                    right: 0, 
                                    bottom: 0,
                                    backgroundColor: 'rgba(0, 0, 0, 0.01)',
                                    zIndex: 999998
                                  }}
                                  onClick={() => {
                                    setActionMenus(new Set());
                                    setActiveMenuId(null);
                                  }}
                                />
                                {/* Dropdown */}
                                <div 
                                  key={`menu-${anomaly.id}`}
                                  className="fixed w-48 bg-white rounded-md shadow-2xl z-[999999] border-2 border-gray-200" 
                                  data-action-menu
                                  style={{ 
                                    position: 'fixed',
                                    top: `${dropdownPosition[anomaly.id]?.top || 0}px`,
                                    left: `${dropdownPosition[anomaly.id]?.left || 0}px`,
                                    minWidth: '192px',
                                    maxHeight: '300px',
                                    overflowY: 'auto',
                                    backgroundColor: 'white',
                                    zIndex: 999999
                                  }}
                                >
                              <div className="py-1">
                                <button
                                  onClick={() => handleQuickAction(anomaly.id, 'new')}
                                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                >
                                  <AlertTriangle className="h-4 w-4 text-orange-600" />
                                  Move to New
                                </button>
                                <button
                                  onClick={() => handleQuickAction(anomaly.id, 'ignore')}
                                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                >
                                  <XCircle className="h-4 w-4 text-gray-600" />
                                  Move to Ignored
                                </button>
                                <button
                                  onClick={() => handleQuickAction(anomaly.id, 'chat')}
                                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                >
                                  <MessageCircle className="h-4 w-4 text-blue-600" />
                                  Chat about this
                                </button>
                                <button
                                  onClick={() => handleQuickAction(anomaly.id, 'rpa')}
                                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                >
                                  <Bot className="h-4 w-4 text-purple-600" />
                                  RPA Details
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    handleQuickAction(anomaly.id, 'delete');
                                  }}
                                  disabled={deletingAnomalies.has(anomaly.id)}
                                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  {deletingAnomalies.has(anomaly.id) ? (
                                    <>
                                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                                      Deleting...
                                    </>
                                  ) : (
                                    <>
                                  <Trash2 className="h-4 w-4" />
                                  Delete
                                    </>
                                  )}
                                </button>
                              </div>
                            </div>
                            </>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ignored">
          <Card>
            <CardHeader>
              <CardTitle>Ignored Anomalies</CardTitle>
              <CardDescription>
                Anomalies marked as false positives
              </CardDescription>
            </CardHeader>
            <CardContent className="overflow-visible">
              <div className="overflow-visible">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <input
                        type="checkbox"
                        checked={ignoredAnomalies.length > 0 && ignoredAnomalies.every(anomaly => selectedAnomalies.has(anomaly.id))}
                        onChange={() => handleSelectAllAnomalies(ignoredAnomalies)}
                        className="rounded"
                      />
                    </TableHead>
                    <TableHead>Anomaly</TableHead>
                    <TableHead>Fix & Confidence</TableHead>
                    <TableHead>RPA Status</TableHead>
                    <TableHead>Ignored</TableHead>
                    <TableHead className="w-12">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {ignoredAnomalies.map((anomaly) => (
                    <TableRow key={anomaly.id} className="hover:bg-gray-50 relative">
                      <TableCell>
                        <input
                          type="checkbox"
                          checked={selectedAnomalies.has(anomaly.id)}
                          onChange={() => handleSelectAnomaly(anomaly.id)}
                          className="rounded"
                        />
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary" className="text-xs">
                              {anomaly.type}
                            </Badge>
                            <span className="font-medium text-sm">{anomaly.waybill_id}</span>
                          </div>
                          <div className="text-xs text-gray-600">
                            {anomaly.details || 'No details available'}
                          </div>
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <span>Car: {anomaly.car_id}</span>
                            <span>•</span>
                            <span className="font-mono">CSN: {anomaly.csn_id}</span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-2">
                          <div 
                            className="inline-block"
                            title={getSuggestedFixRationale(anomaly.suggested_fix)}
                          >
                            <Badge variant="outline" className="text-xs cursor-help">
                              {formatSuggestedFix(anomaly.suggested_fix)}
                          </Badge>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-gray-200 rounded-full h-1.5">
                              <div 
                                className="bg-gray-500 h-1.5 rounded-full" 
                                style={{ width: `${anomaly.confidence * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-xs text-gray-600">
                              {(anomaly.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <RPAStatus 
                          anomaly={anomaly}
                          onRetry={handleRpaRetry}
                          onCancel={handleRpaCancel}
                          onViewDetails={handleViewRpaDetails}
                        />
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-gray-600">
                          {formatDate(anomaly.updated_ts)}
                        </span>
                      </TableCell>
                      <TableCell>
                          <div className="flex items-center gap-1 relative z-10">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleActionMenu(anomaly.id)}
                            className="h-8 w-8 p-0"
                              data-anomaly-id={anomaly.id}
                          >
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                            {activeMenuId === anomaly.id && (
                              <>
                                {/* Backdrop to prevent interaction with elements behind */}
                                <div 
                                  className="fixed inset-0 z-[999998]"
                                  style={{ 
                                    position: 'fixed', 
                                    top: 0, 
                                    left: 0, 
                                    right: 0, 
                                    bottom: 0,
                                    backgroundColor: 'rgba(0, 0, 0, 0.01)',
                                    zIndex: 999998
                                  }}
                                  onClick={() => {
                                    setActionMenus(new Set());
                                    setActiveMenuId(null);
                                  }}
                                />
                                {/* Dropdown */}
                                <div 
                                  key={`menu-${anomaly.id}`}
                                  className="fixed w-48 bg-white rounded-md shadow-2xl z-[999999] border-2 border-gray-200" 
                                  data-action-menu
                                  style={{ 
                                    position: 'fixed',
                                    top: `${dropdownPosition[anomaly.id]?.top || 0}px`,
                                    left: `${dropdownPosition[anomaly.id]?.left || 0}px`,
                                    minWidth: '192px',
                                    maxHeight: '300px',
                                    overflowY: 'auto',
                                    backgroundColor: 'white',
                                    zIndex: 999999
                                  }}
                                >
                              <div className="py-1">
                                <button
                                  onClick={() => handleQuickAction(anomaly.id, 'new')}
                                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                >
                                  <AlertTriangle className="h-4 w-4 text-orange-600" />
                                  Move to New
                                </button>
                                <button
                                  onClick={() => handleQuickAction(anomaly.id, 'ignore')}
                                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                >
                                  <CheckCircle className="h-4 w-4 text-green-600" />
                                  Move to Resolved
                                </button>
                                <button
                                  onClick={() => handleQuickAction(anomaly.id, 'chat')}
                                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                >
                                  <MessageCircle className="h-4 w-4 text-blue-600" />
                                  Chat about this
                                </button>
                                <button
                                  onClick={() => handleQuickAction(anomaly.id, 'rpa')}
                                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                >
                                  <Bot className="h-4 w-4 text-purple-600" />
                                  RPA Details
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    handleQuickAction(anomaly.id, 'delete');
                                  }}
                                  disabled={deletingAnomalies.has(anomaly.id)}
                                  className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  {deletingAnomalies.has(anomaly.id) ? (
                                    <>
                                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                                      Deleting...
                                    </>
                                  ) : (
                                    <>
                                  <Trash2 className="h-4 w-4" />
                                  Delete
                                    </>
                                  )}
                                </button>
                              </div>
                            </div>
                            </>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Floating Chat Button */}
      {!isChatOpen && (
        <Button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-4 right-4 z-40 rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-all duration-300"
          size="icon"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      )}

      {/* Chat Bubble */}
      <ChatBubble
        isOpen={isChatOpen}
        onClose={handleChatClose}
        anomalyContext={chatAnomalyContext}
        onContextChange={handleContextChange}
      />

      {/* RPA Workflow Details Modal */}
      {rpaWorkflowDetails && (
        <RPAWorkflowDetails
          anomaly={rpaWorkflowDetails}
          isOpen={isRpaWorkflowDetailsOpen}
          onClose={() => {
            setIsRpaWorkflowDetailsOpen(false);
            setRpaWorkflowDetails(null);
          }}
        />
      )}
    </div>
  );
}
