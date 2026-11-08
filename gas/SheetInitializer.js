/**
 * ============================================================
 * SheetInitializer.js — Первоначальная настройка и оформление листов
 * ============================================================
 */

function setupSpreadsheet() {
  var ss = getSpreadsheet();
  if (!ss) {
    throw new Error('Не удалось открыть таблицу. Проверьте SPREADSHEET_ID в Config.js');
  }

  // 1. Создаем / получаем листы
  var sheetTaxonomy = getOrCreateSheet(ss, CONFIG.SHEETS.TAXONOMY);
  var sheetDeals = getOrCreateSheet(ss, CONFIG.SHEETS.DEALS);
  var sheetRegistry = getOrCreateSheet(ss, CONFIG.SHEETS.REGISTRY);
  var sheetMarketing = getOrCreateSheet(ss, CONFIG.SHEETS.MARKETING_DASHBOARD);
  var sheetDashboard = getOrCreateSheet(ss, CONFIG.SHEETS.DASHBOARD);

  // Упорядочим листы
  ss.setActiveSheet(sheetTaxonomy);
  ss.moveActiveSheet(5);
  ss.setActiveSheet(sheetDeals);
  ss.moveActiveSheet(4);
  ss.setActiveSheet(sheetRegistry);
  ss.moveActiveSheet(3);
  ss.setActiveSheet(sheetDashboard);
  ss.moveActiveSheet(2);
  ss.setActiveSheet(sheetMarketing);
  ss.moveActiveSheet(1);

  // 2. Настраиваем Справочники
  setupTaxonomySheet(sheetTaxonomy);

  // 3. Настраиваем лист Сделок AmoCRM
  setupDealsSheet(sheetDeals);

  // 4. Настраиваем лист Реестра UTM
  setupRegistrySheet(sheetRegistry, sheetTaxonomy);

  // 5. Настраиваем Дашборд Отдела Маркетинга (janamen1.kz)
  setupMarketingDashboardSheet(sheetMarketing);

  // 6. Настраиваем Общий Дашборд
  setupDashboardSheet(sheetDashboard);

  SpreadsheetApp.flush();
  return 'Таблица успешно инициализирована!';
}

/**
 * Получает или создает лист с заданным именем
 */
function getOrCreateSheet(ss, name) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
  }
  return sheet;
}

/**
 * Очищает форматирование и старые сетки
 */
function styleHeaderRange(range, bgColor, fgColor) {
  range.setBackground(bgColor || '#1e3a8a')
       .setFontColor(fgColor || '#ffffff')
       .setFontWeight('bold')
       .setFontFamily('Roboto')
       .setFontSize(10)
       .setHorizontalAlignment('center')
       .setVerticalAlignment('middle')
       .setWrap(true);
}

/**
 * ────────────────────────────────────────────────────────────
 * 1. Лист «Справочники»
 * ────────────────────────────────────────────────────────────
 */
function setupTaxonomySheet(sheet) {
  sheet.clear();
  sheet.setTabColor('#64748b');

  var headers = [
    'Базовые URL сайтов',
    'Источники (utm_source)',
    'Каналы (utm_medium)',
    'Теги / Направления',
    'Статусы UTM'
  ];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  styleHeaderRange(sheet.getRange(1, 1, 1, headers.length), '#334155');
  sheet.setRowHeight(1, 36);
  sheet.setFrozenRows(1);

  var landings = CONFIG.DEFAULT_LANDINGS.map(function(item) { return [item.url]; });
  var sources = CONFIG.DEFAULT_SOURCES.map(function(item) { return [item]; });
  var mediums = CONFIG.DEFAULT_MEDIUMS.map(function(item) { return [item]; });
  var tags = CONFIG.DEFAULT_TAGS.map(function(item) { return [item]; });
  var statuses = [['Активна'], ['Тест'], ['Приостановлена'], ['Завершена'], ['Архив']];

  if (landings.length) sheet.getRange(2, 1, landings.length, 1).setValues(landings);
  if (sources.length) sheet.getRange(2, 2, sources.length, 1).setValues(sources);
  if (mediums.length) sheet.getRange(2, 3, mediums.length, 1).setValues(mediums);
  if (tags.length) sheet.getRange(2, 4, tags.length, 1).setValues(tags);
  if (statuses.length) sheet.getRange(2, 5, statuses.length, 1).setValues(statuses);

  sheet.setColumnWidth(1, 320);
  sheet.setColumnWidth(2, 180);
  sheet.setColumnWidth(3, 180);
  sheet.setColumnWidth(4, 220);
  sheet.setColumnWidth(5, 150);
}

