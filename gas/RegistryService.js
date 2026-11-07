/**
 * ============================================================
 * RegistryService.js — Регистрация и управление UTM-метками
 * ============================================================
 */

/**
 * Транслитерация и очистка строки для идеального формата UTM
 */
function slugifyUtm(str) {
  if (!str) return '';
  str = String(str).trim().toLowerCase();

  var ruMap = {
    'а':'a', 'б':'b', 'в':'v', 'г':'g', 'д':'d', 'е':'e', 'ё':'yo', 'ж':'zh',
    'з':'z', 'и':'i', 'й':'y', 'к':'k', 'л':'l', 'м':'m', 'н':'n', 'о':'o',
    'п':'p', 'р':'r', 'с':'s', 'т':'t', 'у':'u', 'ф':'f', 'х':'kh', 'ц':'ts',
    'ч':'ch', 'ш':'sh', 'щ':'shch', 'ъ':'', 'ы':'y', 'ь':'', 'э':'e', 'ю':'yu', 'я':'ya',
    'ә':'a', 'ғ':'g', 'қ':'q', 'ң':'n', 'ө':'o', 'ұ':'u', 'ү':'u', 'һ':'h', 'і':'i'
  };

  var transliterated = '';
  for (var i = 0; i < str.length; i++) {
    var ch = str[i];
    transliterated += ruMap[ch] !== undefined ? ruMap[ch] : ch;
  }

  // Заменяем пробелы и спецсимволы на нижнее подчеркивание
  return transliterated
    .replace(/[^a-z0-9_.-]/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '');
}

/**
 * Сборка полной ссылки с параметрами
 */
function buildFullUtmUrl(baseUrl, source, medium, campaign, content, term) {
  var url = baseUrl.trim();
  var params = [];

  if (source) params.push('utm_source=' + encodeURIComponent(slugifyUtm(source)));
  if (medium) params.push('utm_medium=' + encodeURIComponent(slugifyUtm(medium)));
  if (campaign) params.push('utm_campaign=' + encodeURIComponent(slugifyUtm(campaign)));
  if (content) params.push('utm_content=' + encodeURIComponent(slugifyUtm(content)));
  if (term) params.push('utm_term=' + encodeURIComponent(slugifyUtm(term)));

  if (params.length === 0) return url;
  var separator = url.indexOf('?') !== -1 ? '&' : '?';
  return url + separator + params.join('&');
}

/**
 * Регистрирует новую UTM-метку в Реестре Google Таблицы
 */
