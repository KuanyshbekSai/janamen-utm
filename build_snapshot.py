import json, re
from collections import defaultdict
from urllib.parse import unquote_plus
from datetime import datetime

leads = json.load(open('analyzed_leads.json', encoding='utf-8'))
UNSET = {'', 'none', 'direct/none', 'direct / none', '(none)', '(direct/none)', 'undefined', 'null'}

def agg():
    return {'leads': 0, 'won': 0, 'revenue': 0}

def add(m, k, w, p):
    a = m[k]
    a['leads'] += 1
    if w:
        a['won'] += 1
        a['revenue'] += p

def lst(m, skip_unset=False):
    out = []
    for k, v in m.items():
        if skip_unset and (not k or k.lower() in UNSET):
            continue
        cr = round(v['won'] / v['leads'] * 100, 1) if v['leads'] else 0
        avg = round(v['revenue'] / v['won']) if v['won'] else 0
        out.append({
            'name': k,
            'leads': v['leads'],
            'won': v['won'],
            'cr': cr,
            'revenue': v['revenue'],
            'avgCheck': avg
        })
    out.sort(key=lambda x: (x['revenue'], x['won'], x['leads']), reverse=True)
    return out

def pk(p):
    clean = re.sub(r'^https?://', '', p.lower().split('?')[0].split('#')[0]).rstrip('/')
    return re.sub(r'^www\.', '', clean)

def get_domain(p):
    if not p: return 'other'
    if 'janamen1.kz' in p: return 'janamen1.kz'
    if 'janamenhealth.kz' in p: return 'janamenhealth.kz'
    if 'janamen.kz' in p: return 'janamen.kz'
    return 'other'

