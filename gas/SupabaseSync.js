/**
 * ============================================================
 * SupabaseSync.js — Регулярный запуск синхронизации AmoCRM -> Supabase
 * Сама синхронизация живёт на Vercel (/api/sync), здесь только расписание.
 *
 * Работает по курсору: запоминает, до какого момента всё уже синхронизировано,
 * и каждый запуск продолжает оттуда. Если запуск не успел — следующий доделает.
 * ============================================================
 */

var SUPABASE_SYNC_URL = 'https://janamen-utm.vercel.app/api/sync';
var SUPABASE_SYNC_EVERY_MIN = 10;          // как часто запускать
var SUPABASE_SYNC_OVERLAP_SEC = 5 * 60;    // перекрытие, чтобы не потерять сделки на границе
var SUPABASE_SYNC_RUN_BUDGET_MS = 4 * 60 * 1000; // GAS ограничивает запуск 6 минутами
var SUPABASE_SYNC_CURSOR_KEY = 'SUPABASE_SYNC_CURSOR';

/**
 * Синхронизирует всё, что изменилось с прошлого запуска.
 * @param {number=} catchUpHours при первом запуске — сколько часов назад начать
 */
function syncDealsToSupabase(catchUpHours) {
  var props = PropertiesService.getScriptProperties();
  var nowSec = Math.floor(Date.now() / 1000);
  var stored = Number(props.getProperty(SUPABASE_SYNC_CURSOR_KEY));
  // Триггер передаёт сюда объект события, поэтому число берём только если оно явно задано
  var hours = (typeof catchUpHours === 'number' && catchUpHours > 0) ? catchUpHours : 1;

  var from = stored ? stored - SUPABASE_SYNC_OVERLAP_SEC : nowSec - hours * 3600;
  var t0 = Date.now();
  var total = 0;
  var complete = false;

  while (Date.now() - t0 < SUPABASE_SYNC_RUN_BUDGET_MS) {
    var resp = UrlFetchApp.fetch(SUPABASE_SYNC_URL + '?from=' + from, { muteHttpExceptions: true });
    var code = resp.getResponseCode();
    var body = {};
    try { body = JSON.parse(resp.getContentText()); } catch (e) {}

    if (code !== 200) {
      throw new Error('Синхронизация Supabase: HTTP ' + code + ' ' + resp.getContentText().slice(0, 300));
    }
    total += body.synced || 0;

    if (body.complete || !body.next_from) { complete = true; break; }
    from = body.next_from;
    props.setProperty(SUPABASE_SYNC_CURSOR_KEY, String(from + SUPABASE_SYNC_OVERLAP_SEC)); // прогресс сохраняем сразу
  }

  // Всё догнали — следующий запуск начнёт с момента старта этого
  if (complete) props.setProperty(SUPABASE_SYNC_CURSOR_KEY, String(nowSec));

  Logger.log('Supabase: синхронизировано ' + total + ' сделок, ' + (complete ? 'всё догнали' : 'продолжим в следующий запуск'));
  return { synced: total, complete: complete };
}

/**
 * Включает автосинхронизацию с Supabase каждые 10 минут и догружает последние сутки.
 */
function setupSupabaseSyncTrigger() {
  deleteTriggersByHandler_('syncDealsToSupabase');
  PropertiesService.getScriptProperties().deleteProperty(SUPABASE_SYNC_CURSOR_KEY);
  ScriptApp.newTrigger('syncDealsToSupabase')
    .timeBased()
    .everyMinutes(SUPABASE_SYNC_EVERY_MIN)
    .create();
  var res = syncDealsToSupabase(24);
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast(
      'Портал обновляется каждые ' + SUPABASE_SYNC_EVERY_MIN + ' мин. Догружено сделок: ' + res.synced +
      (res.complete ? '' : ' (остаток догрузится автоматически)'),
      'Автосинхронизация Supabase включена', 8);
  } catch (e) {}
}

function clearSupabaseSyncTrigger() {
  deleteTriggersByHandler_('syncDealsToSupabase');
  try { SpreadsheetApp.getActiveSpreadsheet().toast('Автосинхронизация Supabase отключена', 'Триггер удалён', 5); } catch (e) {}
}
