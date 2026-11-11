#!/usr/bin/env python3
"""
Скрипт миграции исторической базы сделок (36 484 сделок) в Supabase
с полным парсингом UTM и атрибуции.
"""
import json
import os
import re
import time
import urllib.request
from datetime import datetime
from urllib.parse import unquote_plus

# Чтение конфигурации из .env
def load_env():
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    os.environ.setdefault(k, v)

load_env()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://upeqrwqhdnmccyymugej.supabase.co")
SECRET_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

STATUS_WON_ID = 142
STATUS_LOST_ID = 143
UNSET = {'', 'none', 'direct/none', 'direct / none', '(none)', '(direct/none)', 'undefined', 'null'}

def pk(p):
    clean = re.sub(r'^https?://', '', p.lower().split('?')[0].split('#')[0]).rstrip('/')
    return re.sub(r'^www\.', '', clean)

def get_domain(p):
    if not p: return 'other'
    if 'janamen1.kz' in p: return 'janamen1.kz'
    if 'janamenhealth.kz' in p: return 'janamenhealth.kz'
    if 'janamen.kz' in p: return 'janamen.kz'
    return 'other'

def clean_str(val, default="none"):
    if not val:
        return default
    s = str(val).strip()
    return s if s else default

def main():
    if not SECRET_KEY:
        raise ValueError("SUPABASE_SERVICE_KEY не установлен в .env")

    print("Чтение analyzed_leads.json...")
    with open("analyzed_leads.json", "r", encoding="utf-8") as f:
        leads = json.load(f)

    print(f"Всего сделок для загрузки: {len(leads)}")

    headers = {
        "apikey": SECRET_KEY,
        "Authorization": f"Bearer {SECRET_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    batch = []
    batch_size = 500
    total_uploaded = 0
    t0 = time.time()

    for idx, d in enumerate(leads):
        created_at = d.get('created_at') or 0
        created_at_iso = datetime.fromtimestamp(created_at).isoformat() if created_at else None

        closed_at = d.get('closed_at') or 0
        closed_at_iso = datetime.fromtimestamp(closed_at).isoformat() if closed_at else None

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
            if src in UNSET:
                src = 'whatsapp'
            if cmp_ in UNSET:
                cmp_ = 'iwa_9828'
            dom = 'janamen1.kz'
            path = '/iwa-9828'
            p = 'janamen1.kz/iwa-9828'

        city = cf.get(855175) or cf.get(679621) or 'none'

        row = {
            "id": d["id"],
            "name": clean_str(d.get("name"), "Без названия")[:255],
            "created_at": created_at_iso,
            "closed_at": closed_at_iso,
            "status_id": st_id,
            "pipeline_id": d.get("pipeline_id") or 0,
            "price": price,
            "is_won": won,
            "is_lost": lost,
            "utm_source": clean_str(src, 'direct/none'),
            "utm_medium": clean_str(med, 'none'),
            "utm_campaign": clean_str(cmp_, 'none'),
            "utm_content": clean_str(cnt, 'none'),
            "utm_term": clean_str(trm, 'none'),
            "utm_id": clean_str(uid, 'none'),
            "landing_page": clean_str(path if path.startswith('/') else '/' + path, '/'),
            "referrer": clean_str(page, 'none')[:500],
            "city": clean_str(city, 'none')[:100],
            "tags": tags[:20]
        }
        batch.append(row)

        if len(batch) >= batch_size:
            req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/deals",
                data=json.dumps(batch).encode("utf-8"),
                headers=headers
            )
            try:
                with urllib.request.urlopen(req) as resp:
                    if resp.status not in (200, 201):
                        raise Exception(f"Failed batch: {resp.status}")
            except urllib.error.HTTPError as e:
                print(f"HTTPError on batch {idx}: {e.code} -> {e.read().decode('utf-8')}")
                raise e

            total_uploaded += len(batch)
            elapsed = time.time() - t0
            speed = total_uploaded / elapsed if elapsed > 0 else 0
            print(f"[{total_uploaded}/{len(leads)}] Загружено сделок... ({speed:.0f} сделок/сек)")
            batch = []

    if batch:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/deals",
            data=json.dumps(batch).encode("utf-8"),
            headers=headers
        )
        with urllib.request.urlopen(req) as resp:
            pass
        total_uploaded += len(batch)

    print(f"🎉 ВСЕ 36 484 сделок успешно загружены в Supabase за {time.time() - t0:.1f} сек!")

if __name__ == "__main__":
    main()
