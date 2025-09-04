import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Shield, 
  Eye, 
  Lock, 
  Users, 
  FileText, 
  Mail,
  Calendar,
  CheckCircle,
  AlertTriangle,
  Heart,
  Target,
  Zap,
  Brain,
  Rocket
} from 'lucide-react';

const PolicyPage = () => {
  const [activeTab, setActiveTab] = useState('mission');

  const missionContent = (
    <div className="space-y-8">
      {/* Our Mission */}
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-2xl">
            <Target className="w-8 h-8 text-blue-500" />
            Our Mission
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg leading-relaxed text-muted-foreground">
            At PentoraSec, our mission is to put an end to the clutter and inefficiency that are the biggest problems faced by cybersecurity professionals and penetration testers. Instead of getting lost in dozens of terminals, disparate notebooks, and complex reports, we aim to consolidate the entire penetration testing lifecycle into a single, modern, fast, and secure platform.
          </p>
        </CardContent>
      </Card>

      {/* Our Story */}
      <Card className="border-l-4 border-l-purple-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-2xl">
            <Heart className="w-8 h-8 text-purple-500" />
            Our Story
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg leading-relaxed text-muted-foreground">
            PentoraSec was born as a solution to the challenges a solo developer has been experiencing for years in the cybersecurity field. The repetitive reconnaissance steps in each new project, the effort to combine the output of different tools, and finally, the process of transforming all this data into a meaningful report, sparked the idea that there had to be a better way. This platform is the product of this need; it's not an idea that emerged overnight, but rather an accumulation of experience in the field.
          </p>
        </CardContent>
      </Card>

      {/* Why PentoraSec */}
      <Card className="border-l-4 border-l-green-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-2xl">
            <Shield className="w-8 h-8 text-green-500" />
            Why PentoraSec?
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-1">
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                  <Lock className="w-6 h-6 text-blue-600" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Security-Focused Architecture</h3>
                <p className="text-muted-foreground">
                  We understand how sensitive our users' data is. That's why, thanks to our "Desktop Agent" model, all cybersecurity tools run on your computer. Sensitive commands are never run on our servers; we only securely manage your test results and notes.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-purple-600" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Modern and Fast Interface</h3>
                <p className="text-muted-foreground">
                  We offer a user experience that simplifies complex operations, eliminates distractions, and allows you to focus solely on your work.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                  <Brain className="w-6 h-6 text-green-600" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Smart Integrations</h3>
                <p className="text-muted-foreground">
                  It's not just a tool repository; it's also an intelligent assistant. With our AI-powered analytics, we aim to help you make sense of your scan output and generate reports faster.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Our Future Vision */}
      <Card className="border-l-4 border-l-orange-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-2xl">
            <Rocket className="w-8 h-8 text-orange-500" />
            Our Future Vision
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg leading-relaxed text-muted-foreground">
            Our journey is just beginning. We plan to continuously improve PentoraSec based on feedback from our community, add new tool integrations, and further enhance its AI capabilities.
          </p>
          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/10 dark:to-purple-900/10 rounded-lg">
            <p className="text-center font-medium text-foreground">
              Thank you for joining us on this journey.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const privacyContent = (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-2xl">
            <Shield className="w-8 h-8 text-blue-500" />
            PentoraSec Privacy Policy
          </CardTitle>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="w-4 h-4" />
            Last Updated: 03.09.2025
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-muted-foreground">
            This Privacy Policy explains how PentoraSec ("we," "us," or "our") collect, use, and share your personal information when you use our services ("Service").
          </p>

          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-500" />
                1. Information We Collect
              </h3>
              <div className="space-y-4 ml-7">
                <div>
                  <h4 className="font-medium mb-2">a. Account Information</h4>
                  <p className="text-muted-foreground">
                    When you register for our Service or activate a license key, we create a user ID to manage your membership. We may request additional information, such as an email address, for future payment and communication purposes. User passwords are not stored in our system.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-2">b. Project and Scan Data</h4>
                  <p className="text-muted-foreground">
                    Data you create, such as projects, goals, notes, and tool outputs, is stored on our servers to provide you with the service. This data is your property and protected by the highest confidentiality standards. The entire database is encrypted "at rest."
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-2">c. Usage Data</h4>
                  <p className="text-muted-foreground">
                    We may collect information about how you interact with our Service (IP address, browser type, pages visited). This information is used to improve and analyze our Service.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <Eye className="w-5 h-5 text-green-500" />
                2. How We Use Information
              </h3>
              <p className="text-muted-foreground mb-3">We use the information we collect to:</p>
              <ul className="space-y-2 ml-7">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">Provide, maintain, and improve our Service.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">Manage your subscription plan and process payments.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">Provide you with technical support.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">Comply with legal obligations.</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <Lock className="w-5 h-5 text-purple-500" />
                3. How We Share Information
              </h3>
              <p className="text-muted-foreground mb-3">
                We do not sell or rent your personal information to third parties. Your information may only be shared:
              </p>
              <ul className="space-y-2 ml-7">
                <li className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">With trusted payment providers, such as Stripe, for payment processing.</span>
                </li>
                <li className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">In response to a legal request or court order.</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <Shield className="w-5 h-5 text-red-500" />
                4. Data Security
              </h3>
              <p className="text-muted-foreground">
                We take the security of your data very seriously. We employ industry-standard security measures to protect data in transit (SSL/TLS) and data at rest (database encryption). Thanks to our "Desktop Agent" model, sensitive browsing scripts are never executed on our servers.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-500" />
                5. Changes to This Policy
              </h3>
              <p className="text-muted-foreground">
                We may update this Privacy Policy from time to time. Changes will be effective immediately upon posting on this page.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <Mail className="w-5 h-5 text-pink-500" />
                6. Contact
              </h3>
              <p className="text-muted-foreground">
                For questions regarding this Privacy Policy, please contact us at{' '}
                <a href="mailto:pentora59@gmail.com" className="text-blue-500 hover:underline">
                  pentora59@gmail.com
                </a>
                .
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const termsContent = (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-2xl">
            <FileText className="w-8 h-8 text-blue-500" />
            PentoraSec Terms of Use
          </CardTitle>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="w-4 h-4" />
            Last Updated: September 3, 2025
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-muted-foreground">
            Please read these Terms of Use ("Terms") carefully. By using our website and services at pentorasec.com (the "Service"), you agree to be legally bound by these Terms.
          </p>

          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-500" />
                1. Use of the Service
              </h3>
              <div className="space-y-4 ml-7">
                <div>
                  <h4 className="font-medium mb-2">a. Eligibility</h4>
                  <p className="text-muted-foreground">
                    You must be at least 18 years old to use our Service.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium mb-2">b. License</h4>
                  <p className="text-muted-foreground">
                    We grant you a limited, non-exclusive, non-transferable license to use the Service in accordance with these Terms.
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-500" />
                2. Ethical Use and Responsibility
              </h3>
              <div className="p-4 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="font-semibold text-red-800 dark:text-red-200 mb-2">
                  THIS IS THE MOST IMPORTANT ARTICLE.
                </p>
                <p className="text-red-700 dark:text-red-300">
                  You acknowledge and agree that you will only use our service on systems where you have clear and demonstrable authorization to conduct penetration testing. Testing on unauthorized systems is illegal and unethical. PentoraSec cannot be held responsible for any legal or financial damages that may arise from illegal or malicious use of the service. All responsibility rests with the user.
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <Shield className="w-5 h-5 text-green-500" />
                3. Membership Plans and Payments
              </h3>
              <p className="text-muted-foreground">
                Our service offers subscription plans with various features. The fee for your chosen plan will be automatically charged during the specified billing period (monthly/annual). You can cancel your subscription at any time, but refunds will not be provided.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <Lock className="w-5 h-5 text-purple-500" />
                4. Intellectual Property
              </h3>
              <p className="text-muted-foreground">
                The service itself, its software, brand, and interface are the property of PentoraSec. Data you create using the service, such as projects, notes, and scan results, is your property.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-500" />
                5. Termination of Service
              </h3>
              <p className="text-muted-foreground">
                In the event of a violation of these Terms, we reserve the right to suspend or terminate your account.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <Shield className="w-5 h-5 text-indigo-500" />
                6. Disclaimer of Warranties and Limitation of Liability
              </h3>
              <p className="text-muted-foreground">
                The Service is provided "as is." We do not warrant that the Service will be uninterrupted or error-free. We will not be liable for any direct or indirect damages arising from the use of the Service.
              </p>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <Mail className="w-5 h-5 text-pink-500" />
                7. Contact
              </h3>
              <p className="text-muted-foreground">
                For questions regarding these Terms, please contact us at{' '}
                <a href="mailto:pentora59@gmail.com" className="text-blue-500 hover:underline">
                  pentora59@gmail.com
                </a>
                .
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-foreground">
          PentoraSec Policies
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Our mission, privacy policy, and terms of service - everything you need to know about how we protect your data and operate our platform.
        </p>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="mission" className="flex items-center gap-2">
            <Target className="w-4 h-4" />
            Our Mission
          </TabsTrigger>
          <TabsTrigger value="privacy" className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Privacy Policy
          </TabsTrigger>
          <TabsTrigger value="terms" className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Terms of Service
          </TabsTrigger>
        </TabsList>

        <TabsContent value="mission" className="mt-6">
          {missionContent}
        </TabsContent>

        <TabsContent value="privacy" className="mt-6">
          {privacyContent}
        </TabsContent>

        <TabsContent value="terms" className="mt-6">
          {termsContent}
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <div className="text-center py-8 border-t border-border">
        <p className="text-muted-foreground">
          Questions? Contact us at{' '}
          <a href="mailto:pentora59@gmail.com" className="text-blue-500 hover:underline font-medium">
            pentora59@gmail.com
          </a>
        </p>
      </div>
    </div>
  );
};

export default PolicyPage;
