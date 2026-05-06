'use client';

import { useEffect, useState } from 'react';

/**
 * Tiny status bar that appears when the browser is offline. The PWA's offline
 * page already handles the case where navigation itself fails, but for an
 * already-loaded SPA the user needs an inline indicator that fetches will fail
 * until the connection comes back.
 */
export function OfflineBanner(): JSX.Element | null {
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const update = () => setOffline(!window.navigator.onLine);
    update();
    window.addEventListener('online', update);
    window.addEventListener('offline', update);
    return () => {
      window.removeEventListener('online', update);
      window.removeEventListener('offline', update);
    };
  }, []);

  if (!offline) return null;
  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed inset-x-0 top-0 z-50 bg-amber-500/90 px-4 py-2 text-center text-xs font-medium text-slate-900 backdrop-blur"
    >
      You&rsquo;re offline. Live scores, contests, and wallet are unavailable until you reconnect.
    </div>
  );
}
