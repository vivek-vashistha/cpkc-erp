'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiService, type Operation } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { Search, Package, Plus, Eye, Clock, CheckCircle } from 'lucide-react';

export default function OperationsPage() {
  const [operations, setOperations] = useState<Operation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Since we don't have a getOperations endpoint, we'll simulate some data
    const mockOperations: Operation[] = [
      {
        id: 'OP001',
        timestamp: new Date().toISOString(),
        type: 'loading',
        waybillId: 'WB3001',
        carId: 'CP401237',
        location: 'Emerson Yard',
        crewMember: 'John Smith',
        override: false,
      },
      {
        id: 'OP002',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        type: 'offloading',
        waybillId: 'WB3002',
        carId: 'CP401238',
        location: 'Destination Yard',
        crewMember: 'Jane Doe',
        override: false,
        signature: 'JD_SIG_001',
      },
      {
        id: 'OP003',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        type: 'loading',
        waybillId: 'WB3003',
        carId: 'CP401239',
        location: 'Emerson Yard',
        crewMember: 'Bob Johnson',
        override: true,
      },
    ];

    setOperations(mockOperations);
    setLoading(false);
  }, []);

  const filteredOperations = operations.filter(operation => 
    operation.waybillId.toLowerCase().includes(searchTerm.toLowerCase()) ||
    operation.carId.toLowerCase().includes(searchTerm.toLowerCase()) ||
    operation.crewMember.toLowerCase().includes(searchTerm.toLowerCase()) ||
    operation.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const loadingOps = filteredOperations.filter(op => op.type === 'loading');
  const offloadingOps = filteredOperations.filter(op => op.type === 'offloading');
  const overrideOps = filteredOperations.filter(op => op.override);

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
            <h1 className="text-3xl font-bold text-gray-900">Operations</h1>
            <p className="text-gray-600 mt-2">Track loading and offloading operations</p>
          </div>
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Log Operation
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Operations
            </CardTitle>
            <Package className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{operations.length}</div>
            <p className="text-xs text-gray-500">All operations</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Loading Operations
            </CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{loadingOps.length}</div>
            <p className="text-xs text-gray-500">Cargo loading</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Offloading Operations
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{offloadingOps.length}</div>
            <p className="text-xs text-gray-500">Cargo offloading</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Override Operations
            </CardTitle>
            <Package className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{overrideOps.length}</div>
            <p className="text-xs text-gray-500">Manual overrides</p>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search operations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <Tabs defaultValue="all" className="space-y-6">
        <TabsList>
          <TabsTrigger value="all">All Operations</TabsTrigger>
          <TabsTrigger value="loading">Loading ({loadingOps.length})</TabsTrigger>
          <TabsTrigger value="offloading">Offloading ({offloadingOps.length})</TabsTrigger>
          <TabsTrigger value="overrides">Overrides ({overrideOps.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <Card>
            <CardHeader>
              <CardTitle>All Operations</CardTitle>
              <CardDescription>
                Complete operation history
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Operation ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Waybill</TableHead>
                    <TableHead>Car ID</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Crew Member</TableHead>
                    <TableHead>Override</TableHead>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredOperations.map((operation) => (
                    <TableRow key={operation.id}>
                      <TableCell className="font-medium">{operation.id}</TableCell>
                      <TableCell>
                        <Badge variant={operation.type === 'loading' ? 'default' : 'secondary'}>
                          {operation.type}
                        </Badge>
                      </TableCell>
                      <TableCell>{operation.waybillId}</TableCell>
                      <TableCell>{operation.carId}</TableCell>
                      <TableCell>{operation.location}</TableCell>
                      <TableCell>{operation.crewMember}</TableCell>
                      <TableCell>
                        {operation.override ? (
                          <Badge variant="destructive">Yes</Badge>
                        ) : (
                          <Badge variant="outline">No</Badge>
                        )}
                      </TableCell>
                      <TableCell>{formatDate(operation.timestamp)}</TableCell>
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

        <TabsContent value="loading">
          <Card>
            <CardHeader>
              <CardTitle>Loading Operations</CardTitle>
              <CardDescription>
                Cargo loading activities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Operation ID</TableHead>
                    <TableHead>Waybill</TableHead>
                    <TableHead>Car ID</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Crew Member</TableHead>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loadingOps.map((operation) => (
                    <TableRow key={operation.id}>
                      <TableCell className="font-medium">{operation.id}</TableCell>
                      <TableCell>{operation.waybillId}</TableCell>
                      <TableCell>{operation.carId}</TableCell>
                      <TableCell>{operation.location}</TableCell>
                      <TableCell>{operation.crewMember}</TableCell>
                      <TableCell>{formatDate(operation.timestamp)}</TableCell>
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

        <TabsContent value="offloading">
          <Card>
            <CardHeader>
              <CardTitle>Offloading Operations</CardTitle>
              <CardDescription>
                Cargo offloading activities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Operation ID</TableHead>
                    <TableHead>Waybill</TableHead>
                    <TableHead>Car ID</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Crew Member</TableHead>
                    <TableHead>Signature</TableHead>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {offloadingOps.map((operation) => (
                    <TableRow key={operation.id}>
                      <TableCell className="font-medium">{operation.id}</TableCell>
                      <TableCell>{operation.waybillId}</TableCell>
                      <TableCell>{operation.carId}</TableCell>
                      <TableCell>{operation.location}</TableCell>
                      <TableCell>{operation.crewMember}</TableCell>
                      <TableCell>
                        {operation.signature ? (
                          <Badge variant="outline">{operation.signature}</Badge>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </TableCell>
                      <TableCell>{formatDate(operation.timestamp)}</TableCell>
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

        <TabsContent value="overrides">
          <Card>
            <CardHeader>
              <CardTitle>Override Operations</CardTitle>
              <CardDescription>
                Operations that required manual override
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Operation ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Waybill</TableHead>
                    <TableHead>Car ID</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Crew Member</TableHead>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {overrideOps.map((operation) => (
                    <TableRow key={operation.id}>
                      <TableCell className="font-medium">{operation.id}</TableCell>
                      <TableCell>
                        <Badge variant={operation.type === 'loading' ? 'default' : 'secondary'}>
                          {operation.type}
                        </Badge>
                      </TableCell>
                      <TableCell>{operation.waybillId}</TableCell>
                      <TableCell>{operation.carId}</TableCell>
                      <TableCell>{operation.location}</TableCell>
                      <TableCell>{operation.crewMember}</TableCell>
                      <TableCell>{formatDate(operation.timestamp)}</TableCell>
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
