'use client';

import { useEffect, useState } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

const DISMISS_KEY = 'fa.pwa.installDismissedAt';
const DISMISS_TTL_MS = 1000 * 60 * 60 * 24 * 14; // 14 days

function isStandalone(): boolean {
  if (typeof window === 'undefined') return false;
  if (window.matchMedia?.('(display-mode: standalone)').matches) return true;
  // iOS Safari
  return (window.navigator as { standalone?: boolean }).standalone === true;
}

/**
 * Renders nothing on its own. On Android Chrome / Edge it captures the
 * `beforeinstallprompt` event so we can defer the native A2HS dialog and show
 * a contextual install card. On iOS Safari we instead show a hint with the
 * Share-sheet steps because `beforeinstallprompt` is not supported there.
 *
 * Service-worker registration also happens here so the app installs and
 * receives push events even before the user opens any page that opts in.
 */
export function PWAInstall(): JSX.Element | null {
  const [installEvent, setInstallEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [showIosHint, setShowIosHint] = useState(false);
  const [hidden, setHidden] = useState(false);

  // Register the service worker once on mount.
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!('serviceWorker' in navigator)) return;
    const onLoad = () => {
      navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(() => {
        // SW failures should not break the page; silently ignore in prod.
      });
    };
    if (document.readyState === 'complete') onLoad();
    else window.addEventListener('load', onLoad, { once: true });
    return () => window.removeEventListener('load', onLoad);
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (isStandalone()) {
      setHidden(true);
      return;
    }
    const dismissedAt = Number(localStorage.getItem(DISMISS_KEY) ?? 0);
    if (dismissedAt && Date.now() - dismissedAt < DISMISS_TTL_MS) {
      setHidden(true);
      return;
    }

    const onPrompt = (e: Event) => {
      e.preventDefault();
      setInstallEvent(e as BeforeInstallPromptEvent);
    };
    window.addEventListener('beforeinstallprompt', onPrompt);

    const ua = window.navigator.userAgent;
    const isIos = /iPhone|iPad|iPod/i.test(ua) && !/(CriOS|FxiOS|EdgiOS)/i.test(ua);
    if (isIos && !isStandalone()) setShowIosHint(true);

    return () => window.removeEventListener('beforeinstallprompt', onPrompt);
  }, []);

  if (hidden) return null;
  if (!installEvent && !showIosHint) return null;

  const dismiss = () => {
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
    setHidden(true);
  };

  const install = async () => {
    if (!installEvent) return;
    try {
      await installEvent.prompt();
      const result = await installEvent.userChoice;
      if (result.outcome === 'accepted') setHidden(true);
      else dismiss();
    } finally {
      setInstallEvent(null);
    }
  };

  return (
    <div
      role="dialog"
      aria-label="Install Fantasy Arena"
      className="fixed inset-x-3 bottom-3 z-50 mx-auto max-w-md rounded-2xl border border-slate-700 bg-slate-900/95 p-4 shadow-2xl backdrop-blur"
    >
      <div className="flex items-start gap-3">
        <div className="grid size-10 place-items-center rounded-xl bg-gradient-to-br from-cyan-400 to-emerald-500 font-bold text-slate-900">
          FA
        </div>
        <div className="flex-1 text-sm">
          <div className="font-semibold text-slate-100">Install Fantasy Arena</div>
          {showIosHint ? (
            <p className="mt-1 text-slate-400">
              In Safari tap <span className="font-semibold">Share</span> →{' '}
              <span className="font-semibold">Add to Home Screen</span> to install the app.
            </p>
          ) : (
            <p className="mt-1 text-slate-400">
              Add to home screen for instant launch, push alerts, and offline access.
            </p>
          )}
          <div className="mt-3 flex gap-2">
            {installEvent ? (
              <button
                type="button"
                onClick={install}
                className="rounded-lg bg-gradient-to-r from-cyan-400 to-emerald-500 px-3 py-1.5 text-xs font-semibold text-slate-900"
              >
                Install
              </button>
            ) : null}
            <button
              type="button"
              onClick={dismiss}
              className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300"
            >
              Not now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
