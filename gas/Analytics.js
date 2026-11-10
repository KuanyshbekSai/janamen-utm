/**
 * ============================================================
 * Analytics.js — Полная аналитика по ВСЕМ UTM-меткам из листа сделок
 * Критерий оплаты: «Успешно реализовано» (статус 142)
 * ============================================================
 */

var WON_CATEGORY = 'Успешно реализовано';

function isUnset_(v) {
  return v === '' || v === 'none' || v === 'direct/none' || v === 'direct / none';
}

function newAgg_() { return { leads: 0, won: 0, revenue: 0 }; }

function addAgg_(map, key, won, price) {
  var a = map[key] || (map[key] = newAgg_());
  a.leads++;
  if (won) { a.won++; a.revenue += price; }
}

function aggList_(map, skipUnset) {
  var out = [];
  for (var k in map) {
    if (skipUnset && isUnset_(k)) continue;
    var v = map[k];
    out.push({
      name: k, leads: v.leads, won: v.won,
      cr: v.leads ? Math.round(v.won / v.leads * 1000) / 10 : 0,
      revenue: v.revenue, avgCheck: v.won ? Math.round(v.revenue / v.won) : 0
    });
  }
  out.sort(function (a, b) { return b.revenue - a.revenue || b.won - a.won || b.leads - a.leads; });
  return out;
}

function pageKey_(page) {
  var p = String(page || '').toLowerCase().split('?')[0].split('#')[0]
    .replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/\/+$/, '');
  return p;
}

function scopeStats_(a) {
  return {
    leads: a.leads, won: a.won, revenue: a.revenue,
    cr: a.leads ? a.won / a.leads : 0,
    avgCheck: a.won ? Math.round(a.revenue / a.won) : 0
  };
}

function ym_(d) {
  if (!(d instanceof Date)) return '';
  return Utilities.formatDate(d, 'Asia/Almaty', 'yyyy-MM');
}

