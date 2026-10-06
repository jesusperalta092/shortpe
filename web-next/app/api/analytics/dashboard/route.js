import { NextResponse } from 'next/server';
import { validateSession, getDashboardData } from '../../../../lib/supabaseAdmin';

export const dynamic = 'force-dynamic';

export async function GET(req) {
  try {
    const { searchParams } = new URL(req.url);
    const authHeader = req.headers.get('authorization') || '';
    let token = '';
    if (authHeader.startsWith('Bearer ')) {
      token = authHeader.slice(7).trim();
    }
    if (!token) {
      token = searchParams.get('token') || '';
    }

    if (!validateSession(token)) {
      return NextResponse.json({ ok: false, error: 'No autorizado' }, { status: 401 });
    }

    const days = parseInt(searchParams.get('days') || '7', 10) || 7;
    const data = await getDashboardData(days);

    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json({ ok: false, error: 'Error al consultar métricas' }, { status: 500 });
  }
}
