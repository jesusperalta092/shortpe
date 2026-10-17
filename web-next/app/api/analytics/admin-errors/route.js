import { NextResponse } from 'next/server';
import { validateSession, getVideoErrorLogs, resolveVideoErrorLog } from '../../../../lib/supabaseAdmin';

export const dynamic = 'force-dynamic';

function getAuthToken(req) {
  const authHeader = req.headers.get('authorization') || '';
  if (authHeader.startsWith('Bearer ')) {
    return authHeader.slice(7).trim();
  }
  const { searchParams } = new URL(req.url);
  return searchParams.get('token') || '';
}

export async function GET(req) {
  try {
    const token = getAuthToken(req);
    if (!validateSession(token)) {
      return NextResponse.json({ ok: false, error: 'No autorizado' }, { status: 401 });
    }

    const data = await getVideoErrorLogs();
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json({ ok: false, error: err.message }, { status: 500 });
  }
}

export async function DELETE(req) {
  try {
    const token = getAuthToken(req);
    if (!validateSession(token)) {
      return NextResponse.json({ ok: false, error: 'No autorizado' }, { status: 401 });
    }

    const body = await req.json().catch(() => ({}));
    const id = body.id;
    if (!id) {
      return NextResponse.json({ ok: false, error: 'ID requerido' }, { status: 400 });
    }

    const result = await resolveVideoErrorLog(id);
    return NextResponse.json(result);
  } catch (err) {
    return NextResponse.json({ ok: false, error: err.message }, { status: 500 });
  }
}
