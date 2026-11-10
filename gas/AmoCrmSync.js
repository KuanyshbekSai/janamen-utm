/**
 * ============================================================
 * AmoCrmSync.js — Полная и инкрементальная синхронизация сделок AmoCRM
 * ------------------------------------------------------------
 *  1) Первый запуск (backfill): выгружает ВСЮ базу сделок порциями по 250,
 *     запоминает страницу и сам продолжает по триггеру (лимит GAS ~6 мин).
 *  2) Далее (incremental): забирает только сделки, изменённые с прошлой
 *     синхронизации (смена статуса, суммы, UTM) — раз в час по триггеру.
 *  Все UTM (source/medium/campaign/content/term/id) + страница + даты
 *  попадают в лист «📥 Сделки AmoCRM» (upsert по ID сделки).
 * ============================================================
 */

var DEAL_COLS = 18;
var DEAL_HEADERS = [
  'ID сделки', 'Название сделки', 'Воронка', 'Этап сделки', 'Категория статуса',
  'Сумма (₸)', 'Дата создания', 'utm_source', 'utm_medium', 'utm_campaign',
  'utm_content', 'utm_term', 'UTM ID', 'Теги сделки', 'Ссылка в AmoCRM',
  'Посадочная страница', 'Маркетинг janamen1.kz', 'Дата закрытия'
];

/** Точка входа для триггера и меню: инкрементальная (или продолжение полной) синхронизация */
function syncAmoCrmDeals() {
  return runSync_();
}

/** Триггер-продолжение: удаляет свой одноразовый триггер и продолжает */
function syncContinuation() {
  deleteTriggersByHandler_('syncContinuation');
  return runSync_();
}

/** Полная перезагрузка всей базы с нуля (запускать вручную при необходимости) */
function fullResync() {
  var p = PropertiesService.getScriptProperties();
  p.deleteProperty('SYNC_FULL_DONE');
  p.deleteProperty('SYNC_BACKFILL_PAGE');
  p.deleteProperty('SYNC_BACKFILL_STARTED');
  return runSync_();
}

function runSync_() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) {
    return { skipped: true, reason: 'Синхронизация уже выполняется' };
  }

  var t0 = Date.now();
  var props = PropertiesService.getScriptProperties();
  try {
    var ss = getSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.SHEETS.DEALS);
    if (!sheet) {
      setupSpreadsheet();
      sheet = ss.getSheetByName(CONFIG.SHEETS.DEALS);
    }
    sheet.getRange(1, 1, 1, DEAL_COLS).setValues([DEAL_HEADERS]);

    var statusMap = fetchPipelinesAndStatuses();

    // Существующие строки в память
    var lastRow = sheet.getLastRow();
    var rows = lastRow > 1 ? sheet.getRange(2, 1, lastRow - 1, DEAL_COLS).getValues() : [];
    var index = {};
    for (var i = 0; i < rows.length; i++) {
      var rid = String(rows[i][0]).trim();
      if (rid) index[rid] = i;
    }

    var fullDone = props.getProperty('SYNC_FULL_DONE') === 'true';
    if (fullDone && rows.length === 0) {           // таблицу очистили — грузим заново
      fullDone = false;
      props.deleteProperty('SYNC_BACKFILL_PAGE');
    }

    var runStartTs = Math.floor(Date.now() / 1000);
    var page = 1;
    var query = '';
    if (!fullDone) {
      page = Number(props.getProperty('SYNC_BACKFILL_PAGE')) || 1;
      if (page === 1) props.setProperty('SYNC_BACKFILL_STARTED', String(runStartTs));
      query = '&order[id]=asc';
    } else {
      var since = (Number(props.getProperty('SYNC_LAST_TS')) || runStartTs) - 600; // запас 10 мин
      query = '&filter[updated_at][from]=' + since + '&order[updated_at]=asc';
    }

    var added = 0, updated = 0, finished = false, loopError = '';
    try {
      while (Date.now() - t0 < CONFIG.AMOCRM.TIME_BUDGET_MS) {
        var url = CONFIG.AMOCRM.BASE_URL + '/leads?limit=' + CONFIG.AMOCRM.PAGE_LIMIT + '&page=' + page + query;
        var data = amoGetJson_(url);
        var leads = (data && data._embedded && data._embedded.leads) || [];
        if (leads.length === 0) { finished = true; break; }

        for (var j = 0; j < leads.length; j++) {
          var row = leadToRow_(leads[j], statusMap);
          var key = String(leads[j].id);
          if (index[key] !== undefined) {
            rows[index[key]] = row;
            updated++;
          } else {
            index[key] = rows.length;
            rows.push(row);
            added++;
          }
        }
        page++;
        if (leads.length < CONFIG.AMOCRM.PAGE_LIMIT) { finished = true; break; }
        Utilities.sleep(200); // лимит AmoCRM ~7 запросов/сек
      }
    } catch (e) {
      loopError = String(e);          // сохраняем всё, что успели загрузить, и продолжим позже
      Logger.log('Сбой на странице ' + page + ': ' + loopError);
    }

    writeDealRows_(sheet, rows);

    if (!fullDone) {
      if (finished) {
        props.setProperty('SYNC_FULL_DONE', 'true');
        props.setProperty('SYNC_LAST_TS', props.getProperty('SYNC_BACKFILL_STARTED') || String(runStartTs));
        props.deleteProperty('SYNC_BACKFILL_PAGE');
      } else {
        props.setProperty('SYNC_BACKFILL_PAGE', String(page));
        ScriptApp.newTrigger('syncContinuation').timeBased().after(60 * 1000).create();
      }
    } else if (finished) {
      props.setProperty('SYNC_LAST_TS', String(runStartTs));
    }

    props.setProperty('SYNC_LAST_RUN_AT', String(Date.now()));
    props.setProperty('SYNC_LAST_RESULT', JSON.stringify({ added: added, updated: updated, finished: finished, total: rows.length }));

    SpreadsheetApp.flush();
    clearAnalyticsCache_();
    try { getFullAnalyticsCached(); } catch (e) { Logger.log('Прогрев кэша: ' + e); }

    var res = { mode: fullDone ? 'incremental' : 'backfill', added: added, updated: updated,
                total: rows.length, complete: finished, nextPage: page, error: loopError || undefined };
    Logger.log('Sync: ' + JSON.stringify(res));
    return res;
  } finally {
    lock.releaseLock();
  }
}

