import { NextResponse } from 'next/server';
import { saveVideoErrorLog, detectDevice } from '../../../../lib/supabaseAdmin';

export const dynamic = 'force-dynamic';

export async function POST(req) {
  try {
    const body = await req.json().catch(() => ({}));
    const ua = req.headers.get('user-agent') || body.user_agent || '';
    const device = body.device || detectDevice(ua);

    await saveVideoErrorLog({
      slug: body.slug || '',
      ep: String(body.ep || ''),
      title: body.title || '',
      error_type: body.error_type || 'UNKNOWN',
      http_status: body.http_status || null,
      stream_url: body.stream_url || '',
      error_message: body.error_message || '',
      details: body.details || {},
      device: device,
      user_agent: ua
    });

    return NextResponse.json({ ok: true });
  } catch (err) {
    return NextResponse.json({ ok: false, error: err.message }, { status: 400 });
  }
}
