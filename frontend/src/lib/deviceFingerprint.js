/**
 * Device Fingerprinting System
 * Creates a unique device identifier based on browser characteristics
 */

export const generateDeviceFingerprint = () => {
  const components = [];
  
  // Screen resolution and color depth
  components.push(`${screen.width}x${screen.height}x${screen.colorDepth}`);
  
  // Timezone
  components.push(Intl.DateTimeFormat().resolvedOptions().timeZone);
  
  // Language
  components.push(navigator.language);
  
  // Platform
  components.push(navigator.platform);
  
  // User agent (first 50 chars to avoid too long strings)
  components.push(navigator.userAgent.substring(0, 50));
  
  // Canvas fingerprint (if available)
  try {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('Device fingerprint', 2, 2);
    components.push(canvas.toDataURL().substring(0, 50));
  } catch (e) {
    components.push('canvas-error');
  }
  
  // WebGL fingerprint (if available)
  try {
    const gl = document.createElement('canvas').getContext('webgl');
    if (gl) {
      const renderer = gl.getParameter(gl.RENDERER);
      const vendor = gl.getParameter(gl.VENDOR);
      components.push(`${renderer}-${vendor}`.substring(0, 50));
    } else {
      components.push('no-webgl');
    }
  } catch (e) {
    components.push('webgl-error');
  }
  
  // Audio context fingerprint (if available)
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const analyser = audioContext.createAnalyser();
    oscillator.connect(analyser);
    oscillator.frequency.value = 1000;
    oscillator.start();
    const data = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(data);
    oscillator.stop();
    components.push(data.slice(0, 10).join(','));
  } catch (e) {
    components.push('audio-error');
  }
  
  // Combine all components and create hash
  const fingerprint = components.join('|');
  
  // Simple hash function (for demo purposes)
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
