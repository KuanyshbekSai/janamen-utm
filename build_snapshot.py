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

# Dictionaries for overall and janamen1
dims_all = {k: defaultdict(agg) for k in ['sources', 'mediums', 'campaigns', 'contents', 'terms']}
dims_jana = {k: defaultdict(agg) for k in ['sources', 'mediums', 'campaigns', 'contents', 'terms']}

combos_all = defaultdict(agg)
combos_jana = defaultdict(agg)
subpages_jana = defaultdict(agg)
landings_all = defaultdict(agg)
monthly_all = defaultdict(agg)
monthly_jana = defaultdict(agg)

scope_defs = ['all', 'janamen1', 'nikita', 'yura', 'organika', 'tiktok']
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

for d in leads:
    won = d.get('status_id') == 142
    price = d.get('price') or 0
    st_id = d.get('status_id')
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
    
    p = pk(page)
    dom = get_domain(p)
    path = p.replace(dom, '').split('#')[0] or '/' if dom != 'other' else p
    is_jana = (dom == 'janamen1.kz') or ('janamen1.kz' in page.lower())
    
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
        
    combo_key_all = (dom, path if dom != 'other' else p, src, med, cmp_, cnt, trm)
    add(combos_all, combo_key_all, won, price)
    
    if month_str:
        add(monthly_all, month_str, won, price)
        
    # Scope matching
    hay = f'{src} {med} {cmp_}'.lower()
    matched_scopes = ['all']
    if is_jana:
        matched_scopes.append('janamen1')
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
        
        clean_path = path if path.startswith('/') else '/' + path
        add(subpages_jana, clean_path, won, price)
        
        combo_key_jana = (clean_path, src, med, cmp_, cnt, trm)
        add(combos_jana, combo_key_jana, won, price)
        
        if month_str:
            add(monthly_jana, month_str, won, price)
            
        if len(recent_janamen) < 60:
            recent_janamen.append({
                'id': d['id'],
                'name': d.get('name') or f"Сделка #{d['id']}",
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

    if won and len(recent_won) < 40:
        recent_won.append({
            'id': d['id'],
            'name': d.get('name') or f"Сделка #{d['id']}",
            'price': price,
            'date': date_str,
            'source': src,
            'medium': med,
            'campaign': cmp_,
            'domain': dom,
            'page': p or '—'
        })

# Sort recent deals by timestamp descending
recent_janamen.sort(key=lambda x: x['created_at'], reverse=True)

# Build combinations list
combo_list_all = []
for (dom, path, s, m, c_, ct, t), v in combos_all.items():
    cr = round(v['won'] / v['leads'] * 100, 1) if v['leads'] else 0
    avg = round(v['revenue'] / v['won']) if v['won'] else 0
    combo_list_all.append({
        'domain': dom,
        'landing': (dom + path) if dom != 'other' else path,
        'path': path,
        'source': s,
        'medium': m,
        'campaign': c_,
        'content': ct,
        'term': t,
        'leads': v['leads'],
        'won': v['won'],
        'cr': cr,
        'revenue': v['revenue'],
        'avgCheck': avg
    })
combo_list_all.sort(key=lambda x: (x['revenue'], x['won'], x['leads']), reverse=True)

combo_list_jana = []
for (path, s, m, c_, ct, t), v in combos_jana.items():
    cr = round(v['won'] / v['leads'] * 100, 1) if v['leads'] else 0
    avg = round(v['revenue'] / v['won']) if v['won'] else 0
    combo_list_jana.append({
        'domain': 'janamen1.kz',
        'landing': f'janamen1.kz{path}',
        'path': path,
        'source': s,
        'medium': m,
        'campaign': c_,
        'content': ct,
        'term': t,
        'leads': v['leads'],
        'won': v['won'],
        'cr': cr,
        'revenue': v['revenue'],
        'avgCheck': avg
    })
combo_list_jana.sort(key=lambda x: (x['revenue'], x['won'], x['leads']), reverse=True)

# Format scopes output
def format_scope(k):
    a = scope_aggs[k]
    cr = round(a['won'] / a['leads'] * 100, 1) if a['leads'] else 0
    avg = round(a['revenue'] / a['won']) if a['won'] else 0
    return {
        'leads': a['leads'],
        'won': a['won'],
        'revenue': a['revenue'],
        'cr': (a['won'] / a['leads']) if a['leads'] else 0,
        'avgCheck': avg,
        'bySource': dict(scope_sources[k]),
        'byMedium': dict(scope_mediums[k])
    }

scopes_out = {k: format_scope(k) for k in scope_defs}

# Meta dictionary for human labels for janamen1 subpages
subpage_meta = {
    '/organika': {'title': 'Органика (Основная)', 'desc': 'Основная посадочная под органический трафик и посты'},
    '/inst-men': {'title': 'Instagram Men', 'desc': 'Мужская аудитория из соцсетей'},
    '/kaspiform': {'title': 'Kaspi-форма', 'desc': 'Быстрый заказ через Kaspi Рассрочку / Red'},
    '/inst-women': {'title': 'Instagram Women', 'desc': 'Женская аудитория из соцсетей'},
    '/lidmagnit': {'title': 'Лид-магнит / Гайд', 'desc': 'Бесплатные материалы и тест за контакт'},
    '/vitamins-inst': {'title': 'Витамины Inst', 'desc': 'Посадочная под витаминные комплексы'},
    '/inst-omega': {'title': 'Омега-3 Inst', 'desc': 'Посадочная под Омега-3 и добавки'},
    '/fun': {'title': 'Квиз / Воронка', 'desc': 'Интерактивный опрос и подбор программы'},
    '/nikitaform': {'title': 'Форма Никита', 'desc': 'Форма таргетолога Никиты'},
    '/yurakv': {'title': 'Квиз Юра', 'desc': 'Квиз-воронка таргетолога Юры'},
    '/influence': {'title': 'Инфлюенс / Блогеры', 'desc': 'Интеграции с блогерами и амбассадорами'},
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
    m = subpage_meta.get(p, {'title': p, 'desc': 'Посадочная страница маркетинг-домена'})
    subpages_list.append({
        'path': p,
        'title': m['title'],
        'desc': m['desc'],
        'leads': v['leads'],
        'won': v['won'],
        'cr': cr,
        'revenue': v['revenue'],
        'avgCheck': avg
    })
subpages_list.sort(key=lambda x: (x['revenue'], x['won'], x['leads']), reverse=True)

# Monthly formatted
monthly_list_all = [{'month': k, 'leads': v['leads'], 'won': v['won'], 'revenue': v['revenue']} for k, v in sorted(monthly_all.items())]
monthly_list_jana = [{'month': k, 'leads': v['leads'], 'won': v['won'], 'revenue': v['revenue']} for k, v in sorted(monthly_jana.items())]

tot = scope_aggs['all']
jt = scope_aggs['janamen1']

analytics_summary = {
    'kpi': {
        'totalLeads': tot['leads'],
        'wonLeads': tot['won'],
        'totalRevenue': tot['revenue'],
        'totalBudget': 0,
        'cr': (tot['won'] / tot['leads']) if tot['leads'] else 0,
        'avgCheck': round(tot['revenue'] / tot['won']) if tot['won'] else 0,
        'romi': 0,
        'taggedLeads': tagged_count
    },
    'janamen1_kpi': {
        'totalLeads': jt['leads'],
        'wonLeads': jt['won'],
        'totalRevenue': jt['revenue'],
        'cr': (jt['won'] / jt['leads']) if jt['leads'] else 0,
        'avgCheck': round(jt['revenue'] / jt['won']) if jt['won'] else 0
    },
    'scopes': scopes_out,
    'janamen1_subpages': {sp['path']: {'leads': sp['leads'], 'won': sp['won'], 'revenue': sp['revenue']} for sp in subpages_list},
    'janamen1_subpages_list': subpages_list,
    'bySource': dict(dims_all['sources']),
    'byMedium': dict(dims_all['mediums']),
    'byCampaign': dict(dims_all['campaigns']),
    'byLanding': lst(landings_all, False)[:50],
    'monthly': monthly_list_all,
    'monthly_jana': monthly_list_jana,
    'recentWonDeals': recent_won,
    'recentJanamenDeals': recent_janamen
}

granularity_data = {
    'combinations': combo_list_all,
    'combinations_janamen1': combo_list_jana,
    'sources': lst(dims_all['sources'], False),
    'mediums': lst(dims_all['mediums'], True),
    'campaigns': lst(dims_all['campaigns'], True),
    'contents': lst(dims_all['contents'], True),
    'terms': lst(dims_all['terms'], True),
    'sources_jana': lst(dims_jana['sources'], False),
    'mediums_jana': lst(dims_jana['mediums'], True),
    'campaigns_jana': lst(dims_jana['campaigns'], True),
    'contents_jana': lst(dims_jana['contents'], True),
    'terms_jana': lst(dims_jana['terms'], True),
    'counts': {
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

print('SUCCESS!')
print(f"Total leads: {tot['leads']}, Won: {tot['won']}, Revenue: {tot['revenue']:,} ₸")
print(f"Janamen1 leads: {jt['leads']}, Won: {jt['won']}, Revenue: {jt['revenue']:,} ₸")
print(f"Combos all: {len(combo_list_all)}, Combos janamen1: {len(combo_list_jana)}")
