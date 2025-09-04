import React, { useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import api from '../lib/api';
import { toast } from 'sonner';

const MockCheckoutPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const tier = searchParams.get('tier') || 'professional';
  const duration_days = Number(searchParams.get('duration_days') || 30);

  const planText = useMemo(() => {
    const pretty = tier.charAt(0).toUpperCase() + tier.slice(1);
    const per = duration_days === 365 ? 'yearly' : 'monthly';
    return `${pretty} plan (${per})`;
  }, [tier, duration_days]);

  const confirm = async () => {
    try {
      await api.post('/payments/mock-successful-payment', { tier, duration_days });
      toast.success('Mock payment succeeded. License key generated.');
      navigate('/payment/success');
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Mock payment failed');
    }
  };

  return (
    <div className="p-6 lg:p-10 max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Mock Checkout</CardTitle>
          <CardDescription>You are about to purchase: {planText}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 opacity-60">
            <div>
              <label className="text-sm text-muted-foreground">Card Number</label>
              <Input placeholder="4242 4242 4242 4242" disabled />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Expiry</label>
              <Input placeholder="12/34" disabled />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">CVC</label>
              <Input placeholder="123" disabled />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Name on Card</label>
              <Input placeholder="John Doe" disabled />
            </div>
          </div>
          <div className="flex justify-end">
            <Button onClick={confirm}>Confirm Payment (Simulation)</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MockCheckoutPage;


