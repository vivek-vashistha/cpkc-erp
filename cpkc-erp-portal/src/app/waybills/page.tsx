'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiService, type Waybill } from '@/lib/api';
import { formatDate, getStatusColor } from '@/lib/utils';
import { Search, Filter, Eye, Edit, Plus, MapPin, Navigation } from 'lucide-react';

export default function WaybillsPage() {
  const [waybills, setWaybills] = useState<Waybill[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    const fetchWaybills = async () => {
      try {
        console.log('Fetching waybills...');
        const data = await apiService.getWaybills({ limit: 100 });
        console.log('Waybills data received:', data);
        setWaybills(data.items || []);
      } catch (error) {
        console.error('Failed to fetch waybills:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWaybills();
  }, []);

  const filteredWaybills = waybills.filter(waybill => {
    const matchesSearch = waybill.waybill_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         waybill.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         waybill.commodity.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || waybill.current_status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const statuses = ['all', 'In Transit', 'Delivered', 'Pending', 'Cancelled'];

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
            <h1 className="text-3xl font-bold text-gray-900">Waybills</h1>
            <p className="text-gray-600 mt-2">Manage and track all waybill operations</p>
          </div>
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            New Waybill
          </Button>
        </div>
      </div>

      <Tabs defaultValue="all" className="space-y-6">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="all">All Waybills</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="pending">Pending</TabsTrigger>
          </TabsList>
          
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search waybills..."
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

        <TabsContent value="all" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Waybill List</CardTitle>
              <CardDescription>
                {filteredWaybills.length} waybills found
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Waybill ID</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead>
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        Origin
                      </div>
                    </TableHead>
                    <TableHead>
                      <div className="flex items-center gap-2">
                        <Navigation className="h-4 w-4" />
                        Destination
                      </div>
                    </TableHead>
                    <TableHead>Commodity</TableHead>
                    <TableHead>Weight</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredWaybills.length > 0 ? (
                    filteredWaybills.map((waybill) => (
                      <TableRow key={waybill.waybill_id}>
                        <TableCell className="font-medium">
                          {waybill.waybill_id}
                        </TableCell>
                        <TableCell>{waybill.customer_id}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <MapPin className="h-3 w-3 text-blue-500" />
                            <span className="font-medium text-blue-600">
                              {waybill.origin_location}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Navigation className="h-3 w-3 text-green-500" />
                            <span className="font-medium text-green-600">
                              {waybill.destination_location}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>{waybill.commodity}</TableCell>
                        <TableCell>{waybill.weight_tons} tons</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(waybill.current_status)}>
                            {waybill.current_status}
                          </Badge>
                        </TableCell>
                        <TableCell>{formatDate(waybill.created_ts)}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                        {loading ? 'Loading waybills...' : 'No waybills found'}
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="active">
          <Card>
            <CardHeader>
              <CardTitle>Active Waybills</CardTitle>
              <CardDescription>
                Waybills currently in transit
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                Active waybills will be displayed here
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="completed">
          <Card>
            <CardHeader>
              <CardTitle>Completed Waybills</CardTitle>
              <CardDescription>
                Successfully delivered waybills
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                Completed waybills will be displayed here
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pending">
          <Card>
            <CardHeader>
              <CardTitle>Pending Waybills</CardTitle>
              <CardDescription>
                Waybills awaiting processing
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                Pending waybills will be displayed here
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
