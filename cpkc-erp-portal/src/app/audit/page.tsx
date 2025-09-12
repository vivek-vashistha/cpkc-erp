'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiService, type AuditEntry } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { Search, History, User, Activity, Filter } from 'lucide-react';

export default function AuditPage() {
  const [auditEntries, setAuditEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Since we don't have a getAudit endpoint, we'll simulate some data
    const mockAuditEntries: AuditEntry[] = [
      {
        audit_id: 'AUD001',
        entity_type: 'ANOMALY',
        entity_id: 'ANOM-1001',
        action: 'AUTO_FIX_APPLIED',
        detail: 'Inserted missing empty event for waybill WB3001',
        timestamp: new Date().toISOString(),
        actor: 'BP_FIX_EXECUTOR',
      },
      {
        audit_id: 'AUD002',
        entity_type: 'WAYBILL',
        entity_id: 'WB3002',
        action: 'STATUS_UPDATED',
        detail: 'Waybill status changed from Pending to In Transit',
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        actor: 'SYSTEM',
      },
      {
        audit_id: 'AUD003',
        entity_type: 'OPERATION',
        entity_id: 'OP001',
        action: 'OPERATION_LOGGED',
        detail: 'Loading operation completed for waybill WB3001',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        actor: 'John Smith',
      },
      {
        audit_id: 'AUD004',
        entity_type: 'CONTRACT',
        entity_id: 'CTR2001',
        action: 'CONTRACT_MATCHED',
        detail: 'Contract CTR2001 matched to waybill WB3003',
        timestamp: new Date(Date.now() - 5400000).toISOString(),
        actor: 'SYSTEM',
      },
      {
        audit_id: 'AUD005',
        entity_type: 'ANOMALY',
        entity_id: 'ANOM-1002',
        action: 'MANUAL_RESOLUTION',
        detail: 'Anomaly manually resolved by operations team',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        actor: 'Jane Doe',
      },
    ];

    setAuditEntries(mockAuditEntries);
    setLoading(false);
  }, []);

  const filteredEntries = auditEntries.filter(entry => 
    entry.entity_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entry.entity_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entry.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entry.actor.toLowerCase().includes(searchTerm.toLowerCase()) ||
    entry.detail.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const entityTypes = [...new Set(auditEntries.map(entry => entry.entity_type))];
  const actions = [...new Set(auditEntries.map(entry => entry.action))];
  const actors = [...new Set(auditEntries.map(entry => entry.actor))];

  const recentEntries = filteredEntries.slice(0, 10);
  const systemEntries = filteredEntries.filter(entry => entry.actor === 'SYSTEM');
  const userEntries = filteredEntries.filter(entry => entry.actor !== 'SYSTEM');

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
            <h1 className="text-3xl font-bold text-gray-900">Audit Trail</h1>
            <p className="text-gray-600 mt-2">Track all system activities and changes</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search audit entries..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
            <Button variant="outline" className="flex items-center gap-2">
              <Filter className="h-4 w-4" />
              Filter
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Entries
            </CardTitle>
            <History className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{auditEntries.length}</div>
            <p className="text-xs text-gray-500">All audit entries</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              System Actions
            </CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemEntries.length}</div>
            <p className="text-xs text-gray-500">Automated actions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              User Actions
            </CardTitle>
            <User className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{userEntries.length}</div>
            <p className="text-xs text-gray-500">Manual actions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Entity Types
            </CardTitle>
            <History className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{entityTypes.length}</div>
            <p className="text-xs text-gray-500">Different entities</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="recent" className="space-y-6">
        <TabsList>
          <TabsTrigger value="recent">Recent Activity</TabsTrigger>
          <TabsTrigger value="system">System Actions</TabsTrigger>
          <TabsTrigger value="users">User Actions</TabsTrigger>
          <TabsTrigger value="all">All Entries</TabsTrigger>
        </TabsList>

        <TabsContent value="recent">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest 10 audit entries
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Entity Type</TableHead>
                    <TableHead>Entity ID</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Actor</TableHead>
                    <TableHead>Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {recentEntries.map((entry) => (
                    <TableRow key={entry.audit_id}>
                      <TableCell>{formatDate(entry.timestamp)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{entry.entity_type}</Badge>
                      </TableCell>
                      <TableCell className="font-medium">{entry.entity_id}</TableCell>
                      <TableCell>
                        <Badge className="bg-blue-100 text-blue-800">
                          {entry.action.replace(/_/g, ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {entry.actor === 'SYSTEM' ? (
                            <Activity className="h-4 w-4 text-blue-500" />
                          ) : (
                            <User className="h-4 w-4 text-green-500" />
                          )}
                          {entry.actor}
                        </div>
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {entry.detail}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system">
          <Card>
            <CardHeader>
              <CardTitle>System Actions</CardTitle>
              <CardDescription>
                Automated system activities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Entity Type</TableHead>
                    <TableHead>Entity ID</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {systemEntries.map((entry) => (
                    <TableRow key={entry.audit_id}>
                      <TableCell>{formatDate(entry.timestamp)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{entry.entity_type}</Badge>
                      </TableCell>
                      <TableCell className="font-medium">{entry.entity_id}</TableCell>
                      <TableCell>
                        <Badge className="bg-blue-100 text-blue-800">
                          {entry.action.replace(/_/g, ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {entry.detail}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users">
          <Card>
            <CardHeader>
              <CardTitle>User Actions</CardTitle>
              <CardDescription>
                Manual user activities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Entity Type</TableHead>
                    <TableHead>Entity ID</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {userEntries.map((entry) => (
                    <TableRow key={entry.audit_id}>
                      <TableCell>{formatDate(entry.timestamp)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{entry.entity_type}</Badge>
                      </TableCell>
                      <TableCell className="font-medium">{entry.entity_id}</TableCell>
                      <TableCell>
                        <Badge className="bg-green-100 text-green-800">
                          {entry.action.replace(/_/g, ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-green-500" />
                          {entry.actor}
                        </div>
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {entry.detail}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="all">
          <Card>
            <CardHeader>
              <CardTitle>All Audit Entries</CardTitle>
              <CardDescription>
                Complete audit trail
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Audit ID</TableHead>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Entity Type</TableHead>
                    <TableHead>Entity ID</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Actor</TableHead>
                    <TableHead>Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredEntries.map((entry) => (
                    <TableRow key={entry.audit_id}>
                      <TableCell className="font-medium">{entry.audit_id}</TableCell>
                      <TableCell>{formatDate(entry.timestamp)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{entry.entity_type}</Badge>
                      </TableCell>
                      <TableCell className="font-medium">{entry.entity_id}</TableCell>
                      <TableCell>
                        <Badge className={
                          entry.actor === 'SYSTEM' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-green-100 text-green-800'
                        }>
                          {entry.action.replace(/_/g, ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {entry.actor === 'SYSTEM' ? (
                            <Activity className="h-4 w-4 text-blue-500" />
                          ) : (
                            <User className="h-4 w-4 text-green-500" />
                          )}
                          {entry.actor}
                        </div>
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {entry.detail}
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
