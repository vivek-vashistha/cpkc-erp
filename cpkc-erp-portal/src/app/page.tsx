'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { apiService, type Waybill, type Anomaly } from '@/lib/api';
import { formatDate, getStatusColor } from '@/lib/utils';
import { 
  Package, 
  FileText, 
  AlertTriangle, 
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react';

export default function Dashboard() {
  const [waybills, setWaybills] = useState<Waybill[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [waybillsData, anomaliesData] = await Promise.all([
          apiService.getWaybills({ limit: 10 }),
          apiService.getAnomalies({ limit: 5 })
        ]);
        
        setWaybills(waybillsData.items);
        setAnomalies(anomaliesData.items);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const stats = [
    {
      name: 'Total Waybills',
      value: waybills.length,
      icon: Package,
      change: '+12%',
      changeType: 'positive' as const,
    },
    {
      name: 'Active Operations',
      value: waybills.filter(w => w.current_status === 'In Transit').length,
      icon: Clock,
      change: '+5%',
      changeType: 'positive' as const,
    },
    {
      name: 'Open Anomalies',
      value: anomalies.filter(a => a.status === 'NEW').length,
      icon: AlertTriangle,
      change: '-8%',
      changeType: 'negative' as const,
    },
    {
      name: 'Resolved Issues',
      value: anomalies.filter(a => a.status === 'RESOLVED').length,
      icon: CheckCircle,
      change: '+15%',
      changeType: 'positive' as const,
    },
  ];

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back! Here's what's happening with your operations.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {stat.name}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className={`text-xs ${
                stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
              }`}>
                {stat.change} from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Waybills */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Recent Waybills
            </CardTitle>
            <CardDescription>
              Latest waybill activities in your system
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {waybills.slice(0, 5).map((waybill) => (
                <div key={waybill.waybill_id} className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {waybill.waybill_id}
                    </p>
                    <p className="text-xs text-gray-500">
                      {waybill.origin_location} → {waybill.destination_location}
                    </p>
                    <p className="text-xs text-gray-400">
                      {formatDate(waybill.created_ts)}
                    </p>
                  </div>
                  <Badge className={getStatusColor(waybill.current_status)}>
                    {waybill.current_status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Anomalies */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Recent Anomalies
            </CardTitle>
            <CardDescription>
              Issues that need your attention
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {anomalies.slice(0, 5).map((anomaly) => (
                <div key={anomaly.id} className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {anomaly.type}
                    </p>
                    <p className="text-xs text-gray-500">
                      Waybill: {anomaly.waybill_id}
                    </p>
                    <p className="text-xs text-gray-400">
                      Confidence: {(anomaly.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                  <Badge className={getStatusColor(anomaly.status)}>
                    {anomaly.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