def parse_lead(d):
    won = d.get('status_id') == 142
    price = d.get('price') or 0
    st_id = d.get('status_id') or 0
    created_at = d.get('created_at') or 0
    date_str = datetime.fromtimestamp(created_at).strftime('%d.%m.%Y %H:%M') if created_at else '—'
    month_str = datetime.fromtimestamp(created_at).strftime('%Y-%m') if created_at else ''

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
        is_jana = True
    else:
        is_jana = (dom == 'janamen1.kz') or ('janamen1.kz' in page.lower())

    clean_path = path if path.startswith('/') else '/' + path

    # Группировка основных каналов Jana Men:
    page_l = page.lower()
    clean_l = clean_path.lower()
    blogger_text = f"{page_l} {src.lower()} {med.lower()} {cmp_.lower()} {cnt.lower()} {trm.lower()}"

    # Списки блогеров из реестра инфлюенс-отдела для атрибуции:
    mpb1_bloggers = {'saule_kuralbaevna', 'ainykshaaa', 'ainyshka', 'asylzat_erbolatovnaa', 'asylzaterbolat', 'aliyaestet', 'aliyakairatkyzy', 'madina.dreams', 'madinaamirbekova', 'qura1aikaa', 'quralai', 'hayrinis_aa', 'hairinissa', 'aknur_ydyrys', 'aknurydyrys', 'bota_abdualii', 'gaukhar_taktarbekova', 'araika.mom', 'gulayan.keneshbaeva', 'gulayan', 'aizadaalnur', 'aizada1', 'aizada_usenqyzy', 'lyazzka001', 'lyazkaa01', 'adina_tolegenova', 'adinatolegenoca', 'sitora_sidelnikova', 'sitora', 'd.guldanaa', 'guldana', 'gauhar_diary', 'gaukhar2'}
    mpb2_bloggers = {'frolova__kristina', 'frolova_kristina', 'frolova', 'asema_kotoraya_alel', 'asema', 'akhmoldinaa', 'ramazankyzy_dana', 'meruna_ll', 'habataev.maksat', 'kazhmuratova_asiya', 'zhuldyz_zaynulina', 'dinarakaltore', 'bika_mazhenova', 'orunkeeva_kz', 'karima_turs', 'kuzenbaikyzy___', 'dankarti', 'almaznyi__', 'sharipova_zhannat', 'damirusha__', 'sarsssembaeva', 'inabattan01', 'inabattan', 'diva_boni', 'kuanysheva.dii', 'anarayerikovna'}
    mpb3_bloggers = {'zar1nka', 'kanatkyzyy___', 'yrysgul.abdukarimova', 'gulnur_zhumagul', 'indira_nyrbekkyzyy', 'aselqyzdan', 'anar_aitzhanova_', 'timon_bmw', 'dr.nazerke_kuatkyzy', 'aya_bainiyet', 'elon.rasulovna', 'sanimka.off', '_zzhuldyzbaeva', 'alua_toltayeva', 'xamida_iles', 'armana_fitness_trainer', 'taubaeva.bayan', 'raushan_ismail'}

    is_blogger = False
    if any(b in blogger_text for b in mpb1_bloggers):
        is_blogger = True
        if med in UNSET or med == 'none':
            med = 'mpb1'
    elif any(b in blogger_text for b in mpb2_bloggers):
        is_blogger = True
        if med in UNSET or med == 'none':
            med = 'mpb2'
    elif any(b in blogger_text for b in mpb3_bloggers):
        is_blogger = True
        if med in UNSET or med == 'none':
            med = 'mpb3'

    if is_blogger:
        clean_path = '/influence'
        dom = 'janamen1.kz'
        is_jana = True
        if cmp_ in UNSET or cmp_ == 'none':
            cmp_ = 'ugc_barter'

    # Фан-аккаунты / Креаторы сетки:
    fan_creators = {
        'fan_ainagul': ['janamenfun', 'ainagul', 'доскажанова'],
        'fan_dilnaz': ['janamen_fans', 'dilnaz', 'бекежанова'],
        'fan_aysulu': ['janamennfans', 'janamen.edit', 'aysulu', 'кенжебаева'],
        'fan_kamila': ['aitym.fanclub', 'kamila', 'гайсина'],
        'fan_aida': ['janamennnfan', 'aida'],
        'fan_adina': ['jana.men68', 'jana.menfan', 'aitymzhakupovfanacc', 'adina']
    }
    if med == 'fan' or 'fan' in med.lower() or 'janamenfun' in blogger_text or 'fanclub' in blogger_text:
        med = 'fan'
        dom = 'janamen1.kz'
        is_jana = True
        for f_camp, kws in fan_creators.items():
            if any(kw in blogger_text for kw in kws):
                if cmp_ in UNSET or cmp_ == 'none':
                    cmp_ = f_camp
                break

    if 'magnit' in clean_l or 'magnet' in clean_l or 'гайд' in clean_l or clean_l.startswith('/lidmagnit') or clean_l.startswith('/ligmagnit') or 'magnit' in page_l:
        clean_path = '/lidmagnit'
        dom = 'janamen1.kz'
        is_jana = True
    elif 'influence' in clean_l or 'influence' in page_l or is_blogger:
        clean_path = '/influence'
        dom = 'janamen1.kz'
        is_jana = True
    elif clean_l.startswith('/fun') or '/fun' in page_l:
        clean_path = '/fun'
        dom = 'janamen1.kz'
        is_jana = True
    elif clean_l.startswith('/smm') or '/smm' in page_l:
        clean_path = '/smm'
        dom = 'janamen1.kz'
        is_jana = True

    return {
        'id': d['id'],
        'won': won,
        'price': price,
        'st_id': st_id,
        'created_at': created_at,
        'date_str': date_str,
        'month_str': month_str,
        'page': page,
        'src': src,
        'med': med,
        'cmp_': cmp_,
        'cnt': cnt,
        'trm': trm,
        'p': p,
        'dom': dom,
        'path': path,
        'clean_path': clean_path,
        'is_jana': is_jana,
        'is_wa_aytym': is_wa_aytym,
        'is_blogger': is_blogger,
        'name': (d.get('name') or '').strip()[:35]
    }

# Dictionaries for overall and janamen1
dims_all = {k: defaultdict(agg) for k in ['sources', 'mediums', 'campaigns', 'contents', 'terms']}
dims_jana = {k: defaultdict(agg) for k in ['sources', 'mediums', 'campaigns', 'contents', 'terms']}

combos_all = defaultdict(agg)
combos_jana = defaultdict(agg)
subpages_jana = defaultdict(agg)
landings_all = defaultdict(agg)
monthly_all = defaultdict(agg)
monthly_jana = defaultdict(agg)

scope_defs = ['all', 'janamen1', 'aytym_organika', 'influence', 'fan', 'nikita', 'yura', 'organika', 'tiktok']
scope_aggs = {k: agg() for k in scope_defs}
scope_sources = {k: defaultdict(agg) for k in scope_defs}
scope_mediums = {k: defaultdict(agg) for k in scope_defs}

recent_won = []
recent_janamen = []
tagged_count = 0

status_names = {
    142: 'Успешно реализовано',
    143: 'Закрыто и не реализовано',
    89083630: 'В обработке',
    83732154: 'Качественный лид',
    83732202: 'Принят в работу',
    85156242: 'Недозвон',
    87044258: 'Консультация',
    89298094: 'Ожидает оплаты',
    87065486: 'Счет выставлен',
    89802574: 'Дубль'
}

