import json

with open('gas/marketing_analytics_summary.json', 'r', encoding='utf-8') as f:
    analytics_json = f.read()

with open('gas/utm_granularity_data.json', 'r', encoding='utf-8') as f:
    granularity_json = f.read()

with open('gas/compact_leads_dict.json', 'r', encoding='utf-8') as f:
    leads_dict_json = f.read()

html_content = f'''<!DOCTYPE html>
<html lang="ru" class="h-full bg-slate-50">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Jana Men — UTM Реестр & Сквозная Аналитика</title>
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              50: '#eff6ff',
              100: '#dbeafe',
              500: '#3b82f6',
              600: '#2563eb',
              700: '#1d4ed8',
              800: '#1e40af',
              900: '#1e3a8a',
            }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
    .code-font {{ font-family: 'JetBrains Mono', monospace; }}
    .tab-active {{ border-bottom: 3px solid #2563eb; color: #1d4ed8; font-weight: 700; }}
    .tab-inactive {{ border-bottom: 3px solid transparent; color: #64748b; font-weight: 500; }}
    .tab-inactive:hover {{ color: #0f172a; border-color: #cbd5e1; }}
  </style>
</head>
<body class="h-full flex flex-col text-slate-800 antialiased selection:bg-brand-500 selection:text-white">

  <!-- ШАПКА ПОРТАЛА -->
  <header class="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm w-full">
    <div class="w-full px-3 sm:px-6">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 to-indigo-600 flex items-center justify-center text-white font-black text-xl shadow-md shadow-brand-500/20">
            JM
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <h1 class="text-base sm:text-lg font-black tracking-tight text-slate-900 leading-none">Jana Men</h1>
              <span class="px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wider bg-brand-50 text-brand-700 border border-brand-200 rounded-full">Маркетинг & Аналитика</span>
            </div>
            <p class="text-[11px] text-slate-500 font-medium">Сквозная оценка UTM-меток, посадочных страниц и оплат AmoCRM</p>
          </div>
        </div>

        <div class="flex items-center space-x-2.5">
          <span id="liveStatus" class="px-2.5 py-1 text-[11px] font-bold rounded-lg border bg-emerald-50 text-emerald-700 border-emerald-200">● Данные AmoCRM актуальны (18.5k сделок)</span>
          <button onclick="syncAmoCRM()" id="btnSyncCRM" class="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition border border-slate-200">
            <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <span>Синхронизировать AmoCRM</span>
          </button>
          <a href="https://docs.google.com/spreadsheets/d/1jBeeF8b_7CORi8Xf9Kjr9YN6c6ZrloQIljT2_-adcYs/edit" target="_blank" class="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-lg transition shadow-sm">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
            <span>Google Таблица</span>
          </a>
        </div>
      </div>

      <!-- НАВИГАЦИОННЫЕ ВКЛАДКИ -->
      <nav class="flex space-x-6 -mb-px text-xs sm:text-sm font-semibold overflow-x-auto">
        <button onclick="switchTab('analytics')" id="tab-analytics" class="tab-active py-3.5 px-1 inline-flex items-center space-x-2 whitespace-nowrap">
          <svg class="w-4 h-4 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          <span>1. Дашборд Маркетинга</span>
          <span class="ml-1.5 px-2 py-0.5 text-[10px] font-bold bg-emerald-100 text-emerald-800 rounded-full" id="badgeNavRevenue">81.6M ₸</span>
        </button>

        <button onclick="switchTab('granularity')" id="tab-granularity" class="tab-inactive py-3.5 px-1 inline-flex items-center space-x-2 whitespace-nowrap">
          <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
          <span>2. Полная детализация UTM (5 параметров)</span>
          <span id="badgeCombos" class="ml-1.5 px-2 py-0.5 text-[10px] font-bold bg-purple-100 text-purple-800 rounded-full">251 связка</span>
        </button>

        <button onclick="switchTab('builder-bloggers')" id="tab-builder-bloggers" class="tab-inactive py-3.5 px-1 inline-flex items-center space-x-2 whitespace-nowrap">
          <span class="text-base leading-none">🌟</span>
          <span>3. Конструктор: Блогеры (МПБ)</span>
          <span class="ml-1.5 px-2 py-0.5 text-[10px] font-bold bg-pink-100 text-pink-800 rounded-full">Инфлюенс</span>
        </button>

        <button onclick="switchTab('builder-fans')" id="tab-builder-fans" class="tab-inactive py-3.5 px-1 inline-flex items-center space-x-2 whitespace-nowrap">
          <span class="text-base leading-none">🎬</span>
          <span>4. Конструктор: Фан-аккаунты (Сетка)</span>
          <span class="ml-1.5 px-2 py-0.5 text-[10px] font-bold bg-indigo-100 text-indigo-800 rounded-full">TikTok & Reels</span>
        </button>
      </nav>
    </div>
  </header>

  <!-- ОСНОВНОЙ КОНТЕНТ (FULL WIDTH НА ВЕСЬ ЭКРАН) -->
  <main class="flex-1 w-full px-3 sm:px-6 py-5 space-y-5">

    <!-- ПАНЕЛЬ УНИВЕРСАЛЬНЫХ ФИЛЬТРОВ (ПЕРИОД И СРЕЗЫ) -->
    <div class="bg-white p-5 sm:p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div class="flex items-center space-x-2">
            <span class="w-2.5 h-2.5 rounded-full bg-brand-600 animate-pulse"></span>
            <h3 class="text-sm font-black text-slate-900 uppercase tracking-wider">Фильтры аналитики: Периоды, Сайты и Сегменты</h3>
          </div>
          <p class="text-xs text-slate-500 mt-0.5">Все таблицы, KPI и графики автоматически пересчитываются за выбранный отрезок времени</p>
        </div>

        <button onclick="resetAllFilters()" class="text-xs font-bold text-slate-500 hover:text-slate-800 transition flex items-center space-x-1 self-start lg:self-center">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          <span>Сбросить фильтры</span>
        </button>
      </div>

      <!-- 1. БЫСТРЫЙ ВЫБОР ПЕРИОДА -->
      <div class="space-y-2 pt-2 border-t border-slate-100">
        <div class="flex flex-wrap items-center gap-1.5" id="periodButtonContainer">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1">Период:</span>
          <button onclick="setPeriodPreset('all')" id="period-btn-all" class="px-3 py-1.5 text-xs font-bold rounded-xl bg-slate-900 text-white transition shadow-sm">Весь период</button>
          <button onclick="setPeriodPreset('today')" id="period-btn-today" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Сегодня (10 ноя)</button>
          <button onclick="setPeriodPreset('yesterday')" id="period-btn-yesterday" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Вчера (9 ноя)</button>
          <button onclick="setPeriodPreset('last7')" id="period-btn-last7" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition">7 дней</button>
          <button onclick="setPeriodPreset('last30')" id="period-btn-last30" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition">30 дней</button>
          <button onclick="setPeriodPreset('nov2026')" id="period-btn-nov2026" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Ноябрь 2026</button>
          <button onclick="setPeriodPreset('oct2026')" id="period-btn-oct2026" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Октябрь 2026</button>
          <button onclick="setPeriodPreset('sep2026')" id="period-btn-sep2026" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Сентябрь 2026</button>
          <button onclick="setPeriodPreset('aug2026')" id="period-btn-aug2026" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Август 2026</button>
          <button onclick="setPeriodPreset('jul2026')" id="period-btn-jul2026" class="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Июль 2026</button>
        </div>

        <!-- ТОЧНЫЕ ДАТЫ -->
        <div class="flex flex-wrap items-center gap-2 pt-1 text-xs">
          <span class="text-slate-400 font-semibold">Или точные даты:</span>
          <div class="flex items-center space-x-1.5">
            <span class="text-slate-400">с</span>
            <input type="date" id="dateInputFrom" onchange="applyCustomDateRange()" class="px-2.5 py-1 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:border-brand-500 font-medium">
            <span class="text-slate-400">по</span>
            <input type="date" id="dateInputTo" onchange="applyCustomDateRange()" class="px-2.5 py-1 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:border-brand-500 font-medium">
          </div>
          <span id="activePeriodLabel" class="ml-auto text-[11px] font-bold px-2 py-0.5 rounded-md bg-blue-50 text-brand-700 border border-blue-100">Период: За всё время</span>
        </div>
      </div>

      <!-- 2. ВТОРИЧНЫЕ СРЕЗЫ: САЙТ, СТРАНИЦА, КАНАЛ, ПОИСК -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-3 border-t border-slate-100">
        <div>
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1">Сайт / Источник:</label>
          <select id="filterDomainSelect" onchange="onFilterChange()" class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-semibold text-slate-800">
            <option value="janamen1.kz" selected>🌟 Все каналы janamen1.kz (Сайт + WhatsApp)</option>
            <option value="whatsapp_9828">📱 Только WhatsApp 9828 (Айтым Берикович - органика)</option>
            <option value="janamen1_site">🌐 Только сайт janamen1.kz (без WhatsApp)</option>
            <option value="all">Все сайты компании (janamen1 + health + WA)</option>
            <option value="janamenhealth.kz">janamenhealth.kz</option>
          </select>
        </div>

        <div>
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1">Посадочная страница / Точка входа:</label>
          <select id="filterPageSelect" onchange="onFilterChange()" class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-medium text-slate-800">
            <option value="all">Все страницы и каналы</option>
            <optgroup label="🎯 5 ОСНОВНЫХ КАНАЛОВ (Jana Men)">
              <option value="/iwa-9828">📱 /iwa-9828 (WhatsApp 9828 — Айтым Берикович)</option>
              <option value="/lidmagnit">🎁 /lidmagnit (Все варианты лид-магнитов и гайдов)</option>
              <option value="/influence">🌟 /influence (Инфлюенс / Блогеры МПБ)</option>
              <option value="/fun">⚡ /fun (Квиз-воронка)</option>
              <option value="/smm">📸 /smm (SMM / Соцсети)</option>
            </optgroup>
            <optgroup label="Остальные посадочные страницы">
              <option value="/organika">/organika (Органика / SMM)</option>
              <option value="/kaspiform">/kaspiform (Kaspi-форма)</option>
              <option value="/inst-men">/inst-men (Instagram Men)</option>
              <option value="/inst-women">/inst-women (Instagram Women)</option>
              <option value="/vitamins-inst">/vitamins-inst (Витамины)</option>
              <option value="/inst-omega">/inst-omega (Омега-3)</option>
              <option value="/nikitaform">/nikitaform (Форма Никиты)</option>
              <option value="/yurakv">/yurakv (Квиз Юры)</option>
              <option value="/aojiru-inst">/aojiru-inst (Аодзиру)</option>
              <option value="/">/ (Главная)</option>
            </optgroup>
          </select>
        </div>

        <div>
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1">Канал (utm_medium):</label>
          <select id="filterMediumSelect" onchange="onFilterChange()" class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-medium text-slate-800">
            <option value="all">Все каналы</option>
            <option value="Айтым Берикович - органика">📱 Айтым Берикович - органика (WhatsApp)</option>
            <option value="mpb1">mpb1 (Блогеры - Анельжан)</option>
            <option value="mpb2">mpb2 (Блогеры - Алина)</option>
            <option value="mpb3">mpb3 (Блогеры - Алуа)</option>
            <option value="mpb4">mpb4 (Блогеры - Дарина)</option>
            <option value="fan">🎬 fan (Фан-аккаунты / Креаторы сетки)</option>
            <option value="nikita">nikita (Таргет Никита)</option>
            <option value="social">social (Соцсети / SMM)</option>
            <option value="paid">paid (Платная реклама)</option>
            <option value="none">none (Прямой переход)</option>
          </select>
        </div>

        <div>
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1">Поиск по UTM / Кампании:</label>
          <input type="text" id="filterSearchInput" oninput="onFilterChange()" placeholder="leads, kaspiform, блогер, fan..." class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-medium text-slate-800">
        </div>
      </div>

      <!-- БЫСТРЫЙ ВЫБОР ОСНОВНЫХ КАНАЛОВ -->
      <div class="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100 text-xs">
        <span class="text-slate-400 font-bold uppercase tracking-wider text-[11px] mr-1">Основные каналы:</span>
        <button onclick="resetAllFilters()" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold transition">Все каналы</button>
        <button onclick="filterByPage('/iwa-9828')" class="px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold transition flex items-center space-x-1 shadow-sm">
          <span>📱 /iwa-9828 (WhatsApp)</span>
          <span class="px-1.5 py-0.2 text-[10px] bg-emerald-200 text-emerald-900 rounded-full font-black">181M ₸</span>
        </button>
        <button onclick="filterByPage('/influence')" class="px-2.5 py-1 rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-200 font-bold transition flex items-center space-x-1 shadow-sm">
          <span>🌟 /influence (Блогеры МПБ)</span>
          <span class="px-1.5 py-0.2 text-[10px] bg-purple-200 text-purple-900 rounded-full font-black">1.5M ₸</span>
        </button>
        <button onclick="filterByMedium('fan')" class="px-2.5 py-1 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-800 border border-indigo-200 font-bold transition flex items-center space-x-1 shadow-sm">
          <span>🎬 Фан-аккаунты (fan)</span>
        </button>
        <button onclick="filterByPage('/lidmagnit')" class="px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-brand-800 border border-brand-200 font-bold transition flex items-center space-x-1 shadow-sm">
          <span>🎁 /lidmagnit* (Лидмагниты)</span>
          <span class="px-1.5 py-0.2 text-[10px] bg-blue-200 text-brand-900 rounded-full font-black">3.4k</span>
        </button>
        <button onclick="filterByPage('/fun')" class="px-2.5 py-1 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 font-bold transition flex items-center space-x-1 shadow-sm">
          <span>⚡ /fun (Квиз)</span>
        </button>
        <button onclick="filterByPage('/smm')" class="px-2.5 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-800 border border-rose-200 font-bold transition flex items-center space-x-1 shadow-sm">
          <span>📸 /smm (Соцсети)</span>
        </button>
      </div>
          <span>📸 /smm (Соцсети)</span>
        </button>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- ВКЛАДКА 1: ДАШБОРД ОТДЕЛА МАРКЕТИНГА (janamen1.kz) -->
    <!-- ============================================================ -->
    <div id="view-analytics" class="space-y-8">

      <!-- 4 КЛЮЧЕВЫХ KPI КАРТОЧКИ -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden">
          <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Всего лидов / заявок</div>
          <div id="kpiTotalLeads" class="text-2xl sm:text-4xl font-black text-slate-900 mt-2">—</div>
          <div id="kpiLeadsSub" class="text-xs text-slate-500 mt-1 flex items-center space-x-1">
            <span>за выбранный период</span>
          </div>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-emerald-100 shadow-sm bg-gradient-to-br from-white to-emerald-50/30">
          <div class="text-[11px] font-bold text-emerald-700 uppercase tracking-wider">Оплачено (Статус 142)</div>
          <div id="kpiWonLeads" class="text-2xl sm:text-4xl font-black text-emerald-600 mt-2">—</div>
          <div id="kpiCr" class="text-xs font-bold text-emerald-700 mt-1">Конверсия (CR): —</div>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-blue-100 shadow-sm bg-gradient-to-br from-white to-blue-50/30">
          <div class="text-[11px] font-bold text-brand-700 uppercase tracking-wider">Подтвержденная Выручка</div>
          <div id="kpiRevenue" class="text-2xl sm:text-4xl font-black text-brand-700 mt-2">—</div>
          <div id="kpiAvgCheck" class="text-xs font-semibold text-slate-600 mt-1">Средний чек: —</div>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-purple-100 shadow-sm bg-gradient-to-br from-white to-purple-50/30">
          <div class="text-[11px] font-bold text-purple-700 uppercase tracking-wider">Активных UTM-связок</div>
          <div id="kpiCombosCount" class="text-2xl sm:text-4xl font-black text-purple-700 mt-2">—</div>
          <div id="kpiCombosSub" class="text-xs text-slate-500 mt-1">с ненулевыми заявками</div>
        </div>
      </div>

      <!-- ПОСАДОЧНЫЕ СТРАНИЦЫ JANAMEN1.KZ (В ВИДЕ СПИСКА / ТАБЛИЦЫ) -->
      <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden space-y-0">
        <div class="p-5 sm:p-6 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div class="flex items-center space-x-2">
              <span class="w-2.5 h-2.5 rounded-full bg-brand-600"></span>
              <h3 class="text-base sm:text-lg font-black text-slate-900">Посадочные страницы маркетинг-сайта janamen1.kz</h3>
              <span class="px-2 py-0.5 text-[10px] font-bold rounded-md bg-blue-50 text-brand-700">Список страниц</span>
            </div>
            <p class="text-xs text-slate-500 mt-0.5">Показатели оплат, конверсий и выручки по каждой посадочной странице за выбранный период</p>
          </div>

          <div class="flex items-center space-x-2.5">
            <!-- Переключатель вида: Список / Карточки -->
            <div class="inline-flex p-0.5 bg-slate-100 rounded-xl border border-slate-200 text-xs font-bold">
              <button onclick="setSubpageView('list')" id="btnSubViewList" class="px-3 py-1.5 rounded-lg bg-white text-slate-900 shadow-sm transition flex items-center space-x-1.5">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/></svg>
                <span>Списком</span>
              </button>
              <button onclick="setSubpageView('cards')" id="btnSubViewCards" class="px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition flex items-center space-x-1.5">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
                <span>Карточками</span>
              </button>
            </div>

            <button onclick="switchTab('granularity')" class="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-bold text-purple-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-xl transition shadow-sm">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
              <span>Все UTM-связки →</span>
            </button>
          </div>
        </div>

        <!-- ОСНОВНОЙ ВИД: СПИСОК / ТАБЛИЦА -->
        <div id="subpagesListView" class="overflow-x-auto">
          <table class="w-full text-left text-xs sm:text-sm">
            <thead class="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[11px] tracking-wider">
              <tr>
                <th class="py-3 px-4">Страница на janamen1.kz</th>
                <th class="py-3 px-4">Назначение / Описание</th>
                <th class="py-3 px-4 text-center">Всего лидов</th>
                <th class="py-3 px-4 text-center">Оплачено (142)</th>
                <th class="py-3 px-4 text-center">Конверсия (CR %)</th>
                <th class="py-3 px-4 text-right">Выручка (₸)</th>
                <th class="py-3 px-4 text-right">Средний чек (₸)</th>
                <th class="py-3 px-4 text-center">Действие</th>
              </tr>
            </thead>
            <tbody id="subpagesTableBody" class="divide-y divide-slate-100">
              <!-- Заполняется динамически -->
            </tbody>
          </table>
        </div>

        <!-- АЛЬТЕРНАТИВНЫЙ ВИД: КАРТОЧКИ (скрыты по умолчанию) -->
        <div id="subpagesCardsView" class="hidden p-5 sm:p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Заполняется динамически -->
        </div>
      </div>

      <!-- ГРАФИКИ: ВЫРУЧКА И ЛИДЫ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-bold text-slate-900" id="chartSourcesTitle">Выручка по источникам (utm_source)</h3>
            <span class="text-xs text-slate-400">Топ каналов по оплатам (₸)</span>
          </div>
          <div class="h-64">
            <canvas id="chartSources"></canvas>
          </div>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-bold text-slate-900" id="chartMediumsTitle">Лиды по форматам рекламы (utm_medium)</h3>
            <span class="text-xs text-slate-400">Распределение заявок</span>
          </div>
          <div class="h-64">
            <canvas id="chartMediums"></canvas>
          </div>
        </div>
      </div>

      <!-- ТАБЛИЦА ИСТОЧНИКОВ ТРАФИКА ДЛЯ ТЕКУЩЕГО СРЕЗА -->
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="p-5 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 class="text-base font-bold text-slate-900">Сквозная эффективность по источникам (utm_source)</h3>
            <p class="text-xs text-slate-500">Показатели источников за выбранный период</p>
          </div>
          <span class="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-600 rounded-lg">Сортировка по выручке</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs sm:text-sm">
            <thead class="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[11px] tracking-wider">
              <tr>
                <th class="py-3 px-4">Источник (utm_source)</th>
                <th class="py-3 px-4 text-center">Всего лидов</th>
                <th class="py-3 px-4 text-center">Оплачено (142)</th>
                <th class="py-3 px-4 text-center">Конверсия (CR %)</th>
                <th class="py-3 px-4 text-right">Выручка (₸)</th>
                <th class="py-3 px-4 text-right">Средний чек (₸)</th>
                <th class="py-3 px-4 text-right">Доля выручки</th>
              </tr>
            </thead>
            <tbody id="analyticsTableBody" class="divide-y divide-slate-100">
              <!-- Заполняется динамически -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- РАЗДЕЛ СДЕЛОК: ПОСЛЕДНИЕ СДЕЛКИ JANAMEN1.KZ И ОПЛАТЫ -->
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="p-5 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="flex items-center space-x-2">
              <h3 class="text-base font-bold text-slate-900">Лента сделок сайта janamen1.kz из AmoCRM</h3>
              <span class="px-2 py-0.5 text-[10px] font-black rounded-full bg-emerald-100 text-emerald-800">Живая выгрузка</span>
            </div>
            <p class="text-xs text-slate-500">Сделки за выбранный период с деталями посадочной страницы и UTM-метками</p>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <div class="inline-flex p-0.5 bg-slate-100 rounded-lg border border-slate-200 text-xs font-semibold">
              <button onclick="setDealsFilter('all')" id="btnDealsAll" class="px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm transition">Все сделки</button>
              <button onclick="setDealsFilter('won')" id="btnDealsWon" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 transition">Только оплачено (142)</button>
              <button onclick="setDealsFilter('open')" id="btnDealsOpen" class="px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 transition">В работе</button>
            </div>
            <input type="text" id="dealsSearchInput" oninput="filterDealsTable()" placeholder="Поиск в сделках..." class="px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg w-44 focus:bg-white focus:outline-none focus:border-brand-500 transition">
          </div>
        </div>

        <div class="overflow-x-auto max-h-96">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold text-[10px] tracking-wider sticky top-0 z-10">
              <tr>
                <th class="py-2.5 px-4"># ID</th>
                <th class="py-2.5 px-4">Клиент / Сделка</th>
                <th class="py-2.5 px-4">Статус</th>
                <th class="py-2.5 px-4 text-right">Сумма (₸)</th>
                <th class="py-2.5 px-4">Дата</th>
                <th class="py-2.5 px-4">Страница janamen1.kz</th>
                <th class="py-2.5 px-4">Источник / Канал</th>
                <th class="py-2.5 px-4">Кампания (utm_campaign)</th>
                <th class="py-2.5 px-4 text-center">AmoCRM</th>
              </tr>
            </thead>
            <tbody id="recentDealsTableBody" class="divide-y divide-slate-100">
              <!-- Заполняется динамически -->
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- ============================================================ -->
    <!-- ВКЛАДКА 2: ПОЛНАЯ ДЕТАЛИЗАЦИЯ ПО ВСЕМ UTM (5 ПАРАМЕТРОВ) -->
    <!-- ============================================================ -->
    <div id="view-granularity" class="hidden space-y-6">
      
      <div class="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div class="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-purple-800">
              <span>Сквозная детализация по всем 5 UTM параметрам</span>
            </div>
            <h2 class="text-2xl sm:text-3xl font-black tracking-tight text-slate-900 mt-1">Таблица всех UTM-связок и эффективности</h2>
            <p class="text-xs sm:text-sm text-slate-500">
              Точная оценка каждой связки: посадочная страница, utm_source, utm_medium, utm_campaign, utm_content, utm_term с показателями конверсии и выручки
            </p>
          </div>

          <div class="flex items-center space-x-2">
            <button onclick="exportGranularityCsv()" class="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition border border-slate-200 shadow-sm">
              <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              <span>Экспорт отфильтрованного в CSV</span>
            </button>
          </div>
        </div>

        <!-- КНОПКИ ПЕРЕКЛЮЧЕНИЯ РАЗРЕЗА -->
        <div class="flex flex-wrap gap-2 pt-2 border-t border-slate-100" id="granularityDimNav">
          <button onclick="setGranularityDim('combos')" id="dim-btn-combos" class="px-3.5 py-2 rounded-xl bg-purple-600 text-white font-bold text-xs transition">
            🔗 Полные связки (Combo)
          </button>
          <button onclick="setGranularityDim('campaigns')" id="dim-btn-campaigns" class="px-3.5 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
            utm_campaign (Кампании)
          </button>
          <button onclick="setGranularityDim('contents')" id="dim-btn-contents" class="px-3.5 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
            utm_content (Креативы)
          </button>
          <button onclick="setGranularityDim('mediums')" id="dim-btn-mediums" class="px-3.5 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
            utm_medium (Каналы)
          </button>
          <button onclick="setGranularityDim('terms')" id="dim-btn-terms" class="px-3.5 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
            utm_term (Аудитории)
          </button>
          <button onclick="setGranularityDim('sources')" id="dim-btn-sources" class="px-3.5 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
            utm_source (Площадки)
          </button>
        </div>
      </div>

      <!-- ПОИСК И ТАБЛИЦА ДЕТАЛИЗАЦИИ -->
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="p-4 border-b border-slate-200 flex items-center justify-between gap-4">
          <div class="relative flex-1 max-w-md">
            <input type="text" id="granularitySearchInput" oninput="renderGranularityTable()" placeholder="Быстрый поиск по любому слову из таблицы..." class="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 transition">
            <svg class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </div>
          <span id="granularityRowCount" class="text-xs font-bold text-slate-500">Показано: 0 связок</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead id="granularityTableHead" class="bg-slate-50 border-b border-slate-200 text-slate-700 uppercase font-bold text-[11px] tracking-wider">
              <!-- Заполняется динамически -->
            </thead>
            <tbody id="granularityTableBody" class="divide-y divide-slate-100">
              <!-- Заполняется динамически -->
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- ============================================================ -->
    <!-- ВКЛАДКА 3: КОНСТРУКТОР UTM ДЛЯ БЛОГЕРОВ (МПБ) -->
    <!-- ============================================================ -->
    <div id="view-builder-bloggers" class="hidden space-y-6">
      
      <!-- ШАПКА КОНСТРУКТОРА БЛОГЕРОВ -->
      <div class="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-pink-500/10 via-purple-500/10 to-indigo-500/10 border border-pink-200 shadow-sm relative overflow-hidden">
        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-pink-100 text-pink-800 text-xs font-bold mb-2">
              <span>🌟 Инфлюенс-маркетинг (UGC & Амбассадоры)</span>
            </div>
            <h2 class="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">Конструктор персональных UTM для Блогеров</h2>
            <p class="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl">
              Генерирует 100% валидную ссылку для блогера с автоматической привязкой к менеджеру (mpb1, mpb2, mpb3). Исключает потери лидов в AmoCRM и формирует готовое ТЗ для отправки блогеру в WhatsApp.
            </p>
          </div>
          <div class="flex items-center space-x-2">
            <span class="px-3 py-1.5 rounded-xl bg-white/80 backdrop-blur border border-pink-200 text-xs font-bold text-pink-800 shadow-sm">
              Целевой CR: > 3.0%
            </span>
          </div>
        </div>
      </div>

      <!-- СЕТКА: ФОРМА И РЕЗУЛЬТАТ -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        <!-- ЛЕВАЯ КОЛОНКА: ПАРАМЕТРЫ ССЫЛКИ -->
        <div class="lg:col-span-7 bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-5">
          <h3 class="text-sm font-black text-slate-900 uppercase tracking-wider flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-pink-500"></span>
            <span>Параметры интеграции</span>
          </h3>

          <!-- МЕНЕДЖЕР -->
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1.5">
              1. Ответственный менеджер (utm_medium):
            </label>
            <select id="blgManager" onchange="updateBloggerUrl()" class="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-pink-500 font-semibold text-slate-800">
              <option value="mpb1">Анельжан (mpb1)</option>
              <option value="mpb2" selected>Алина (mpb2)</option>
              <option value="mpb3">Алуа (mpb3)</option>
              <option value="mpb4">Дарина (mpb4)</option>
            </select>
          </div>

          <!-- ПОСАДОЧНАЯ СТРАНИЦА -->
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1.5">
              2. Посадочная страница сайта:
            </label>
            <select id="blgPage" onchange="onBloggerPageChange()" class="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-pink-500 font-semibold text-slate-800">
              <option value="https://janamen1.kz/influence" selected>🎯 https://janamen1.kz/influence (РЕКОМЕНДУЕТСЯ — страница блогеров)</option>
              <option value="https://janamen1.kz/lidmagnit">🎁 https://janamen1.kz/lidmagnit (Лидмагнит / Гайд)</option>
              <option value="https://janamen1.kz/fun">⚡ https://janamen1.kz/fun (Квиз-воронка)</option>
              <option value="https://janamen1.kz/organika">🌿 https://janamen1.kz/organika (Органика)</option>
              <option value="custom">✍️ Другая ссылка / Свой URL...</option>
            </select>
            <input type="text" id="blgCustomPage" oninput="updateBloggerUrl()" placeholder="https://janamen1.kz/..." class="hidden mt-2 w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-pink-500 font-medium">
          </div>

          <!-- НИК БЛОГЕРА С УМНОЙ ОЧИСТКОЙ -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-xs font-bold text-slate-700 uppercase">
                3. Никнейм блогера (utm_source):
              </label>
              <span class="text-[11px] text-pink-600 font-semibold">Очищается от @ и ссылок</span>
            </div>
            <input type="text" id="blgNick" oninput="updateBloggerUrl()" placeholder="Например: bota_abdualii, sarsssembaeva или ссылка" class="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-pink-500 font-bold text-slate-800">
            
            <!-- БЫСТРЫЕ ЧИПСЫ ТОП-БЛОГЕРОВ ИЗ РЕЕСТРА -->
            <div class="flex flex-wrap items-center gap-1.5 mt-2.5">
              <span class="text-[10px] font-bold text-slate-400 uppercase">Из реестра:</span>
              <button type="button" onclick="setBloggerNick('sarsssembaeva')" class="px-2 py-0.5 text-[11px] font-semibold bg-slate-100 hover:bg-pink-100 hover:text-pink-800 text-slate-700 rounded-lg transition">@sarsssembaeva</button>
              <button type="button" onclick="setBloggerNick('asema_kotoraya_alel')" class="px-2 py-0.5 text-[11px] font-semibold bg-slate-100 hover:bg-pink-100 hover:text-pink-800 text-slate-700 rounded-lg transition">@asema</button>
              <button type="button" onclick="setBloggerNick('frolova__kristina')" class="px-2 py-0.5 text-[11px] font-semibold bg-slate-100 hover:bg-pink-100 hover:text-pink-800 text-slate-700 rounded-lg transition">@frolova</button>
              <button type="button" onclick="setBloggerNick('bota_abdualii')" class="px-2 py-0.5 text-[11px] font-semibold bg-slate-100 hover:bg-pink-100 hover:text-pink-800 text-slate-700 rounded-lg transition">@bota</button>
              <button type="button" onclick="setBloggerNick('inabattan01')" class="px-2 py-0.5 text-[11px] font-semibold bg-slate-100 hover:bg-pink-100 hover:text-pink-800 text-slate-700 rounded-lg transition">@inabattan</button>
              <button type="button" onclick="setBloggerNick('kuanysheva.dii')" class="px-2 py-0.5 text-[11px] font-semibold bg-slate-100 hover:bg-pink-100 hover:text-pink-800 text-slate-700 rounded-lg transition">@kuanysheva</button>
              <button type="button" onclick="setBloggerNick('armana_fitness_trainer')" class="px-2 py-0.5 text-[11px] font-semibold bg-slate-100 hover:bg-pink-100 hover:text-pink-800 text-slate-700 rounded-lg transition">@armana</button>
            </div>
          </div>

          <!-- ФОРМАТ И КАМПАНИЯ В 2 КОЛОНКИ -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase mb-1.5">
                4. Формат (utm_content):
              </label>
              <select id="blgFormat" onchange="updateBloggerUrl()" class="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-pink-500 font-semibold text-slate-800">
                <option value="stories" selected>Stories со стикером (ТОП)</option>
                <option value="reels_stories">Reels + Stories</option>
                <option value="reels_bio">Ссылка в Bio профиля</option>
                <option value="tg_post">Пост в Telegram</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase mb-1.5">
                5. Кампания (utm_campaign):
              </label>
              <select id="blgCampaign" onchange="updateBloggerUrl()" class="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-pink-500 font-semibold text-slate-800">
                <option value="ugc_barter" selected>ugc_barter (Бартер за витамины)</option>
                <option value="paid_promo">paid_promo (Платная интеграция)</option>
                <option value="ambassador">ambassador (Амбассадор)</option>
              </select>
            </div>
          </div>

        </div>

        <!-- ПРАВАЯ КОЛОНКА: ГОТОВАЯ ССЫЛКА И ТЗ -->
        <div class="lg:col-span-5 space-y-5">
          
          <!-- ГОТОВАЯ ССЫЛКА КАРТОЧКА -->
          <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Готовая ссылка для блогера</span>
              </span>
              <span class="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">100% Валидно</span>
            </div>

            <div class="p-3.5 bg-slate-900 rounded-2xl text-emerald-400 font-mono text-xs break-all leading-relaxed shadow-inner selection:bg-emerald-500 selection:text-slate-900" id="blgResultUrl">
              https://janamen1.kz/influence?utm_source=sarsssembaeva&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=stories
            </div>

            <div class="flex items-center space-x-2">
              <button onclick="copyBloggerUrl()" id="btnCopyBlgUrl" class="flex-1 py-2.5 px-4 rounded-xl bg-pink-600 hover:bg-pink-700 text-white font-bold text-xs transition flex items-center justify-center space-x-1.5 shadow-sm">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                <span>Скопировать ссылку</span>
              </button>
              <a href="#" id="btnTestBlgUrl" target="_blank" class="py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center space-x-1">
                <span>Тест ↗</span>
              </a>
            </div>

            <div class="pt-3 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
              <div class="flex justify-between"><span>Канал (medium):</span> <b id="lblBlgMedium" class="text-slate-800">mpb2</b></div>
              <div class="flex justify-between"><span>Блогер (source):</span> <b id="lblBlgSource" class="text-slate-800">sarsssembaeva</b></div>
              <div class="flex justify-between"><span>Формат (content):</span> <b id="lblBlgContent" class="text-slate-800">stories</b></div>
            </div>
          </div>

          <!-- ГОТОВОЕ ТЗ ДЛЯ WHATSAPP -->
          <div class="bg-gradient-to-br from-emerald-50 to-white p-6 rounded-3xl border border-emerald-200/80 shadow-sm space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-black text-emerald-900 uppercase tracking-wider flex items-center space-x-1.5">
                <span>💬 Сообщение для блогера в WhatsApp</span>
              </span>
            </div>
            
            <textarea id="blgWhatsAppText" readonly rows="4" class="w-full p-3 bg-white border border-emerald-200 rounded-xl text-xs text-slate-700 font-sans leading-relaxed resize-none focus:outline-none"></textarea>

            <button onclick="copyBloggerMessage()" id="btnCopyBlgMsg" class="w-full py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition flex items-center justify-center space-x-1.5 shadow-sm">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
              <span>Скопировать ТЗ для WhatsApp</span>
            </button>
          </div>

        </div>

      </div>

    </div>

    <!-- ============================================================ -->
    <!-- ВКЛАДКА 4: КОНСТРУКТОР UTM ДЛЯ ФАН-АККАУНТОВ (СЕТКА) -->
    <!-- ============================================================ -->
    <div id="view-builder-fans" class="hidden space-y-6">
      
      <!-- ШАПКА КОНСТРУКТОРА ФАН-АККАУНТОВ -->
      <div class="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-indigo-500/10 via-blue-500/10 to-cyan-500/10 border border-indigo-200 shadow-sm relative overflow-hidden">
        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-800 text-xs font-bold mb-2">
              <span>🎬 Сетка видео (TikTok · Reels · YouTube Shorts)</span>
            </div>
            <h2 class="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">Конструктор UTM для Фан-аккаунтов</h2>
            <p class="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl">
              Генерирует индивидуальные ссылки для 12+ аккаунтов сетки (Доскажанова Айнагуль и 5 креаторов). Все заявки привязываются персонально к сотруднику в AmoCRM для точного расчета бонуса по KPI.
            </p>
          </div>
          <div class="flex items-center space-x-2">
            <span class="px-3 py-1.5 rounded-xl bg-white/80 backdrop-blur border border-indigo-200 text-xs font-bold text-indigo-800 shadow-sm">
              1 440 видео / месяц
            </span>
          </div>
        </div>
      </div>

      <!-- СЕТКА: ПАРАМЕТРЫ И ИНСТРУКЦИЯ -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        <!-- ЛЕВАЯ КОЛОНКА: ВЫБОР ПАРАМЕТРОВ -->
        <div class="lg:col-span-7 bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-5">
          <h3 class="text-sm font-black text-slate-900 uppercase tracking-wider flex items-center space-x-2">
            <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
            <span>Параметры аккаунта сетки</span>
          </h3>

          <!-- КРЕАТОР / СОТРУДНИК -->
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1.5">
              1. Креатор / Ответственный сотрудник (utm_campaign):
            </label>
            <select id="fanCreator" onchange="onFanCreatorChange()" class="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-indigo-500 font-semibold text-slate-800">
              <option value="fan_ainagul" selected>Доскажанова Айнагуль (Руководитель) — fan_ainagul</option>
              <option value="fan_dilnaz">Бекежанова Дильназ — fan_dilnaz</option>
              <option value="fan_aysulu">Кенжебаева Айсулу — fan_aysulu</option>
              <option value="fan_kamila">Гайсина Камила — fan_kamila</option>
              <option value="fan_aida">Кенжебаева Аида — fan_aida</option>
              <option value="fan_adina">Адина Хайдарова — fan_adina</option>
            </select>
          </div>

          <!-- ПЛОЩАДКА И АККАУНТ В 2 КОЛОНКИ -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase mb-1.5">
                2. Площадка (utm_source):
              </label>
              <select id="fanPlatform" onchange="updateFanUrl()" class="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-indigo-500 font-semibold text-slate-800">
                <option value="tiktok" selected>TikTok (tiktok)</option>
                <option value="instagram">Instagram Reels (instagram)</option>
                <option value="youtube">YouTube Shorts (youtube)</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-700 uppercase mb-1.5">
                3. Фан-аккаунт сетки:
              </label>
              <select id="fanAccount" onchange="onFanAccountChange()" class="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-indigo-500 font-semibold text-slate-800">
                <!-- Заполняется динамически -->
              </select>
            </div>
          </div>

          <input type="text" id="fanCustomAccount" oninput="updateFanUrl()" placeholder="Введите ник аккаунта..." class="hidden w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-indigo-500 font-medium">

          <!-- КУДА ВЕДЕМ ТРАФИК -->
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1.5">
              4. Целевая страница сайта (Куда направлять трафик):
            </label>
            <select id="fanPage" onchange="updateFanUrl()" class="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-indigo-500 font-semibold text-slate-800">
              <option value="https://janamen1.kz/fun" selected>⚡ https://janamen1.kz/fun (ТОП ДЛЯ ВИДЕО — Квиз-воронка с тестом)</option>
              <option value="https://janamen1.kz/lidmagnit">🎁 https://janamen1.kz/lidmagnit (Бесплатный гайд от Айтыма)</option>
              <option value="https://janamen1.kz/iwa-9828">📱 https://janamen1.kz/iwa-9828 (WhatsApp Айтыма +7 708 377-98-28)</option>
              <option value="https://janamen1.kz/">🌿 https://janamen1.kz/ (Главная страница)</option>
            </select>
          </div>

          <!-- МЕСТО РАЗМЕЩЕНИЯ -->
          <div>
            <label class="block text-xs font-bold text-slate-700 uppercase mb-1.5">
              5. Место ссылки в аккаунте:
            </label>
            <select id="fanPlacement" onchange="updateFanUrl()" class="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-indigo-500 font-semibold text-slate-800">
              <option value="bio" selected>bio — Шапка профиля (Ссылка в Bio / Веб-сайт профиля)</option>
              <option value="comment">comment — Закрепленный комментарий под видео</option>
              <option value="stories">stories — Стикер в Instagram Stories</option>
            </select>
          </div>

        </div>

        <!-- ПРАВАЯ КОЛОНКА: ССЫЛКА И ИНСТРУКЦИЯ -->
        <div class="lg:col-span-5 space-y-5">
          
          <!-- КАРТОЧКА ГОТОВОЙ ССЫЛКИ -->
          <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
                <span>Ссылка для шапки профиля (Bio)</span>
              </span>
              <span class="text-[10px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-200">utm_medium=fan</span>
            </div>

            <div class="p-3.5 bg-slate-900 rounded-2xl text-cyan-400 font-mono text-xs break-all leading-relaxed shadow-inner selection:bg-cyan-500 selection:text-slate-900" id="fanResultUrl">
              https://janamen1.kz/fun?utm_source=tiktok&utm_medium=fan&utm_campaign=fan_ainagul&utm_content=janamenfun_bio
            </div>

            <div class="flex items-center space-x-2">
              <button onclick="copyFanUrl()" id="btnCopyFanUrl" class="flex-1 py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition flex items-center justify-center space-x-1.5 shadow-sm">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                <span>Скопировать ссылку для Bio</span>
              </button>
              <a href="#" id="btnTestFanUrl" target="_blank" class="py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center space-x-1">
                <span>Тест ↗</span>
              </a>
            </div>

            <div class="pt-3 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
              <div class="flex justify-between"><span>Канал:</span> <b class="text-slate-800">fan (Фан-сетка)</b></div>
              <div class="flex justify-between"><span>Креатор (campaign):</span> <b id="lblFanCampaign" class="text-slate-800">fan_ainagul</b></div>
              <div class="flex justify-between"><span>Площадка (source):</span> <b id="lblFanSource" class="text-slate-800">tiktok</b></div>
            </div>
          </div>

          <!-- ИНСТРУКЦИЯ ДЛЯ КРЕАТОРА -->
          <div class="bg-gradient-to-br from-indigo-50 to-white p-6 rounded-3xl border border-indigo-200/80 shadow-sm space-y-3">
            <h4 class="text-xs font-black text-indigo-950 uppercase tracking-wider flex items-center space-x-1.5">
              <span>📌 Как установить ссылку в профиль</span>
            </h4>
            <ol class="text-xs text-slate-600 space-y-2 list-decimal list-inside leading-relaxed">
              <li>Скопируйте ссылку выше кнопкой «Скопировать».</li>
              <li>Откройте TikTok / Instagram / YouTube и зайдите в <b>«Изменить профиль»</b>.</li>
              <li>Вставьте ссылку в поле <b>«Веб-сайт» / «Website»</b> (в шапке профиля).</li>
              <li>В описании роликов пишите: <i>«Пройди тест по ссылке в шапке профиля 👆»</i>.</li>
              <li><b>Все заявки попадут в AmoCRM под вашей фамилией</b> и пойдут в зачёт плана по лидам!</li>
            </ol>
          </div>

        </div>

      </div>

    </div>

  <!-- JAVASCRIPT ЛОГИКА -->
  <script>
    const GAS_WEBAPP_URL = 'https://script.google.com/macros/s/AKfycbygzr7KwiYqza9uXbrnjHzV9DRPLyVZ_FrbBxaX6ucuLDJzGpe31zEcdq_dktVCy_A8/exec';

    // Встроенный компактный датасет для мгновенной фильтрации за любые периоды
    const COMPACT_PAYLOAD = {leads_dict_json};
    const S = COMPACT_PAYLOAD.strings;
    const ALL_LEADS = COMPACT_PAYLOAD.rows.map(r => ({{
      id: r[0],
      ts: r[1],
      won: r[2],
      price: r[3],
      dom: S[r[4]],
      path: S[r[5]],
      src: S[r[6]],
      med: S[r[7]],
      cmp: S[r[8]],
      cnt: S[r[9]],
      trm: S[r[10]],
      status_id: r[11],
      name: r[12]
    }}));

    // Текущие фильтры
    let currentPeriod = 'all';
    let filterDateFrom = null; // unix timestamp in seconds
    let filterDateTo = null;   // unix timestamp in seconds
    let currentGranularityDim = 'combos';
    let currentDealsFilter = 'all';

    let filteredLeads = [];
    let currentAggregates = {{}};

    let chartSourcesInstance = null;
    let chartMediumsInstance = null;
    // Инициализация при загрузке страницы
    document.addEventListener('DOMContentLoaded', function () {{
      applyAllFilters();
    }});

    // ============================================================
    // УНИВЕРСАЛЬНАЯ ФИЛЬТРАЦИЯ ЗА ПЕРИОДЫ И ПАРАМЕТРЫ
    // ============================================================
    function setPeriodPreset(preset) {{
      currentPeriod = preset;
      const now = new Date(2026, 10, 10, 11, 30, 0); // local app time Nov 10 2026
      const startOfDay = (d) => Math.floor(new Date(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0).getTime() / 1000);
      const endOfDay = (d) => Math.floor(new Date(d.getFullYear(), d.getMonth(), d.getDate(), 23, 59, 59).getTime() / 1000);

      const presets = ['all', 'today', 'yesterday', 'last7', 'last30', 'nov2026', 'oct2026', 'sep2026', 'aug2026', 'jul2026'];
      presets.forEach(p => {{
        const b = document.getElementById('period-btn-' + p);
        if (b) {{
          if (p === preset) b.className = 'px-3 py-1.5 text-xs font-bold rounded-xl bg-slate-900 text-white transition shadow-sm';
          else b.className = 'px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
        }}
      }});

      document.getElementById('dateInputFrom').value = '';
      document.getElementById('dateInputTo').value = '';

      if (preset === 'all') {{
        filterDateFrom = null; filterDateTo = null;
        document.getElementById('activePeriodLabel').innerText = 'Период: За всё время';
      }} else if (preset === 'today') {{
        filterDateFrom = startOfDay(now);
        filterDateTo = endOfDay(now);
        document.getElementById('activePeriodLabel').innerText = 'Период: Сегодня (10 ноя 2026)';
      }} else if (preset === 'yesterday') {{
        const y = new Date(now); y.setDate(y.getDate() - 1);
        filterDateFrom = startOfDay(y);
        filterDateTo = endOfDay(y);
        document.getElementById('activePeriodLabel').innerText = 'Период: Вчера (9 ноя 2026)';
      }} else if (preset === 'last7') {{
        filterDateFrom = startOfDay(now) - (7 * 86400);
        filterDateTo = endOfDay(now);
        document.getElementById('activePeriodLabel').innerText = 'Период: Последние 7 дней';
      }} else if (preset === 'last30') {{
        filterDateFrom = startOfDay(now) - (30 * 86400);
        filterDateTo = endOfDay(now);
        document.getElementById('activePeriodLabel').innerText = 'Период: Последние 30 дней';
      }} else if (preset === 'nov2026') {{
        filterDateFrom = Math.floor(new Date(2026, 10, 1).getTime() / 1000);
        filterDateTo = Math.floor(new Date(2026, 10, 30, 23, 59, 59).getTime() / 1000);
        document.getElementById('activePeriodLabel').innerText = 'Период: Ноябрь 2026';
      }} else if (preset === 'oct2026') {{
        filterDateFrom = Math.floor(new Date(2026, 9, 1).getTime() / 1000);
        filterDateTo = Math.floor(new Date(2026, 9, 31, 23, 59, 59).getTime() / 1000);
        document.getElementById('activePeriodLabel').innerText = 'Период: Октябрь 2026';
      }} else if (preset === 'sep2026') {{
        filterDateFrom = Math.floor(new Date(2026, 8, 1).getTime() / 1000);
        filterDateTo = Math.floor(new Date(2026, 8, 30, 23, 59, 59).getTime() / 1000);
        document.getElementById('activePeriodLabel').innerText = 'Период: Сентябрь 2026';
      }} else if (preset === 'aug2026') {{
        filterDateFrom = Math.floor(new Date(2026, 7, 1).getTime() / 1000);
        filterDateTo = Math.floor(new Date(2026, 7, 31, 23, 59, 59).getTime() / 1000);
        document.getElementById('activePeriodLabel').innerText = 'Период: Август 2026';
      }} else if (preset === 'jul2026') {{
        filterDateFrom = Math.floor(new Date(2026, 6, 1).getTime() / 1000);
        filterDateTo = Math.floor(new Date(2026, 6, 31, 23, 59, 59).getTime() / 1000);
        document.getElementById('activePeriodLabel').innerText = 'Период: Июль 2026';
      }}

      applyAllFilters();
    }}

    function applyCustomDateRange() {{
      const dFrom = document.getElementById('dateInputFrom').value;
      const dTo = document.getElementById('dateInputTo').value;
      if (!dFrom && !dTo) return;

      const presets = ['all', 'today', 'yesterday', 'last7', 'last30', 'nov2026', 'oct2026', 'sep2026', 'aug2026', 'jul2026'];
      presets.forEach(p => {{
        const b = document.getElementById('period-btn-' + p);
        if (b) b.className = 'px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
      }});

      filterDateFrom = dFrom ? Math.floor(new Date(dFrom + 'T00:00:00').getTime() / 1000) : null;
      filterDateTo = dTo ? Math.floor(new Date(dTo + 'T23:59:59').getTime() / 1000) : null;

      document.getElementById('activePeriodLabel').innerText = 'Период: с ' + (dFrom || 'начала') + ' по ' + (dTo || 'сегодня');
      applyAllFilters();
    }}

    function onFilterChange() {{
      applyAllFilters();
    }}

    function filterByChannel(channel) {{
      document.getElementById('filterMediumSelect').value = channel;
      onFilterChange();
    }}

    function filterByMedium(medium) {{
      const sel = document.getElementById('filterMediumSelect');
      if (sel) sel.value = medium;
      onFilterChange();
    }}

    function filterByPage(page) {{
      document.getElementById('filterPageSelect').value = page;
      onFilterChange();
    }}

    function resetAllFilters() {{
      document.getElementById('filterDomainSelect').value = 'janamen1.kz';
      document.getElementById('filterPageSelect').value = 'all';
      document.getElementById('filterMediumSelect').value = 'all';
      document.getElementById('filterSearchInput').value = '';
      setPeriodPreset('all');
    }}

    function applyAllFilters() {{
      const domFilter = document.getElementById('filterDomainSelect').value;
      const pageFilter = document.getElementById('filterPageSelect').value;
      const medFilter = document.getElementById('filterMediumSelect').value;
      const search = (document.getElementById('filterSearchInput').value || '').toLowerCase().trim();

      // Мгновенная фильтрация массива в памяти (~1-2 мс)
      filteredLeads = ALL_LEADS.filter(l => {{
        if (filterDateFrom && l.ts < filterDateFrom) return false;
        if (filterDateTo && l.ts > filterDateTo) return false;

        if (domFilter === 'janamen1.kz' && l.dom !== 'janamen1.kz') return false;
        if (domFilter === 'janamen1_site' && (l.dom !== 'janamen1.kz' || l.path === '/iwa-9828' || l.path === '/wa-9828')) return false;
        if (domFilter === 'whatsapp_9828' && (l.path !== '/iwa-9828' && l.path !== '/wa-9828' && l.med !== 'Айтым Берикович - органика')) return false;
        if (domFilter === 'janamenhealth.kz' && l.dom !== 'janamenhealth.kz') return false;

        if (pageFilter !== 'all') {{
          if (pageFilter === '/lidmagnit') {{
            if (!l.path.startsWith('/lidmagnit') && !l.path.startsWith('/ligmagnit')) return false;
          }} else if (pageFilter === '/iwa-9828') {{
            if (l.path !== '/iwa-9828' && l.path !== '/wa-9828') return false;
          }} else if (l.path !== pageFilter) {{
            return false;
          }}
        }}

        if (medFilter !== 'all' && l.med !== medFilter) return false;

        if (search) {{
          const hay = (l.src + ' ' + l.med + ' ' + l.cmp + ' ' + l.cnt + ' ' + l.trm + ' ' + l.path + ' ' + l.name).toLowerCase();
          if (!hay.includes(search)) return false;
        }}

        return true;
      }});

      // Агрегация отфильтрованных данных
      computeAggregates();

      // Обновление всех блоков интерфейса
      updateKpis();
      renderSubpageCards();
      renderTables();
      renderCharts();
      renderGranularityTable();
      renderJanamenDealsTable();
    }}

    function computeAggregates() {{
      let leads = 0, won = 0, rev = 0;
      const bySource = {{}}, byMedium = {{}}, byCampaign = {{}}, byContent = {{}}, byTerm = {{}};
      const combos = {{}};
      const subpages = {{}};

      for (let i = 0; i < filteredLeads.length; i++) {{
        const l = filteredLeads[i];
        leads++;
        if (l.won) {{ won++; rev += l.price; }}

        const addDim = (map, k) => {{
          let a = map[k];
          if (!a) a = map[k] = {{ leads: 0, won: 0, rev: 0 }};
          a.leads++;
          if (l.won) {{ a.won++; a.rev += l.price; }}
        }};

        addDim(bySource, l.src);
        addDim(byMedium, l.med);
        addDim(byCampaign, l.cmp);
        addDim(byContent, l.cnt);
        addDim(byTerm, l.trm);
        addDim(subpages, l.path);

        const ck = l.path + '|' + l.src + '|' + l.med + '|' + l.cmp + '|' + l.cnt + '|' + l.trm;
        let c = combos[ck];
        if (!c) {{
          c = combos[ck] = {{
            landing: 'janamen1.kz' + l.path,
            path: l.path,
            src: l.src,
            med: l.med,
            cmp: l.cmp,
            cnt: l.cnt,
            trm: l.trm,
            leads: 0,
            won: 0,
            revenue: 0
          }};
        }}
        c.leads++;
        if (l.won) {{ c.won++; c.revenue += l.price; }}
      }}

      const comboList = Object.values(combos).map(c => {{
        c.cr = c.leads ? Math.round(c.won / c.leads * 1000) / 10 : 0;
        c.avgCheck = c.won ? Math.round(c.revenue / c.won) : 0;
        return c;
      }}).sort((a, b) => b.revenue - a.revenue || b.won - a.won || b.leads - a.leads);

      currentAggregates = {{
        leads, won, rev,
        cr: leads ? (won / leads) : 0,
        avgCheck: won ? Math.round(rev / won) : 0,
        bySource, byMedium, byCampaign, byContent, byTerm,
        subpages,
        combos: comboList
      }};
    }}

    // ============================================================
    // ВКЛАДКИ
    // ============================================================
    function switchTab(tabId) {{
      const tabs = ['analytics', 'granularity', 'builder-bloggers', 'builder-fans'];
      tabs.forEach(t => {{
        const btn = document.getElementById('tab-' + t);
        const view = document.getElementById('view-' + t);
        if (btn && view) {{
          if (t === tabId) {{
            btn.className = 'tab-active py-3.5 px-1 inline-flex items-center space-x-2 whitespace-nowrap';
            view.classList.remove('hidden');
          }} else {{
            btn.className = 'tab-inactive py-3.5 px-1 inline-flex items-center space-x-2 whitespace-nowrap';
            view.classList.add('hidden');
          }}
        }}
      }});
      if (tabId === 'analytics') renderCharts();
      if (tabId === 'granularity') renderGranularityTable();
      if (tabId === 'builder-bloggers') updateBloggerUrl();
      if (tabId === 'builder-fans') updateFanUrl();
    }}

    function drilldownSubpage(subpage) {{
      const sel = document.getElementById('filterPageSelect');
      if (sel) {{
        sel.value = subpage;
        onFilterChange();
      }}
      switchTab('granularity');
    }}

    // ============================================================
    // ОБНОВЛЕНИЕ KPI И ДАШБОРДА
    // ============================================================
    function updateKpis() {{
      const a = currentAggregates;
      document.getElementById('kpiTotalLeads').innerText = a.leads.toLocaleString('ru-RU');
      document.getElementById('kpiWonLeads').innerText = a.won.toLocaleString('ru-RU');
      document.getElementById('kpiCr').innerText = 'Конверсия в оплату: ' + (a.cr * 100).toFixed(1) + '%';
      document.getElementById('kpiRevenue').innerText = a.rev.toLocaleString('ru-RU') + ' ₸';
      document.getElementById('kpiAvgCheck').innerText = 'Средний чек: ' + (a.avgCheck || 0).toLocaleString('ru-RU') + ' ₸';
      document.getElementById('kpiCombosCount').innerText = (a.combos ? a.combos.length : 0).toLocaleString('ru-RU');
      document.getElementById('badgeCombos').innerText = (a.combos ? a.combos.length : 0) + ' связок';
      document.getElementById('badgeNavRevenue').innerText = (a.rev >= 1000000 ? (a.rev / 1000000).toFixed(1) + 'M ₸' : (a.rev / 1000).toFixed(0) + 'k ₸');
    }}

    let currentSubpageView = 'list';

    function setSubpageView(view) {{
      currentSubpageView = view;
      const bList = document.getElementById('btnSubViewList');
      const bCards = document.getElementById('btnSubViewCards');
      const vList = document.getElementById('subpagesListView');
      const vCards = document.getElementById('subpagesCardsView');

      if (view === 'list') {{
        bList.className = 'px-3 py-1.5 rounded-lg bg-white text-slate-900 shadow-sm transition flex items-center space-x-1.5';
        bCards.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition flex items-center space-x-1.5';
        vList.classList.remove('hidden');
        vCards.classList.add('hidden');
      }} else {{
        bCards.className = 'px-3 py-1.5 rounded-lg bg-white text-slate-900 shadow-sm transition flex items-center space-x-1.5';
        bList.className = 'px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition flex items-center space-x-1.5';
        vCards.classList.remove('hidden');
        vList.classList.add('hidden');
      }}
    }}

    function renderSubpageCards() {{
      const meta = {{
        '/iwa-9828': ['📱 Айтым Берикович - органика', 'WhatsApp +7 708 377-98-28 (Wazzup переписки и заявки)'],
        '/lidmagnit': ['🎁 Лид-магнит / Гайды (все вариации)', 'Все варианты лид-магнитов и гайдов (/lidmagnit*)'],
        '/influence': ['🌟 Инфлюенс / Блогеры (МПБ)', 'Интеграции с блогерами и амбассадорами (mpb1, mpb2, mpb3)'],
        '/fun': ['⚡ Квиз / Воронка', 'Интерактивный опрос и подбор программы (/fun)'],
        '/smm': ['📸 SMM / Соцсети', 'Посадочная для SMM и соцсетей (janamen1.kz/smm)'],
        '/organika': ['Органика (Основная)', 'Основная посадочная под органический трафик и посты'],
        '/inst-men': ['Instagram Men', 'Мужская аудитория из соцсетей'],
        '/kaspiform': ['Kaspi-форма', 'Быстрый заказ через Kaspi Рассрочку / Red'],
        '/inst-women': ['Instagram Women', 'Женская аудитория из соцсетей'],
        '/vitamins-inst': ['Витамины Inst', 'Посадочная под витаминные комплексы'],
        '/inst-omega': ['Омега-3 Inst', 'Посадочная под Омега-3 и добавки'],
        '/nikitaform': ['Форма Никита', 'Форма таргетолога Никиты'],
        '/yurakv': ['Квиз Юра', 'Квиз-воронка таргетолога Юры'],
        '/aojiru-inst': ['Аодзиру Inst', 'Посадочная под японский аодзиру'],
        '/': ['Главная страница', 'Главная janamen1.kz']
      }};

      const sub = currentAggregates.subpages || {{}};
      const paths = Object.keys(meta);
      const items = paths.map(p => {{
        const d = sub[p] || {{ leads: 0, won: 0, rev: 0 }};
        const cr = d.leads ? Math.round(d.won / d.leads * 1000) / 10 : 0;
        return {{
          path: p,
          title: meta[p][0],
          desc: meta[p][1],
          leads: d.leads,
          won: d.won,
          revenue: d.rev,
          cr: cr
        }};
      }}).sort((a, b) => b.revenue - a.revenue || b.leads - a.leads);

      const maxRev = Math.max(0, ...items.map(i => i.revenue));
      const maxLeads = Math.max(0, ...items.map(i => i.leads));

      // 1. Отрисовка СПИСКА (Таблицы)
      const tbody = document.getElementById('subpagesTableBody');
      if (tbody) {{
        tbody.innerHTML = items.map(sp => {{
          let badge = '';
          if (sp.revenue === maxRev && maxRev > 0) {{
            badge = '<span class="ml-2 px-2 py-0.5 text-[10px] rounded-md font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">ТОП ВЫРУЧКА</span>';
          }} else if (sp.leads === maxLeads && maxLeads > 0) {{
            badge = '<span class="ml-2 px-2 py-0.5 text-[10px] rounded-md font-bold bg-blue-100 text-blue-800 border border-blue-200">МАКС. ЛИДОВ</span>';
          }} else if (sp.cr >= 5.0 && sp.won >= 3) {{
            badge = '<span class="ml-2 px-2 py-0.5 text-[10px] rounded-md font-bold bg-purple-100 text-purple-800 border border-purple-200">ВЫСОКИЙ CR</span>';
          }}

          const url = (sp.path === '/iwa-9828' || sp.path.startsWith('/wa-')) ? 'https://wa.me/77083779828' : ('https://janamen1.kz' + (sp.path === '/' ? '' : sp.path));
          const avgCheck = sp.won ? Math.round(sp.revenue / sp.won) : 0;

          return `
            <tr class="hover:bg-slate-50 transition">
              <td class="py-3 px-4 whitespace-nowrap">
                <a href="${{url}}" target="_blank" class="font-black text-sm text-brand-600 hover:text-brand-800 code-font inline-flex items-center">
                  <span>${{sp.path}}</span>
                  ${{badge}}
                </a>
                <div class="text-[11px] font-bold text-slate-700 mt-0.5">${{sp.title}}</div>
              </td>
              <td class="py-3 px-4 text-xs text-slate-500 max-w-xs leading-relaxed">
                ${{sp.desc}}
              </td>
              <td class="py-3 px-4 text-center font-extrabold text-slate-900">
                ${{sp.leads.toLocaleString('ru-RU')}}
              </td>
              <td class="py-3 px-4 text-center font-black text-emerald-600 text-sm">
                ${{sp.won.toLocaleString('ru-RU')}}
              </td>
              <td class="py-3 px-4 text-center">
                <span class="px-2 py-1 rounded-lg text-xs font-bold ${{sp.cr >= 5 ? 'bg-emerald-100 text-emerald-800' : (sp.cr >= 3 ? 'bg-blue-50 text-brand-700' : 'bg-slate-100 text-slate-700')}}">
                  ${{sp.cr}}%
                </span>
              </td>
              <td class="py-3 px-4 text-right font-black text-slate-900 text-sm whitespace-nowrap">
                ${{sp.revenue.toLocaleString('ru-RU')}} ₸
              </td>
              <td class="py-3 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">
                ${{avgCheck.toLocaleString('ru-RU')}} ₸
              </td>
              <td class="py-3 px-4 text-center whitespace-nowrap">
                <button onclick="drilldownSubpage('${{sp.path}}')" class="px-3 py-1.5 text-xs font-bold text-purple-700 hover:text-white hover:bg-purple-600 rounded-lg transition border border-purple-200">
                  Смотреть UTM →
                </button>
              </td>
            </tr>
          `;
        }}).join('');
      }}

      // 2. Отрисовка КАРТОЧЕК
      const grid = document.getElementById('subpagesCardsView');
      if (grid) {{
        grid.innerHTML = items.map(sp => {{
          let badge = '', color = 'bg-slate-100 text-slate-700 border-slate-200';
          if (sp.revenue === maxRev && maxRev > 0) {{
            badge = 'ТОП ВЫРУЧКА (' + (sp.revenue / 1000000).toFixed(1) + 'M ₸)';
            color = 'bg-emerald-100 text-emerald-800 border-emerald-200 font-bold';
          }} else if (sp.leads === maxLeads && maxLeads > 0) {{
            badge = 'Максимум лидов (' + sp.leads + ')';
            color = 'bg-blue-100 text-blue-800 border-blue-200 font-bold';
          }} else if (sp.cr >= 5.0 && sp.won >= 3) {{
            badge = 'Высокий CR (' + sp.cr + '%)';
            color = 'bg-purple-100 text-purple-800 border-purple-200 font-bold';
          }}

          const url = (sp.path === '/iwa-9828' || sp.path.startsWith('/wa-')) ? 'https://wa.me/77083779828' : ('https://janamen1.kz' + (sp.path === '/' ? '' : sp.path));
          return `
            <div class="p-5 rounded-2xl border border-slate-200 hover:border-brand-500/50 hover:shadow-md transition bg-gradient-to-br from-white to-slate-50/50 space-y-4">
              <div class="flex items-start justify-between">
                <div>
                  <span class="font-black text-sm text-slate-900 code-font">${{sp.path}}</span>
                  <div class="text-xs font-bold text-slate-700 mt-0.5">${{sp.title}}</div>
                </div>
                ${{badge ? `<span class="px-2 py-0.5 text-[10px] rounded-md border ${{color}}">${{badge}}</span>` : ''}}
              </div>
              <p class="text-[11px] text-slate-500 leading-relaxed">${{sp.desc}}</p>
              <div class="grid grid-cols-3 gap-2 pt-2 border-t border-slate-100 text-center">
                <div class="bg-white p-2 rounded-xl border border-slate-100">
                  <div class="text-[10px] text-slate-400 font-bold uppercase">Лидов</div>
                  <div class="text-sm font-extrabold text-slate-900 mt-0.5">${{sp.leads.toLocaleString('ru-RU')}}</div>
                </div>
                <div class="bg-white p-2 rounded-xl border border-slate-100">
                  <div class="text-[10px] text-emerald-600 font-bold uppercase">Опл. 142</div>
                  <div class="text-sm font-extrabold text-emerald-600 mt-0.5">${{sp.won}}</div>
                </div>
                <div class="bg-white p-2 rounded-xl border border-slate-100">
                  <div class="text-[10px] text-brand-600 font-bold uppercase">Выручка</div>
                  <div class="text-[11px] font-extrabold text-brand-700 mt-1">${{sp.revenue > 0 ? (sp.revenue / 1000).toFixed(0) + 'k ₸' : '0 ₸'}}</div>
                </div>
              </div>
              <div class="pt-1 flex items-center justify-between">
                <span class="text-[11px] text-slate-500 font-medium">Конверсия: <b class="${{sp.cr >= 4 ? 'text-emerald-700 font-extrabold' : 'text-slate-800'}}">${{sp.cr}}%</b></span>
                <button onclick="drilldownSubpage('${{sp.path}}')" class="text-xs font-bold text-purple-700 hover:text-purple-900 transition">Смотреть UTM →</button>
              </div>
            </div>
          `;
        }}).join('');
      }}
    }}

    function renderTables() {{
      const sources = currentAggregates.bySource || {{}};
      const srcTbody = document.getElementById('analyticsTableBody');
      const totalRev = currentAggregates.rev || 1;

      const sortedSources = Object.keys(sources).sort((a,b) => sources[b].rev - sources[a].rev);

      if (sortedSources.length === 0) {{
        srcTbody.innerHTML = '<tr><td colspan="7" class="py-6 text-center text-slate-400">Нет данных за выбранный период</td></tr>';
        return;
      }}

      srcTbody.innerHTML = sortedSources.map(s => {{
        const item = sources[s];
        const cr = item.leads > 0 ? ((item.won / item.leads) * 100).toFixed(1) : '0.0';
        const avg = item.won > 0 ? Math.round(item.rev / item.won) : 0;
        const share = totalRev > 0 ? ((item.rev / totalRev) * 100).toFixed(1) : '0';
        return `
          <tr class="hover:bg-slate-50 transition">
            <td class="py-3 px-4 font-bold text-slate-900 code-font">${{s}}</td>
            <td class="py-3 px-4 text-center font-bold text-slate-800">${{item.leads.toLocaleString('ru-RU')}}</td>
            <td class="py-3 px-4 text-center font-black text-emerald-600">${{item.won}}</td>
            <td class="py-3 px-4 text-center font-bold ${{parseFloat(cr) > 2 ? 'text-emerald-700' : 'text-slate-600'}}">${{cr}}%</td>
            <td class="py-3 px-4 text-right font-black text-slate-900">${{item.rev.toLocaleString('ru-RU')}} ₸</td>
            <td class="py-3 px-4 text-right font-semibold text-slate-700">${{avg.toLocaleString('ru-RU')}} ₸</td>
            <td class="py-3 px-4 text-right">
              <span class="px-2 py-0.5 text-[11px] font-bold bg-blue-50 text-brand-700 rounded-md">${{share}}%</span>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function renderCharts() {{
      const ctxSources = document.getElementById('chartSources');
      const ctxMediums = document.getElementById('chartMediums');
      if (!ctxSources || !ctxMediums) return;
      if (chartSourcesInstance) chartSourcesInstance.destroy();
      if (chartMediumsInstance) chartMediumsInstance.destroy();

      const src = currentAggregates.bySource || {{}};
      const topSrc = Object.keys(src).sort((a, b) => src[b].rev - src[a].rev).slice(0, 8);

      chartSourcesInstance = new Chart(ctxSources.getContext('2d'), {{
        type: 'bar',
        data: {{
          labels: topSrc.length ? topSrc : ['(нет)'],
          datasets: [{{
            label: 'Выручка (₸)',
            data: topSrc.length ? topSrc.map(k => src[k].rev) : [0],
            backgroundColor: ['#2563eb','#10b981','#4f46e5','#f59e0b','#ec4899','#14b8a6','#8b5cf6','#94a3b8'],
            borderRadius: 8
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            y: {{
              beginAtZero: true,
              ticks: {{ callback: v => (v >= 1000000 ? (v / 1000000).toFixed(1) + 'M ₸' : (v / 1000).toFixed(0) + 'k ₸') }}
            }}
          }}
        }}
      }});

      const med = currentAggregates.byMedium || {{}};
      const topMed = Object.keys(med).filter(k => k !== 'none').sort((a, b) => med[b].leads - med[a].leads).slice(0, 8);

      chartMediumsInstance = new Chart(ctxMediums.getContext('2d'), {{
        type: 'doughnut',
        data: {{
          labels: topMed.length ? topMed : ['(нет)'],
          datasets: [{{
            data: topMed.length ? topMed.map(k => med[k].leads) : [1],
            backgroundColor: ['#2563eb','#f59e0b','#ec4899','#10b981','#6366f1','#14b8a6','#8b5cf6','#ef4444']
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ position: 'right' }} }}
        }}
      }});
    }}

    // ============================================================
    // ТАБЛИЦА СДЕЛОК JANAMEN1.KZ
    // ============================================================
    function setDealsFilter(f) {{
      currentDealsFilter = f;
      ['all', 'won', 'open'].forEach(id => {{
        const b = document.getElementById('btnDeals' + id.charAt(0).toUpperCase() + id.slice(1));
        if (b) {{
          if (id === f) b.className = 'px-2.5 py-1 rounded-md bg-white text-slate-900 shadow-sm transition';
          else b.className = 'px-2.5 py-1 rounded-md text-slate-600 hover:text-slate-900 transition';
        }}
      }});
      renderJanamenDealsTable();
    }}

    function filterDealsTable() {{
      renderJanamenDealsTable();
    }}

    function renderJanamenDealsTable() {{
      const tbody = document.getElementById('recentDealsTableBody');
      if (!tbody) return;

      const search = (document.getElementById('dealsSearchInput') ? document.getElementById('dealsSearchInput').value : '').toLowerCase().trim();

      let list = filteredLeads.filter(l => l.dom === 'janamen1.kz');
      if (currentDealsFilter === 'won') {{
        list = list.filter(d => d.won);
      }} else if (currentDealsFilter === 'open') {{
        list = list.filter(d => !d.won && d.status_id !== 143);
      }}

      if (search) {{
        list = list.filter(d => 
          String(d.id).includes(search) ||
          (d.name || '').toLowerCase().includes(search) ||
          (d.src || '').toLowerCase().includes(search) ||
          (d.med || '').toLowerCase().includes(search) ||
          (d.cmp || '').toLowerCase().includes(search) ||
          (d.path || '').toLowerCase().includes(search)
        );
      }}

      // Показываем последние 100 сделок
      list = list.slice(0, 100);

      if (list.length === 0) {{
        tbody.innerHTML = '<tr><td colspan="9" class="py-6 text-center text-slate-400">Сделок не найдено</td></tr>';
        return;
      }}

      tbody.innerHTML = list.map(d => {{
        let statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700">В работе (' + d.status_id + ')</span>';
        if (d.won) {{
          statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">✓ Оплачено (142)</span>';
        }} else if (d.status_id === 143) {{
          statusBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700">Отказ (143)</span>';
        }}

        const dDate = d.ts ? new Date(d.ts * 1000).toLocaleString('ru-RU', {{ day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }}) : '—';

        return `
          <tr class="hover:bg-slate-50 transition">
            <td class="py-2.5 px-4 font-bold text-slate-900 code-font">#${{d.id}}</td>
            <td class="py-2.5 px-4 font-semibold text-slate-800 truncate max-w-[170px]">${{d.name || 'Сделка'}}</td>
            <td class="py-2.5 px-4">${{statusBadge}}</td>
            <td class="py-2.5 px-4 text-right font-black ${{d.won ? 'text-emerald-700' : 'text-slate-800'}}">${{(d.price || 0).toLocaleString('ru-RU')}} ₸</td>
            <td class="py-2.5 px-4 text-slate-500 whitespace-nowrap">${{dDate}}</td>
            <td class="py-2.5 px-4 code-font text-brand-600 font-bold">${{d.path || '/'}}</td>
            <td class="py-2.5 px-4">
              <span class="px-1.5 py-0.5 text-[11px] font-bold bg-slate-100 text-slate-800 rounded">${{d.src}}</span>
              <span class="text-[10px] text-slate-400 ml-1 font-mono">${{d.med}}</span>
            </td>
            <td class="py-2.5 px-4 code-font text-slate-700 text-[11px] truncate max-w-[150px]">${{d.cmp}}</td>
            <td class="py-2.5 px-4 text-center">
              <a href="https://janamen.amocrm.ru/leads/detail/${{d.id}}" target="_blank" class="p-1 text-brand-600 hover:text-brand-800 font-bold inline-block" title="Открыть в AmoCRM">
                ↗
              </a>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    // ============================================================
    // ВКЛАДКА 2: ПОЛНАЯ ДЕТАЛИЗАЦИЯ UTM (ТАБЛИЦА)
    // ============================================================
    function setGranularityDim(dim) {{
      currentGranularityDim = dim;
      const dims = ['combos', 'campaigns', 'contents', 'mediums', 'terms', 'sources'];
      dims.forEach(d => {{
        const btn = document.getElementById('dim-btn-' + d);
        if (btn) {{
          if (d === dim) {{
            btn.className = 'px-3.5 py-2 rounded-xl bg-purple-600 text-white font-bold text-xs transition shadow-sm';
          }} else {{
            btn.className = 'px-3.5 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition';
          }}
        }}
      }});
      renderGranularityTable();
    }}

    function renderGranularityTable() {{
      const thead = document.getElementById('granularityTableHead');
      const tbody = document.getElementById('granularityTableBody');
      const countEl = document.getElementById('granularityRowCount');
      const search = (document.getElementById('granularitySearchInput') ? document.getElementById('granularitySearchInput').value : '').toLowerCase().trim();

      if (currentGranularityDim === 'combos') {{
        thead.innerHTML = `
          <tr>
            <th class="py-2.5 px-3">Посадочная страница</th>
            <th class="py-2.5 px-3">utm_source</th>
            <th class="py-2.5 px-3">utm_medium</th>
            <th class="py-2.5 px-3">utm_campaign</th>
            <th class="py-2.5 px-3">utm_content</th>
            <th class="py-2.5 px-3">utm_term</th>
            <th class="py-2.5 px-3 text-center">Лидов</th>
            <th class="py-2.5 px-3 text-center">Оплачено (142)</th>
            <th class="py-2.5 px-3 text-center">CR %</th>
            <th class="py-2.5 px-3 text-right">Выручка (₸)</th>
            <th class="py-2.5 px-3 text-right">Ср. чек</th>
          </tr>
        `;

        let list = currentAggregates.combos || [];
        if (search) {{
          list = list.filter(item => 
            (item.landing || '').toLowerCase().includes(search) ||
            (item.src || '').toLowerCase().includes(search) ||
            (item.med || '').toLowerCase().includes(search) ||
            (item.cmp || '').toLowerCase().includes(search) ||
            (item.cnt || '').toLowerCase().includes(search) ||
            (item.trm || '').toLowerCase().includes(search)
          );
        }}

        if (countEl) countEl.innerText = 'Показано: ' + list.length + ' связок';

        if (list.length === 0) {{
          tbody.innerHTML = '<tr><td colspan="11" class="py-8 text-center text-slate-400">Ничего не найдено за выбранный период</td></tr>';
          return;
        }}

        tbody.innerHTML = list.map(c => `
          <tr class="hover:bg-purple-50/30 transition">
            <td class="py-2 px-3 font-bold text-brand-700 code-font whitespace-nowrap">${{c.landing || c.path}}</td>
            <td class="py-2 px-3 font-bold text-slate-800 code-font">${{c.src}}</td>
            <td class="py-2 px-3 text-slate-600 code-font">${{c.med}}</td>
            <td class="py-2 px-3 font-semibold text-slate-800 code-font">${{c.cmp}}</td>
            <td class="py-2 px-3 text-slate-500 code-font text-[11px]">${{c.cnt}}</td>
            <td class="py-2 px-3 text-slate-500 code-font text-[11px]">${{c.trm}}</td>
            <td class="py-2 px-3 text-center font-bold text-slate-800">${{c.leads.toLocaleString('ru-RU')}}</td>
            <td class="py-2 px-3 text-center font-black text-emerald-600">${{c.won}}</td>
            <td class="py-2 px-3 text-center font-bold ${{c.cr >= 5 ? 'text-emerald-700 bg-emerald-50 rounded' : (c.won > 0 ? 'text-slate-800' : 'text-slate-400')}}">${{c.cr}}%</td>
            <td class="py-2 px-3 text-right font-black text-slate-900 whitespace-nowrap">${{c.revenue.toLocaleString('ru-RU')}} ₸</td>
            <td class="py-2 px-3 text-right font-semibold text-slate-700 whitespace-nowrap">${{c.avgCheck.toLocaleString('ru-RU')}} ₸</td>
          </tr>
        `).join('');

      }} else {{
        const paramMap = {{
          'campaigns': currentAggregates.byCampaign,
          'contents': currentAggregates.byContent,
          'mediums': currentAggregates.byMedium,
          'terms': currentAggregates.byTerm,
          'sources': currentAggregates.bySource
        }};
        const pNames = {{
          'campaigns': 'utm_campaign (Кампания)',
          'contents': 'utm_content (Креатив)',
          'mediums': 'utm_medium (Канал)',
          'terms': 'utm_term (Аудитория)',
          'sources': 'utm_source (Площадка)'
        }};

        thead.innerHTML = `
          <tr>
            <th class="py-3 px-4">${{pNames[currentGranularityDim] || 'Параметр'}}</th>
            <th class="py-3 px-4 text-center">Всего заявок</th>
            <th class="py-3 px-4 text-center">Оплачено (Статус 142)</th>
            <th class="py-3 px-4 text-center">Конверсия (CR %)</th>
            <th class="py-3 px-4 text-right">Выручка (₸)</th>
            <th class="py-3 px-4 text-right">Средний чек (₸)</th>
          </tr>
        `;

        const srcObj = paramMap[currentGranularityDim] || {{}};
        let list = Object.keys(srcObj).map(k => ({{
          name: k,
          leads: srcObj[k].leads,
          won: srcObj[k].won,
          revenue: srcObj[k].rev,
          cr: srcObj[k].leads ? Math.round(srcObj[k].won / srcObj[k].leads * 1000) / 10 : 0,
          avgCheck: srcObj[k].won ? Math.round(srcObj[k].rev / srcObj[k].won) : 0
        }})).sort((a,b) => b.revenue - a.revenue || b.won - a.won || b.leads - a.leads);

        if (search) {{
          list = list.filter(item => item.name.toLowerCase().includes(search));
        }}

        if (countEl) countEl.innerText = 'Показано: ' + list.length + ' позиций';

        if (list.length === 0) {{
          tbody.innerHTML = '<tr><td colspan="6" class="py-8 text-center text-slate-400">Ничего не найдено за выбранный период</td></tr>';
          return;
        }}

        tbody.innerHTML = list.map(item => `
          <tr class="hover:bg-slate-50 transition">
            <td class="py-2.5 px-4 font-bold text-slate-900 code-font">${{item.name}}</td>
            <td class="py-2.5 px-4 text-center font-bold text-slate-800">${{item.leads.toLocaleString('ru-RU')}}</td>
            <td class="py-2.5 px-4 text-center font-black text-emerald-600">${{item.won}}</td>
            <td class="py-2.5 px-4 text-center font-bold ${{item.cr >= 5 ? 'text-emerald-700 bg-emerald-50 rounded' : 'text-slate-600'}}">${{item.cr}}%</td>
            <td class="py-2.5 px-4 text-right font-black text-slate-900">${{item.revenue.toLocaleString('ru-RU')}} ₸</td>
            <td class="py-2.5 px-4 text-right font-semibold text-slate-700">${{item.avgCheck.toLocaleString('ru-RU')}} ₸</td>
          </tr>
        `).join('');
      }}
    }}

    function exportGranularityCsv() {{
      const list = currentAggregates.combos || [];
      if (!list.length) return;

      let csv = 'Landing,utm_source,utm_medium,utm_campaign,utm_content,utm_term,Leads,Won,CR_Percent,Revenue_KZT,AvgCheck_KZT\\n';
      list.forEach(c => {{
        const row = [
          c.landing || c.path,
          c.src,
          c.med,
          c.cmp,
          c.cnt,
          c.trm,
          c.leads,
          c.won,
          c.cr,
          c.revenue,
          c.avgCheck
        ].map(v => '"' + String(v).replace(/"/g, '""') + '"').join(',');
        csv += row + '\\n';
      }});

      const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.setAttribute('download', 'utm_analytics_filtered.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    // ============================================================
    // КОНСТРУКТОР UTM ДЛЯ БЛОГЕРОВ (МПБ)
    // ============================================================
    function cleanNick(raw) {{
      if (!raw) return '';
      let s = raw.trim();
      s = s.replace(/^https?:\/\/(www\.)?instagram\.com\//i, '');
      s = s.replace(/^https?:\/\/(www\.)?tiktok\.com\/@?/i, '');
      s = s.replace(/^@+/, '');
      s = s.split('?')[0].split('/')[0].trim();
      return s.toLowerCase();
    }}

    function onBloggerPageChange() {{
      const sel = document.getElementById('blgPage').value;
      const inp = document.getElementById('blgCustomPage');
      if (sel === 'custom') {{
        inp.classList.remove('hidden');
      }} else {{
        inp.classList.add('hidden');
      }}
      updateBloggerUrl();
    }}

    function setBloggerNick(nick) {{
      document.getElementById('blgNick').value = nick;
      updateBloggerUrl();
    }}

    function updateBloggerUrl() {{
      const elManager = document.getElementById('blgManager');
      if (!elManager) return;
      const manager = elManager.value;
      const pageSel = document.getElementById('blgPage').value;
      const customPage = document.getElementById('blgCustomPage').value.trim();
      let baseUrl = pageSel === 'custom' ? (customPage || 'https://janamen1.kz/influence') : pageSel;
      
      const rawNick = document.getElementById('blgNick').value;
      const source = cleanNick(rawNick) || 'sarsssembaeva';
      const format = document.getElementById('blgFormat').value;
      const campaign = document.getElementById('blgCampaign').value;

      baseUrl = baseUrl.replace(/\/+$/, '');
      const url = baseUrl + '?utm_source=' + encodeURIComponent(source) +
                  '&utm_medium=' + encodeURIComponent(manager) +
                  '&utm_campaign=' + encodeURIComponent(campaign) +
                  '&utm_content=' + encodeURIComponent(format);

      document.getElementById('blgResultUrl').innerText = url;
      document.getElementById('btnTestBlgUrl').href = url;
      document.getElementById('lblBlgMedium').innerText = manager;
      document.getElementById('lblBlgSource').innerText = source;
      document.getElementById('lblBlgContent').innerText = format;

      const waText = "Сәлеметсіз бе! 🌿\\n\\nВот ваша персональная ссылка для отметки в Stories:\\n" + url + "\\n\\nПожалуйста, добавьте её кликабельным стикером-наклейкой в Stories (текст на стикере: «Заказать витамины Jana Men» или «Пройти тест»).\\nСпасибо большое!";
      document.getElementById('blgWhatsAppText').value = waText;
    }}

    function copyBloggerUrl() {{
      const url = document.getElementById('blgResultUrl').innerText.trim();
      navigator.clipboard.writeText(url).then(() => {{
        const btn = document.getElementById('btnCopyBlgUrl');
        const orig = btn.innerHTML;
        btn.innerHTML = '<span class="text-white font-bold">Скопировано! ✅</span>';
        setTimeout(() => {{ btn.innerHTML = orig; }}, 2000);
      }});
    }}

    function copyBloggerMessage() {{
      const txt = document.getElementById('blgWhatsAppText').value;
      navigator.clipboard.writeText(txt).then(() => {{
        const btn = document.getElementById('btnCopyBlgMsg');
        const orig = btn.innerHTML;
        btn.innerHTML = '<span class="text-white font-bold">ТЗ скопировано! ✅ Вставьте в WhatsApp</span>';
        setTimeout(() => {{ btn.innerHTML = orig; }}, 2000);
      }});
    }}

    // ============================================================
    // КОНСТРУКТОР UTM ДЛЯ ФАН-АККАУНТОВ (СЕТКА)
    // ============================================================
    const FAN_ACCOUNTS_DATA = {{
      'fan_ainagul': [
        {{ label: '@janamenfun (TikTok / Reels)', nick: 'janamenfun' }},
        {{ label: 'Другой аккаунт...', nick: 'custom' }}
      ],
      'fan_dilnaz': [
        {{ label: '@janamen_fans (TikTok / Inst)', nick: 'janamen_fans' }},
        {{ label: '@janamen_fanss (YouTube Shorts)', nick: 'janamen_fanss' }},
        {{ label: 'Другой аккаунт...', nick: 'custom' }}
      ],
      'fan_aysulu': [
        {{ label: '@janamennfans (TikTok / Inst)', nick: 'janamennfans' }},
        {{ label: '@janamen.edit (Сетка 2)', nick: 'janamen.edit' }},
        {{ label: '@janamenaitymfan (Shorts)', nick: 'janamenaitymfan' }},
        {{ label: 'Другой аккаунт...', nick: 'custom' }}
      ],
      'fan_kamila': [
        {{ label: '@aitym.fanclub (TikTok / Inst)', nick: 'aitym.fanclub' }},
        {{ label: 'Другой аккаунт...', nick: 'custom' }}
      ],
      'fan_aida': [
        {{ label: '@janamennn.fan (TikTok)', nick: 'janamennn.fan' }},
        {{ label: '@janamennnfan (Inst / Shorts)', nick: 'janamennnfan' }},
        {{ label: 'Другой аккаунт...', nick: 'custom' }}
      ],
      'fan_adina': [
        {{ label: '@jana.men68 (TikTok)', nick: 'jana.men68' }},
        {{ label: '@aitymzhakupovfanacc (Inst)', nick: 'aitymzhakupovfanacc' }},
        {{ label: '@jana.menfan (TikTok 2)', nick: 'jana.menfan' }},
        {{ label: '@janamen_fan (Inst 2)', nick: 'janamen_fan' }},
        {{ label: 'Другой аккаунт...', nick: 'custom' }}
      ]
    }};

    function onFanCreatorChange() {{
      const elCreator = document.getElementById('fanCreator');
      if (!elCreator) return;
      const creator = elCreator.value;
      const accSelect = document.getElementById('fanAccount');
      const accounts = FAN_ACCOUNTS_DATA[creator] || [{{ label: 'Другой аккаунт...', nick: 'custom' }}];

      accSelect.innerHTML = accounts.map(a => `<option value="${{a.nick}}">${{a.label}}</option>`).join('');
      onFanAccountChange();
    }}

    function onFanAccountChange() {{
      const val = document.getElementById('fanAccount').value;
      const inp = document.getElementById('fanCustomAccount');
      if (val === 'custom') {{
        inp.classList.remove('hidden');
      }} else {{
        inp.classList.add('hidden');
      }}
      updateFanUrl();
    }}

    function updateFanUrl() {{
      const elCreator = document.getElementById('fanCreator');
      if (!elCreator) return;
      const creator = elCreator.value;
      const platform = document.getElementById('fanPlatform').value;
      const accSel = document.getElementById('fanAccount').value;
      const customAcc = document.getElementById('fanCustomAccount').value.trim();
      const rawNick = accSel === 'custom' ? (customAcc || 'fan_acc') : accSel;
      const nickClean = rawNick.replace(/^@/, '').replace(/[^a-zA-Z0-9._-]/g, '_');

      const page = document.getElementById('fanPage').value.replace(/\/+$/, '');
      const placement = document.getElementById('fanPlacement').value;

      const content = nickClean + '_' + placement;

      const url = page + '?utm_source=' + encodeURIComponent(platform) +
                  '&utm_medium=fan' +
                  '&utm_campaign=' + encodeURIComponent(creator) +
                  '&utm_content=' + encodeURIComponent(content);

      document.getElementById('fanResultUrl').innerText = url;
      document.getElementById('btnTestFanUrl').href = url;
      document.getElementById('lblFanCampaign').innerText = creator;
      document.getElementById('lblFanSource').innerText = platform;
    }}

    function copyFanUrl() {{
      const url = document.getElementById('fanResultUrl').innerText.trim();
      navigator.clipboard.writeText(url).then(() => {{
        const btn = document.getElementById('btnCopyFanUrl');
        const orig = btn.innerHTML;
        btn.innerHTML = '<span class="text-white font-bold">Ссылка скопирована! ✅</span>';
        setTimeout(() => {{ btn.innerHTML = orig; }}, 2000);
      }});
    }}

    // Инициализация конструкторов при старте:
    setTimeout(() => {{
      onFanCreatorChange();
      updateBloggerUrl();
    }}, 100);

    // ============================================================
    // СИНХРОНИЗАЦИЯ AMOCRM
    // ============================================================
    function syncAmoCRM() {{
      const btn = document.getElementById('btnSyncCRM');
      const idle = btn.innerHTML;
      btn.innerHTML = '<span>⏳ Синхронизация...</span>';
      btn.disabled = true;

      fetch(GAS_WEBAPP_URL + '?action=sync_amocrm')
        .then(r => r.json())
        .then(() => {{
          btn.innerHTML = '<span>✓ Обновлено</span>';
        }})
        .catch(() => {{
          btn.innerHTML = '<span>Нет связи с Google Script</span>';
        }})
        .finally(() => setTimeout(() => {{ btn.disabled = false; btn.innerHTML = idle; }}, 2500));
    }}
  </script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

with open('gas/Dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Generated portal HTML with interactive period and multi-filter toolbar!")
