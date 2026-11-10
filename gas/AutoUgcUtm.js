/**
 * ============================================================
 * AutoUgcUtm.js — Автоматическая генерация UTM-ссылок для листов:
 * 1) "UGC" (Бартер за витамины)
 * 2) "Боксы" (Реестр боксов медийным людям)
 * ============================================================
 */

function onEdit(e) {
  if (!e || !e.range) return;
  var sheet = e.range.getSheet();
  if (!sheet) return;
  
  var sheetName = sheet.getName();
  var row = e.range.getRow();
  var col = e.range.getColumn();

  // 1. ЛИСТ "UGC"
  if (sheetName === 'UGC') {
    // Данные начинаются со строки 3
    if (row < 3) return;
    // C(3)=Менеджер, D(4)=Имя, E(5)=Ник/Ссылка, M(13)=Формат
    if (col === 3 || col === 4 || col === 5 || col === 13) {
      updateRowUtmUgc_(sheet, row);
    }
  }

  // 2. ЛИСТ "Боксы" (Реестр боксов медийным людям)
  if (sheetName === 'Боксы') {
    // Данные начинаются со строки 5 (строки 1-4 — шапка)
    if (row < 5) return;
    // C(3)=Менеджер, D(4)=Персона, F(6)=Ник/Ссылка, O(15)=Формат упоминания
    if (col === 3 || col === 4 || col === 6 || col === 15) {
      updateRowUtmBoxes_(sheet, row);
    }
  }
}

/**
 * Меню в Google Таблице
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🎯 Авто-UTM Jana Men')
    .addItem('⚡ Заполнить UTM для всех строк UGC (Бартер)', 'generateAllUgcUtmLinks')
    .addItem('🎁 Заполнить UTM для всех строк Боксов (Медийные)', 'generateAllBoxesUtmLinks')
    .addSeparator()
    .addItem('🔄 Обновить всё (UGC + Боксы)', 'generateAllUtmEverywhere')
    .addToUi();
}

/**
 * Обновление ссылки на листе UGC
 */
function updateRowUtmUgc_(sheet, row) {
  var rowValues = sheet.getRange(row, 1, 1, 16).getValues()[0];
  
  var managerRaw = rowValues[2];  // C (индекс 2)
  var nameRaw    = rowValues[3];  // D (индекс 3)
  var nickRaw    = rowValues[4];  // E (индекс 4)
  var formatRaw  = rowValues[12]; // M (индекс 12)

  var cleanNick = extractCleanNick_(nickRaw);
  if (!cleanNick && nameRaw) {
    cleanNick = transliterate_(nameRaw);
  }

  if (!cleanNick) return;

  var managerCode = getManagerCode_(managerRaw);
  var formatCode  = getFormatCode_(formatRaw, 'stories');

  var url = 'https://janamen1.kz/influence?utm_source=' + cleanNick
          + '&utm_medium=' + managerCode
          + '&utm_campaign=ugc_barter'
          + '&utm_content=' + formatCode;

  // Столбец P (16)
  sheet.getRange(row, 16).setValue(url);
}

/**
 * Обновление ссылки на листе "Боксы"
 */
function updateRowUtmBoxes_(sheet, row) {
  var rowValues = sheet.getRange(row, 1, 1, 16).getValues()[0];
  
  var managerRaw = rowValues[2];  // C (индекс 2) — Менеджер
  var personRaw  = rowValues[3];  // D (индекс 3) — Персона
  var nickRaw    = rowValues[5];  // F (индекс 5) — Ник / ссылка
  var formatRaw  = rowValues[14]; // O (индекс 14) — Формат упоминания

  var cleanNick = extractCleanNick_(nickRaw);
  if (!cleanNick && personRaw) {
    cleanNick = transliterate_(personRaw);
  }

  if (!cleanNick) return;

  var managerCode = getManagerCode_(managerRaw);
  var formatCode  = getFormatCode_(formatRaw, 'unboxing');

  var url = 'https://janamen1.kz/influence?utm_source=' + cleanNick
          + '&utm_medium=' + managerCode
          + '&utm_campaign=media_box'
          + '&utm_content=' + formatCode;

  // Столбец P (16) — Автоматический UTM
  sheet.getRange(row, 16).setValue(url);
}

/**
 * Массовая генерация для листа UGC
 */
function generateAllUgcUtmLinks() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('UGC');
  if (!sheet) {
    SpreadsheetApp.getUi().alert('Лист "UGC" не найден!');
    return;
  }

  var lastRow = sheet.getLastRow();
  if (lastRow < 3) {
    SpreadsheetApp.getUi().alert('В таблице UGC нет строк начиная с 3!');
    return;
  }

  var numRows = lastRow - 2;
  var range = sheet.getRange(3, 1, numRows, 16);
  var values = range.getValues();
  var count = 0;

  for (var i = 0; i < values.length; i++) {
    var row = values[i];
    var managerRaw = row[2];  // C
    var nameRaw    = row[3];  // D
    var nickRaw    = row[4];  // E
    var formatRaw  = row[12]; // M

    var cleanNick = extractCleanNick_(nickRaw);
    if (!cleanNick && nameRaw) {
      cleanNick = transliterate_(nameRaw);
    }

    if (cleanNick) {
      var managerCode = getManagerCode_(managerRaw);
      var formatCode  = getFormatCode_(formatRaw, 'stories');

      var url = 'https://janamen1.kz/influence?utm_source=' + cleanNick
              + '&utm_medium=' + managerCode
              + '&utm_campaign=ugc_barter'
              + '&utm_content=' + formatCode;

      row[15] = url; // P
      count++;
    }
  }

  range.setValues(values);
  SpreadsheetApp.getActiveSpreadsheet().toast('Сгенерировано для UGC: ' + count, 'Готово ✅', 5);
}

