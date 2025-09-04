import React, { createContext, useContext, useState, useEffect } from 'react';
import api, { getAuthToken, setAuthToken } from '../lib/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children, initialToken = null }) => {
  const [user, setUser] = useState(null);
  const [tier, setTier] = useState('essential');
  const [subscriptionValidUntil, setSubscriptionValidUntil] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [forceUpdate, setForceUpdate] = useState(0);
  const [isAIPanelOpen, setIsAIPanelOpen] = useState(false);
  const [aiContext, setAIContext] = useState(null);

  // Fetch user data from backend
  const fetchUserData = async () => {
    try {
      const token = getAuthToken();
      console.log('AuthContext: Token from localStorage:', token ? 'Present' : 'Missing');
      
      if (!token) {
        console.log('AuthContext: No token found, skipping user data fetch');
        setLoading(false);
        return;
      }

      console.log('AuthContext: Fetching user data with token...');
      const response = await api.get('/auth/me');
      const userData = response.data;
      
      setUser(userData);
      setTier(userData.tier || 'essential');
      setSubscriptionValidUntil(userData.subscription_valid_until);
      setRefreshTrigger(Date.now()); // Force re-render with timestamp
      setForceUpdate(prev => prev + 1); // Additional force update
    } catch (error) {
      console.error('AuthContext: Failed to fetch user data:', error);
      // If token is invalid, clear user data
      setUser(null);
      setTier('essential');
      setSubscriptionValidUntil(null);
    } finally {
      setLoading(false);
    }
  };

  // Update user data (for when tier changes)
  const updateUserData = (newUserData) => {
    console.log('AuthContext: updateUserData called with:', newUserData);
    setUser(newUserData);
    setTier(newUserData.tier || 'essential');
    setSubscriptionValidUntil(newUserData.subscription_valid_until);
    setRefreshTrigger(Date.now()); // Force re-render with timestamp
    setForceUpdate(prev => prev + 1); // Additional force update
    console.log('AuthContext: Updated tier to:', newUserData.tier || 'essential');
  };

  // Force refresh user data (useful after key activation)
  const forceRefreshUserData = async () => {
    console.log('AuthContext: forceRefreshUserData called');
    await fetchUserData();
  };

  // Check if subscription is active
  const isSubscriptionActive = () => {
    // Use user.tier if available, fallback to tier from context
    const currentTier = user?.tier || tier || 'essential';
    
    // Essential plan is always active (free)
    if (currentTier === 'essential') return true;
    
    if (!subscriptionValidUntil) return false;
    return new Date(subscriptionValidUntil) > new Date();
  };

  // Get days remaining in subscription
  const getDaysRemaining = () => {
    // Use user.tier if available, fallback to tier from context
    const currentTier = user?.tier || tier || 'essential';
    
    // Essential plan has unlimited days (free)
    if (currentTier === 'essential') return 999999;
    
    if (!subscriptionValidUntil) return 0;
    const now = new Date();
    const expiry = new Date(subscriptionValidUntil);
    const diffTime = expiry - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(0, diffDays);
  };

  // Initialize user data on app start
  useEffect(() => {
    // If we have an initial token, set it first
    if (initialToken) {
      console.log('AuthContext: Setting initial token from App.js');
      setAuthToken(initialToken);
    }
    
    // Debug: Check if token exists
    const token = getAuthToken();
    console.log('🔐 AuthContext: Token exists:', !!token);
    if (token) {
      console.log('🔐 AuthContext: Token preview:', token.substring(0, 20) + '...');
    }
    
    fetchUserData();
  }, [initialToken]);

  const value = {
    user,
    tier,
    subscriptionValidUntil,
    loading,
    fetchUserData,
    updateUserData,
    forceRefreshUserData, // Add force refresh function
    isSubscriptionActive,
    getDaysRemaining,
    refreshTrigger, // Include refresh trigger in context
    forceUpdate, // Include force update in context
    isAIPanelOpen,
    setIsAIPanelOpen,
    aiContext,
    setAIContext,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
