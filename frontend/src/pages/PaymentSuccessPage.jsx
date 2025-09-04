import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import api from '../lib/api';
import { toast } from 'sonner';

const PaymentSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const [licenseKey, setLicenseKey] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      console.log('Stripe session:', sessionId);
    }
    const fetchKey = async () => {
      try {
        const res = await api.get('/keys/get-latest-key-for-user');
        setLicenseKey(res.data?.key || '');
      } catch (e) {
        toast.error(e?.response?.data?.detail || 'Could not fetch license key');
      } finally {
        setLoading(false);
      }
    };
    fetchKey();
  }, [searchParams]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(licenseKey);
      toast.success('Key copied to clipboard');
    } catch (e) {
      toast.error('Copy failed');
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-10 max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Payment Received Successfully!</CardTitle>
          <CardDescription>To activate your membership, copy the key below and paste it into the "Key Activation" dialog.</CardDescription>
        </CardHeader>
        <CardContent>
          {licenseKey ? (
            <div className="flex gap-2">
              <input className="w-full px-3 py-2 rounded border bg-background" value={licenseKey} readOnly />
              <Button onClick={copy}>Copy</Button>
            </div>
          ) : (
            <p className="text-muted-foreground">No pending license key found for your account.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentSuccessPage;