/**
 * ────────────────────────────────────────────────────────────
 * 2. Лист «Сделки AmoCRM»
 * ────────────────────────────────────────────────────────────
 */
function setupDealsSheet(sheet) {
  sheet.clear();
  sheet.setTabColor('#0284c7');

  var headers = [
    'ID сделки',          // A (1)
    'Название сделки',    // B (2)
    'Воронка',            // C (3)
    'Этап сделки',        // D (4)
    'Категория статуса',  // E (5) -> Успешно реализовано / В работе / Отказ
    'Сумма (₸)',          // F (6)
    'Дата создания',      // G (7)
    'utm_source',         // H (8)
    'utm_medium',         // I (9)
    'utm_campaign',       // J (10)
    'utm_content',        // K (11)
    'utm_term',           // L (12)
    'UTM ID',             // M (13)
    'Теги сделки',        // N (14)
    'Ссылка в AmoCRM',    // O (15)
    'Посадочная страница',// P (16)
    'Маркетинг janamen1.kz' // Q (17)
  ];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  styleHeaderRange(sheet.getRange(1, 1, 1, headers.length), '#0369a1');
  sheet.setRowHeight(1, 38);
  sheet.setFrozenRows(1);

  sheet.setColumnWidth(1, 110);
  sheet.setColumnWidth(2, 220);
  sheet.setColumnWidth(3, 140);
  sheet.setColumnWidth(4, 160);
  sheet.setColumnWidth(5, 160);
  sheet.setColumnWidth(6, 120);
  sheet.setColumnWidth(7, 130);
  sheet.setColumnWidth(8, 130);
  sheet.setColumnWidth(9, 130);
  sheet.setColumnWidth(10, 160);
  sheet.setColumnWidth(11, 130);
  sheet.setColumnWidth(12, 130);
  sheet.setColumnWidth(13, 120);
  sheet.setColumnWidth(14, 180);
  sheet.setColumnWidth(15, 200);
  sheet.setColumnWidth(16, 260);
  sheet.setColumnWidth(17, 240);

  // Формат валюты
  sheet.getRange('F2:F').setNumberFormat('#,##0" ₸"');
  // Формат даты
  sheet.getRange('G2:G').setNumberFormat('yyyy-mm-dd hh:mm');
}

/**
 * ────────────────────────────────────────────────────────────
 * 3. Лист «Реестр UTM»
 * ────────────────────────────────────────────────────────────
 */
