'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { 
  getRPAStatusColor, 
  getRPAStatusIcon, 
  formatRPAProgress, 
  isRPAEligible, 
  getRPAEligibilityReason 
} from '@/lib/utils';
import { type Anomaly, type RPAAction } from '@/lib/api';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  Bot,
  User,
  Eye
} from 'lucide-react';
import { useState, useEffect } from 'react';

interface RPAStatusProps {
  anomaly: Anomaly;
  onRetry?: (workflowId: string) => void;
  onCancel?: (workflowId: string) => void;
  onViewDetails?: (anomaly: Anomaly) => void;
}

export function RPAStatus({ anomaly, onRetry, onCancel, onViewDetails }: RPAStatusProps) {
  const rpaStatus = anomaly.rpa_status || 'PENDING';
  const isEligible = isRPAEligible(anomaly);

  const getStatusDisplay = () => {
    if (!anomaly.rpa_status) {
      return {
        icon: isEligible ? <Bot className="h-3 w-3" /> : <User className="h-3 w-3" />,
        text: isEligible ? 'Auto-Fix' : 'Manual',
        color: isEligible ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
      };
    }

    // Handle the new status values from system prompt
    const statusText = rpaStatus === 'Auto Fix' ? 'Auto Fix' : 
                      rpaStatus === 'Manual Review Required' ? 'Manual Review' :
                      rpaStatus === 'Needs Data' ? 'Needs Data' :
                      rpaStatus.replace('_', ' ');

    return {
      icon: <span className="text-xs">{getRPAStatusIcon(rpaStatus)}</span>,
      text: statusText,
      color: getRPAStatusColor(rpaStatus)
    };
  };

  const statusDisplay = getStatusDisplay();

  const getQuickAction = () => {
    if (!anomaly.rpa_status && isEligible) {
      return (
        <Button
          size="sm"
          variant="ghost"
          onClick={() => onViewDetails?.(anomaly)}
          className="h-6 px-2 text-xs"
        >
          <Play className="h-3 w-3" />
        </Button>
      );
    }

    // Handle new status values
    if (rpaStatus === 'Auto Fix') {
      return (
        <Button
          size="sm"
          variant="ghost"
          onClick={() => onViewDetails?.(anomaly)}
          className="h-6 px-2 text-xs"
        >
          <Play className="h-3 w-3" />
        </Button>
      );
    }

    if (rpaStatus === 'Manual Review Required' || rpaStatus === 'Needs Data') {
      return (
        <Button
          size="sm"
          variant="ghost"
          onClick={() => onViewDetails?.(anomaly)}
          className="h-6 px-2 text-xs"
        >
          <Eye className="h-3 w-3" />
        </Button>
      );
    }

    // Handle workflow statuses
    if (rpaStatus === 'FAILED') {
      return (
        <Button
          size="sm"
          variant="ghost"
          onClick={() => onRetry?.(anomaly.rpa_workflow_id!)}
          className="h-6 px-2 text-xs"
        >
          <RotateCcw className="h-3 w-3" />
        </Button>
      );
    }

    if (rpaStatus === 'COMPLETED' || rpaStatus === 'IN_PROGRESS') {
      return (
        <Button
          size="sm"
          variant="ghost"
          onClick={() => onViewDetails?.(anomaly)}
          className="h-6 px-2 text-xs"
        >
          <Eye className="h-3 w-3" />
        </Button>
      );
    }

    return null;
  };

  return (
    <div className="flex items-center gap-2">
      <Badge className={`${statusDisplay.color} text-xs px-2 py-1`}>
        {statusDisplay.icon}
        <span className="ml-1">{statusDisplay.text}</span>
      </Badge>
      {getQuickAction()}
    </div>
  );
}

interface RPAWorkflowDetailsProps {
  anomaly: Anomaly;
  isOpen: boolean;
  onClose: () => void;
}

export function RPAWorkflowDetails({ anomaly, isOpen, onClose }: RPAWorkflowDetailsProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            RPA Workflow Details
          </CardTitle>
          <CardDescription>
            Anomaly: {anomaly.waybill_id} - {anomaly.type}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-600">Workflow ID</label>
              <p className="text-sm font-mono">{anomaly.rpa_workflow_id || 'N/A'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Status</label>
              <p className="text-sm">{anomaly.rpa_status || 'Not submitted'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Confidence</label>
              <p className="text-sm">{(anomaly.confidence * 100).toFixed(0)}%</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Auto-Fix Eligible</label>
              <p className="text-sm">{isRPAEligible(anomaly) ? 'Yes' : 'No'}</p>
            </div>
          </div>

          {anomaly.rpa_actions && anomaly.rpa_actions.length > 0 && (
            <div>
              <label className="text-sm font-medium text-gray-600 mb-2 block">Actions</label>
              <div className="space-y-2">
                {anomaly.rpa_actions.map((action, index) => (
                  <div key={action.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{index + 1}.</span>
                      <span className="text-sm">{action.action_type.replace('_', ' ')}</span>
                      {action.event_type && (
                        <span className="text-xs text-gray-500">({action.event_type})</span>
                      )}
                    </div>
                    <Badge className={getRPAStatusColor(action.status)}>
                      {action.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