parsed_leads = []
for d in leads:
    item = parse_lead(d)
    parsed_leads.append(item)
    
    won = item['won']
    price = item['price']
    st_id = item['st_id']
    date_str = item['date_str']
    month_str = item['month_str']
    created_at = item['created_at']
    src = item['src']
    med = item['med']
    cmp_ = item['cmp_']
    cnt = item['cnt']
    trm = item['trm']
    p = item['p']
    dom = item['dom']
    clean_path = item['clean_path']
    is_jana = item['is_jana']
    is_wa_aytym = item['is_wa_aytym']
    is_blogger = item['is_blogger']
    page = item['page']

    is_tagged = (src.lower() not in UNSET) or (cmp_.lower() not in UNSET) or (med.lower() not in UNSET)
    if is_tagged:
        tagged_count += 1
        
    # Global dims
    add(dims_all['sources'], src, won, price)
    add(dims_all['mediums'], med, won, price)
    add(dims_all['campaigns'], cmp_, won, price)
    add(dims_all['contents'], cnt, won, price)
    add(dims_all['terms'], trm, won, price)
    if p:
        add(landings_all, p, won, price)
        
    combo_key_all = (dom, clean_path, src, med, cmp_, cnt, trm)
    add(combos_all, combo_key_all, won, price)
    
    if month_str:
        add(monthly_all, month_str, won, price)
        
    # Scope matching
    hay = f'{src} {med} {cmp_}'.lower()
    matched_scopes = ['all']
    if is_jana:
        matched_scopes.append('janamen1')
    if is_wa_aytym or 'айтым' in hay:
        matched_scopes.append('aytym_organika')
    if is_blogger or 'influence' in page.lower() or 'mpb' in hay:
        matched_scopes.append('influence')
    if med == 'fan' or 'fan' in hay or 'fan_' in hay:
        matched_scopes.append('fan')
    if 'nikita' in hay:
        matched_scopes.append('nikita')
    if 'yura' in hay or 'yurakv' in page.lower():
        matched_scopes.append('yura')
    if 'organika' in page.lower():
        matched_scopes.append('organika')
    if 'tiktok' in hay:
        matched_scopes.append('tiktok')
        
    for sc in matched_scopes:
        add(scope_aggs, sc, won, price)
        add(scope_sources[sc], src, won, price)
        add(scope_mediums[sc], med, won, price)
        
    # Janamen1 specific
    if is_jana:
        add(dims_jana['sources'], src, won, price)
        add(dims_jana['mediums'], med, won, price)
        add(dims_jana['campaigns'], cmp_, won, price)
        add(dims_jana['contents'], cnt, won, price)
        add(dims_jana['terms'], trm, won, price)
        
        add(subpages_jana, clean_path, won, price)
        
        combo_key_jana = (clean_path, src, med, cmp_, cnt, trm)
        add(combos_jana, combo_key_jana, won, price)
        
        if month_str:
            add(monthly_jana, month_str, won, price)
            
        if len(recent_janamen) < 80:
            recent_janamen.append({
                'id': item['id'],
                'name': item['name'] or f"Сделка #{item['id']}",
                'status_id': st_id,
                'status_name': status_names.get(st_id, f'Статус {st_id}'),
                'won': won,
                'price': price,
                'date': date_str,
                'created_at': created_at,
                'path': clean_path,
                'source': src,
                'medium': med,
                'campaign': cmp_,
                'content': cnt,
                'term': trm
            })
            
    if won and len(recent_won) < 80:
        recent_won.append({
            'id': item['id'],
            'name': item['name'] or f"Сделка #{item['id']}",
            'price': price,
            'date': date_str,
            'created_at': created_at,
            'path': clean_path,
            'source': src,
            'medium': med,
            'campaign': cmp_,
            'domain': dom
        })

# Totals
def mk_tot(m):
    l = sum(x['leads'] for x in m.values())
    w = sum(x['won'] for x in m.values())
    r = sum(x['revenue'] for x in m.values())
    return {
        'leads': l,
        'won': w,
        'revenue': r,
        'cr': round(w / l * 100, 1) if l else 0,
        'avgCheck': round(r / w) if w else 0
    }

tot = mk_tot(combos_all)
jt = mk_tot(combos_jana)