/** Полный пересчёт аналитики из листа «Сделки AmoCRM» */
function buildFullAnalytics() {
  var ss = getSpreadsheet();
  var sheet = ss.getSheetByName(CONFIG.SHEETS.DEALS);
  var last = sheet ? sheet.getLastRow() : 0;
  var data = last > 1 ? sheet.getRange(2, 1, last - 1, DEAL_COLS).getValues() : [];

  var total = newAgg_();
  var tagged = 0;
  var jTotal = newAgg_();
  var dims = { sources: {}, mediums: {}, campaigns: {}, contents: {}, terms: {} };
  var combos = {};
  var jSub = {};
  var landings = {};
  var monthly = {};
  var scopes = { all: newAgg_(), janamen1: newAgg_(), aytym_organika: newAgg_(), organika: newAgg_(), nikita: newAgg_(), yura: newAgg_(), tiktok: newAgg_() };
  var recentWon = [];
  var recentJanamen = [];
  var domain = String(CONFIG.MARKETING_DOMAIN).toLowerCase();

  for (var i = 0; i < data.length; i++) {
    var r = data[i];
    if (!r[0]) continue;
    var won = r[4] === WON_CATEGORY;
    var price = Number(r[5]) || 0;
    var src = String(r[7] || 'direct/none'), med = String(r[8] || 'none'), cmp = String(r[9] || 'none');
    var cnt = String(r[10] || 'none'), trm = String(r[11] || 'none');
    var page = String(r[15] || '');
    var pk = pageKey_(page);

    total.leads++;
    if (won) { total.won++; total.revenue += price; }
    if (!isUnset_(src) || !isUnset_(cmp)) tagged++;

    addAgg_(dims.sources, src, won, price);
    addAgg_(dims.mediums, med, won, price);
    addAgg_(dims.campaigns, cmp, won, price);
    addAgg_(dims.contents, cnt, won, price);
    addAgg_(dims.terms, trm, won, price);

    // Полная связка из 5 параметров
    var ck = [src, med, cmp, cnt, trm].join('\u0001');
    var c = combos[ck] || (combos[ck] = { source: src, medium: med, campaign: cmp, content: cnt, term: trm, leads: 0, won: 0, revenue: 0 });
    c.leads++;
    if (won) { c.won++; c.revenue += price; }

    // Посадочные
    if (pk) addAgg_(landings, pk, won, price);

    // Маркетинговый домен janamen1.kz
    if (pk.indexOf(domain) === 0) {
      jTotal.leads++;
      if (won) { jTotal.won++; jTotal.revenue += price; }
      var path = pk.substring(domain.length) || '/';
      addAgg_(jSub, path, won, price);
      scopes.janamen1.leads++;
      if (won) { scopes.janamen1.won++; scopes.janamen1.revenue += price; }
    }

    // Быстрые срезы
    scopes.all.leads++;
    if (won) { scopes.all.won++; scopes.all.revenue += price; }
    var hay = (src + ' ' + med + ' ' + cmp).toLowerCase();
    var who = [];
    if (hay.indexOf('nikita') !== -1) who.push('nikita');
    if (hay.indexOf('yura') !== -1) who.push('yura');
    if (src.toLowerCase().indexOf('tiktok') !== -1) who.push('tiktok');
    if (page.toLowerCase().indexOf('organika') !== -1) who.push('organika');
    if (hay.indexOf('9828') !== -1 || hay.indexOf('айтым') !== -1) who.push('aytym_organika');
    for (var w = 0; w < who.length; w++) {
      scopes[who[w]].leads++;
      if (won) { scopes[who[w]].won++; scopes[who[w]].revenue += price; }
    }

    // Динамика по месяцам: лиды по дате создания, оплаты — по дате закрытия
    var mk = ym_(r[6]);
    if (mk) { (monthly[mk] || (monthly[mk] = { leads: 0, won: 0, revenue: 0 })).leads++; }
    if (won) {
      var ck2 = ym_(r[17]) || mk;
      if (ck2) {
        var m2 = monthly[ck2] || (monthly[ck2] = { leads: 0, won: 0, revenue: 0 });
        m2.won++; m2.revenue += price;
      }
      recentWon.push({
        id: r[0], name: r[1], price: price, source: src, medium: med, campaign: cmp,
        page: pk || '—',
        date: r[17] instanceof Date ? r[17].getTime() : (r[6] instanceof Date ? r[6].getTime() : 0)
      });
    }
  }

  recentWon.sort(function (a, b) { return b.date - a.date; });

  var comboList = [];
  for (var k in combos) {
    var v = combos[k];
    if (isUnset_(v.source) && isUnset_(v.campaign) && isUnset_(v.medium)) continue;
    comboList.push({
      source: v.source, medium: v.medium, campaign: v.campaign, content: v.content, term: v.term,
      leads: v.leads, won: v.won, cr: v.leads ? Math.round(v.won / v.leads * 1000) / 10 : 0,
      revenue: v.revenue, avgCheck: v.won ? Math.round(v.revenue / v.won) : 0
    });
  }
  comboList.sort(function (a, b) { return b.revenue - a.revenue || b.won - a.won || b.leads - a.leads; });

  var budget = 0;
  var reg = ss.getSheetByName(CONFIG.SHEETS.REGISTRY);
  if (reg && reg.getLastRow() > 1) {
    var rv = reg.getRange(2, 13, reg.getLastRow() - 1, 1).getValues();
    for (var b = 0; b < rv.length; b++) budget += Number(rv[b][0]) || 0;
  }

  var props = PropertiesService.getScriptProperties();
  var lastRes = {};
  try { lastRes = JSON.parse(props.getProperty('SYNC_LAST_RESULT') || '{}'); } catch (e) {}

  var bySource = {}, byMedium = {}, byCampaign = {};
  for (var s in dims.sources) bySource[s] = dims.sources[s];
  for (var m in dims.mediums) byMedium[m] = dims.mediums[m];
  for (var cc in dims.campaigns) byCampaign[cc] = dims.campaigns[cc];

  var monthlyList = Object.keys(monthly).sort().map(function (k2) {
    return { month: k2, leads: monthly[k2].leads, won: monthly[k2].won, revenue: monthly[k2].revenue };
  });

  var scopeOut = {};
  for (var sk in scopes) scopeOut[sk] = scopeStats_(scopes[sk]);

  return {
    generatedAt: Date.now(),
    sync: {
      lastRunAt: Number(props.getProperty('SYNC_LAST_RUN_AT')) || 0,
      fullDone: props.getProperty('SYNC_FULL_DONE') === 'true',
      backfillPage: Number(props.getProperty('SYNC_BACKFILL_PAGE')) || 0,
      lastResult: lastRes,
      totalRows: data.length
    },
    analytics: {
      kpi: {
        totalLeads: total.leads, wonLeads: total.won, totalRevenue: total.revenue, totalBudget: budget,
        cr: total.leads ? total.won / total.leads : 0,
        avgCheck: total.won ? Math.round(total.revenue / total.won) : 0,
        romi: budget ? (total.revenue - budget) / budget : 0,
        taggedLeads: tagged
      },
      janamen1_kpi: {
        totalLeads: jTotal.leads, wonLeads: jTotal.won, totalRevenue: jTotal.revenue,
        cr: jTotal.leads ? jTotal.won / jTotal.leads : 0,
        avgCheck: jTotal.won ? Math.round(jTotal.revenue / jTotal.won) : 0
      },
      janamen1_subpages: jSub,
      scopes: scopeOut,
      bySource: bySource,
      byMedium: byMedium,
      byCampaign: byCampaign,
      byLanding: aggList_(landings, false).slice(0, 100),
      monthly: monthlyList,
      recentWonDeals: recentWon.slice(0, 30)
    },
    granularity: {
      sources: aggList_(dims.sources, false),
      mediums: aggList_(dims.mediums, true),
      campaigns: aggList_(dims.campaigns, true),
      contents: aggList_(dims.contents, true),
      terms: aggList_(dims.terms, true),
      combinations: comboList.slice(0, 1500),
      counts: {
        sources: Object.keys(dims.sources).length, mediums: Object.keys(dims.mediums).length,
        campaigns: Object.keys(dims.campaigns).length, contents: Object.keys(dims.contents).length,
        terms: Object.keys(dims.terms).length, combinations: comboList.length
      }
    }
  };
}

