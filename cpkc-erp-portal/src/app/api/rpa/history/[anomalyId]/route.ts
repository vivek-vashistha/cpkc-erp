import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { anomalyId: string } }
) {
  try {
    const { anomalyId } = params;

    if (!anomalyId) {
      return NextResponse.json(
        { error: 'Anomaly ID is required' },
        { status: 400 }
      );
    }

    // Simulate RPA workflow history retrieval
    // In a real implementation, this would:
    // 1. Query database for all workflows related to this anomaly
    // 2. Get detailed action history
    // 3. Return comprehensive workflow timeline

    // Mock workflow history
    const mockWorkflows = [
      {
        workflow_id: `rpa_workflow_${anomalyId}_1`,
        status: 'COMPLETED',
        submitted_ts: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        completed_ts: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
        actions: [
          {
            id: 'action_1',
            action_type: 'SET_CARID',
            status: 'COMPLETED',
            executed_ts: new Date(Date.now() - 90 * 60 * 1000).toISOString()
          },
          {
            id: 'action_2',
            action_type: 'SET_CSNID', 
            status: 'COMPLETED',
            executed_ts: new Date(Date.now() - 85 * 60 * 1000).toISOString()
          }
        ]
      },
      {
        workflow_id: `rpa_workflow_${anomalyId}_2`,
        status: 'FAILED',
        submitted_ts: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        actions: [
          {
            id: 'action_3',
            action_type: 'INSERT_EVENT',
            status: 'FAILED',
            error_message: 'ERP connection timeout',
            executed_ts: new Date(Date.now() - 25 * 60 * 1000).toISOString()
          }
        ]
      }
    ];

    return NextResponse.json({
      anomaly_id: anomalyId,
      workflows: mockWorkflows
    });

  } catch (error) {
    console.error('RPA history retrieval error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to get RPA workflow history',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
