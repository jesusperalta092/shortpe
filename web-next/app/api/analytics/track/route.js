import { NextResponse } from 'next/server';
import { saveEvent, hashVisitor, detectDevice, detectOS, detectBrowser, getCountryDetails } from '../../../../lib/supabaseAdmin';

export const dynamic = 'force-dynamic';

export async function POST(req) {
  try {
    const body = await req.json().catch(() => ({}));
    const ip = req.headers.get('cf-connecting-ip') || req.headers.get('x-forwarded-for')?.split(',')[0].trim() || '127.0.0.1';
    const ua = req.headers.get('user-agent') || '';
    const referer = req.headers.get('referer') || '';

    // Extracción de geolocalización desde cabeceras Cloudflare / Vercel
    const countryCode = (req.headers.get('cf-ipcountry') || req.headers.get('x-vercel-ip-country') || 'PE').toUpperCase();
    const city = decodeURIComponent(req.headers.get('cf-ipcity') || req.headers.get('x-vercel-ip-city') || '');
    const region = decodeURIComponent(req.headers.get('cf-region') || req.headers.get('x-vercel-ip-country-region') || '');
    const countryInfo = getCountryDetails(countryCode);

    const visitorHash = hashVisitor(ip, ua);
    const device = detectDevice(ua);
    const os = detectOS(ua);
    const browser = detectBrowser(ua);

    await saveEvent({
      event_type: body.event_type || 'pageview',
      path: body.path || '',
      slug: body.slug || '',
      ep: String(body.ep || ''),
      title: body.title || '',
      visitor_hash: visitorHash,
      device: device,
      os: os,
      browser: browser,
      referer: referer,
      country: countryCode,
      country_name: countryInfo.name,
      city: city,
      region: region,
      network: body.network || (body.event_type === 'ad_click' ? body.title : ''),
      ad_step: body.step || 1
    });

    return NextResponse.json({ ok: true });
  } catch (err) {
    return NextResponse.json({ ok: false, error: err.message }, { status: 400 });
  }
}
