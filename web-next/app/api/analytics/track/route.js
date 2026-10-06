import { NextResponse } from 'next/server';
import { saveEvent, hashVisitor, detectDevice } from '../../../../lib/supabaseAdmin';

export const dynamic = 'force-dynamic';

export async function POST(req) {
  try {
    const body = await req.json().catch(() => ({}));
    const ip = req.headers.get('cf-connecting-ip') || req.headers.get('x-forwarded-for')?.split(',')[0].trim() || '127.0.0.1';
    const ua = req.headers.get('user-agent') || '';
    const referer = req.headers.get('referer') || '';

    const visitorHash = hashVisitor(ip, ua);
    const device = detectDevice(ua);

    await saveEvent({
      event_type: body.event_type || 'pageview',
      path: body.path || '',
      slug: body.slug || '',
      ep: String(body.ep || ''),
      title: body.title || '',
      visitor_hash: visitorHash,
      device: device,
      referer: referer
    });

    return NextResponse.json({ ok: true });
  } catch (err) {
    return NextResponse.json({ ok: false, error: err.message }, { status: 400 });
  }
}