function registerUtm(data) {
  var ss = getSpreadsheet();
  var registrySheet = ss.getSheetByName(CONFIG.SHEETS.REGISTRY);
  if (!registrySheet) {
    setupSpreadsheet();
    registrySheet = ss.getSheetByName(CONFIG.SHEETS.REGISTRY);
  }

  var baseUrl = (data.baseUrl || 'https://janamen1.kz/influence').trim();
  var source = slugifyUtm(data.source || 'instagram');
  var medium = slugifyUtm(data.medium || 'influencer');
  var campaign = slugifyUtm(data.campaign || '');
  var content = slugifyUtm(data.content || '');
  var term = slugifyUtm(data.term || '');
  var tag = (data.tag || 'Инфлюенс / Блогеры').trim();
  var author = (data.author || 'Маркетолог').trim();
  var budget = Number(data.budget) || 0;
  var description = (data.description || '').trim();
  var status = (data.status || 'Активна').trim();

  if (!campaign) {
    return { success: false, message: 'Обязательное поле: utm_campaign (название кампании или блогера)' };
  }

  var fullUrl = buildFullUtmUrl(baseUrl, source, medium, campaign, content, term);

  // Проверка на дубликаты
  var values = registrySheet.getDataRange().getValues();
  for (var i = 1; i < values.length; i++) {
    var rowSource = slugifyUtm(values[i][3]);
    var rowMedium = slugifyUtm(values[i][4]);
    var rowCampaign = slugifyUtm(values[i][5]);
    var rowContent = slugifyUtm(values[i][6]);
    var rowTerm = slugifyUtm(values[i][7]);

    if (rowSource === source && rowMedium === medium && rowCampaign === campaign && rowContent === content && rowTerm === term) {
      return {
        success: false,
        message: 'Такая комбинация UTM уже зарегистрирована (строка ' + (i + 1) + ')!',
        fullUrl: values[i][8],
        existingId: values[i][0]
      };
    }
  }

  var nextRow = registrySheet.getLastRow() + 1;
  var utmId = 'UTM-' + ('000' + (nextRow - 1)).slice(-4);
  var r = nextRow;

  // Формулы расчета для строки
  var formulaFullUrl = '=IF(C' + r + '="","", C' + r + ' & IF(ISNUMBER(FIND("?", C' + r + ')), "&", "?") & "utm_source=" & D' + r + ' & "&utm_medium=" & E' + r + ' & "&utm_campaign=" & F' + r + ' & IF(G' + r + '="","", "&utm_content=" & G' + r + ') & IF(H' + r + '="","", "&utm_term=" & H' + r + '))';
  var formulaLeads = '=IF(F' + r + '="","", COUNTIFS(\'📥 Сделки AmoCRM\'!$H:$H, D' + r + ', \'📥 Сделки AmoCRM\'!$J:$J, F' + r + '))';
  var formulaWon = '=IF(F' + r + '="","", COUNTIFS(\'📥 Сделки AmoCRM\'!$H:$H, D' + r + ', \'📥 Сделки AmoCRM\'!$J:$J, F' + r + ', \'📥 Сделки AmoCRM\'!$E:$E, "Проверка пройдена"))';
  var formulaRevenue = '=IF(F' + r + '="","", SUMIFS(\'📥 Сделки AmoCRM\'!$F:$F, \'📥 Сделки AmoCRM\'!$H:$H, D' + r + ', \'📥 Сделки AmoCRM\'!$J:$J, F' + r + ', \'📥 Сделки AmoCRM\'!$E:$E, "Проверка пройдена"))';
  var formulaCr = '=IF(O' + r + '>0, P' + r + '/O' + r + ', 0)';
  var formulaCpl = '=IF(O' + r + '>0, M' + r + '/O' + r + ', 0)';
  var formulaCac = '=IF(P' + r + '>0, M' + r + '/P' + r + ', 0)';
  var formulaRomi = '=IF(M' + r + '>0, (Q' + r + ' - M' + r + ')/M' + r + ', 0)';

  var newRow = [
    utmId,
    new Date(),
    baseUrl,
    source,
    medium,
    campaign,
    content,
    term,
    formulaFullUrl,
    tag,
    author,
    status,
    budget,
    description,
    formulaLeads,
    formulaWon,
    formulaRevenue,
    formulaCr,
    formulaCpl,
    formulaCac,
    formulaRomi
  ];

  registrySheet.getRange(nextRow, 1, 1, newRow.length).setValues([newRow]);

  // Форматирование ячеек новой строки
  registrySheet.getRange(nextRow, 2).setNumberFormat('yyyy-mm-dd');
  registrySheet.getRange(nextRow, 13).setNumberFormat('#,##0" ₸"');
  registrySheet.getRange(nextRow, 15, 1, 2).setNumberFormat('#,##0');
  registrySheet.getRange(nextRow, 17).setNumberFormat('#,##0" ₸"');
  registrySheet.getRange(nextRow, 18).setNumberFormat('0.0%');
  registrySheet.getRange(nextRow, 19, 1, 2).setNumberFormat('#,##0" ₸"');
  registrySheet.getRange(nextRow, 21).setNumberFormat('0.0%');

  SpreadsheetApp.flush();

  var qrCodeUrl = 'https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=' + encodeURIComponent(fullUrl);

  return {
    success: true,
    id: utmId,
    fullUrl: fullUrl,
    qrCodeUrl: qrCodeUrl,
    message: 'UTM-метка успешно зарегистрирована!'
  };
}

/**
 * Возвращает полный список зарегистрированных меток со значениями
 */