function setupRegistrySheet(sheet, taxonomySheet) {
  sheet.clear();
  sheet.setTabColor('#16a34a');

  var headers = [
    'ID',                    // A (1)
    'Дата создания',         // B (2)
    'Базовый URL',           // C (3)
    'utm_source',            // D (4)
    'utm_medium',            // E (5)
    'utm_campaign',          // F (6)
    'utm_content',           // G (7)
    'utm_term',              // H (8)
    'Готовая UTM-ссылка',    // I (9) - автоформула
    'Тег / Категория',       // J (10)
    'Ответственный',         // K (11)
    'Статус',                // L (12)
    'Бюджет / Расход (₸)',   // M (13)
    'Описание / Инфо',       // N (14)
    'Лидов (CRM)',                     // O (15) - автоформула
    'Успешно реализовано (142)',       // P (16) - статус «Успешно реализовано» (Этап 2 / Воронка продаж)
    'Выручка (₸)',                     // Q (17) - сумма подтвержденных чеков
    'Конверсия (%)',                   // R (18) - Оплачено / Лиды
    'CPL (₸)',                         // S (19) - автоформула
    'CAC (₸)',                         // T (20) - автоформула
    'ROMI (%)'                         // U (21) - автоформула
  ];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  styleHeaderRange(sheet.getRange(1, 1, 1, headers.length), '#15803d');
  sheet.setRowHeight(1, 40);
  sheet.setFrozenRows(1);

  // Настройка ширин
  sheet.setColumnWidth(1, 80);   // ID
  sheet.setColumnWidth(2, 110);  // Дата
  sheet.setColumnWidth(3, 220);  // Базовый URL
  sheet.setColumnWidth(4, 130);  // Source
  sheet.setColumnWidth(5, 130);  // Medium
  sheet.setColumnWidth(6, 170);  // Campaign
  sheet.setColumnWidth(7, 130);  // Content
  sheet.setColumnWidth(8, 120);  // Term
  sheet.setColumnWidth(9, 320);  // Ссылка
  sheet.setColumnWidth(10, 160); // Тег
  sheet.setColumnWidth(11, 130); // Ответственный
  sheet.setColumnWidth(12, 110); // Статус
  sheet.setColumnWidth(13, 130); // Расход
  sheet.setColumnWidth(14, 180); // Описание
  sheet.setColumnWidth(15, 100); // Лиды
  sheet.setColumnWidth(16, 150); // Успешно реализовано
  sheet.setColumnWidth(17, 150); // Выручка
  sheet.setColumnWidth(18, 110); // CR
  sheet.setColumnWidth(19, 100); // CPL
  sheet.setColumnWidth(20, 100); // CAC
  sheet.setColumnWidth(21, 100); // ROMI

  // Выпадающие списки (Data Validation)
  var sourceRule = SpreadsheetApp.newDataValidation()
    .requireValueInRange(taxonomySheet.getRange('B2:B50'))
    .setAllowInvalid(true)
    .build();
  sheet.getRange('D2:D1000').setDataValidation(sourceRule);

  var mediumRule = SpreadsheetApp.newDataValidation()
    .requireValueInRange(taxonomySheet.getRange('C2:C50'))
    .setAllowInvalid(true)
    .build();
  sheet.getRange('E2:E1000').setDataValidation(mediumRule);

  var tagRule = SpreadsheetApp.newDataValidation()
    .requireValueInRange(taxonomySheet.getRange('D2:D50'))
    .setAllowInvalid(true)
    .build();
  sheet.getRange('J2:J1000').setDataValidation(tagRule);

  var statusRule = SpreadsheetApp.newDataValidation()
    .requireValueInRange(taxonomySheet.getRange('E2:E20'))
    .setAllowInvalid(true)
    .build();
  sheet.getRange('L2:L1000').setDataValidation(statusRule);

  // Форматирование чисел
  sheet.getRange('B2:B1000').setNumberFormat('yyyy-mm-dd');
  sheet.getRange('M2:M1000').setNumberFormat('#,##0" ₸"');
  sheet.getRange('O2:P1000').setNumberFormat('#,##0');
  sheet.getRange('Q2:Q1000').setNumberFormat('#,##0" ₸"');
  sheet.getRange('R2:R1000').setNumberFormat('0.0%');
  sheet.getRange('S2:T1000').setNumberFormat('#,##0" ₸"');
  sheet.getRange('U2:U1000').setNumberFormat('0.0%');

  // Добавим примеры для наглядности (ориентация на статус «Успешно реализовано»)
  var sampleRows = [
    [
      'UTM-001',
      new Date(),
      'https://janamen1.kz/influence',
      'instagram',
      'influencer',
      'blogger_danik',
      'stories_review',
      'danik20',
      '=IF(C2="","", C2 & IF(ISNUMBER(FIND("?", C2)), "&", "?") & "utm_source=" & D2 & "&utm_medium=" & E2 & "&utm_campaign=" & F2 & IF(G2="","", "&utm_content=" & G2) & IF(H2="","", "&utm_term=" & H2))',
      'Инфлюенс / Блогеры',
      'Маркетолог',
      'Активна',
      150000,
      'Блогер Даник — обзор витаминов',
      '=IF(F2="","", COUNTIFS(\'📥 Сделки AmoCRM\'!$H:$H, D2, \'📥 Сделки AmoCRM\'!$J:$J, F2))',
      '=IF(F2="","", COUNTIFS(\'📥 Сделки AmoCRM\'!$H:$H, D2, \'📥 Сделки AmoCRM\'!$J:$J, F2, \'📥 Сделки AmoCRM\'!$E:$E, "Успешно реализовано"))',
      '=IF(F2="","", SUMIFS(\'📥 Сделки AmoCRM\'!$F:$F, \'📥 Сделки AmoCRM\'!$H:$H, D2, \'📥 Сделки AmoCRM\'!$J:$J, F2, \'📥 Сделки AmoCRM\'!$E:$E, "Успешно реализовано"))',
      '=IF(O2>0, P2/O2, 0)',
      '=IF(O2>0, M2/O2, 0)',
      '=IF(P2>0, M2/P2, 0)',
      '=IF(M2>0, (Q2 - M2)/M2, 0)'
    ],
    [
      'UTM-002',
      new Date(),
      'https://janamen1.kz/lidmagnit',
      'facebook',
      'nikita',
      'leads_5442',
      'video_energy_1',
      '',
      '=IF(C3="","", C3 & IF(ISNUMBER(FIND("?", C3)), "&", "?") & "utm_source=" & D3 & "&utm_medium=" & E3 & "&utm_campaign=" & F3 & IF(G3="","", "&utm_content=" & G3) & IF(H3="","", "&utm_term=" & H3))',
      'Таргет FB/Insta',
      'Никита',
      'Активна',
      120000,
      'Лид-магнит тест таргета',
      '=IF(F3="","", COUNTIFS(\'📥 Сделки AmoCRM\'!$H:$H, D3, \'📥 Сделки AmoCRM\'!$J:$J, F3))',
      '=IF(F3="","", COUNTIFS(\'📥 Сделки AmoCRM\'!$H:$H, D3, \'📥 Сделки AmoCRM\'!$J:$J, F3, \'📥 Сделки AmoCRM\'!$E:$E, "Успешно реализовано"))',
      '=IF(F3="","", SUMIFS(\'📥 Сделки AmoCRM\'!$F:$F, \'📥 Сделки AmoCRM\'!$H:$H, D3, \'📥 Сделки AmoCRM\'!$J:$J, F3, \'📥 Сделки AmoCRM\'!$E:$E, "Успешно реализовано"))',
      '=IF(O3>0, P3/O3, 0)',
      '=IF(O3>0, M3/O3, 0)',
      '=IF(P3>0, M3/P3, 0)',
      '=IF(M3>0, (Q3 - M3)/M3, 0)'
    ]
  ];

  sheet.getRange(2, 1, sampleRows.length, headers.length).setValues(sampleRows);
}

