/**
 * ============================================================
 * AutoUgcUtm.js — Автоматическая генерация UTM-ссылок для листа UGC
 * ============================================================
 * При вводе/изменении:
 *  - Столбец C (Менеджер: Анельжан, Алина, Алуа, Дарина)
 *  - Столбец D (Имя блогера)
 *  - Столбец E (Ник или ссылка на Instagram/TikTok)
 *  - Столбец M (Формат: REELS + STORIES, Серия сторис...)
 * 
 * В столбец P ("Промокод / UTM") автоматически подставляется ссылка:
 * https://janamen1.kz/influence?utm_source={ник}&utm_medium={mpb1/2/3}&utm_campaign=ugc_barter&utm_content={stories}
 */

function onEdit(e) {
  if (!e || !e.range) return;
  var sheet = e.range.getSheet();
  if (!sheet) return;
  
  var sheetName = sheet.getName();
  // Работаем на листе UGC
  if (sheetName !== 'UGC') return;

  var row = e.range.getRow();
  var col = e.range.getColumn();

  // Заголовки на строках 1 и 2, данные начинаются со строки 3
  if (row < 3) return;

  // Отслеживаем колонки C (3), D (4), E (5), M (13)
  if (col === 3 || col === 4 || col === 5 || col === 13) {
    updateRowUtm_(sheet, row);
  }
}

/**
 * Меню при открытии таблицы
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🎯 Авто-UTM Блогеров')
    .addItem('⚡ Заполнить правильные UTM для всех строк UGC', 'generateAllUgcUtmLinks')
    .addToUi();
}

/**
 * Обновление ссылки в одной строке
 */
function updateRowUtm_(sheet, row) {
  var rowValues = sheet.getRange(row, 1, 1, 16).getValues()[0];
  
  var managerRaw = rowValues[2]; // Столбец C (индекс 2)
  var nameRaw    = rowValues[3]; // Столбец D (индекс 3)
  var nickRaw    = rowValues[4]; // Столбец E (индекс 4)
  var formatRaw  = rowValues[12];// Столбец M (индекс 12)

  var cleanNick = extractCleanNick_(nickRaw);
  if (!cleanNick && nameRaw) {
    cleanNick = transliterate_(nameRaw);
  }

  // Если нет ни ника, ни имени — не генерируем
  if (!cleanNick) return;

  var managerCode = getManagerCode_(managerRaw);
  var formatCode = getFormatCode_(formatRaw);

  var url = 'https://janamen1.kz/influence?utm_source=' + cleanNick
          + '&utm_medium=' + managerCode
          + '&utm_campaign=ugc_barter'
          + '&utm_content=' + formatCode;

  // Столбец P (16) — Промокод / UTM
  sheet.getRange(row, 16).setValue(url);
}

/**
 * Массовая генерация для всех строк на листе UGC в 1 клик
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
    SpreadsheetApp.getUi().alert('В таблице нет данных начиная со строки 3!');
    return;
  }

  var numRows = lastRow - 2;
  var range = sheet.getRange(3, 1, numRows, 16);
  var values = range.getValues();
  var updatedCount = 0;

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
      var formatCode  = getFormatCode_(formatRaw);

      var url = 'https://janamen1.kz/influence?utm_source=' + cleanNick
              + '&utm_medium=' + managerCode
              + '&utm_campaign=ugc_barter'
              + '&utm_content=' + formatCode;

      row[15] = url; // P
      updatedCount++;
    }
  }

  range.setValues(values);
  SpreadsheetApp.getActiveSpreadsheet().toast('Сгенерировано и обновлено ссылок: ' + updatedCount, 'Готово ✅', 5);
}

/**
 * Извлечение чистого ника из ссылки или строки
 */
function extractCleanNick_(val) {
  if (!val) return '';
  var s = val.toString().trim();
  if (!s) return '';

  // Очистка от GET-параметров и хэшей
  s = s.split('?')[0].split('#')[0].replace(/\/+$/, '');

  // Поиск по instagram.com/ник или tiktok.com/@ник
  var m = s.match(/(?:instagram\.com\/|tiktok\.com\/@?)([a-zA-Z0-9._]+)/i);
  if (m && m[1]) {
    var cand = m[1].toLowerCase();
    // Исключаем системные пути Instagram
    if (cand !== 'p' && cand !== 'reel' && cand !== 'reels' && cand !== 'stories' && cand !== 'share') {
      return cand;
    }
  }

  // Если начинается с @
  if (s.indexOf('@') === 0) {
    return s.substring(1).replace(/[^a-zA-Z0-9._]/g, '').toLowerCase();
  }

  // Если введен чистый ник (без http)
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
 * Определение формата креатива (stories, reels_stories, reels)
 */
function getFormatCode_(format) {
  if (!format) return 'stories';
  var f = format.toString().toLowerCase().trim();
  if (f.indexOf('reel') !== -1 && (f.indexOf('stori') !== -1 || f.indexOf('сторис') !== -1)) {
    return 'reels_stories';
  }
  if (f.indexOf('reel') !== -1) {
    return 'reels';
  }
  if (f.indexOf('stori') !== -1 || f.indexOf('сторис') !== -1) {
    return 'stories';
  }
  return 'stories';
}

/**
 * Транслитерация кириллических имен блогеров в латиницу (если нет инстаграм ссылки)
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