# Format combinations
combo_list_all = []
for (dom, p, src, med, cmp_, cnt, trm), v in combos_all.items():
    cr = round(v['won'] / v['leads'] * 100, 1) if v['leads'] else 0
    avg = round(v['revenue'] / v['won']) if v['won'] else 0
    combo_list_all.append({
        'landing': dom + (p if p.startswith('/') else '/' + p),
        'domain': dom,
        'path': p,
        'source': src,
        'medium': med,
        'campaign': cmp_,
        'content': cnt,
        'term': trm,
        'leads': v['leads'],
        'won': v['won'],
        'cr': cr,
        'revenue': v['revenue'],
        'avgCheck': avg
    })
combo_list_all.sort(key=lambda x: (x['revenue'], x['won'], x['leads']), reverse=True)

combo_list_jana = []
for (p, src, med, cmp_, cnt, trm), v in combos_jana.items():
    cr = round(v['won'] / v['leads'] * 100, 1) if v['leads'] else 0
    avg = round(v['revenue'] / v['won']) if v['won'] else 0
    combo_list_jana.append({
        'landing': 'janamen1.kz' + p,
        'path': p,
        'source': src,
        'medium': med,
        'campaign': cmp_,
        'content': cnt,
        'term': trm,
        'leads': v['leads'],
        'won': v['won'],
        'cr': cr,
        'revenue': v['revenue'],
        'avgCheck': avg
    })
combo_list_jana.sort(key=lambda x: (x['revenue'], x['won'], x['leads']), reverse=True)

# Format scopes
def format_scope(k):
    a = scope_aggs[k]
    l = a['leads']
    w = a['won']
    r = a['revenue']
    return {
        'leads': l,
        'won': w,
        'revenue': r,
        'cr': round(w / l * 100, 1) if l else 0,
        'avgCheck': round(r / w) if w else 0,
        'bySource': dict(scope_sources[k]),
        'byMedium': dict(scope_mediums[k])
    }

scopes_out = {k: format_scope(k) for k in scope_defs}

# Meta dictionary for human labels for janamen1 subpages
subpage_meta = {
    '/iwa-9828': {'title': 'Instagram WhatsApp (iwa-9828)', 'desc': 'Айтым Берикович (+7 708 377-98-28) — переписки и заявки'},
    '/lidmagnit': {'title': 'Лид-магниты (все варианты /lidmagnit*)', 'desc': 'Бесплатные материалы, гайды и тесты с любыми приставками'},
    '/influence': {'title': 'Инфлюенс / Блогеры (МПБ)', 'desc': 'Интеграции с блогерами через менеджеров (mpb1, mpb2, mpb3)'},
    '/fun': {'title': 'Квиз / Воронка (/fun)', 'desc': 'Интерактивный опрос и подбор программы курса'},
    '/smm': {'title': 'SMM / Соцсети (/smm)', 'desc': 'Посадочная страница для социальных сетей и постов'},
    '/organika': {'title': 'Органика (Основная)', 'desc': 'Основная посадочная под органический трафик и посты'},
    '/kaspiform': {'title': 'Kaspi-форма', 'desc': 'Быстрый заказ через Kaspi Рассрочку / Red'},
    '/inst-men': {'title': 'Instagram Men', 'desc': 'Мужская аудитория из соцсетей'},
    '/inst-women': {'title': 'Instagram Women', 'desc': 'Женская аудитория из соцсетей'},
    '/vitamins-inst': {'title': 'Витамины Inst', 'desc': 'Посадочная под витаминные комплексы'},
    '/inst-omega': {'title': 'Омега-3 Inst', 'desc': 'Посадочная под Омега-3 и добавки'},
    '/nikitaform': {'title': 'Форма Никита', 'desc': 'Форма таргетолога Никиты'},
    '/yurakv': {'title': 'Квиз Юра', 'desc': 'Квиз-воронка таргетолога Юры'},
    '/aojiru-inst': {'title': 'Аодзиру Inst', 'desc': 'Посадочная под японский аодзиру'},
    '/kaspiformsps': {'title': 'Kaspi Спасибо', 'desc': 'Страница благодарности после формы'},
    '/orlanforma': {'title': 'Орлан форма', 'desc': 'Специальная форма партнеров'},
    '/': {'title': 'Главная страница', 'desc': 'Главная janamen1.kz'}
}

# Subpages formatted list
subpages_list = []
for p, v in subpages_jana.items():
    cr = round(v['won'] / v['leads'] * 100, 1) if v['leads'] else 0
    avg = round(v['revenue'] / v['won']) if v['won'] else 0
    meta = subpage_meta.get(p, {'title': p.lstrip('/') or 'Главная', 'desc': f'Посадочная страница {p}'})
    subpages_list.append({
        'path': p,
        'title': meta['title'],
        'desc': meta['desc'],
        'leads': v['leads'],
        'won': v['won'],
        'cr': cr,
        'revenue': v['revenue'],
        'avgCheck': avg
    })
