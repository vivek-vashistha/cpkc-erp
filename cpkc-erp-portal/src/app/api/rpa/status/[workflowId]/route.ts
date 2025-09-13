import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { workflowId: string } }
) {
  try {
    const { workflowId } = params;

    if (!workflowId) {
      return NextResponse.json(
        { error: 'Workflow ID is required' },
        { status: 400 }
      );
    }

    // Simulate RPA status check
    // In a real implementation, this would:
    // 1. Query Blue Prism RPA system for workflow status
    // 2. Get current progress and action details
    // 3. Return real-time status information

    // Simulate different statuses based on workflow ID
    const statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED'];
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
    
    const mockActions = [
      {
        id: 'action_1',
        action_type: 'SET_CARID',
        status: randomStatus === 'COMPLETED' ? 'COMPLETED' : 
                randomStatus === 'IN_PROGRESS' ? 'IN_PROGRESS' : 'PENDING',
        executed_ts: randomStatus === 'COMPLETED' ? new Date().toISOString() : undefined
      },
      {
        id: 'action_2', 
        action_type: 'SET_CSNID',
        status: randomStatus === 'COMPLETED' ? 'COMPLETED' : 'PENDING',
        executed_ts: randomStatus === 'COMPLETED' ? new Date().toISOString() : undefined
      }
    ];

    const completedActions = mockActions.filter(action => action.status === 'COMPLETED').length;
    const progress = (completedActions / mockActions.length) * 100;

    return NextResponse.json({
      workflow_id: workflowId,
      status: randomStatus,
      progress: Math.round(progress),
      current_action: randomStatus === 'IN_PROGRESS' ? 'Updating ERP records' : undefined,
      error_message: randomStatus === 'FAILED' ? 'Failed to connect to ERP system' : undefined,
      completed_actions: completedActions,
      total_actions: mockActions.length,
      estimated_completion: randomStatus === 'IN_PROGRESS' ? 
        new Date(Date.now() + 5 * 60 * 1000).toISOString() : undefined
    });

  } catch (error) {
    console.error('RPA status check error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to get RPA status',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
