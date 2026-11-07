/**
 * ============================================================
 * WebApp.js — HTTP-сервер для Веб-интерфейса и Tilda Webhooks
 * ============================================================
 */

function doGet(e) {
  var action = (e && e.parameter && e.parameter.action) || 'view';

  // API: Получение данных реестра
  if (action === 'get_registry') {
    var registry = getRegistryData();
    return createJsonResponse({ success: true, data: registry });
  }

  // API: Получение аналитики
  if (action === 'get_analytics') {
    var summary = getAnalyticsSummary();
    return createJsonResponse({ success: true, data: summary });
  }

  // API: Получение справочников
  if (action === 'get_taxonomy') {
    return createJsonResponse({
      success: true,
      data: {
        landings: CONFIG.DEFAULT_LANDINGS,
        sources: CONFIG.DEFAULT_SOURCES,
        mediums: CONFIG.DEFAULT_MEDIUMS,
        tags: CONFIG.DEFAULT_TAGS
      }
    });
  }

  // API: Ручной запуск синхронизации из браузера
  if (action === 'sync_amocrm') {
    var syncResult = syncAmoCrmDeals();
    return createJsonResponse({ success: true, data: syncResult });
  }

  // По умолчанию: возвращаем HTML-дашборд
  var template = HtmlService.createTemplateFromFile('Dashboard');
  return template.evaluate()
    .setTitle('Jana Men — UTM Реестр и Сквозная Аналитика')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL); // Разрешает встраивание в Tilda через iframe!
}

function doPost(e) {
  try {
    var data = {};

    // 1. Проверяем, JSON ли это
    if (e.postData && e.postData.contents) {
      try {
        data = JSON.parse(e.postData.contents);
      } catch (jsonErr) {
        // Если не JSON, смотрим параметры запроса
        data = e.parameter || {};
      }
    } else {
      data = e.parameter || {};
    }

    // Поддержка полей из формы Tilda (name маппинг)
    var payload = {
      baseUrl: data.baseUrl || data.url || data['Базовый сайт'] || 'https://janamen1.kz/influence',
      source: data.source || data.utm_source || data['Источник'] || 'instagram',
      medium: data.medium || data.utm_medium || data['Канал'] || 'influencer',
      campaign: data.campaign || data.utm_campaign || data['Кампания'] || data['Блогер'],
      content: data.content || data.utm_content || data['Креатив'] || '',
      term: data.term || data.utm_term || data['Промокод'] || '',
      tag: data.tag || data['Категория'] || data['Тег'] || 'Инфлюенс / Блогеры',
      author: data.author || data['Ответственный'] || data['Имя'] || 'Маркетолог',
      budget: data.budget || data['Бюджет'] || data['Расход'] || 0,
      description: data.description || data['Описание'] || data['Комментарий'] || '',
      status: data.status || 'Активна'
    };

    var result = registerUtm(payload);

    return createJsonResponse(result);
  } catch (err) {
    return createJsonResponse({
      success: false,
      message: 'Ошибка при сохранении: ' + err.toString()
    });
  }
}

function createJsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Вспомогательная функция для включения HTML-паршиалов в шаблоны
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}
