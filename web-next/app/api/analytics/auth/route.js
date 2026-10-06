import { NextResponse } from 'next/server';
import { verifyPin } from '../../../../lib/supabaseAdmin';

export const dynamic = 'force-dynamic';

export async function POST(req) {
  try {
    const body = await req.json().catch(() => ({}));
    const pin = body.pin || '';
    const ip = req.headers.get('cf-connecting-ip') || req.headers.get('x-forwarded-for')?.split(',')[0].trim() || '127.0.0.1';

    const result = verifyPin(pin, ip);
    if (result.ok) {
      return NextResponse.json({ ok: true, token: result.token });
    } else {
      return NextResponse.json({ ok: false, error: result.error }, { status: 401 });
    }
  } catch (err) {
    return NextResponse.json({ ok: false, error: 'Error interno del servidor' }, { status: 500 });
  }
}
