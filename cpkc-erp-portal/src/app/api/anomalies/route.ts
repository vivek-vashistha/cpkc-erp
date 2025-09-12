import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

const ANOMALIES_FILE_PATH = path.join(process.cwd(), 'data', 'anomalies.json');

// Ensure data directory exists
async function ensureDataDirectory() {
  const dataDir = path.dirname(ANOMALIES_FILE_PATH);
  try {
    await fs.access(dataDir);
  } catch {
    await fs.mkdir(dataDir, { recursive: true });
  }
}

// Read anomalies from file
async function readAnomalies() {
  try {
    await ensureDataDirectory();
    const data = await fs.readFile(ANOMALIES_FILE_PATH, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    // If file doesn't exist, return empty array
    return [];
  }
}

// Write anomalies to file
async function writeAnomalies(anomalies: any[]) {
  try {
    await ensureDataDirectory();
    await fs.writeFile(ANOMALIES_FILE_PATH, JSON.stringify(anomalies, null, 2));
    return true;
  } catch (error) {
    console.error('Failed to write anomalies file:', error);
    return false;
  }
}

// GET - Read all anomalies
export async function GET() {
  try {
    const anomalies = await readAnomalies();
    console.log('Read anomalies from file:', anomalies.length, 'items');
    return NextResponse.json({ items: anomalies, total: anomalies.length });
  } catch (error) {
    console.error('Failed to read anomalies:', error);
    return NextResponse.json({ error: 'Failed to read anomalies' }, { status: 500 });
  }
}

// POST - Save anomalies
export async function POST(request: NextRequest) {
  try {
    const { anomalies } = await request.json();
    
    if (!Array.isArray(anomalies)) {
      return NextResponse.json({ error: 'Anomalies must be an array' }, { status: 400 });
    }

    const success = await writeAnomalies(anomalies);
    
    if (success) {
      console.log('Saved anomalies to file:', anomalies.length, 'items');
      return NextResponse.json({ 
        success: true, 
        message: `Saved ${anomalies.length} anomalies to file`,
        count: anomalies.length 
      });
    } else {
      return NextResponse.json({ error: 'Failed to save anomalies' }, { status: 500 });
    }
  } catch (error) {
    console.error('Failed to save anomalies:', error);
    return NextResponse.json({ error: 'Failed to save anomalies' }, { status: 500 });
  }
}

// DELETE - Clear all anomalies OR delete specific anomaly by ID
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const anomalyId = searchParams.get('id');
    
    if (anomalyId) {
      // Delete specific anomaly by ID
      const anomalies = await readAnomalies();
      
      const initialLength = anomalies.length;
      const filteredAnomalies = anomalies.filter((anomaly: any) => anomaly.id !== anomalyId);
      
      if (filteredAnomalies.length === initialLength) {
        return NextResponse.json({ error: 'Anomaly not found' }, { status: 404 });
      }

      const success = await writeAnomalies(filteredAnomalies);
      
      if (success) {
        console.log('Deleted anomaly from file:', anomalyId);
        return NextResponse.json({ 
          success: true, 
          message: `Deleted anomaly ${anomalyId}`,
          deletedId: anomalyId
        });
      } else {
        return NextResponse.json({ error: 'Failed to delete anomaly' }, { status: 500 });
      }
    } else {
      // Clear all anomalies
      const success = await writeAnomalies([]);
      
      if (success) {
        console.log('Cleared all anomalies from file');
        return NextResponse.json({ 
          success: true, 
          message: 'All anomalies cleared from file' 
        });
      } else {
        return NextResponse.json({ error: 'Failed to clear anomalies' }, { status: 500 });
      }
    }
  } catch (error) {
    console.error('Failed to delete/clear anomalies:', error);
    return NextResponse.json({ error: 'Failed to delete/clear anomalies' }, { status: 500 });
  }
}

// PATCH - Update specific anomaly by ID
export async function PATCH(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const anomalyId = searchParams.get('id');
    
    if (!anomalyId) {
      return NextResponse.json({ error: 'Anomaly ID is required' }, { status: 400 });
    }
    
    const updates = await request.json();
    const anomalies = await readAnomalies();
    
    const anomalyIndex = anomalies.findIndex((anomaly: any) => anomaly.id === anomalyId);
    
    if (anomalyIndex === -1) {
      return NextResponse.json({ error: 'Anomaly not found' }, { status: 404 });
    }

    // Update the anomaly
    anomalies[anomalyIndex] = {
      ...anomalies[anomalyIndex],
      ...updates,
      updated_ts: new Date().toISOString()
    };

    const success = await writeAnomalies(anomalies);
    
    if (success) {
      console.log('Updated anomaly in file:', anomalyId);
      return NextResponse.json({ 
        success: true, 
        message: `Updated anomaly ${anomalyId}`,
        anomaly: anomalies[anomalyIndex]
      });
    } else {
      return NextResponse.json({ error: 'Failed to update anomaly' }, { status: 500 });
    }
  } catch (error) {
    console.error('Failed to update anomaly:', error);
    return NextResponse.json({ error: 'Failed to update anomaly' }, { status: 500 });
  }
}
