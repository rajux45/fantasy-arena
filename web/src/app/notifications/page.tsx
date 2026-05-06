'use client';

import { useState } from 'react';

import { Nav } from '@/components/Nav';

interface Note {
  id: string;
  title: string;
  body: string;
  ts: string;
  unread: boolean;
}

const SAMPLE: Note[] = [
  { id: '1', title: 'Match starting in 1 hour', body: 'IPL: MI vs CSK. Lock your team before 7:30pm.', ts: '2 min ago', unread: true },
  { id: '2', title: 'Contest joined', body: 'You joined "₹10 Mega" with team "Rohit XI".', ts: '15 min ago', unread: true },
  { id: '3', title: 'Weekly bonus credited', body: '₹100 added to your bonus pocket.', ts: '1 day ago', unread: false },
];

export default function NotificationsPage() {
  const [notes, setNotes] = useState<Note[]>(SAMPLE);
  const markAll = () => setNotes(notes.map((n) => ({ ...n, unread: false })));
  return (
    <>
      <Nav />
      <main className="mx-auto max-w-2xl px-4 py-8">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Notifications</h1>
          <button onClick={markAll} className="btn-secondary text-sm">Mark all read</button>
        </div>
        <div className="mt-6 space-y-3">
          {notes.map((n) => (
            <div
              key={n.id}
              className={`card ${n.unread ? 'border-brand-700/50' : ''}`}
            >
              <div className="flex items-start justify-between">
                <h2 className="font-semibold">{n.title}</h2>
                <span className="text-xs text-slate-500">{n.ts}</span>
              </div>
              <p className="mt-1 text-sm text-slate-300">{n.body}</p>
              {n.unread ? <span className="pill mt-2 bg-brand-700 text-white">New</span> : null}
            </div>
          ))}
        </div>
      </main>
    </>
  );
}
