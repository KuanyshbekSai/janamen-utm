/**
 * ============================================================
 * AmoCrmSync.js — Синхронизация сделок и UTM-меток из AmoCRM
 * ============================================================
 */

/**
 * Основная функция синхронизации: скачивает свежие сделки и обновляет лист AmoCRM
 */
function syncAmoCrmDeals() {
  var ss = getSpreadsheet();
  var dealsSheet = ss.getSheetByName(CONFIG.SHEETS.DEALS);
  if (!dealsSheet) {
    setupSpreadsheet();
    dealsSheet = ss.getSheetByName(CONFIG.SHEETS.DEALS);
  }

  Logger.log('Начало синхронизации с AmoCRM...');

  // 1. Получаем справочник статусов и воронок для красивых названий
  var pipelineStatusMap = fetchPipelinesAndStatuses();

  // 2. Считываем уже существующие сделки в таблице, чтобы делать Upsert (не дублировать)
  var existingData = dealsSheet.getDataRange().getValues();
  var existingRowIndexById = {}; // leadId -> rowNumber (1-based)
  for (var i = 1; i < existingData.length; i++) {
    var rowId = String(existingData[i][0]).trim();
    if (rowId) {
      existingRowIndexById[rowId] = i + 1; // 1-based index in sheet
    }
  }

  // 3. Выгружаем сделки из AmoCRM
  var leads = fetchRecentLeadsFromAmoCRM(CONFIG.AMOCRM.MAX_DEALS_FETCH);
  Logger.log('Получено сделок из AmoCRM: ' + leads.length);

  if (!leads || leads.length === 0) {
    SpreadsheetApp.getActiveSpreadsheet().toast('Новых сделок в AmoCRM не найдено', 'AmoCRM Sync', 5);
    return;
  }

  var newRows = [];
  var updatedCount = 0;

  for (var j = 0; j < leads.length; j++) {
    var lead = leads[j];
    var leadId = String(lead.id);

    // Определяем статус и воронку
    var pipelineInfo = pipelineStatusMap[lead.status_id] || { pipeline: 'Воронка #' + lead.pipeline_id, status: 'Статус #' + lead.status_id };
    var sName = (pipelineInfo.status || '').toUpperCase();
    var statusCategory = 'В работе';

    // Целевой статус: «ПРОВЕРКА ПРОЙДЕНА» (и подтвержденные заказы доставки)
    if (lead.status_id === CONFIG.AMOCRM.STATUS_VERIFIED_CHECK_ID ||
        sName.indexOf('ПРОВЕРКА ПРОЙДЕНА') !== -1 ||
        CONFIG.AMOCRM.VERIFIED_STATUS_IDS.indexOf(lead.status_id) !== -1 ||
        sName.indexOf('ДОСТАВЛЕНО') !== -1) {
      statusCategory = 'Проверка пройдена';
    } else if (CONFIG.AMOCRM.LOST_STATUS_IDS.indexOf(lead.status_id) !== -1 ||
               sName.indexOf('ОТКАЗАНО') !== -1 ||
               sName.indexOf('ЗАКРЫТО И НЕ') !== -1) {
      statusCategory = 'Отказ';
    }

    // Парсим кастомные поля UTM
    var utmSource = '';
    var utmMedium = '';
    var utmCampaign = '';
    var utmContent = '';
    var utmTerm = '';
    var utmId = '';

    var cfs = lead.custom_fields_values || [];
    for (var k = 0; k < cfs.length; k++) {
      var cf = cfs[k];
      var name = (cf.field_name || '').toLowerCase();
      var code = (cf.field_code || '').toLowerCase();
      var val = cf.values && cf.values[0] && cf.values[0].value ? String(cf.values[0].value).trim() : '';

      if (name.indexOf('utm_source') !== -1 || code === 'utm_source') {
        utmSource = val.toLowerCase();
      } else if (name.indexOf('utm_medium') !== -1 || code === 'utm_medium') {
        utmMedium = val.toLowerCase();
      } else if (name.indexOf('utm_campaign') !== -1 || code === 'utm_campaign') {
        utmCampaign = val.toLowerCase();
      } else if (name.indexOf('utm_content') !== -1 || code === 'utm_content') {
        utmContent = val.toLowerCase();
      } else if (name.indexOf('utm_term') !== -1 || code === 'utm_term') {
        utmTerm = val.toLowerCase();
      } else if (name === 'utm_id' || code === 'utm_id') {
        utmId = val;
      }
    }

    if (!utmSource) utmSource = 'direct/none';
    if (!utmMedium) utmMedium = 'none';
    if (!utmCampaign) utmCampaign = 'none';

    // Теги
    var tags = (lead._embedded && lead._embedded.tags) ? lead._embedded.tags.map(function(t) { return t.name; }).join(', ') : '';

    // Ссылка на сделку в AmoCRM
    var leadUrl = 'https://' + CONFIG.AMOCRM.SUBDOMAIN + '.amocrm.ru/leads/detail/' + leadId;

    var createdAt = lead.created_at ? new Date(lead.created_at * 1000) : new Date();

    var rowValues = [
      leadId,
      lead.name || 'Без названия',
      pipelineInfo.pipeline,
      pipelineInfo.status,
      statusCategory,
      lead.price || 0,
      createdAt,
      utmSource,
      utmMedium,
      utmCampaign,
      utmContent,
      utmTerm,
      utmId,
      tags,
      leadUrl
    ];

    if (existingRowIndexById[leadId]) {
      // Обновляем статус, сумму, этап
      var targetRow = existingRowIndexById[leadId];
      dealsSheet.getRange(targetRow, 1, 1, rowValues.length).setValues([rowValues]);
      updatedCount++;
    } else {
      newRows.push(rowValues);
    }
  }

  // Добавляем новые сделки пачкой
  if (newRows.length > 0) {
    var startRow = dealsSheet.getLastRow() + 1;
    dealsSheet.getRange(startRow, 1, newRows.length, newRows[0].length).setValues(newRows);
  }

  SpreadsheetApp.flush();
  var msg = 'Синхронизация завершена! Новых: ' + newRows.length + ', Обновлено: ' + updatedCount;
  Logger.log(msg);
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast(msg, 'AmoCRM Sync', 5);
  } catch (e) {}

  return { newLeads: newRows.length, updatedLeads: updatedCount };
}

