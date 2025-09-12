'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Package, AlertTriangle, FileText, Truck } from 'lucide-react';

// Mock data for charts
const waybillStatusData = [
  { name: 'In Transit', value: 45, color: '#3B82F6' },
  { name: 'Delivered', value: 30, color: '#10B981' },
  { name: 'Pending', value: 15, color: '#F59E0B' },
  { name: 'Cancelled', value: 10, color: '#EF4444' },
];

const monthlyOperationsData = [
  { month: 'Jan', loading: 120, offloading: 115 },
  { month: 'Feb', loading: 135, offloading: 130 },
  { month: 'Mar', loading: 150, offloading: 145 },
  { month: 'Apr', loading: 140, offloading: 135 },
  { month: 'May', loading: 160, offloading: 155 },
  { month: 'Jun', loading: 170, offloading: 165 },
];

const anomalyTrendData = [
  { month: 'Jan', anomalies: 25, resolved: 20 },
  { month: 'Feb', anomalies: 30, resolved: 28 },
  { month: 'Mar', anomalies: 35, resolved: 32 },
  { month: 'Apr', anomalies: 28, resolved: 26 },
  { month: 'May', anomalies: 32, resolved: 30 },
  { month: 'Jun', anomalies: 40, resolved: 38 },
];

const assetUtilizationData = [
  { asset: 'Railcars', active: 85, inactive: 15 },
  { asset: 'Locomotives', active: 92, inactive: 8 },
  { asset: 'Containers', active: 78, inactive: 22 },
];

const performanceMetrics = [
  {
    title: 'On-Time Delivery',
    value: '94.2%',
    change: '+2.1%',
    trend: 'up',
    icon: TrendingUp,
    color: 'text-green-600',
  },
  {
    title: 'Anomaly Resolution',
    value: '87.5%',
    change: '+5.3%',
    trend: 'up',
    icon: TrendingUp,
    color: 'text-green-600',
  },
  {
    title: 'Asset Utilization',
    value: '82.1%',
    change: '-1.2%',
    trend: 'down',
    icon: TrendingDown,
    color: 'text-red-600',
  },
  {
    title: 'Contract Compliance',
    value: '96.8%',
    change: '+0.8%',
    trend: 'up',
    icon: TrendingUp,
    color: 'text-green-600',
  },
];

export default function AnalyticsPage() {
  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-2">Comprehensive insights into your operations</p>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {performanceMetrics.map((metric) => (
          <Card key={metric.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {metric.title}
              </CardTitle>
              <metric.icon className={`h-4 w-4 ${metric.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
              <p className={`text-xs ${metric.color} flex items-center gap-1`}>
                {metric.trend === 'up' ? (
                  <TrendingUp className="h-3 w-3" />
                ) : (
                  <TrendingDown className="h-3 w-3" />
                )}
                {metric.change} from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="operations">Operations</TabsTrigger>
          <TabsTrigger value="anomalies">Anomalies</TabsTrigger>
          <TabsTrigger value="assets">Assets</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Waybill Status Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Waybill Status Distribution
                </CardTitle>
                <CardDescription>
                  Current status of all waybills
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={waybillStatusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {waybillStatusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Asset Utilization */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Truck className="h-5 w-5" />
                  Asset Utilization
                </CardTitle>
                <CardDescription>
                  Active vs inactive assets
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={assetUtilizationData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="asset" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="active" fill="#10B981" name="Active" />
                    <Bar dataKey="inactive" fill="#EF4444" name="Inactive" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="operations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                Monthly Operations Trend
              </CardTitle>
              <CardDescription>
                Loading and offloading operations over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={monthlyOperationsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="loading" stroke="#3B82F6" strokeWidth={2} name="Loading" />
                  <Line type="monotone" dataKey="offloading" stroke="#10B981" strokeWidth={2} name="Offloading" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="anomalies" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Anomaly Trends
              </CardTitle>
              <CardDescription>
                Anomaly detection and resolution over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={anomalyTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="anomalies" fill="#EF4444" name="Anomalies Detected" />
                  <Bar dataKey="resolved" fill="#10B981" name="Anomalies Resolved" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="assets" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Asset Performance</CardTitle>
                <CardDescription>
                  Key performance indicators for assets
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Average Utilization</span>
                    <Badge className="bg-green-100 text-green-800">85.2%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Maintenance Due</span>
                    <Badge className="bg-yellow-100 text-yellow-800">12 Assets</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Out of Service</span>
                    <Badge className="bg-red-100 text-red-800">3 Assets</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Asset Types</CardTitle>
                <CardDescription>
                  Distribution of asset types
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={assetUtilizationData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="asset" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="active" fill="#3B82F6" name="Active" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
