/**
 * Device Fingerprinting System
 * Creates a unique device identifier based on browser characteristics
 */

export const generateDeviceFingerprint = () => {
  // Simplified fingerprinting for better compatibility
  const components = [];
  
  // Screen resolution and color depth
  components.push(`${screen.width}x${screen.height}x${screen.colorDepth}`);
  
  // Timezone
  components.push(Intl.DateTimeFormat().resolvedOptions().timeZone);
  
  // Language
  components.push(navigator.language);
  
  // Platform
  components.push(navigator.platform);
  
  // User agent (first 30 chars)
  components.push(navigator.userAgent.substring(0, 30));
  
  // Simple canvas fingerprint
  try {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('Device fingerprint', 2, 2);
    components.push(canvas.toDataURL().substring(0, 30));
  } catch (e) {
    components.push('canvas-error');
  }
  
  // Combine all components and create hash
  const fingerprint = components.join('|');
  
  // Simple hash function
  let hash = 0;
  for (let i = 0; i < fingerprint.length; i++) {
    const char = fingerprint.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  return Math.abs(hash).toString(36);
};

export const getDeviceInfo = () => {
  return {
    device_fingerprint: generateDeviceFingerprint(),
    device_name: getDeviceName(),
    device_type: 'web'
  };
};

const getDeviceName = () => {
  const userAgent = navigator.userAgent;
  
  if (userAgent.includes('Chrome')) {
    return 'Chrome Browser';
  } else if (userAgent.includes('Firefox')) {
    return 'Firefox Browser';
  } else if (userAgent.includes('Safari')) {
    return 'Safari Browser';
  } else if (userAgent.includes('Edge')) {
    return 'Edge Browser';
  } else {
    return 'Web Browser';
  }
};

export const storeDeviceInfo = (deviceInfo) => {
  try {
    localStorage.setItem('deviceInfo', JSON.stringify(deviceInfo));
  } catch (e) {
    console.warn('Could not store device info:', e);
  }
};

export const getStoredDeviceInfo = () => {
  try {
    const stored = localStorage.getItem('deviceInfo');
    return stored ? JSON.parse(stored) : null;
  } catch (e) {
    console.warn('Could not retrieve device info:', e);
    return null;
  }
};
