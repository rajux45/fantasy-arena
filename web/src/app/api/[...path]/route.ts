import { NextRequest, NextResponse } from 'next/server';

/**
 * Same-origin proxy to the backend API. Used for the live preview tunnel
 * because the browser cannot construct a fetch() with Basic-Auth credentials
 * embedded in the URL — but a server-side fetch from this route handler can.
 *
 * Set `API_PROXY_TARGET` to the upstream base URL (with `https://user:pw@host`
 * if needed) and `API_PROXY_BASIC` to a separately-supplied `user:password`
 * pair if you would rather the credentials live in an Authorization header.
 */

export const dynamic = 'force-dynamic';

const TARGET = process.env.API_PROXY_TARGET || 'http://localhost:8000';
const BASIC = process.env.API_PROXY_BASIC || '';

function buildUrl(target: string, segments: string[], search: string): { url: string; auth: string | null } {
  // If TARGET embeds credentials, strip them and emit an Authorization header.
  let auth: string | null = null;
  let cleanTarget = target;
  try {
    const u = new URL(target);
    if (u.username || u.password) {
      auth = 'Basic ' + Buffer.from(`${decodeURIComponent(u.username)}:${decodeURIComponent(u.password)}`).toString('base64');
      u.username = '';
      u.password = '';
      cleanTarget = u.toString().replace(/\/$/, '');
    } else {
      cleanTarget = target.replace(/\/$/, '');
    }
  } catch {
    cleanTarget = target.replace(/\/$/, '');
  }
  if (!auth && BASIC) {
    auth = 'Basic ' + Buffer.from(BASIC).toString('base64');
  }
  const path = segments.join('/');
  return { url: `${cleanTarget}/${path}${search}`, auth };
}

async function proxy(req: NextRequest, segments: string[]): Promise<Response> {
  const search = req.nextUrl.search ?? '';
  const { url, auth } = buildUrl(TARGET, segments, search);

  const headers = new Headers();
  // Forward selected client headers; never leak the cookie or host.
  for (const [k, v] of req.headers.entries()) {
    if (k === 'host' || k === 'cookie' || k === 'connection' || k === 'content-length') continue;
    headers.set(k, v);
  }
  if (auth) headers.set('authorization', auth);

  let body: BodyInit | undefined;
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    body = await req.arrayBuffer();
  }

  const upstream = await fetch(url, {
    method: req.method,
    headers,
    body,
    redirect: 'manual',
  });

  const respHeaders = new Headers(upstream.headers);
  // Strip hop-by-hop headers
  respHeaders.delete('content-encoding');
  respHeaders.delete('content-length');
  respHeaders.delete('transfer-encoding');
  respHeaders.delete('connection');

  return new NextResponse(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: respHeaders,
  });
}

type RouteCtx = { params: { path: string[] } };

export async function GET(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, ctx.params.path ?? []);
}
export async function POST(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, ctx.params.path ?? []);
}
export async function PUT(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, ctx.params.path ?? []);
}
export async function PATCH(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, ctx.params.path ?? []);
}
export async function DELETE(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, ctx.params.path ?? []);
}
export async function OPTIONS(req: NextRequest, ctx: RouteCtx) {
  return proxy(req, ctx.params.path ?? []);
}
