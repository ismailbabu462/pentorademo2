import React from 'react';
import { Check, Star, Gem, Shield, Target, Users } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import api from '../lib/api';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';

const FeatureItem = ({ children }) => (
  <div className="flex items-start gap-2">
    <Check className="w-4 h-4 text-green-500 mt-0.5" />
    <span className="text-sm text-muted-foreground">{children}</span>
  </div>
);

const PricingPage = () => {
  const { tier, isSubscriptionActive, refreshTrigger, user } = useAuth();
  
  // Elite kullanıcı kontrolü
  const isEliteUser = (user?.tier || tier) === 'elite';

  // Lemon Squeezy checkout URLs
  const lemonSqueezyUrls = {
    'professional-monthly': 'https://pentorasec.lemonsqueezy.com/buy/1204da81-f438-4337-be09-863e7bb80f18',
    'professional-yearly': 'https://pentorasec.lemonsqueezy.com/buy/bf0feeb3-82d4-4f74-ae21-fbcba078ccc2',
    'teams-monthly': 'https://pentorasec.lemonsqueezy.com/buy/cf1dc49d-de8f-4115-8cb4-639233931106',
    'teams-yearly': 'https://pentorasec.lemonsqueezy.com/buy/bb5bb6ff-f58b-4921-9335-912a1f88ee79',
  };

  const goToLemonSqueezyCheckout = (planId) => {
    const checkoutUrl = lemonSqueezyUrls[planId];
    if (checkoutUrl) {
      // Add redirect URL parameter for success page
      const url = new URL(checkoutUrl);
      url.searchParams.set('redirect_url', `${window.location.origin}/payment/success`);
      window.open(url.toString(), '_blank');
    } else {
      toast.error('Checkout URL not configured for this plan');
    }
  };

  const isCurrentPlan = (planTier) => {
    // Use user.tier if available, fallback to tier from context
    const currentTier = user?.tier || tier || 'essential';
    return currentTier === planTier && isSubscriptionActive();
  };

  const getButtonText = (planTier) => {
    if (isCurrentPlan(planTier)) {
      if (planTier === 'essential') {
        return 'You Already Have This';
      }
      return 'Your Current Plan';
    }
    return 'Upgrade Plan';
  };

  const getButtonVariant = (planTier) => {
    if (isCurrentPlan(planTier)) {
      return 'secondary';
    }
    return 'default';
  };

  // Elite kullanıcılar için özel component
  const EliteExclusiveMessage = () => (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-4xl mx-auto text-center">
        {/* Elite Badge */}
        <div className="flex items-center justify-center mb-8">
          <Badge className="px-6 py-3 text-lg bg-gradient-to-r from-red-600 to-orange-600 text-white border-none">
            <Gem className="w-6 h-6 mr-2" />
            ELITE MEMBER
          </Badge>
        </div>

        {/* Main Message */}
        <div className="space-y-8 mb-12">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight bg-gradient-to-r from-red-600 via-orange-600 to-pink-600 bg-clip-text text-transparent">
            The game has changed.
          </h1>
          
          <div className="space-y-6 text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            <p>
              With <span className="text-red-600 font-semibold">Elite membership</span>, you are no longer just a pentester, 
              but a <span className="text-orange-600 font-semibold">strategist</span> one step ahead.
            </p>
            
            <p>
              Uncover the <span className="text-pink-600 font-semibold">deepest vulnerabilities</span>.
            </p>
            
            <p className="text-2xl md:text-3xl font-semibold text-foreground">
              You are not alone in your mission.
            </p>
          </div>
        </div>

        {/* Elite Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <Card className="bg-gradient-to-br from-red-900/10 to-red-800/5 border-red-500/20 hover:border-red-500/40 transition-all duration-300">
            <CardContent className="p-8 text-center">
              <Shield className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-3 text-red-600">Advanced Arsenal</h3>
              <p className="text-muted-foreground">
                Zero-day modules, AI-powered vulnerability discovery, and automatic PoC generation at your fingertips.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-900/10 to-orange-800/5 border-orange-500/20 hover:border-orange-500/40 transition-all duration-300">
            <CardContent className="p-8 text-center">
              <Target className="w-12 h-12 text-orange-500 mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-3 text-orange-600">Unlimited Power</h3>
              <p className="text-muted-foreground">
                No limits on projects, users, or resources. Dedicated Elite server with unlimited CPU and 32GB RAM.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-pink-900/10 to-pink-800/5 border-pink-500/20 hover:border-pink-500/40 transition-all duration-300">
            <CardContent className="p-8 text-center">
              <Users className="w-12 h-12 text-pink-500 mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-3 text-pink-600">Elite Support</h3>
              <p className="text-muted-foreground">
                VIP support, special SLA, and direct access to the development team for custom integrations.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button 
            size="lg" 
            className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white px-8 py-4"
            onClick={() => window.open('https://x.com/PentoraSec', '_blank')}
          >
            <Gem className="w-5 h-5 mr-2" />
            Elite Support Portal
          </Button>
          
          <Button 
            size="lg" 
            variant="outline"
            className="border-red-500/50 text-red-600 hover:bg-red-500/10 px-8 py-4"
            onClick={() => window.open('https://x.com/PentoraSec', '_blank')}
          >
            Request Custom Features
          </Button>
        </div>
      </div>
    </div>
  );

  // Elite kullanıcılar için özel sayfa göster
  if (isEliteUser) {
    return <EliteExclusiveMessage />;
  }

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-foreground">
          Choose Your Plan and Level Up
        </h1>
        <p className="mt-3 text-muted-foreground">
          Choose the plan that fits your needs and take your pentest workflows to the next level.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        {/* Essential Plan */}
        <Card className={`relative flex flex-col h-full ${isCurrentPlan('essential') ? 'border-green-500 bg-green-50/10' : ''}`}>
          {isCurrentPlan('essential') && (
            <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 z-10">
              <Badge className="bg-green-500 text-white">Active</Badge>
            </div>
          )}
          <CardHeader>
            <CardTitle className="text-xl">Essential</CardTitle>
            <CardDescription>Great to get started</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 flex-grow">
            <div>
              <div className="text-3xl font-bold">$0</div>
            </div>
            <div className="space-y-2">
              <FeatureItem>3 Project Limit</FeatureItem>
              <FeatureItem>Essential Tools (Subfinder, Nmap, Gobuster)</FeatureItem>
              <FeatureItem>5s Tool Delay</FeatureItem>
              <FeatureItem>No Collaboration</FeatureItem>
            </div>
          </CardContent>
          <CardFooter className="mt-auto">
            <Button 
              disabled={true} 
              className="w-full" 
              variant={getButtonVariant('essential')}
            >
              {getButtonText('essential')}
            </Button>
          </CardFooter>
        </Card>

        {/* Professional Plan */}
        <Card className={`relative flex flex-col h-full ${isCurrentPlan('professional') ? 'border-green-500 bg-green-50/10' : 'border-primary/50'}`}>
          {isCurrentPlan('professional') ? (
            <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 z-10">
              <Badge className="bg-green-500 text-white">Active</Badge>
            </div>
          ) : (
            <div className="absolute -top-3 left-4 z-10">
              <Badge className="flex items-center gap-1"><Star className="w-3 h-3" /> Most Popular</Badge>
            </div>
          )}
          <CardHeader>
            <CardTitle className="text-xl">Professional</CardTitle>
            <CardDescription>For freelancers and professionals</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 flex-grow">
            <div className="space-y-2">
              <FeatureItem>10 Project Limit</FeatureItem>
              <FeatureItem>All Standard Tools</FeatureItem>
              <FeatureItem>3s Tool Delay</FeatureItem>
              <FeatureItem>Add Teammate (1 user)</FeatureItem>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-2 mt-auto">
            {!isCurrentPlan('professional') ? (
              <>
                <Button 
                  className="w-full" 
                  variant="default"
                  onClick={() => goToLemonSqueezyCheckout('professional-monthly')}
                >
                  $10 / Month
                </Button>
                <Button 
                  className="w-full" 
                  variant="outline"
                  onClick={() => goToLemonSqueezyCheckout('professional-yearly')}
                >
                  $100 / Year (Save 17%)
                </Button>
              </>
            ) : (
              <Button 
                className="w-full" 
                variant="secondary"
                disabled
              >
                Your Current Plan
              </Button>
            )}
          </CardFooter>
        </Card>

        {/* Teams Plan */}
        <Card className={`relative flex flex-col h-full ${isCurrentPlan('teams') ? 'border-green-500 bg-green-50/10' : ''}`}>
          {isCurrentPlan('teams') && (
            <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 z-10">
              <Badge className="bg-green-500 text-white">Active</Badge>
            </div>
          )}
          <CardHeader>
            <CardTitle className="text-xl">Teams</CardTitle>
            <CardDescription>For growing teams and collaboration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 flex-grow">
            <div className="space-y-2">
              <FeatureItem>Unlimited Projects</FeatureItem>
              <FeatureItem>Team Management (up to 5 users)</FeatureItem>
              <FeatureItem>All Tools & Zero Delay</FeatureItem>
              <FeatureItem>Priority Support</FeatureItem>
              <FeatureItem>Self-hosted Deployment Option</FeatureItem>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-2 mt-auto">
            {!isCurrentPlan('teams') ? (
              <>
                <Button 
                  className="w-full" 
                  variant="default"
                  onClick={() => goToLemonSqueezyCheckout('teams-monthly')}
                >
                  $50 / Month
                </Button>
                <Button 
                  className="w-full" 
                  variant="outline"
                  onClick={() => goToLemonSqueezyCheckout('teams-yearly')}
                >
                  $490 / Year (Save 18%)
                </Button>
              </>
            ) : (
              <Button 
                className="w-full" 
                variant="secondary"
                disabled
              >
                Your Current Plan
              </Button>
            )}
          </CardFooter>
        </Card>

        {/* Enterprise Plan */}
        <Card className="flex flex-col h-full">
          <CardHeader>
            <CardTitle className="text-xl">Enterprise</CardTitle>
            <CardDescription>Advanced security and control</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 flex-grow">
            <div>
              <div className="text-3xl font-bold">$1000 <span className="text-base font-normal text-muted-foreground">/ mo</span></div>
              <div className="text-xs text-muted-foreground">$9899 / yr</div>
            </div>
            <div className="space-y-2">
              <FeatureItem>Self-hosted Deployment (Unlimited)</FeatureItem>
              <FeatureItem>Advanced Security (RBAC, Audit Logs)</FeatureItem>
              <FeatureItem>Custom Integrations (CI/CD, API)</FeatureItem>
              <FeatureItem>20 User Support</FeatureItem>
              <FeatureItem>Early Access to New Features</FeatureItem>
            </div>
          </CardContent>
          <CardFooter className="mt-auto">
            <Button className="w-full" variant="outline">
              Contact Us
            </Button>
          </CardFooter>
        </Card>
      </div>

      {/* Elite Section */}
      <div className="mt-16">
        <Card className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border-purple-500/20">
          <CardHeader className="text-center pb-6">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Star className="w-8 h-8 text-yellow-500" />
              <CardTitle className="text-3xl font-bold">Elite Plan: Beyond Limits</CardTitle>
            </div>
            <CardDescription className="text-lg mb-6">
              The most powerful web pentesting and application tools with AI-powered analysis and zero-day research capabilities.
            </CardDescription>
            <Button 
              variant="secondary" 
              size="lg"
              onClick={() => window.open('https://x.com/PentoraSec', '_blank')}
              className="mb-8"
            >
              Talk to Sales
            </Button>
          </CardHeader>
          
          <CardContent className="space-y-8">
            {/* Core Features */}
            <div>
              <h3 className="text-xl font-semibold mb-4 text-foreground">Core Features</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FeatureItem>The most powerful web pentesting and application tools</FeatureItem>
                <FeatureItem>Specially developed AI assistant</FeatureItem>
                <FeatureItem>Special logs page for Zero-Day Exploit guidance</FeatureItem>
                <FeatureItem>AI-powered tool output analysis</FeatureItem>
                <FeatureItem>CVE calculator</FeatureItem>
                <FeatureItem>Elite Package – Local Docker Limits</FeatureItem>
              </div>
            </div>

            {/* User / Project Limits */}
            <div>
              <h3 className="text-xl font-semibold mb-4 text-foreground">User / Project Limits</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FeatureItem>Unlimited projects</FeatureItem>
                <FeatureItem>Unlimited user support</FeatureItem>
                <FeatureItem>Multi-tenant support (multiple organizations/teams can work on the same installation)</FeatureItem>
              </div>
            </div>

            {/* Module / Tool Access */}
            <div>
              <h3 className="text-xl font-semibold mb-4 text-foreground">Module / Tool Access</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FeatureItem>All Enterprise tools + special Zero-Day modules / advanced exploit integrations</FeatureItem>
                <FeatureItem>AI-powered vulnerability discovery and automatic PoC generation</FeatureItem>
                <FeatureItem>Full API access + third-party integrations (Jira, ServiceNow, Splunk, etc.)</FeatureItem>
              </div>
            </div>

            {/* Performance / Resource Limits */}
            <div>
              <h3 className="text-xl font-semibold mb-4 text-foreground">Performance / Resource Limits</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FeatureItem>Dedicated Elite Server: CPU: Unlimited</FeatureItem>
                <FeatureItem>RAM: 32GB</FeatureItem>
                <FeatureItem>Runtime: Unlimited (persistent containers)</FeatureItem>
              </div>
            </div>

            {/* Functional Limits */}
            <div>
              <h3 className="text-xl font-semibold mb-4 text-foreground">Functional Limits</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FeatureItem>CI/CD integration: All platforms + custom pipeline scripts</FeatureItem>
                <FeatureItem>Team collaboration: Multi-org management, granular permissions, LDAP/SAML integration</FeatureItem>
                <FeatureItem>Reporting: All formats + real-time dashboard export + SIEM integration</FeatureItem>
              </div>
            </div>

            {/* Security / Management */}
            <div>
              <h3 className="text-xl font-semibold mb-4 text-foreground">Security / Management</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FeatureItem>Full audit & forensics records</FeatureItem>
                <FeatureItem>Special security layer (e.g., hardware-based encryption, HSM integration)</FeatureItem>
                <FeatureItem>VIP support & special SLA</FeatureItem>
                <FeatureItem>Hardware-based licensing option</FeatureItem>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PricingPage;


