import type { MetadataRoute } from 'next';

const PUBLIC_ROUTES = [
  '/',
  '/lobby',
  '/casino',
  '/leaderboard',
  '/tournaments',
  '/promotions',
  '/winners',
  '/how-it-works',
  '/scoring-rules',
  '/provably-fair',
  '/responsible',
  '/legal',
  '/privacy',
  '/support',
  '/careers',
  '/auth/signup',
  '/auth/login',
];

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL || 'https://fantasy-arena.example.com';
  const now = new Date();
  return PUBLIC_ROUTES.map((route) => ({
    url: `${base}${route}`,
    lastModified: now,
    changeFrequency: route === '/lobby' ? 'hourly' : 'weekly',
    priority: route === '/' ? 1 : 0.7,
  }));
}