/**
 * Массовая генерация для листа "Боксы"
 */
function generateAllBoxesUtmLinks() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Боксы');
  if (!sheet) {
    SpreadsheetApp.getUi().alert('Лист "Боксы" не найден!');
    return;
  }

  var lastRow = sheet.getLastRow();
  if (lastRow < 5) {
    SpreadsheetApp.getUi().alert('На листе "Боксы" нет данных начиная со строки 5!');
    return;
  }

  var numRows = lastRow - 4;
  var range = sheet.getRange(5, 1, numRows, 16);
  var values = range.getValues();
  var count = 0;

  for (var i = 0; i < values.length; i++) {
    var row = values[i];
    var managerRaw = row[2];  // C (Менеджер)
    var personRaw  = row[3];  // D (Персона)
    var nickRaw    = row[5];  // F (Ник / ссылка)
    var formatRaw  = row[14]; // O (Формат упоминания)

    var cleanNick = extractCleanNick_(nickRaw);
    if (!cleanNick && personRaw) {
      cleanNick = transliterate_(personRaw);
    }

    if (cleanNick) {
      var managerCode = getManagerCode_(managerRaw);
      var formatCode  = getFormatCode_(formatRaw, 'unboxing');

      var url = 'https://janamen1.kz/influence?utm_source=' + cleanNick
              + '&utm_medium=' + managerCode
              + '&utm_campaign=media_box'
              + '&utm_content=' + formatCode;

      row[15] = url; // P (Автоматический UTM)
      count++;
    }
  }

  range.setValues(values);
  SpreadsheetApp.getActiveSpreadsheet().toast('Сгенерировано для Боксов: ' + count, 'Готово ✅', 5);
}

/**
 * Обновить сразу оба листа (UGC + Боксы)
 */
function generateAllUtmEverywhere() {
  generateAllUgcUtmLinks();
  generateAllBoxesUtmLinks();
}

/**
 * Извлечение чистого ника из ссылки или строки
 */
function extractCleanNick_(val) {
  if (!val) return '';
  var s = val.toString().trim();
  if (!s) return '';

  s = s.split('?')[0].split('#')[0].replace(/\/+$/, '');

  var m = s.match(/(?:instagram\.com\/|tiktok\.com\/@?)([a-zA-Z0-9._]+)/i);
  if (m && m[1]) {
    var cand = m[1].toLowerCase();
    if (cand !== 'p' && cand !== 'reel' && cand !== 'reels' && cand !== 'stories' && cand !== 'share') {
      return cand;
    }
  }

  if (s.indexOf('@') === 0) {
    return s.substring(1).replace(/[^a-zA-Z0-9._]/g, '').toLowerCase();
  }

  if (s.indexOf('http') === -1) {
    var clean = s.split(/\s+/)[0].replace(/[^a-zA-Z0-9._]/g, '').toLowerCase();
    if (clean) return clean;
  }

  return '';
}

/**
 * Определение кода менеджера (mpb1, mpb2, mpb3, mpb4)
 */
function getManagerCode_(name) {
  if (!name) return 'mpb1';
  var n = name.toString().toLowerCase().trim();
  if (n.indexOf('анельжан') !== -1 || n === 'mpb1') return 'mpb1';
  if (n.indexOf('алина') !== -1 || n === 'mpb2')    return 'mpb2';
  if (n.indexOf('алуа') !== -1 || n === 'mpb3')     return 'mpb3';
  if (n.indexOf('дарина') !== -1 || n === 'mpb4')   return 'mpb4';
  return 'mpb1';
}

/**
 * Определение формата креатива
 */
function getFormatCode_(format, defaultCode) {
  if (!format) return defaultCode || 'stories';
  var f = format.toString().toLowerCase().trim();
  if (f.indexOf('распаков') !== -1 || f.indexOf('unbox') !== -1) {
    return 'unboxing';
  }
  if (f.indexOf('reel') !== -1 && (f.indexOf('stori') !== -1 || f.indexOf('сторис') !== -1)) {
    return 'reels_stories';
  }
  if (f.indexOf('reel') !== -1) {
    return 'reels';
  }
  if (f.indexOf('stori') !== -1 || f.indexOf('сторис') !== -1 || f.indexOf('отметк') !== -1) {
    return 'stories';
  }
  return defaultCode || 'stories';
}

/**
 * Транслитерация имени блогера или персоны
 */
function transliterate_(str) {
  if (!str) return '';
  var ru = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh',
    'з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o',
    'п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts',
    'ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
    'ә':'a','і':'i','ң':'n','ғ':'g','ү':'u','ұ':'u','қ':'q','ө':'o','һ':'h'
  };
  return str.toString().toLowerCase().split('').map(function(char) {
    return ru[char] || char;
  }).join('').replace(/[^a-z0-9._]/g, '_').replace(/_+/g, '_').replace(/^_+|_+$/g, '');
}
