
import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

// Read env values safely — avoid referencing `process` directly in the browser
const getEnv = (viteName, nodeName) => {
  // vite (import.meta.env) takes precedence
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env[viteName]) {
    return import.meta.env[viteName];
  }

  // fallback to process.env only if `process` exists (server/CRA)
  if (typeof process !== 'undefined' && process.env && process.env[nodeName]) {
    return process.env[nodeName];
  }

  return undefined;
};

const firebaseConfig = {
  apiKey: getEnv('VITE_FIREBASE_API_KEY', 'REACT_APP_FIREBASE_API_KEY'),
  authDomain: getEnv('VITE_FIREBASE_AUTH_DOMAIN', 'REACT_APP_FIREBASE_AUTH_DOMAIN'),
  databaseURL: getEnv('VITE_FIREBASE_DATABASE_URL', 'REACT_APP_FIREBASE_DATABASE_URL'),
  projectId: getEnv('VITE_FIREBASE_PROJECT_ID', 'REACT_APP_FIREBASE_PROJECT_ID'),
  storageBucket: getEnv('VITE_FIREBASE_STORAGE_BUCKET', 'REACT_APP_FIREBASE_STORAGE_BUCKET'),
  messagingSenderId: getEnv('VITE_FIREBASE_MESSAGING_SENDER_ID', 'REACT_APP_FIREBASE_MESSAGING_SENDER_ID'),
  appId: getEnv('VITE_FIREBASE_APP_ID', 'REACT_APP_FIREBASE_APP_ID'),
  measurementId: getEnv('VITE_FIREBASE_MEASUREMENT_ID', 'REACT_APP_FIREBASE_MEASUREMENT_ID'),
};

// If databaseURL is missing but projectId exists, derive a reasonable default
if (!firebaseConfig.databaseURL && firebaseConfig.projectId) {
  // Most Realtime Database URLs follow this pattern; this is a best-effort fallback.
  firebaseConfig.databaseURL = `https://${firebaseConfig.projectId}.firebaseio.com`;
  // eslint-disable-next-line no-console
  console.warn('Firebase databaseURL was not set; using derived URL from projectId:', firebaseConfig.databaseURL);
}

// Initialize Firebase app
const app = initializeApp(firebaseConfig);

// Initialize database only if a databaseURL or projectId is available; catch errors so app doesn't crash
let database = null;
try {
  database = getDatabase(app);
} catch (err) {
  // eslint-disable-next-line no-console
  console.warn('Unable to initialize Firebase Realtime Database:', err && err.message ? err.message : err);
}

export { database };
export default app;

// Warn in dev if config appears missing
if (typeof window !== 'undefined') {
  const missing = Object.entries(firebaseConfig).filter(([, v]) => !v).map(([k]) => k);
  if (missing.length) {
    // Friendly developer warning — do not include secrets in production logs.
    // In Vite, set env vars in a .env file with VITE_ prefix (e.g. VITE_FIREBASE_API_KEY=...)
    // Then restart the dev server.
    // eslint-disable-next-line no-console
    console.warn('Firebase config missing keys:', missing.join(', '));
  }
}