function getRegistryData() {
  var ss = getSpreadsheet();
  var registrySheet = ss.getSheetByName(CONFIG.SHEETS.REGISTRY);
  if (!registrySheet) return [];

  var data = registrySheet.getDataRange().getValues();
  if (data.length <= 1) return [];

  var items = [];
  for (var i = 1; i < data.length; i++) {
    var row = data[i];
    if (!row[0]) continue;
    items.push({
      id: row[0],
      createdAt: row[1] instanceof Date ? Utilities.formatDate(row[1], 'Asia/Almaty', 'yyyy-MM-dd') : String(row[1]),
      baseUrl: row[2],
      source: row[3],
      medium: row[4],
      campaign: row[5],
      content: row[6],
      term: row[7],
      fullUrl: row[8],
      tag: row[9],
      author: row[10],
      status: row[11],
      budget: Number(row[12]) || 0,
      description: row[13],
      leads: Number(row[14]) || 0,
      won: Number(row[15]) || 0,
      revenue: Number(row[16]) || 0,
      cr: Number(row[17]) || 0,
      cpl: Number(row[18]) || 0,
      cac: Number(row[19]) || 0,
      romi: Number(row[20]) || 0
    });
  }
  return items;
}

/**
 * Возвращает агрегированную аналитику по источникам и каналам
 */
function getAnalyticsSummary() {
  var ss = getSpreadsheet();
  var dealsSheet = ss.getSheetByName(CONFIG.SHEETS.DEALS);
  var registrySheet = ss.getSheetByName(CONFIG.SHEETS.REGISTRY);

  if (!dealsSheet) return { error: 'Лист сделок не найден' };

  var dealsData = dealsSheet.getDataRange().getValues();
  var registryData = registrySheet ? registrySheet.getDataRange().getValues() : [];

  var totalLeads = 0;
  var wonLeads = 0;
  var totalRevenue = 0;
  var totalBudget = 0;

  var bySource = {};
  var byMedium = {};
  var byCampaign = {};

  // Бюджеты из реестра
  for (var r = 1; r < registryData.length; r++) {
    var regRow = registryData[r];
    var b = Number(regRow[12]) || 0;
    totalBudget += b;
  }

  // Обработка сделок AmoCRM
  for (var i = 1; i < dealsData.length; i++) {
    var d = dealsData[i];
    var dealId = d[0];
    if (!dealId) continue;

    totalLeads++;
    var statusCategory = d[4];
    var price = Number(d[5]) || 0;
    var isWon = (statusCategory === 'Проверка пройдена');

    if (isWon) {
      wonLeads++;
      totalRevenue += price;
    }

    var src = String(d[7] || 'direct/none').toLowerCase();
    var med = String(d[8] || 'none').toLowerCase();
    var camp = String(d[9] || 'none').toLowerCase();

    // Source stats
    if (!bySource[src]) bySource[src] = { leads: 0, won: 0, revenue: 0 };
    bySource[src].leads++;
    if (isWon) {
      bySource[src].won++;
      bySource[src].revenue += price;
    }

    // Medium stats
    if (!byMedium[med]) byMedium[med] = { leads: 0, won: 0, revenue: 0 };
    byMedium[med].leads++;
    if (isWon) {
      byMedium[med].won++;
      byMedium[med].revenue += price;
    }

    // Campaign stats
    if (camp !== 'none') {
      if (!byCampaign[camp]) byCampaign[camp] = { source: src, leads: 0, won: 0, revenue: 0 };
      byCampaign[camp].leads++;
      if (isWon) {
        byCampaign[camp].won++;
        byCampaign[camp].revenue += price;
      }
    }
  }

  var cr = totalLeads > 0 ? (wonLeads / totalLeads) : 0;
  var romi = totalBudget > 0 ? ((totalRevenue - totalBudget) / totalBudget) : 0;
  var avgCheck = wonLeads > 0 ? (totalRevenue / wonLeads) : 0;

  return {
    kpi: {
      totalLeads: totalLeads,
      wonLeads: wonLeads,
      totalRevenue: totalRevenue,
      totalBudget: totalBudget,
      cr: cr,
      romi: romi,
      avgCheck: avgCheck
    },
    bySource: bySource,
    byMedium: byMedium,
    byCampaign: byCampaign
  };
}