/* ---------- Кэш (CacheService, чанки по 90 КБ, TTL 10 мин) ---------- */

var CACHE_KEY = 'full_analytics_v1';

function getFullAnalyticsCached() {
  var cache = CacheService.getScriptCache();
  var n = Number(cache.get(CACHE_KEY + '_n'));
  if (n) {
    var parts = [];
    for (var i = 0; i < n; i++) {
      var p = cache.get(CACHE_KEY + '_' + i);
      if (p === null) { parts = null; break; }
      parts.push(p);
    }
    if (parts) {
      try { return JSON.parse(parts.join('')); } catch (e) {}
    }
  }
  var result = buildFullAnalytics();
  try {
    var json = JSON.stringify(result);
    var size = 90000, chunks = Math.ceil(json.length / size), put = {};
    for (var c = 0; c < chunks; c++) put[CACHE_KEY + '_' + c] = json.substring(c * size, (c + 1) * size);
    put[CACHE_KEY + '_n'] = String(chunks);
    cache.putAll(put, 600);
  } catch (e) { Logger.log('Cache put failed: ' + e); }
  return result;
}

function clearAnalyticsCache_() {
  var cache = CacheService.getScriptCache();
  var n = Number(cache.get(CACHE_KEY + '_n')) || 0;
  var keys = [CACHE_KEY + '_n'];
  for (var i = 0; i < n; i++) keys.push(CACHE_KEY + '_' + i);
  cache.removeAll(keys);
}
