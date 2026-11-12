// Атрибуция лида по каналам отдела (SMM / Influence / Фан-аккаунты / лид-магниты).
// Это порт parse_lead() из build_snapshot.py: правила должны совпадать один в один,
// чтобы живые сделки в портале распределялись так же, как в снимке.

export const UNSET = new Set(['', 'none', 'direct/none', 'direct / none', '(none)', '(direct/none)', 'undefined', 'null']);

export function pk(p) {
  const clean = String(p || '').toLowerCase().split('?')[0].split('#')[0].replace(/^https?:\/\//, '').replace(/\/+$/, '');
  return clean.replace(/^www\./, '');
}

export function getDomain(p) {
  if (!p) return 'other';
  if (p.includes('janamen1.kz')) return 'janamen1.kz';
  if (p.includes('janamenhealth.kz')) return 'janamenhealth.kz';
  if (p.includes('janamen.kz')) return 'janamen.kz';
  return 'other';
}

/**
 * @param {object} x  { page, src, med, cmp, cnt, trm, tags }
 *   src..trm — значения UTM уже с подставленными 'direct/none' / 'none', как в parse_lead
 * @param {object=} extraBloggers  { handle: 'mpb1' | 'mpb2' | ... } из таблицы bloggers
 */
export function attribute(x, extraBloggers = {}) {
  const page = x.page || '';
  let src = x.src, med = x.med, cmp = x.cmp;
  const cnt = x.cnt, trm = x.trm;
  const tags = x.tags || [];

  const isWa = tags.some(t => String(t).includes('9828')) || page.toLowerCase().includes('iwa-9828') || page.toLowerCase().includes('9828');
  let p = pk(page);
  let dom = getDomain(p);
  // Python: path = (p.replace(dom,'').split('#')[0] or '/') if dom != 'other' else p
  let path = dom !== 'other' ? (p.split(dom).join('').split('#')[0] || '/') : p;
  let isJana;

  if (isWa) {
    med = 'Айтым Берикович - органика';
    if (UNSET.has(src)) src = 'whatsapp';
    if (UNSET.has(cmp)) cmp = 'iwa_9828';
    dom = 'janamen1.kz';
    path = '/iwa-9828';
    p = 'janamen1.kz/iwa-9828';
    isJana = true;
  } else {
    isJana = dom === 'janamen1.kz' || page.toLowerCase().includes('janamen1.kz');
  }

  let cleanPath = path.startsWith('/') ? path : '/' + path;
  const pageL = page.toLowerCase();
  const cleanL = cleanPath.toLowerCase();
  const bloggerText = `${pageL} ${src.toLowerCase()} ${med.toLowerCase()} ${cmp.toLowerCase()} ${cnt.toLowerCase()} ${trm.toLowerCase()}`;

  // Блогеры: сначала встроенные списки (как в build_snapshot.py), затем добавленные в портале (таблица bloggers)
  const lists = Object.entries(BLOGGERS_BY_MANAGER).map(([mgr, handles]) => [mgr, handles]);
  const extraByMgr = {};
  for (const [handle, mgr] of Object.entries(extraBloggers)) {
    if (!handle || handle.length < 4 || !mgr) continue; // слишком короткие ники дают ложные совпадения
    (extraByMgr[mgr] = extraByMgr[mgr] || []).push(handle);
  }
  for (const mgr of Object.keys(extraByMgr).sort()) lists.push([mgr, extraByMgr[mgr]]);

  let isBlogger = false;
  for (const [mgr, handles] of lists) {
    if (handles.some(b => bloggerText.includes(b))) {
      isBlogger = true;
      if (UNSET.has(med) || med === 'none') med = mgr;
      break;
    }
  }

  if (isBlogger) {
    cleanPath = '/influence';
    dom = 'janamen1.kz';
    isJana = true;
    if (UNSET.has(cmp) || cmp === 'none') cmp = 'ugc_barter';
  }

  if (med === 'fan' || med.toLowerCase().includes('fan') || bloggerText.includes('janamenfun') || bloggerText.includes('fanclub')) {
    med = 'fan';
    dom = 'janamen1.kz';
    isJana = true;
    for (const [fCamp, kws] of Object.entries(FAN_CREATORS)) {
      if (kws.some(kw => bloggerText.includes(kw))) {
        if (UNSET.has(cmp) || cmp === 'none') cmp = fCamp;
        break;
      }
    }
  }

  if (cleanL.includes('magnit') || cleanL.includes('magnet') || cleanL.includes('гайд') || cleanL.startsWith('/lidmagnit') || cleanL.startsWith('/ligmagnit') || pageL.includes('magnit')) {
    cleanPath = '/lidmagnit';
    dom = 'janamen1.kz';
    isJana = true;
  } else if (cleanL.includes('influence') || pageL.includes('influence') || isBlogger) {
    cleanPath = '/influence';
    dom = 'janamen1.kz';
    isJana = true;
  } else if (cleanL.startsWith('/fun') || pageL.includes('/fun')) {
    cleanPath = '/fun';
    dom = 'janamen1.kz';
    isJana = true;
  } else if (cleanL.startsWith('/smm') || pageL.includes('/smm')) {
    cleanPath = '/smm';
    dom = 'janamen1.kz';
    isJana = true;
  }

  return { src, med, cmp, cnt, trm, dom, path: cleanPath, is_jana: isJana, is_wa: isWa, is_blogger: isBlogger };
}

// Сгенерировано из build_snapshot.py — списки должны совпадать
export const BLOGGERS_BY_MANAGER = {
  "mpb1": [
    "adina_tolegenova",
    "adinatolegenoca",
    "ainykshaaa",
    "ainyshka",
    "aizada1",
    "aizada_usenqyzy",
    "aizadaalnur",
    "aknur_ydyrys",
    "aknurydyrys",
    "aliyaestet",
    "aliyakairatkyzy",
    "araika.mom",
    "asylzat_erbolatovnaa",
    "asylzaterbolat",
    "bota_abdualii",
    "d.guldanaa",
    "gauhar_diary",
    "gaukhar2",
    "gaukhar_taktarbekova",
    "gulayan",
    "gulayan.keneshbaeva",
    "guldana",
    "hairinissa",
    "hayrinis_aa",
    "lyazkaa01",
    "lyazzka001",
    "madina.dreams",
    "madinaamirbekova",
    "qura1aikaa",
    "quralai",
    "saule_kuralbaevna",
    "sitora",
    "sitora_sidelnikova"
  ],
  "mpb2": [
    "akhmoldinaa",
    "almaznyi__",
    "anarayerikovna",
    "asema",
    "asema_kotoraya_alel",
    "bika_mazhenova",
    "damirusha__",
    "dankarti",
    "dinarakaltore",
    "diva_boni",
    "frolova",
    "frolova__kristina",
    "frolova_kristina",
    "habataev.maksat",
    "inabattan",
    "inabattan01",
    "karima_turs",
    "kazhmuratova_asiya",
    "kuanysheva.dii",
    "kuzenbaikyzy___",
    "meruna_ll",
    "orunkeeva_kz",
    "ramazankyzy_dana",
    "sarsssembaeva",
    "sharipova_zhannat",
    "zhuldyz_zaynulina"
  ],
  "mpb3": [
    "_zzhuldyzbaeva",
    "alua_toltayeva",
    "anar_aitzhanova_",
    "armana_fitness_trainer",
    "aselqyzdan",
    "aya_bainiyet",
    "dr.nazerke_kuatkyzy",
    "elon.rasulovna",
    "gulnur_zhumagul",
    "indira_nyrbekkyzyy",
    "kanatkyzyy___",
    "raushan_ismail",
    "sanimka.off",
    "taubaeva.bayan",
    "timon_bmw",
    "xamida_iles",
    "yrysgul.abdukarimova",
    "zar1nka"
  ]
};

export const FAN_CREATORS = {
  "fan_ainagul": [
    "janamenfun",
    "ainagul",
    "доскажанова"
  ],
  "fan_dilnaz": [
    "janamen_fans",
    "dilnaz",
    "бекежанова"
  ],
  "fan_aysulu": [
    "janamennfans",
    "janamen.edit",
    "aysulu",
    "кенжебаева"
  ],
  "fan_kamila": [
    "aitym.fanclub",
    "kamila",
    "гайсина"
  ],
  "fan_aida": [
    "janamennnfan",
    "aida"
  ],
  "fan_adina": [
    "jana.men68",
    "jana.menfan",
    "aitymzhakupovfanacc",
    "adina"
  ]
};