subpages_list.sort(key=lambda x: (x['revenue'], x['won'], x['leads']), reverse=True)

# Monthly formatted lists
monthly_list_all = []
for m, v in sorted(monthly_all.items()):
    cr = round(v['won'] / v['leads'] * 100, 1) if v['leads'] else 0
    avg = round(v['revenue'] / v['won']) if v['won'] else 0
    monthly_list_all.append({
        'month': m,
        'leads': v['leads'],
        'won': v['won'],
        'cr': cr,
        'revenue': v['revenue'],
        'avgCheck': avg
    })

monthly_list_jana = []
for m, v in sorted(monthly_jana.items()):
    cr = round(v['won'] / v['leads'] * 100, 1) if v['leads'] else 0
    avg = round(v['revenue'] / v['won']) if v['won'] else 0
    monthly_list_jana.append({
        'month': m,
        'leads': v['leads'],
        'won': v['won'],
        'cr': cr,
        'revenue': v['revenue'],
        'avgCheck': avg
    })

# Format dimensions
dims_all_out = {k: lst(v) for k, v in dims_all.items()}
dims_jana_out = {k: lst(v) for k, v in dims_jana.items()}

analytics_summary = {
    'total': tot,
    'janamen1': jt,
    'scopes': scopes_out,
    'subpages_janamen1': subpages_list,
    'monthly_all': monthly_list_all,
    'monthly_janamen1': monthly_list_jana,
    'recent_deals_janamen1': recent_janamen,
    'recent_won_deals': recent_won,
    'meta': {
        'generated_at': datetime.now().isoformat(),
        'total_analyzed_leads': len(leads),
        'total_tagged_leads': tagged_count,
        'janamen1_leads_count': jt['leads'],
        'combinations_count': len(combo_list_jana)
    }
}

granularity_data = {
    'all_company': {
        'totals': tot,
        'combos': combo_list_all,
        'dimensions': dims_all_out,
        'landings': lst(landings_all)
    },
    'janamen1': {
        'totals': jt,
        'combos': combo_list_jana,
        'dimensions': dims_jana_out,
        'subpages': subpages_list
    },
    'meta': {
        'generated_at': datetime.now().isoformat(),
        'combinations_all': len(combo_list_all),
        'combinations_jana': len(combo_list_jana),
        'sources': len(dims_all['sources']),
        'mediums': len(dims_all['mediums']),
        'campaigns': len(dims_all['campaigns']),
        'contents': len(dims_all['contents']),
        'terms': len(dims_all['terms']),
        'pages_jana': len(subpages_list)
    }
}

with open('gas/marketing_analytics_summary.json', 'w', encoding='utf-8') as f:
    json.dump(analytics_summary, f, ensure_ascii=False, indent=2)

with open('gas/utm_granularity_data.json', 'w', encoding='utf-8') as f:
    json.dump(granularity_data, f, ensure_ascii=False, indent=2)

# Build compact dictionary-encoded leads for real-time period filtering
strings = []
s_map = {}
def get_s(s):
    if s not in s_map:
        s_map[s] = len(strings)
        strings.append(s)
    return s_map[s]

encoded_rows = []
for item in parsed_leads:
    won_int = 1 if item['won'] else 0
    encoded_rows.append([
        item['id'],
        item['created_at'],
        won_int,
        item['price'],
        get_s(item['dom']),
        get_s(item['clean_path']),
        get_s(item['src']),
        get_s(item['med']),
        get_s(item['cmp_']),
        get_s(item['cnt']),
        get_s(item['trm']),
        item['st_id'],
        item['name']
    ])

compact_data = {'strings': strings, 'rows': encoded_rows}
with open('gas/compact_leads_dict.json', 'w', encoding='utf-8') as f:
    json.dump(compact_data, f, ensure_ascii=False)

print('SUCCESS!')
print(f"Total leads: {tot['leads']}, Won: {tot['won']}, Revenue: {tot['revenue']:,} ₸")
print(f"Janamen1 leads (incl WA 9828): {jt['leads']}, Won: {jt['won']}, Revenue: {jt['revenue']:,} ₸")
print(f"Combos all: {len(combo_list_all)}, Combos janamen1: {len(combo_list_jana)}")
print(f"Compact leads encoded: {len(encoded_rows)} rows, {len(strings)} unique strings")
