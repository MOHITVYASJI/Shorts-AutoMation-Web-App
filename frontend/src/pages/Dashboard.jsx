import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Video, Users, TrendingUp, Calendar } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-8" data-testid="dashboard-container">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Welcome back, {user?.full_name}!</h1>
        <p className="text-slate-400">Here's what's happening with your content today</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm" data-testid="total-videos-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Total Videos</CardTitle>
            <Video className="h-4 w-4 text-indigo-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">0</div>
            <p className="text-xs text-slate-400 mt-1">No videos yet</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm" data-testid="total-views-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Total Views</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">0</div>
            <p className="text-xs text-slate-400 mt-1">Start creating content</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm" data-testid="connected-accounts-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Connected Accounts</CardTitle>
            <Users className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">0</div>
            <p className="text-xs text-slate-400 mt-1">Connect your platforms</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm" data-testid="scheduled-posts-card">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Scheduled Posts</CardTitle>
            <Calendar className="h-4 w-4 text-orange-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">0</div>
            <p className="text-xs text-slate-400 mt-1">No scheduled posts</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-white">Quick Actions</CardTitle>
            <CardDescription className="text-slate-400">Get started with AutoShorts AI</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 border border-slate-800 rounded-lg hover:border-indigo-600 transition-colors cursor-pointer">
              <h3 className="font-medium text-white mb-1">Create Your First Video</h3>
              <p className="text-sm text-slate-400">Use AI to generate engaging short-form content</p>
            </div>
            <div className="p-4 border border-slate-800 rounded-lg hover:border-indigo-600 transition-colors cursor-pointer">
              <h3 className="font-medium text-white mb-1">Connect Social Accounts</h3>
              <p className="text-sm text-slate-400">Link your YouTube, Instagram, and Facebook</p>
            </div>
            <div className="p-4 border border-slate-800 rounded-lg hover:border-indigo-600 transition-colors cursor-pointer">
              <h3 className="font-medium text-white mb-1">View Analytics</h3>
              <p className="text-sm text-slate-400">Track your content performance</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-white">Recent Activity</CardTitle>
            <CardDescription className="text-slate-400">Your latest actions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">No recent activity</p>
              <p className="text-sm text-slate-500 mt-2">Start creating content to see your activity here</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;