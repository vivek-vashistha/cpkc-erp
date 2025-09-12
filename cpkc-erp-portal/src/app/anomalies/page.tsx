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
import { Search, AlertTriangle, CheckCircle, XCircle, Eye, Settings } from 'lucide-react';

export default function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        const data = await apiService.getAnomalies({ limit: 100 });
        setAnomalies(data.items);
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
      await apiService.updateAnomalyStatus(id, status);
      setAnomalies(prev => prev.map(anomaly => 
        anomaly.id === id ? { ...anomaly, status } : anomaly
      ));
    } catch (error) {
      console.error('Failed to update anomaly status:', error);
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
            <Button className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Auto-Fix
            </Button>
          </div>
        </div>
      </div>

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
                    <TableHead>ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Waybill</TableHead>
                    <TableHead>Car ID</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {newAnomalies.map((anomaly) => (
                    <TableRow key={anomaly.id}>
                      <TableCell className="font-medium">{anomaly.id}</TableCell>
                      <TableCell>
                        <Badge variant="destructive">{anomaly.type}</Badge>
                      </TableCell>
                      <TableCell>{anomaly.waybill_id}</TableCell>
                      <TableCell>{anomaly.car_id}</TableCell>
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
                          >
                            <CheckCircle className="h-4 w-4" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleStatusUpdate(anomaly.id, 'IGNORED')}
                          >
                            <XCircle className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
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
