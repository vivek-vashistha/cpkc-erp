'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { apiService, type Contract } from '@/lib/api';
import { formatDate, formatCurrency } from '@/lib/utils';
import { Search, FileCheck, Plus, Eye, Edit, DollarSign } from 'lucide-react';

export default function ContractsPage() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchContracts = async () => {
      try {
        const data = await apiService.getContracts({ limit: 100 });
        setContracts(data.items);
      } catch (error) {
        console.error('Failed to fetch contracts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchContracts();
  }, []);

  const filteredContracts = contracts.filter(contract => 
    contract.contract_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contract.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contract.commodity.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contract.origin_location.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contract.destination_location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const activeContracts = filteredContracts.filter(contract => {
    const now = new Date();
    const validFrom = new Date(contract.valid_from);
    const validTo = new Date(contract.valid_to);
    return now >= validFrom && now <= validTo;
  });

  const expiredContracts = filteredContracts.filter(contract => {
    const now = new Date();
    const validTo = new Date(contract.valid_to);
    return now > validTo;
  });

  const futureContracts = filteredContracts.filter(contract => {
    const now = new Date();
    const validFrom = new Date(contract.valid_from);
    return now < validFrom;
  });

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
            <h1 className="text-3xl font-bold text-gray-900">Contracts</h1>
            <p className="text-gray-600 mt-2">Manage customer contracts and pricing</p>
          </div>
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            New Contract
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Contracts
            </CardTitle>
            <FileCheck className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{contracts.length}</div>
            <p className="text-xs text-gray-500">All contracts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Active Contracts
            </CardTitle>
            <FileCheck className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeContracts.length}</div>
            <p className="text-xs text-gray-500">Currently valid</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Expired Contracts
            </CardTitle>
            <FileCheck className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{expiredContracts.length}</div>
            <p className="text-xs text-gray-500">Past validity</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Future Contracts
            </CardTitle>
            <FileCheck className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{futureContracts.length}</div>
            <p className="text-xs text-gray-500">Not yet active</p>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search contracts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Contracts Table */}
      <Card>
        <CardHeader>
          <CardTitle>Contract List</CardTitle>
          <CardDescription>
            {filteredContracts.length} contracts found
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Contract ID</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Route</TableHead>
                <TableHead>Commodity</TableHead>
                <TableHead>Base Rate</TableHead>
                <TableHead>Fuel Surcharge</TableHead>
                <TableHead>Valid Period</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredContracts.map((contract) => {
                const now = new Date();
                const validFrom = new Date(contract.valid_from);
                const validTo = new Date(contract.valid_to);
                const isActive = now >= validFrom && now <= validTo;
                const isExpired = now > validTo;
                const isFuture = now < validFrom;

                let status = 'Active';
                let statusColor = 'bg-green-100 text-green-800';
                
                if (isExpired) {
                  status = 'Expired';
                  statusColor = 'bg-red-100 text-red-800';
                } else if (isFuture) {
                  status = 'Future';
                  statusColor = 'bg-blue-100 text-blue-800';
                }

                return (
                  <TableRow key={contract.contract_id}>
                    <TableCell className="font-medium">
                      {contract.contract_id}
                    </TableCell>
                    <TableCell>{contract.customer_id}</TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>{contract.origin_location}</div>
                        <div className="text-gray-500">→ {contract.destination_location}</div>
                      </div>
                    </TableCell>
                    <TableCell>{contract.commodity}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-3 w-3" />
                        {contract.base_rate_per_ton}
                      </div>
                    </TableCell>
                    <TableCell>{contract.fuel_surcharge_pct}%</TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>{formatDate(contract.valid_from)}</div>
                        <div className="text-gray-500">to {formatDate(contract.valid_to)}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={statusColor}>
                        {status}
                      </Badge>
                    </TableCell>
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
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