function writeDealRows_(sheet, rows) {
  if (!rows.length) return;
  var need = rows.length + 1;
  var max = sheet.getMaxRows();
  if (max < need) sheet.insertRowsAfter(max, need - max);
  sheet.getRange(2, 1, rows.length, DEAL_COLS).setValues(rows);
  sheet.getRange('F2:F').setNumberFormat('#,##0" ₸"');
  sheet.getRange('G2:G').setNumberFormat('yyyy-mm-dd hh:mm');
  sheet.getRange('R2:R').setNumberFormat('yyyy-mm-dd hh:mm');
}

/** GET к AmoCRM с повтором при 429/5xx. 204 → null */
function amoGetJson_(url) {
  var lastErr = '';
  for (var attempt = 0; attempt < 5; attempt++) {
    try {
      var resp = UrlFetchApp.fetch(url, {
        method: 'get',
        headers: { 'Authorization': 'Bearer ' + CONFIG.AMOCRM.ACCESS_TOKEN, 'Content-Type': 'application/json' },
        muteHttpExceptions: true
      });
      var code = resp.getResponseCode();
      if (code === 204) return null;
      if (code === 200) {
        var body = resp.getContentText();
        return body ? JSON.parse(body) : null;
      }
      lastErr = 'HTTP ' + code + ': ' + resp.getContentText().substring(0, 200);
      if (code === 401 || code === 403) break;           // токен — повторять бессмысленно
      Utilities.sleep(1000 * (attempt + 1));             // 429 / 5xx — повтор
    } catch (e) {                                        // сетевой сбой UrlFetchApp
      lastErr = String(e);
      Utilities.sleep(1500 * (attempt + 1));
    }
  }
  throw new Error('AmoCRM API: ' + lastErr);
}

