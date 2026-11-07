/**
 * ============================================================
 * Menu.js — Меню в Google Таблице и Управление Триггерами
 * ============================================================
 */

function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🎯 Jana Men UTM & Аналитика')
    .addItem('🚀 1. Первоначальная настройка таблицы', 'setupSpreadsheet')
    .addSeparator()
    .addItem('⚡ 2. Синхронизировать сделки из AmoCRM', 'syncAmoCrmDeals')
    .addItem('🌐 3. Открыть веб-дашборд и генератор', 'showWebDashboardDialog')
    .addSeparator()
    .addItem('⏰ 4. Включить автообновление AmoCRM (каждые 2ч)', 'setupHourlyTrigger')
    .addItem('🛑 5. Отключить автообновление', 'clearHourlyTriggers')
    .addToUi();
}

/**
 * Диалог со ссылкой на веб-приложение
 */
function showWebDashboardDialog() {
  var ui = SpreadsheetApp.getUi();
  var webAppUrl = ScriptApp.getService().getUrl();

  var htmlContent = '<div style="font-family: sans-serif; padding: 15px; color: #1e293b;">'
    + '<h3 style="color: #1e3a8a; margin-top:0;">🚀 Внутренний портал Jana Men</h3>'
    + '<p>Генератор ссылок, валидация по тегам и живой дашборд аналитики доступны по ссылке:</p>';

  if (webAppUrl) {
    htmlContent += '<p><a href="' + webAppUrl + '" target="_blank" style="display:inline-block; background:#2563eb; color:#fff; padding:10px 18px; border-radius:6px; text-decoration:none; font-weight:bold;">Перейти в веб-приложение ↗</a></p>'
      + '<p style="font-size:12px; color:#64748b;">Вы также можете встроить эту ссылку в Tilda через iframe (блок T123) на своем внутреннем сайте.</p>';
  } else {
    htmlContent += '<p style="color:#d97706; font-weight:bold;">⚠️ Веб-приложение еще не опубликовано.</p>'
      + '<p style="font-size:13px;">Для публикации откройте редактор скрипта (Расширения → Apps Script), нажмите <b>Развернуть → Новое развертывание → Веб-приложение</b> (доступ: Все, у кого есть ссылка).</p>';
  }

  htmlContent += '</div>';

  var output = HtmlService.createHtmlOutput(htmlContent).setWidth(480).setHeight(240);
  ui.showModalDialog(output, '🎯 UTM Портал & Аналитика');
}

/**
 * Установка триггера регулярной синхронизации сделок
 */
function setupHourlyTrigger() {
  clearHourlyTriggers();
  ScriptApp.newTrigger('syncAmoCrmDeals')
    .timeBased()
    .everyHours(2)
    .create();

  SpreadsheetApp.getActiveSpreadsheet().toast('Автообновление включено (каждые 2 часа)', 'Триггер установлен', 5);
}

/**
 * Удаление триггеров синхронизации
 */
function clearHourlyTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'syncAmoCrmDeals') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  SpreadsheetApp.getActiveSpreadsheet().toast('Автообновление отключено', 'Триггеры удалены', 5);
}