/**
 * ────────────────────────────────────────────────────────────
 * 3.5 Лист «Отдел Маркетинга (janamen1.kz)»
 * ────────────────────────────────────────────────────────────
 */
function setupMarketingDashboardSheet(sheet) {
  sheet.clear();
  sheet.setTabColor('#2563eb');

  // Заголовок
  sheet.getRange('A1:J1').merge()
       .setValue('🎯 JANA MEN — ДАШБОРД ОТДЕЛА МАРКЕТИНГА (janamen1.kz)')
       .setBackground('#1e3a8a')
       .setFontColor('#ffffff')
       .setFontSize(14)
       .setFontWeight('bold')
       .setHorizontalAlignment('center')
       .setVerticalAlignment('middle');
  sheet.setRowHeight(1, 45);

  sheet.getRange('A2:J2').merge()
       .setValue('Выделенный домен: https://janamen1.kz | Целевая конверсия: Воронка продаж, Этап 2 — «Успешно реализовано» (Status 142)')
       .setBackground('#1d4ed8')
       .setFontColor('#eff6ff')
       .setFontSize(10)
       .setHorizontalAlignment('center');
  sheet.setRowHeight(2, 24);

  // Плашки KPI для janamen1.kz
  var kpis = [
    { title: 'ЛИДОВ janamen1.kz', formula: '=COUNTIF(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz*")', format: '#,##0', col: 1 },
    { title: 'ОПЛАЧЕНО (СТАТУС 142)', formula: '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', format: '#,##0', col: 3 },
    { title: 'ВЫРУЧКА janamen1.kz', formula: '=SUMIFS(\'📥 Сделки AmoCRM\'!$F$2:$F, \'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', format: '#,##0" ₸"', col: 5 },
    { title: 'СРЕДНИЙ ЧЕК', formula: '=IF(C5>0, E5/C5, 0)', format: '#,##0" ₸"', col: 7 },
    { title: 'КОНВЕРСИЯ CR (%)', formula: '=IF(A5>0, C5/A5, 0)', format: '0.0%', col: 9 }
  ];

  kpis.forEach(function(k) {
    var c = k.col;
    sheet.getRange(4, c, 1, 2).merge()
         .setValue(k.title)
         .setBackground('#f1f5f9')
         .setFontColor('#475569')
         .setFontWeight('bold')
         .setFontSize(9)
         .setHorizontalAlignment('center');

    sheet.getRange(5, c, 1, 2).merge()
         .setValue(k.formula)
         .setBackground('#ffffff')
         .setFontColor('#0f172a')
         .setFontWeight('bold')
         .setFontSize(16)
         .setHorizontalAlignment('center')
         .setNumberFormat(k.format);

    sheet.getRange(4, c, 2, 2).setBorder(true, true, true, true, false, false, '#cbd5e1', SpreadsheetApp.BorderStyle.SOLID);
  });
  sheet.setRowHeight(4, 24);
  sheet.setRowHeight(5, 36);

  // Таблица 1: Посадочные страницы и поддомены janamen1.kz
  sheet.getRange('A8:J8').merge()
       .setValue('📄 ЭФФЕКТИВНОСТЬ ПОСАДОЧНЫХ СТРАНИЦ JANAMEN1.KZ')
       .setBackground('#1e40af')
       .setFontColor('#ffffff')
       .setFontWeight('bold')
       .setFontSize(11)
       .setHorizontalAlignment('left')
       .setVerticalAlignment('middle');
  sheet.setRowHeight(8, 30);

  var pageHeaders = [
    'Страница / Раздел',     // A (1)
    'Назначение',             // B (2)
    'Лидов всего',            // C (3)
    'Оплачено (142)',         // D (4)
    'Конверсия CR (%)',       // E (5)
    'Выручка (₸)',            // F (6)
    'Средний чек (₸)',        // G (7)
    'Топ источник',           // H (8)
    'Статус страницы',        // I (9)
    'Ссылка'                  // J (10)
  ];
  sheet.getRange(9, 1, 1, pageHeaders.length).setValues([pageHeaders]);
  styleHeaderRange(sheet.getRange(9, 1, 1, pageHeaders.length), '#2563eb');
  sheet.setRowHeight(9, 32);

  var subpages = [
    ['/influence', 'Инфлюенс / Блогеры', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/influence*")', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/influence*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(C10>0, D10/C10, 0)', '=SUMIFS(\'📥 Сделки AmoCRM\'!$F$2:$F, \'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/influence*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(D10>0, F10/D10, 0)', 'instagram', 'Активна', 'https://janamen1.kz/influence'],
    ['/lidmagnit', 'Лидмагнит (Гайд/Тест)', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/lidmagnit*")', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/lidmagnit*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(C11>0, D11/C11, 0)', '=SUMIFS(\'📥 Сделки AmoCRM\'!$F$2:$F, \'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/lidmagnit*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(D11>0, F11/D11, 0)', 'facebook / direct', 'Активна', 'https://janamen1.kz/lidmagnit'],
    ['/kaspiform', 'Kaspi-форма', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/kaspiform*")', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/kaspiform*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(C12>0, D12/C12, 0)', '=SUMIFS(\'📥 Сделки AmoCRM\'!$F$2:$F, \'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/kaspiform*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(D12>0, F12/D12, 0)', 'facebook (Никита)', 'Активна (Лидер CR)', 'https://janamen1.kz/kaspiform'],
    ['/inst-women', 'Instagram Women', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/inst-women*")', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/inst-women*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(C13>0, D13/C13, 0)', '=SUMIFS(\'📥 Сделки AmoCRM\'!$F$2:$F, \'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/inst-women*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(D13>0, F13/D13, 0)', 'instagram', 'Активна', 'https://janamen1.kz/inst-women'],
    ['/inst-men', 'Instagram Men', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/inst-men*")', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/inst-men*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(C14>0, D14/C14, 0)', '=SUMIFS(\'📥 Сделки AmoCRM\'!$F$2:$F, \'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/inst-men*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(D14>0, F14/D14, 0)', 'instagram bio', 'Активна', 'https://janamen1.kz/inst-men'],
    ['/fun', 'Воронка / Квиз (/fun)', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/fun*")', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/fun*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(C15>0, D15/C15, 0)', '=SUMIFS(\'📥 Сделки AmoCRM\'!$F$2:$F, \'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/fun*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(D15>0, F15/D15, 0)', 'quiz/bio', 'Активна', 'https://janamen1.kz/fun'],
    ['/vitamins-inst', 'Витамины Instagram', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/vitamins-inst*")', '=COUNTIFS(\'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/vitamins-inst*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(C16>0, D16/C16, 0)', '=SUMIFS(\'📥 Сделки AmoCRM\'!$F$2:$F, \'📥 Сделки AmoCRM\'!$P$2:$P, "*janamen1.kz/vitamins-inst*", \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', '=IF(D16>0, F16/D16, 0)', 'instagram', 'Активна', 'https://janamen1.kz/vitamins-inst']
  ];
  sheet.getRange(10, 1, subpages.length, pageHeaders.length).setValues(subpages);

  sheet.getRange('C10:D16').setNumberFormat('#,##0');
  sheet.getRange('E10:E16').setNumberFormat('0.0%');
  sheet.getRange('F10:G16').setNumberFormat('#,##0" ₸"');

  // Ширины колонок
  sheet.setColumnWidth(1, 150);
  sheet.setColumnWidth(2, 200);
  sheet.setColumnWidth(3, 110);
  sheet.setColumnWidth(4, 130);
  sheet.setColumnWidth(5, 130);
  sheet.setColumnWidth(6, 150);
  sheet.setColumnWidth(7, 130);
  sheet.setColumnWidth(8, 160);
  sheet.setColumnWidth(9, 140);
  sheet.setColumnWidth(10, 240);
}

/**
 * ────────────────────────────────────────────────────────────
 * 4. Лист «Сквозная Аналитика»
 * ────────────────────────────────────────────────────────────
 */
function setupDashboardSheet(sheet) {
  sheet.clear();
  sheet.setTabColor('#7c3aed');

  // Заголовок дашборда
  sheet.getRange('A1:J1').merge()
       .setValue('🚀 JANA MEN — СКВОЗНАЯ АНАЛИТИКА ТРАФИКА И ОКУПАЕМОСТИ КАНАЛОВ')
       .setBackground('#1e1b4b')
       .setFontColor('#ffffff')
       .setFontSize(14)
       .setFontWeight('bold')
       .setHorizontalAlignment('center')
       .setVerticalAlignment('middle');
  sheet.setRowHeight(1, 45);

  // Подзаголовок
  sheet.getRange('A2:J2').merge()
       .setValue('Автоматический расчет по данным сделок AmoCRM и Реестра маркетинговых UTM-меток')
       .setBackground('#312e81')
       .setFontColor('#e0e7ff')
       .setFontSize(10)
       .setHorizontalAlignment('center');
  sheet.setRowHeight(2, 24);

  // Плашки KPI (Строка 4-5)
  var kpis = [
    { title: 'ВСЕГО ЛИДОВ (CRM)', formula: '=COUNTA(\'📥 Сделки AmoCRM\'!A2:A)', format: '#,##0', col: 1 },
    { title: 'УСПЕШНО РЕАЛИЗОВАНО (142)', formula: '=COUNTIF(\'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")', format: '#,##0', col: 3 },
    { title: 'ВЫРУЧКА (СТАТУС 142)', formula: '=SUMIF(\'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано", \'📥 Сделки AmoCRM\'!$F$2:$F)', format: '#,##0" ₸"', col: 5 },
    { title: 'ОБЩИЙ РАСХОД', formula: '=SUM(\'🎯 Реестр UTM\'!$M$2:$M)', format: '#,##0" ₸"', col: 7 },
    { title: 'КОНВЕРСИЯ CR (%)', formula: '=IF(A5>0, C5/A5, 0)', format: '0.0%', col: 9 }
  ];

  kpis.forEach(function(k) {
    var c = k.col;
    sheet.getRange(4, c, 1, 2).merge()
         .setValue(k.title)
         .setBackground('#f1f5f9')
         .setFontColor('#475569')
         .setFontWeight('bold')
         .setFontSize(9)
         .setHorizontalAlignment('center');

    sheet.getRange(5, c, 1, 2).merge()
         .setValue(k.formula)
         .setBackground('#ffffff')
         .setFontColor('#0f172a')
         .setFontWeight('bold')
         .setFontSize(16)
         .setHorizontalAlignment('center')
         .setNumberFormat(k.format);

    sheet.getRange(4, c, 2, 2).setBorder(true, true, true, true, false, false, '#cbd5e1', SpreadsheetApp.BorderStyle.SOLID);
  });

  sheet.setRowHeight(4, 24);
  sheet.setRowHeight(5, 36);

  // Вторая строка KPI (ROMI, Средний чек, Размеченный трафик)
  var kpis2 = [
    { title: 'СРЕДНИЙ ЧЕК', formula: '=IF(C5>0, E5/C5, 0)', format: '#,##0" ₸"', col: 2 },
    { title: 'ОБЩИЙ ROMI (%)', formula: '=IF(G5>0, (E5-G5)/G5, 0)', format: '0.0%', col: 4 },
    { title: 'РАЗМЕЧЕНО UTM', formula: '=COUNTIFS(\'📥 Сделки AmoCRM\'!$H$2:$H, "<>", \'📥 Сделки AmoCRM\'!$H$2:$H, "<>direct/none")', format: '#,##0', col: 6 },
    { title: 'ДОЛЯ РАЗМЕЧЕННЫХ', formula: '=IF(A5>0, F8/A5, 0)', format: '0.0%', col: 8 }
  ];

  kpis2.forEach(function(k) {
    var c = k.col;
    sheet.getRange(7, c, 1, 2).merge()
         .setValue(k.title)
         .setBackground('#f1f5f9')
         .setFontColor('#475569')
         .setFontWeight('bold')
         .setFontSize(9)
         .setHorizontalAlignment('center');

    sheet.getRange(8, c, 1, 2).merge()
         .setValue(k.formula)
         .setBackground('#ffffff')
         .setFontColor('#0f172a')
         .setFontWeight('bold')
         .setFontSize(14)
         .setHorizontalAlignment('center')
         .setNumberFormat(k.format);

    sheet.getRange(7, c, 2, 2).setBorder(true, true, true, true, false, false, '#cbd5e1', SpreadsheetApp.BorderStyle.SOLID);
  });
  sheet.setRowHeight(7, 22);
  sheet.setRowHeight(8, 30);

  // Таблица 1: Сводка по источникам (utm_source)
  sheet.getRange('A11:J11').merge()
       .setValue('📈 ЭФФЕКТИВНОСТЬ ПО ПЛОЩАДКАМ (UTM_SOURCE)')
       .setBackground('#4338ca')
       .setFontColor('#ffffff')
       .setFontWeight('bold')
       .setFontSize(11)
       .setHorizontalAlignment('left')
       .setVerticalAlignment('middle');
  sheet.setRowHeight(11, 30);

  var sourceHeaders = [
    'Источник (utm_source)', // A (1)
    'Лидов всего',           // B (2)
    'Оплачено (142)',        // C (3)
    'Конверсия CR',          // D (4)
    'Выручка (₸)',           // E (5)
    'Средний чек (₸)',       // F (6)
    'Маркетинг бюджет (₸)',  // G (7)
    'CPL (₸)',               // H (8)
    'CAC (₸)',               // I (9)
    'ROMI (%)'               // J (10)
  ];
  sheet.getRange(12, 1, 1, sourceHeaders.length).setValues([sourceHeaders]);
  styleHeaderRange(sheet.getRange(12, 1, 1, sourceHeaders.length), '#4f46e5');
  sheet.setRowHeight(12, 32);

  var topSources = [
    'instagram',
    'tiktok',
    'facebook',
    'telegram',
    'youtube',
    'google',
    'kaspi',
    'whatsapp',
    'direct/none'
  ];

  var sourceRows = topSources.map(function(src, idx) {
    var r = 13 + idx;
    return [
      src,
      '=COUNTIF(\'📥 Сделки AmoCRM\'!$H$2:$H, A' + r + ')',
      '=COUNTIFS(\'📥 Сделки AmoCRM\'!$H$2:$H, A' + r + ', \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")',
      '=IF(B' + r + '>0, C' + r + '/B' + r + ', 0)',
      '=SUMIFS(\'📥 Сделки AmoCRM\'!$F$2:$F, \'📥 Сделки AmoCRM\'!$H$2:$H, A' + r + ', \'📥 Сделки AmoCRM\'!$E$2:$E, "Успешно реализовано")',
      '=IF(C' + r + '>0, E' + r + '/C' + r + ', 0)',
      '=SUMIF(\'🎯 Реестр UTM\'!$D$2:$D, A' + r + ', \'🎯 Реестр UTM\'!$M$2:$M)',
      '=IF(B' + r + '>0, G' + r + '/B' + r + ', 0)',
      '=IF(C' + r + '>0, G' + r + '/C' + r + ', 0)',
      '=IF(G' + r + '>0, (E' + r + '-G' + r + ')/G' + r + ', 0)'
    ];
  });

  sheet.getRange(13, 1, sourceRows.length, sourceHeaders.length).setValues(sourceRows);

  // Форматирование таблицы 1
  sheet.getRange('B13:C21').setNumberFormat('#,##0');
  sheet.getRange('D13:D21').setNumberFormat('0.0%');
  sheet.getRange('E13:G21').setNumberFormat('#,##0" ₸"');
  sheet.getRange('H13:I21').setNumberFormat('#,##0" ₸"');
  sheet.getRange('J13:J21').setNumberFormat('0.0%');

  // Итоговая строка таблицы источников
  var sumRow = 13 + sourceRows.length;
  sheet.getRange(sumRow, 1).setValue('ИТОГО:').setFontWeight('bold');
  sheet.getRange(sumRow, 2).setValue('=SUM(B13:B' + (sumRow - 1) + ')').setFontWeight('bold').setNumberFormat('#,##0');
  sheet.getRange(sumRow, 3).setValue('=SUM(C13:C' + (sumRow - 1) + ')').setFontWeight('bold').setNumberFormat('#,##0');
  sheet.getRange(sumRow, 4).setValue('=IF(B' + sumRow + '>0, C' + sumRow + '/B' + sumRow + ', 0)').setFontWeight('bold').setNumberFormat('0.0%');
  sheet.getRange(sumRow, 5).setValue('=SUM(E13:E' + (sumRow - 1) + ')').setFontWeight('bold').setNumberFormat('#,##0" ₸"');
  sheet.getRange(sumRow, 6).setValue('=IF(C' + sumRow + '>0, E' + sumRow + '/C' + sumRow + ', 0)').setFontWeight('bold').setNumberFormat('#,##0" ₸"');
  sheet.getRange(sumRow, 7).setValue('=SUM(G13:G' + (sumRow - 1) + ')').setFontWeight('bold').setNumberFormat('#,##0" ₸"');
  sheet.getRange(sumRow, 8).setValue('=IF(B' + sumRow + '>0, G' + sumRow + '/B' + sumRow + ', 0)').setFontWeight('bold').setNumberFormat('#,##0" ₸"');
  sheet.getRange(sumRow, 9).setValue('=IF(C' + sumRow + '>0, G' + sumRow + '/C' + sumRow + ', 0)').setFontWeight('bold').setNumberFormat('#,##0" ₸"');
  sheet.getRange(sumRow, 10).setValue('=IF(G' + sumRow + '>0, (E' + sumRow + '-G' + sumRow + ')/G' + sumRow + ', 0)').setFontWeight('bold').setNumberFormat('0.0%');
  sheet.getRange(sumRow, 1, 1, sourceHeaders.length).setBackground('#e0e7ff');

  // Ширины колонок дашборда
  sheet.setColumnWidth(1, 190);
  sheet.setColumnWidth(2, 110);
  sheet.setColumnWidth(3, 110);
  sheet.setColumnWidth(4, 120);
  sheet.setColumnWidth(5, 140);
  sheet.setColumnWidth(6, 130);
  sheet.setColumnWidth(7, 160);
  sheet.setColumnWidth(8, 110);
  sheet.setColumnWidth(9, 110);
  sheet.setColumnWidth(10, 110);
}