/**
 * Получает маппинг pipelineId -> statusName
 */
function fetchPipelinesAndStatuses() {
  var url = CONFIG.AMOCRM.BASE_URL + '/leads/pipelines';
  var statusMap = {};

  try {
    var response = UrlFetchApp.fetch(url, {
      method: 'get',
      headers: {
        'Authorization': 'Bearer ' + CONFIG.AMOCRM.ACCESS_TOKEN,
        'Content-Type': 'application/json'
      },
      muteHttpExceptions: true
    });

    if (response.getResponseCode() === 200) {
      var data = JSON.parse(response.getContentText());
      var pipelines = (data._embedded && data._embedded.pipelines) || [];
      for (var i = 0; i < pipelines.length; i++) {
        var p = pipelines[i];
        var statuses = (p._embedded && p._embedded.statuses) || [];
        for (var j = 0; j < statuses.length; j++) {
          var s = statuses[j];
          statusMap[s.id] = {
            pipeline: p.name,
            status: s.name
          };
        }
      }
    }
  } catch (err) {
    Logger.log('Ошибка при получении воронок: ' + err.toString());
  }

  return statusMap;
}

/**
 * Выгружает свежие сделки с пагинацией
 */
function fetchRecentLeadsFromAmoCRM(maxLeads) {
  var allLeads = [];
  var page = 1;
  var limit = CONFIG.AMOCRM.BATCH_SIZE || 50;
  var totalToFetch = maxLeads || 500;

  while (allLeads.length < totalToFetch) {
    var url = CONFIG.AMOCRM.BASE_URL + '/leads?limit=' + limit + '&page=' + page + '&order[created_at]=desc&with=contacts';
    try {
      var response = UrlFetchApp.fetch(url, {
        method: 'get',
        headers: {
          'Authorization': 'Bearer ' + CONFIG.AMOCRM.ACCESS_TOKEN,
          'Content-Type': 'application/json'
        },
        muteHttpExceptions: true
      });

      var code = response.getResponseCode();
      if (code === 204) {
        // Нет данных
        break;
      }
      if (code !== 200) {
        Logger.log('HTTP ' + code + ' при загрузке сделок: ' + response.getContentText());
        break;
      }

      var data = JSON.parse(response.getContentText());
      var leads = (data._embedded && data._embedded.leads) || [];
      if (leads.length === 0) break;

      allLeads = allLeads.concat(leads);

      if (leads.length < limit) break; // Последняя страница
      page++;

      // Пауза от rate limit
      Utilities.sleep(250);
    } catch (e) {
      Logger.log('Ошибка fetchRecentLeads: ' + e.toString());
      break;
    }
  }

  return allLeads;
}
