#!/usr/bin/env python3
"""
auto_sync_amocrm.py — Прямая синхронизация AmoCRM -> Supabase.
Запускается вручную или по расписанию (cron).
Стягивает последние измененные сделки (100-250 штук) и заливает в Supabase за 1 секунду.
"""
import os
import sys
import json
import time
import datetime
import urllib.request
from urllib.parse import unquote_plus
from upload_to_supabase import pk, get_domain, clean_str, STATUS_WON_ID, STATUS_LOST_ID, UNSET, load_env

load_env()

AMOCRM_TOKEN = os.environ.get('AMOCRM_TOKEN')
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://upeqrwqhdnmccyymugej.supabase.co')
SECRET_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

def sync_now(limit=250):
    if not AMOCRM_TOKEN or not SECRET_KEY:
        print("Ошибка: AMOCRM_TOKEN или SUPABASE_SERVICE_KEY не заданы в .env")
        return 0

    t0 = time.time()
    url = f"https://janamen.amocrm.ru/api/v4/leads?order[updated_at]=desc&limit={limit}"
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {AMOCRM_TOKEN}'})
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Ошибка запроса к AmoCRM: {e}")
        return 0

    leads = data.get('_embedded', {}).get('leads', [])
    if not leads:
        print("Сделок не найдено.")
        return 0

    rows = []
    for d in leads:
        created_at = d.get('created_at') or 0
        created_at_iso = datetime.datetime.fromtimestamp(created_at).isoformat() if created_at else None
        closed_at = d.get('closed_at') or 0
        closed_at_iso = datetime.datetime.fromtimestamp(closed_at).isoformat() if closed_at else None

        st_id = d.get('status_id') or 0
        won = (st_id == STATUS_WON_ID)
        lost = (st_id == STATUS_LOST_ID)
        price = float(d.get('price') or 0)

        cf = {c['field_id']: str(c['values'][0]['value']).strip() for c in (d.get('custom_fields_values') or []) if c.get('values')}
        page = cf.get(849891) or cf.get(833007) or ''
        q = {}
        if '?' in page:
            for kv in page.split('?', 1)[1].split('#')[0].split('&'):
                if '=' in kv:
                    a, b = kv.split('=', 1)
                    if a.lower().startswith('utm_'):
                        q[a.lower()] = unquote_plus(b).strip()

        g = lambda fid, key: (cf.get(fid) or q.get(key) or '').strip()
        src = g(679639, 'utm_source') or 'direct/none'
        med = g(679635, 'utm_medium') or 'none'
        cmp_ = g(679637, 'utm_campaign') or 'none'
        cnt = g(679633, 'utm_content') or 'none'
        trm = g(679641, 'utm_term') or 'none'
        uid = g(833139, 'utm_id') or 'none'

        tags = [str(t.get('name', '')) for t in (d.get('_embedded') or {}).get('tags') or []]
        is_wa_aytym = any('9828' in t for t in tags) or ('iwa-9828' in page.lower()) or ('9828' in page.lower())

        p = pk(page)
        dom = get_domain(p)
        path = p.replace(dom, '').split('#')[0] or '/' if dom != 'other' else p
        if is_wa_aytym:
            med = 'Айтым Берикович - органика'
            if src in UNSET: src = 'whatsapp'
            if cmp_ in UNSET: cmp_ = 'iwa_9828'
            dom = 'janamen1.kz'
            path = '/iwa-9828'

        city = cf.get(855175) or cf.get(679621) or 'none'

        row = {
            'id': d['id'],
            'name': clean_str(d.get('name'), 'Без названия')[:255],
            'created_at': created_at_iso,
            'closed_at': closed_at_iso,
            'status_id': st_id,
            'pipeline_id': d.get('pipeline_id') or 0,
            'price': price,
            'is_won': won,
            'is_lost': lost,
            'utm_source': clean_str(src, 'direct/none'),
            'utm_medium': clean_str(med, 'none'),
            'utm_campaign': clean_str(cmp_, 'none'),
            'utm_content': clean_str(cnt, 'none'),
            'utm_term': clean_str(trm, 'none'),
            'utm_id': clean_str(uid, 'none'),
            'landing_page': clean_str(path if path.startswith('/') else '/' + path, '/'),
            'referrer': clean_str(page, 'none')[:500],
            'city': clean_str(city, 'none')[:100],
            'tags': tags[:20],
            'updated_at': datetime.datetime.now().isoformat()
        }
        rows.append(row)

    s_headers = {
        'apikey': SECRET_KEY,
        'Authorization': f'Bearer {SECRET_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }
    s_req = urllib.request.Request(f'{SUPABASE_URL}/rest/v1/deals', data=json.dumps(rows).encode('utf-8'), headers=s_headers)
    with urllib.request.urlopen(s_req) as resp:
        pass

    elapsed = time.time() - t0
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Синхронизировано {len(rows)} сделок за {elapsed:.2f} сек!")
    return len(rows)

if __name__ == "__main__":
    count = sync_now()