/** Сделка AmoCRM → строка листа (18 колонок) */
function leadToRow_(lead, statusMap) {
  var info = statusMap[lead.pipeline_id + ':' + lead.status_id] || { pipeline: 'Воронка #' + lead.pipeline_id, status: 'Статус #' + lead.status_id };
  var sName = (info.status || '').toUpperCase();

  // Целевой статус: Воронка продаж, Этап 2 — «Успешно реализовано» (ID 142)
  var category = 'В работе';
  if (lead.status_id === 142) category = 'Успешно реализовано';
  else if (lead.status_id === 143 || CONFIG.AMOCRM.LOST_STATUS_IDS.indexOf(lead.status_id) !== -1 ||
           sName.indexOf('ЗАКРЫТО И НЕ') !== -1) category = 'Отказ';

  var f = { src: '', med: '', cmp: '', cnt: '', trm: '', uid: '', page: '' };
  var cfs = lead.custom_fields_values || [];
  for (var k = 0; k < cfs.length; k++) {
    var cf = cfs[k];
    var val = cf.values && cf.values[0] && cf.values[0].value != null ? String(cf.values[0].value).trim() : '';
    switch (cf.field_id) {
      case 679639: f.src = val; break;
      case 679635: f.med = val; break;
      case 679637: f.cmp = val; break;
      case 679633: f.cnt = val; break;
      case 679641: f.trm = val; break;
      case 833139: f.uid = val; break;
      case 849891: if (val) f.page = val; break;
      case 833007: if (!f.page && val) f.page = val; break;
    }
  }

  // Если UTM-поля пустые, но метки есть в ссылке страницы — достаём их оттуда
  var fromUrl = parseUtmFromUrl_(f.page);
  if (!f.src) f.src = fromUrl.utm_source || '';
  if (!f.med) f.med = fromUrl.utm_medium || '';
  if (!f.cmp) f.cmp = fromUrl.utm_campaign || '';
  if (!f.cnt) f.cnt = fromUrl.utm_content || '';
  if (!f.trm) f.trm = fromUrl.utm_term || '';
  if (!f.uid) f.uid = fromUrl.utm_id || '';

  // Нормализация (нижний регистр — как в правилах реестра)
  var src = (f.src || 'direct/none').toLowerCase();
  var med = (f.med || 'none').toLowerCase();
  var cmp = (f.cmp || 'none').toLowerCase();

  var tags = (lead._embedded && lead._embedded.tags) ? lead._embedded.tags.map(function (t) { return t.name; }).join(', ') : '';

  return [
    String(lead.id),
    lead.name || 'Без названия',
    info.pipeline,
    info.status,
    category,
    lead.price || 0,
    lead.created_at ? new Date(lead.created_at * 1000) : '',
    src, med, cmp,
    (f.cnt || '').toLowerCase(),
    (f.trm || '').toLowerCase(),
    f.uid,
    tags,
    'https://' + CONFIG.AMOCRM.SUBDOMAIN + '.amocrm.ru/leads/detail/' + lead.id,
    f.page,
    detectMarketingSection_(f.page),
    lead.closed_at ? new Date(lead.closed_at * 1000) : ''
  ];
}

function parseUtmFromUrl_(url) {
  var out = {};
  if (!url) return out;
  var q = url.indexOf('?');
  if (q < 0) return out;
  var qs = url.substring(q + 1).split('#')[0].split('&');
  for (var i = 0; i < qs.length; i++) {
    var eq = qs[i].indexOf('=');
    if (eq < 0) continue;
    var key = qs[i].substring(0, eq).toLowerCase();
    if (key.indexOf('utm_') !== 0) continue;
    var v = qs[i].substring(eq + 1).replace(/\+/g, ' ');
    try { v = decodeURIComponent(v); } catch (e) {}
    out[key] = v.trim();
  }
  return out;
}

/** Раздел маркетингового домена janamen1.kz по ссылке страницы */
function detectMarketingSection_(page) {
  var p = String(page || '').toLowerCase();
  if (p.indexOf(CONFIG.MARKETING_DOMAIN) === -1) return 'Общий трафик';
  var path = p.split('?')[0].split('#')[0].replace(/^https?:\/\//, '').replace(CONFIG.MARKETING_DOMAIN, '').replace(/\/+$/, '');
  return CONFIG.MARKETING_DOMAIN + (path || ' (Главная)');
}

/** Маппинг «pipelineId:statusId» → { pipeline, status } */
function fetchPipelinesAndStatuses() {
  var statusMap = {};
  try {
    var data = amoGetJson_(CONFIG.AMOCRM.BASE_URL + '/leads/pipelines');
    var pipelines = (data && data._embedded && data._embedded.pipelines) || [];
    for (var i = 0; i < pipelines.length; i++) {
      var p = pipelines[i];
      var statuses = (p._embedded && p._embedded.statuses) || [];
      for (var j = 0; j < statuses.length; j++) {
        // ID 142/143 общие для всех воронок — ключ «воронка:статус»
        statusMap[p.id + ':' + statuses[j].id] = { pipeline: p.name, status: statuses[j].name };
      }
    }
  } catch (err) {
    Logger.log('Ошибка при получении воронок: ' + err);
  }
  return statusMap;
}
