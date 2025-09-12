'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiService, type Anomaly } from '@/lib/api';
import { formatDate, getStatusColor } from '@/lib/utils';
import { Search, AlertTriangle, CheckCircle, XCircle, Eye, Settings, Trash2 } from 'lucide-react';

export default function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [waybillId, setWaybillId] = useState('');
  const [checkingAnomalies, setCheckingAnomalies] = useState(false);
  const [duplicateWarning, setDuplicateWarning] = useState('');

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
    if (confirm('Are you sure you want to delete this anomaly?')) {
      try {
        // Delete from file first
        const success = await apiService.deleteAnomalyFromFile(id);
        if (success) {
          // Update local state
          const updatedAnomalies = anomalies.filter(anomaly => anomaly.id !== id);
          setAnomalies(updatedAnomalies);
          console.log('Anomaly deleted:', id);
          // Clear duplicate warning if it was related to this deletion
          setDuplicateWarning('');
        }
      } catch (error) {
        console.error('Failed to delete anomaly:', error);
      }
    }
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
        id: `anomaly_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        waybill_id: anomaly.waybill_id,
        car_id: anomaly.car_id,
        csn_id: anomaly.csn_id,
        type: anomaly.type,
        confidence: anomaly.confidence,
        suggested_fix: anomaly.suggested_fix?.action || 'Manual review required',
        status: anomaly.status || 'NEW',
        created_ts: new Date().toISOString(),
        updated_ts: new Date().toISOString(),
        details: anomaly.details || '',
        needs_confirmation: anomaly.needs_confirmation || false
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
    <div className="p-6">
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
            <Button className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Auto-Fix
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

      <Tabs defaultValue="new" className="space-y-6">
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
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Type</TableHead>
                    <TableHead>Waybill</TableHead>
                    <TableHead>Car ID</TableHead>
                    <TableHead>Details</TableHead>
                    <TableHead>Suggested Fix</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {newAnomalies.map((anomaly) => (
                    <TableRow key={anomaly.id}>
                      <TableCell>
                        <Badge variant="destructive">{anomaly.type}</Badge>
                      </TableCell>
                      <TableCell className="font-medium">{anomaly.waybill_id}</TableCell>
                      <TableCell>{anomaly.car_id}</TableCell>
                      <TableCell>
                        <div className="max-w-xs">
                          <p className="text-sm text-gray-600 truncate" title={anomaly.details}>
                            {anomaly.details || 'No details available'}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs">
                          {anomaly.suggested_fix}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-red-500 h-2 rounded-full" 
                              style={{ width: `${anomaly.confidence * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm">{(anomaly.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </TableCell>
                      <TableCell>{formatDate(anomaly.created_ts)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleStatusUpdate(anomaly.id, 'RESOLVED')}
                            title="Mark as Resolved"
                          >
                            <CheckCircle className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleStatusUpdate(anomaly.id, 'IGNORED')}
                            title="Mark as Ignored"
                          >
                            <XCircle className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            title="View Details"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleDeleteAnomaly(anomaly.id)}
                            title="Delete Anomaly"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
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
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Waybill</TableHead>
                    <TableHead>Car ID</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Resolved</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {resolvedAnomalies.map((anomaly) => (
                    <TableRow key={anomaly.id}>
                      <TableCell className="font-medium">{anomaly.id}</TableCell>
                      <TableCell>
                        <Badge className="bg-green-100 text-green-800">{anomaly.type}</Badge>
                      </TableCell>
                      <TableCell>{anomaly.waybill_id}</TableCell>
                      <TableCell>{anomaly.car_id}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-500 h-2 rounded-full" 
                              style={{ width: `${anomaly.confidence * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm">{(anomaly.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </TableCell>
                      <TableCell>{formatDate(anomaly.updated_ts)}</TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
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
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Waybill</TableHead>
                    <TableHead>Car ID</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Ignored</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {ignoredAnomalies.map((anomaly) => (
                    <TableRow key={anomaly.id}>
                      <TableCell className="font-medium">{anomaly.id}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{anomaly.type}</Badge>
                      </TableCell>
                      <TableCell>{anomaly.waybill_id}</TableCell>
                      <TableCell>{anomaly.car_id}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-gray-500 h-2 rounded-full" 
                              style={{ width: `${anomaly.confidence * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm">{(anomaly.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </TableCell>
                      <TableCell>{formatDate(anomaly.updated_ts)}</TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
