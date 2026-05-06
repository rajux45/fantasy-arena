import Link from 'next/link';

export function Nav() {
  return (
    <nav className="sticky top-0 z-30 border-b border-slate-800 bg-slate-950/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold">
          <span aria-hidden className="rounded-md bg-brand-600 px-2 py-0.5 text-sm">FA</span>
          Fantasy Arena
        </Link>
        <div className="flex items-center gap-4 text-sm text-slate-300">
          <Link href="/lobby" className="hover:text-white">Lobby</Link>
          <Link href="/casino" className="hover:text-white">Casino</Link>
          <Link href="/wallet" className="hover:text-white">Wallet</Link>
          <Link href="/profile" className="hover:text-white">Profile</Link>
          <Link href="/auth/login" className="btn-primary text-sm">Log in</Link>
        </div>
      </div>
    </nav>
  );
}
