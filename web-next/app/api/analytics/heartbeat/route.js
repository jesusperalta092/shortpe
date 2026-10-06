import { NextResponse } from 'next/server';
import { recordLiveHeartbeat } from '../../../../lib/supabaseAdmin';

export const dynamic = 'force-dynamic';

export async function POST(req) {
  try {
    const body = await req.json().catch(() => ({}));
    const ip = req.headers.get('cf-connecting-ip') || req.headers.get('x-forwarded-for')?.split(',')[0].trim() || '127.0.0.1';
    const ua = req.headers.get('user-agent') || '';

    recordLiveHeartbeat(
      Boolean(body.is_watching),
      body.slug || '',
      body.ep || '',
      body.title || '',
      ip,
      ua
    );

    return NextResponse.json({ ok: true });
  } catch (err) {
    return NextResponse.json({ ok: false, error: err.message }, { status: 400 });
  }
}
