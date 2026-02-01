import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Youtube, Instagram, Facebook, Plus, Loader2, Check, AlertCircle, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Accounts = () => {
  const { token } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(null);
  const [disconnectingId, setDisconnectingId] = useState(null);
  const [showDisconnectDialog, setShowDisconnectDialog] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);

  const platforms = [
    {
      id: 'youtube',
      name: 'YouTube',
      icon: Youtube,
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
      description: 'Connect your YouTube channel to publish Shorts'
    },
    {
      id: 'instagram',
      name: 'Instagram',
      icon: Instagram,
      color: 'text-pink-500',
      bgColor: 'bg-pink-500/10',
      description: 'Connect your Instagram account to publish Reels'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: Facebook,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
      description: 'Connect your Facebook page to publish videos'
    }
  ];

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/platforms/accounts`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setAccounts(response.data.accounts || []);
    } catch (error) {
      console.error('Error fetching accounts:', error);
      toast.error('Failed to load connected accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (platformId) => {
    setConnecting(platformId);
    
    try {
      const response = await axios.get(`${API_URL}/api/platforms/${platformId}/auth-url`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (response.data.auth_url) {
        // Open OAuth popup
        const width = 600;
        const height = 700;
        const left = (window.screen.width - width) / 2;
        const top = (window.screen.height - height) / 2;
        
        const popup = window.open(
          response.data.auth_url,
          'OAuth',
          `width=${width},height=${height},left=${left},top=${top}`
        );

        // Poll for popup closure
        const pollTimer = setInterval(() => {
          if (popup.closed) {
            clearInterval(pollTimer);
            setConnecting(null);
            // Refresh accounts list
            fetchAccounts();
            toast.success(`${platformId.charAt(0).toUpperCase() + platformId.slice(1)} account connected!`);
          }
        }, 1000);
      }
    } catch (error) {
      console.error('Connection error:', error);
      const errorMessage = error.response?.data?.detail || error.message;
      
      if (error.response?.status === 503) {
        toast.warning(errorMessage);
      } else {
        toast.error(errorMessage || 'Failed to connect account');
      }
      setConnecting(null);
    }
  };

  const handleDisconnectClick = (account) => {
    setSelectedAccount(account);
    setShowDisconnectDialog(true);
  };

  const handleDisconnectConfirm = async () => {
    if (!selectedAccount) return;

    setDisconnectingId(selectedAccount.id);
    setShowDisconnectDialog(false);

    try {
      await axios.delete(`${API_URL}/api/platforms/accounts/${selectedAccount.id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      toast.success('Account disconnected successfully');
      fetchAccounts();
    } catch (error) {
      console.error('Disconnect error:', error);
      toast.error('Failed to disconnect account');
    } finally {
      setDisconnectingId(null);
      setSelectedAccount(null);
    }
  };

  const isConnected = (platformId) => {
    return accounts.some(account => account.platform === platformId && account.status === 'active');
  };

  const getConnectedAccount = (platformId) => {
    return accounts.find(account => account.platform === platformId && account.status === 'active');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="space-y-8" data-testid="accounts-page">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Connected Accounts</h1>
        <p className="text-slate-400">Manage your social media platform connections</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {platforms.map((platform) => {
          const connected = isConnected(platform.id);
          const account = getConnectedAccount(platform.id);
          const isConnectingThis = connecting === platform.id;
          const isDisconnectingThis = disconnectingId === account?.id;
          const PlatformIcon = platform.icon;

          return (
            <Card 
              key={platform.id} 
              className="border-slate-800 bg-slate-900/50 backdrop-blur-sm hover:border-slate-700 transition-colors"
              data-testid={`platform-card-${platform.id}`}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className={`p-3 rounded-lg ${platform.bgColor}`}>
                    <PlatformIcon className={`w-6 h-6 ${platform.color}`} />
                  </div>
                  {connected && (
                    <Badge className="bg-green-500/10 text-green-400 hover:bg-green-500/20" data-testid={`status-badge-${platform.id}`}>
                      <Check className="w-3 h-3 mr-1" />
                      Connected
                    </Badge>
                  )}
                </div>
                <CardTitle className="text-white mt-4">{platform.name}</CardTitle>
                <CardDescription className="text-slate-400">
                  {platform.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {connected ? (
                  <div className="space-y-3">
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-sm text-slate-400">Connected as</p>
                      <p className="text-white font-medium mt-1">{account.account_name || 'Unknown'}</p>
                    </div>
                    <Button
                      variant="destructive"
                      className="w-full"
                      onClick={() => handleDisconnectClick(account)}
                      disabled={isDisconnectingThis}
                      data-testid={`disconnect-button-${platform.id}`}
                    >
                      {isDisconnectingThis ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Disconnecting...
                        </>
                      ) : (
                        <>
                          <Trash2 className="w-4 h-4 mr-2" />
                          Disconnect
                        </>
                      )}
                    </Button>
                  </div>
                ) : (
                  <Button
                    className="w-full bg-indigo-600 hover:bg-indigo-700"
                    onClick={() => handleConnect(platform.id)}
                    disabled={isConnectingThis}
                    data-testid={`connect-button-${platform.id}`}
                  >
                    {isConnectingThis ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      <>
                        <Plus className="w-4 h-4 mr-2" />
                        Connect Account
                      </>
                    )}
                  </Button>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {accounts.length > 0 && (
        <Card className="border-slate-800 bg-slate-900/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-white">All Connected Accounts</CardTitle>
            <CardDescription className="text-slate-400">
              View and manage all your connected social media accounts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {accounts.map((account) => {
                const platform = platforms.find(p => p.id === account.platform);
                const PlatformIcon = platform?.icon || AlertCircle;
                
                return (
                  <div
                    key={account.id}
                    className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg border border-slate-800 hover:border-slate-700 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-lg ${platform?.bgColor || 'bg-slate-700'}`}>
                        <PlatformIcon className={`w-5 h-5 ${platform?.color || 'text-slate-400'}`} />
                      </div>
                      <div>
                        <p className="text-white font-medium">{account.account_name}</p>
                        <p className="text-sm text-slate-400">{platform?.name || account.platform}</p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                      onClick={() => handleDisconnectClick(account)}
                      disabled={disconnectingId === account.id}
                    >
                      {disconnectingId === account.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      <AlertDialog open={showDisconnectDialog} onOpenChange={setShowDisconnectDialog}>
        <AlertDialogContent className="bg-slate-900 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Disconnect Account?</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Are you sure you want to disconnect <span className="text-white font-medium">{selectedAccount?.account_name}</span>? 
              You won't be able to publish to this account until you reconnect it.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-slate-800 text-white hover:bg-slate-700 border-slate-700">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDisconnectConfirm}
              className="bg-red-600 hover:bg-red-700"
            >
              Disconnect
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Accounts;
