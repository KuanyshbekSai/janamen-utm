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
  <title>Jana Men — Сквозная UTM-Аналитика & Оплаты</title>
  
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Supabase JS Client for Realtime & Instant Data -->
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
  
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
  </style>
</head>
<body class="h-full flex flex-col text-slate-800 antialiased selection:bg-brand-500 selection:text-white">

  <!-- ШАПКА ПОРТАЛА (КОМПАКТНАЯ В 1 СТРОКУ) -->
  <header class="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm w-full">
    <div class="w-full px-4 sm:px-6">
      <div class="flex justify-between items-center h-16">
        
        <!-- ЛОГОТИП И СТАТУС -->
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 to-indigo-600 flex items-center justify-center text-white font-black text-xl shadow-md shadow-brand-500/20">
            JM
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <h1 class="text-base sm:text-lg font-black tracking-tight text-slate-900 leading-none">Jana Men</h1>
              <span class="px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wider bg-brand-50 text-brand-700 border border-brand-200 rounded-full">Сквозная Аналитика</span>
            </div>
            <p class="text-[11px] text-slate-500 font-medium">Полная детализация связок, конверсий и оплат AmoCRM</p>
          </div>
        </div>

        <!-- КНОПКИ ДЕЙСТВИЙ -->
        <div class="flex items-center space-x-2.5">
          <span id="liveStatus" class="hidden sm:inline-flex px-2.5 py-1 text-[11px] font-bold rounded-lg border bg-emerald-50 text-emerald-700 border-emerald-200">🟢 Supabase Realtime (36.7k сделок)</span>
          <button onclick="openLinkGeneratorModal()" class="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-bold text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg transition border border-purple-200 shadow-sm">
            <span>🔗 Ссылка для блогера</span>
          </button>
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
    </div>
  </header>

  <!-- ОСНОВНОЙ КОНТЕНТ (FULL WIDTH НА ВЕСЬ ЭКРАН) -->
  <main class="flex-1 w-full px-3 sm:px-6 py-4 space-y-4">

    <!-- 1. ПОЛОСА КЛЮЧЕВЫХ KPI КАРТОЧЕК (ПЕРЕСЧИТЫВАЕТСЯ НА ЛЕТУ) -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      
      <div class="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Всего заявок (лидов)</div>
        <div id="kpiTotalLeads" class="text-xl sm:text-3xl font-black text-slate-900 mt-1">—</div>
        <div class="text-[11px] text-slate-500 mt-0.5" id="kpiLeadsPeriod">за выбранный период</div>
      </div>

      <div class="bg-white p-4 sm:p-5 rounded-2xl border border-emerald-200 shadow-sm bg-gradient-to-br from-white to-emerald-50/40">
        <div class="text-[11px] font-bold text-emerald-700 uppercase tracking-wider">Оплачено (Статус 142)</div>
        <div id="kpiWonLeads" class="text-xl sm:text-3xl font-black text-emerald-600 mt-1">—</div>
        <div id="kpiCr" class="text-[11px] font-bold text-emerald-700 mt-0.5">Конверсия (CR): —</div>
      </div>

      <div class="bg-white p-4 sm:p-5 rounded-2xl border border-blue-200 shadow-sm bg-gradient-to-br from-white to-blue-50/40">
        <div class="text-[11px] font-bold text-brand-700 uppercase tracking-wider">Подтвержденная Выручка</div>
        <div id="kpiRevenue" class="text-xl sm:text-3xl font-black text-brand-700 mt-1">—</div>
        <div id="kpiAvgCheck" class="text-[11px] font-semibold text-slate-600 mt-0.5">Средний чек: —</div>
      </div>

      <div class="bg-white p-4 sm:p-5 rounded-2xl border border-purple-200 shadow-sm bg-gradient-to-br from-white to-purple-50/40">
        <div class="text-[11px] font-bold text-purple-700 uppercase tracking-wider">Активных UTM-связок</div>
        <div id="kpiCombosCount" class="text-xl sm:text-3xl font-black text-purple-700 mt-1">—</div>
        <div class="text-[11px] text-slate-500 mt-0.5">в выбранном срезе</div>
      </div>

    </div>

    <!-- 2. СВОРАЧИВАЕМЫЙ БЛОК ФИЛЬТРАЦИИ -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      
      <!-- ШАПКА ФИЛЬТРОВ: АКТИВНЫЙ БЕЙДЖ + КНОПКА СВЕРНУТЬ/РАЗВЕРНУТЬ -->
      <div class="px-4 py-3 bg-slate-50/70 border-b border-slate-200/80 flex items-center justify-between gap-3">
        <div class="flex items-center space-x-2 overflow-hidden">
          <span class="w-2 h-2 rounded-full bg-brand-600 animate-pulse"></span>
          <span class="text-xs font-black text-slate-800 uppercase tracking-wider whitespace-nowrap">Фильтры:</span>
          <span id="activeFilterBadge" class="text-xs font-bold px-2.5 py-0.5 rounded-lg bg-blue-100 text-brand-800 border border-blue-200 truncate">
            Весь период · Все каналы
          </span>
        </div>

        <div class="flex items-center space-x-2">
          <button onclick="resetAllFilters()" class="text-xs font-semibold text-slate-500 hover:text-slate-800 px-2 py-1 rounded-lg hover:bg-slate-200/60 transition flex items-center space-x-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <span class="hidden sm:inline">Сбросить</span>
          </button>
          
          <button onclick="toggleFilters()" id="btnToggleFilters" class="px-3 py-1.5 text-xs font-bold rounded-xl bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition shadow-sm flex items-center space-x-1.5">
            <span id="toggleFilterText">Свернуть фильтры</span>
            <svg id="toggleFilterIcon" class="w-3.5 h-3.5 text-slate-500 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
          </button>
        </div>
      </div>

      <!-- ТЕЛО ФИЛЬТРОВ (СВОРАЧИВАЕМОЕ) -->
      <div id="filtersBody" class="p-4 sm:p-5 space-y-3.5 transition-all">
        
        <!-- СТРОКА 1: ПЕРИОД -->
        <div class="flex flex-wrap items-center gap-1.5">
          <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1">Период:</span>
          <button onclick="setPeriodPreset('all')" id="period-btn-all" class="px-2.5 py-1 text-xs font-bold rounded-lg bg-slate-900 text-white transition shadow-sm">Весь период</button>
          <button onclick="setPeriodPreset('today')" id="period-btn-today" class="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Сегодня (10 ноя)</button>
          <button onclick="setPeriodPreset('yesterday')" id="period-btn-yesterday" class="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Вчера (9 ноя)</button>
          <button onclick="setPeriodPreset('last7')" id="period-btn-last7" class="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition">7 дней</button>
          <button onclick="setPeriodPreset('last30')" id="period-btn-last30" class="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition">30 дней</button>
          <button onclick="setPeriodPreset('nov2026')" id="period-btn-nov2026" class="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Ноябрь 2026</button>
          <button onclick="setPeriodPreset('oct2026')" id="period-btn-oct2026" class="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Октябрь 2026</button>

          <!-- ТОЧНЫЕ ДАТЫ -->
          <div class="inline-flex items-center space-x-1 ml-auto text-xs">
            <span class="text-slate-400 text-[11px]">с</span>
            <input type="date" id="dateInputFrom" onchange="applyCustomDateRange()" class="px-2 py-0.5 text-xs bg-slate-50 border border-slate-200 rounded-lg font-medium">
            <span class="text-slate-400 text-[11px]">по</span>
            <input type="date" id="dateInputTo" onchange="applyCustomDateRange()" class="px-2 py-0.5 text-xs bg-slate-50 border border-slate-200 rounded-lg font-medium">
          </div>
        </div>

        <!-- СТРОКА 2: БЫСТРЫЕ КАНАЛЫ (PILLS) -->
        <div class="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100 text-xs">
          <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1">Каналы:</span>
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
          <button onclick="setGranularityDim('tags')" class="px-2.5 py-1 rounded-lg bg-amber-100 hover:bg-amber-200 text-amber-900 border-2 border-amber-400 font-black transition flex items-center space-x-1 shadow-sm">
            <span>🏷️ Срез по Тегам CRM</span>
          </button>
        </div>

        <!-- СТРОКА 3: ДЕТАЛЬНЫЕ ВЫПАДАЮЩИЕ СПИСКИ И ПОИСК -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 border-t border-slate-100">
          <div>
            <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Посадочная страница:</label>
            <select id="filterPageSelect" onchange="onFilterChange()" class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-medium text-slate-800">
              <option value="all">Все страницы и точки входа</option>
              <optgroup label="🎯 5 ОСНОВНЫХ КАНАЛОВ (Jana Men)">
                <option value="/iwa-9828">📱 WhatsApp 9828 (WZ 77083779828 — Айтым Берикович)</option>
                <option value="wa-0333">📱 WhatsApp 0333 (WZ 7475000333 / 500 03 33)</option>
                <option value="/lidmagnit">🎁 /lidmagnit (Все варианты лид-магнитов и гайдов)</option>
                <option value="/influence">🌟 /influence (Инфлюенс / Блогеры МПБ)</option>
                <option value="/fun">⚡ /fun (Квиз-воронка)</option>
                <option value="/smm">📸 /smm (SMM / Соцсети)</option>
              </optgroup>
              <optgroup label="Остальные страницы">
                <option value="/organika">/organika (Форма заявки / Консультация)</option>
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
            <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Канал (utm_medium):</label>
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
            <label class="block text-[10px] font-bold text-slate-500 uppercase mb-1">Поиск по UTM / Блогеру / Кампании:</label>
            <input type="text" id="filterSearchInput" oninput="onFilterChange()" placeholder="sarsssembaeva, ugc, kaspiform..." class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-medium text-slate-800">
          </div>
        </div>

      </div>

    </div>

    <!-- 3. ГЛАВНАЯ ТАБЛИЦА: ДЕТАЛИЗАЦИЯ ВСЕХ UTM-СВЯЗОК -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden space-y-0">
      
      <!-- ШАПКА ТАБЛИЦЫ И СРЕЗЫ (SUB-TABS) -->
      <div class="p-4 sm:p-5 border-b border-slate-200 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h2 class="text-base sm:text-lg font-black text-slate-900 tracking-tight">Таблица связок и эффективности UTM</h2>
          <p class="text-xs text-slate-500 mt-0.5">Оценка переходов, конверсии в оплату и подтвержденной выручки по всем параметрам</p>
        </div>

        <button onclick="exportGranularityCsv()" class="self-start lg:self-auto px-3 py-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition border border-slate-200 flex items-center space-x-1.5">
          <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
          <span>Экспорт отфильтрованного в CSV</span>
        </button>
      </div>

      <!-- КНОПКИ ВЫБОРА СРЕЗА (SUB-TABS) -->
      <div class="px-4 py-3 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center gap-1.5 overflow-x-auto text-xs">
        <button onclick="setGranularityDim('combos')" id="dim-btn-combos" class="px-3.5 py-1.5 rounded-xl bg-purple-600 text-white font-bold text-xs transition shadow-sm">
          Полные связки (Combo)
        </button>
        <button onclick="setGranularityDim('tags')" id="dim-btn-tags" class="px-3.5 py-1.5 rounded-xl bg-amber-100 text-amber-900 hover:bg-amber-200 border-2 border-amber-400 font-black text-xs transition shadow-sm flex items-center space-x-1">
          <span>🏷️</span>
          <span>ТЕГИ AmoCRM</span>
        </button>
        <button onclick="setGranularityDim('sources')" id="dim-btn-sources" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
          utm_source (Площадки / Блогеры)
        </button>
        <button onclick="setGranularityDim('mediums')" id="dim-btn-mediums" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
          utm_medium (Менеджеры / Каналы)
        </button>
        <button onclick="setGranularityDim('campaigns')" id="dim-btn-campaigns" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
          utm_campaign (Кампании)
        </button>
        <button onclick="setGranularityDim('contents')" id="dim-btn-contents" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
          utm_content (Креативы)
        </button>
        <button onclick="setGranularityDim('terms')" id="dim-btn-terms" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
          utm_term (Аудитории)
        </button>
        <button onclick="setGranularityDim('subpages')" id="dim-btn-subpages" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition">
          📄 Посадочные страницы (Subpages)
        </button>
      </div>

      <!-- ЖИВОЙ ПОИСК ПО ТАБЛИЦЕ -->
      <div class="p-3 border-b border-slate-200 flex items-center justify-between gap-4">
        <div class="relative flex-1 max-w-md">
          <input type="text" id="granularitySearchInput" oninput="renderGranularityTable()" placeholder="Быстрый поиск по любому слову из таблицы..." class="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 transition">
          <svg class="w-4 h-4 text-slate-400 absolute left-3 top-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        </div>
        <span id="granularityRowCount" class="text-xs font-bold text-slate-500 whitespace-nowrap">Показано: 0 связок</span>
      </div>

      <!-- ТАБЛИЦА НА ВСЮ ШИРИНУ -->
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

    <!-- МОДАЛЬНОЕ ОКНО ГЕНЕРАТОРА ССЫЛОК ДЛЯ БЛОГЕРОВ -->
    <div id="linkGenModal" class="hidden fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center font-bold">🔗</div>
            <h3 class="text-base font-black text-slate-900">Генератор трекинг-ссылки блогера</h3>
          </div>
          <button onclick="closeLinkGeneratorModal()" class="text-slate-400 hover:text-slate-600 p-1 text-lg font-bold">✕</button>
        </div>

        <p class="text-xs text-slate-500 leading-relaxed">
          Ссылка автоматически считает <b>каждый клик подписчиков</b> в нашей базе Supabase и передает UTM в <b>AmoCRM</b> при отправке заявки.
        </p>

        <div class="space-y-3 text-xs font-semibold text-slate-700">
          <div>
            <label class="block text-[11px] uppercase tracking-wider text-slate-400 font-bold mb-1">Ник или имя блогера (utm_content):</label>
            <input type="text" id="genBloggerName" oninput="updateGeneratedLink()" placeholder="например: sarsssembaeva, bika_mazhenova, ainyshka" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 font-bold text-slate-900">
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-[11px] uppercase tracking-wider text-slate-400 font-bold mb-1">Менеджер (utm_medium):</label>
              <select id="genManager" onchange="updateGeneratedLink()" class="w-full px-2.5 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 font-bold text-slate-900">
                <option value="mpb2">mpb2 (Алина)</option>
                <option value="mpb1">mpb1 (Анельжан)</option>
                <option value="mpb3">mpb3 (Алуа)</option>
                <option value="mpb4">mpb4 (Дарина)</option>
                <option value="organic">organic (Органика)</option>
              </select>
            </div>

            <div>
              <label class="block text-[11px] uppercase tracking-wider text-slate-400 font-bold mb-1">Посадочная страница:</label>
              <select id="genPage" onchange="updateGeneratedLink()" class="w-full px-2.5 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 font-bold text-slate-900">
                <option value="/organika">/organika (Форма заявки)</option>
                <option value="/influence">/influence (Инфлюенс)</option>
                <option value="/lidmagnit">/lidmagnit (Лид-магнит)</option>
                <option value="/">/ (Главная)</option>
              </select>
            </div>
          </div>

          <div class="pt-2">
            <label class="block text-[11px] uppercase tracking-wider text-purple-700 font-bold mb-1">Готовая ссылка для блогера (с авто-трекером кликов):</label>
            <div class="relative">
              <input type="text" id="genResultUrl" readonly class="w-full pl-3 pr-24 py-2.5 bg-purple-50/60 border border-purple-200 rounded-xl text-xs font-mono font-bold text-purple-900 select-all">
              <button onclick="copyGeneratedLink()" id="btnCopyGenLink" class="absolute right-1 top-1 bottom-1 px-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-bold transition shadow-sm">
                Копировать
              </button>
            </div>
            <span id="copySuccessMsg" class="hidden text-[11px] text-emerald-600 font-bold mt-1">✓ Ссылка скопирована в буфер обмена!</span>
          </div>
        </div>
      </div>
    </div>

  </main>

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
      name: r[12],
      tags: (r[13] || []).map(idx => S[idx])
    }}));

    // Текущие фильтры
    let currentPeriod = 'all';
    let filterDateFrom = null; // unix timestamp in seconds
    let filterDateTo = null;   // unix timestamp in seconds
    let currentGranularityDim = 'combos';
    let filtersCollapsed = false;

    // Агрегаты
    let currentAggregates = {{}};

    // ============================================================
    // СВОРАЧИВАНИЕ / РАЗВОРАЧИВАНИЕ ФИЛЬТРОВ
    // ============================================================
    function toggleFilters() {{
      filtersCollapsed = !filtersCollapsed;
      const body = document.getElementById('filtersBody');
      const txt = document.getElementById('toggleFilterText');
      const icon = document.getElementById('toggleFilterIcon');
      if (filtersCollapsed) {{
        body.classList.add('hidden');
        txt.innerText = 'Развернуть фильтры';
        icon.style.transform = 'rotate(180deg)';
      }} else {{
        body.classList.remove('hidden');
        txt.innerText = 'Свернуть фильтры';
        icon.style.transform = 'rotate(0deg)';
      }}
    }}

    // ============================================================
    // ФИЛЬТРАЦИЯ ПО ПЕРИОДУ
    // ============================================================
    function setPeriodPreset(preset) {{
      currentPeriod = preset;
      const now = new Date();
      const nowTs = Math.floor(now.getTime() / 1000);

      // Сброс подсветки кнопок периодов
      const buttons = document.querySelectorAll('#periodButtonContainer button, [id^="period-btn-"]');
      buttons.forEach(b => {{
        if (b.id === 'period-btn-' + preset) {{
          b.className = 'px-2.5 py-1 text-xs font-bold rounded-lg bg-slate-900 text-white transition shadow-sm';
        }} else {{
          b.className = 'px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
        }}
      }});

      if (preset === 'all') {{
        filterDateFrom = null;
        filterDateTo = null;
      }} else if (preset === 'today') {{
        const start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        filterDateFrom = Math.floor(start.getTime() / 1000);
        filterDateTo = nowTs;
      }} else if (preset === 'yesterday') {{
        const start = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
        const end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
        filterDateFrom = Math.floor(start.getTime() / 1000);
        filterDateTo = Math.floor(end.getTime() / 1000);
      }} else if (preset === 'last7') {{
        filterDateFrom = nowTs - 7 * 86400;
        filterDateTo = nowTs;
      }} else if (preset === 'last30') {{
        filterDateFrom = nowTs - 30 * 86400;
        filterDateTo = nowTs;
      }} else if (preset === 'nov2026') {{
        const start = new Date(2026, 10, 1);
        const end = new Date(2026, 10, 30, 23, 59, 59);
        filterDateFrom = Math.floor(start.getTime() / 1000);
        filterDateTo = Math.floor(end.getTime() / 1000);
      }} else if (preset === 'oct2026') {{
        const start = new Date(2026, 9, 1);
        const end = new Date(2026, 9, 31, 23, 59, 59);
        filterDateFrom = Math.floor(start.getTime() / 1000);
        filterDateTo = Math.floor(end.getTime() / 1000);
      }}

      onFilterChange();
    }}

    function applyCustomDateRange() {{
      const fromVal = document.getElementById('dateInputFrom').value;
      const toVal = document.getElementById('dateInputTo').value;
      if (!fromVal && !toVal) return;

      currentPeriod = 'custom';
      filterDateFrom = fromVal ? Math.floor(new Date(fromVal).getTime() / 1000) : null;
      filterDateTo = toVal ? Math.floor(new Date(toVal + 'T23:59:59').getTime() / 1000) : null;

      const buttons = document.querySelectorAll('#periodButtonContainer button, [id^="period-btn-"]');
      buttons.forEach(b => b.className = 'px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition');

      onFilterChange();
    }}

    function filterByPage(page) {{
      const sel = document.getElementById('filterPageSelect');
      if (sel) sel.value = page;
      onFilterChange();
    }}

    function filterByMedium(medium) {{
      const sel = document.getElementById('filterMediumSelect');
      if (sel) sel.value = medium;
      onFilterChange();
    }}

    function resetAllFilters() {{
      const pSel = document.getElementById('filterPageSelect');
      if (pSel) pSel.value = 'all';
      const mSel = document.getElementById('filterMediumSelect');
      if (mSel) mSel.value = 'all';
      const sInp = document.getElementById('filterSearchInput');
      if (sInp) sInp.value = '';
      const dFrom = document.getElementById('dateInputFrom');
      if (dFrom) dFrom.value = '';
      const dTo = document.getElementById('dateInputTo');
      if (dTo) dTo.value = '';
      setPeriodPreset('all');
    }}

    // ============================================================
    // ОСНОВНАЯ ФИЛЬТРАЦИЯ И ПЕРЕСЧЕТ
    // ============================================================
    function onFilterChange() {{
      applyAllFilters();
      updateKpis();
      renderGranularityTable();
      updateActiveFilterBadge();
    }}

    function updateActiveFilterBadge() {{
      const pSel = document.getElementById('filterPageSelect').value;
      const mSel = document.getElementById('filterMediumSelect').value;
      const badge = document.getElementById('activeFilterBadge');

      let periodLabel = 'Весь период';
      if (currentPeriod === 'today') periodLabel = 'Сегодня';
      else if (currentPeriod === 'yesterday') periodLabel = 'Вчера';
      else if (currentPeriod === 'last7') periodLabel = '7 дней';
      else if (currentPeriod === 'last30') periodLabel = '30 дней';
      else if (currentPeriod === 'nov2026') periodLabel = 'Ноябрь 2026';
      else if (currentPeriod === 'oct2026') periodLabel = 'Октябрь 2026';
      else if (currentPeriod === 'custom') periodLabel = 'Точные даты';

      let channelLabel = 'Все каналы';
      if (pSel !== 'all') channelLabel = pSel;
      else if (mSel !== 'all') channelLabel = mSel;

      badge.innerText = periodLabel + ' · ' + channelLabel;
    }}

    function applyAllFilters() {{
      const pageFilter = document.getElementById('filterPageSelect').value;
      const medFilter = document.getElementById('filterMediumSelect').value;
      const textSearch = (document.getElementById('filterSearchInput').value || '').toLowerCase().trim();

      let leads = 0;
      let won = 0;
      let rev = 0;

      const bySource = {{}};
      const byMedium = {{}};
      const byCampaign = {{}};
      const byContent = {{}};
      const byTerm = {{}};
      const byTag = {{}};
      const subpages = {{}};
      const combos = {{}};

      function addDim(dict, key) {{
        let d = dict[key];
        if (!d) d = dict[key] = {{ leads: 0, won: 0, rev: 0 }};
        d.leads++;
        if (l.won) {{ d.won++; d.rev += l.price; }}
      }}

      let l;
      const len = ALL_LEADS.length;
      for (let i = 0; i < len; i++) {{
        l = ALL_LEADS[i];

        // 1. Фильтр дат
        if (filterDateFrom && l.ts < filterDateFrom) continue;
        if (filterDateTo && l.ts > filterDateTo) continue;

        // 2. Фильтр страниц / каналов
        if (pageFilter !== 'all') {{
          if (pageFilter === '/iwa-9828') {{
            const isWa9828 = l.path === '/iwa-9828' || l.med.includes('Айтым') || (l.tags && l.tags.some(t => t.includes('9828') || t.includes('77083779828')));
            if (!isWa9828) continue;
          }} else if (pageFilter === 'wa-0333') {{
            const isWa0333 = (l.tags && l.tags.some(t => t.includes('7475000333') || t.includes('500 03 33') || t.includes('5000333')));
            if (!isWa0333) continue;
          }} else if (pageFilter === '/lidmagnit' && !l.path.startsWith('/lidmagnit') && !l.path.startsWith('/ligmagnit')) continue;
          else if (pageFilter !== '/iwa-9828' && pageFilter !== 'wa-0333' && pageFilter !== '/lidmagnit' && l.path !== pageFilter) continue;
        }}

        // 3. Фильтр utm_medium
        if (medFilter !== 'all') {{
          if (medFilter === 'fan' && l.med !== 'fan') continue;
          else if (medFilter !== 'fan' && l.med !== medFilter) continue;
        }}

        // 4. Текстовый поиск
        if (textSearch) {{
          const tagStr = (l.tags || []).join(' ');
          const hay = (l.src + ' ' + l.med + ' ' + l.cmp + ' ' + l.cnt + ' ' + l.trm + ' ' + l.path + ' ' + l.name + ' ' + tagStr).toLowerCase();
          if (!hay.includes(textSearch)) continue;
        }}

        leads++;
        if (l.won) {{ won++; rev += l.price; }}

        addDim(bySource, l.src);
        addDim(byMedium, l.med);
        addDim(byCampaign, l.cmp);
        addDim(byContent, l.cnt);
        addDim(byTerm, l.trm);
        addDim(subpages, l.path);
        if (l.tags && l.tags.length) {{
          for (let ti = 0; ti < l.tags.length; ti++) {{
            if (l.tags[ti]) addDim(byTag, l.tags[ti]);
          }}
        }}

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
        bySource, byMedium, byCampaign, byContent, byTerm, byTag,
        subpages,
        combos: comboList
      }};
    }}

    // ============================================================
    // ОБНОВЛЕНИЕ KPI КАРТОЧЕК
    // ============================================================
    function updateKpis() {{
      const a = currentAggregates;
      document.getElementById('kpiTotalLeads').innerText = a.leads.toLocaleString('ru-RU');
      document.getElementById('kpiWonLeads').innerText = a.won.toLocaleString('ru-RU');
      document.getElementById('kpiCr').innerText = 'Конверсия (CR): ' + (a.cr * 100).toFixed(1) + '%';
      document.getElementById('kpiRevenue').innerText = a.rev.toLocaleString('ru-RU') + ' ₸';
      document.getElementById('kpiAvgCheck').innerText = 'Средний чек: ' + (a.avgCheck || 0).toLocaleString('ru-RU') + ' ₸';
      document.getElementById('kpiCombosCount').innerText = (a.combos ? a.combos.length : 0).toLocaleString('ru-RU');
    }}

    // ============================================================
    // ТАБЛИЦА СВЯЗОК И СРЕЗОВ
    // ============================================================
    function setGranularityDim(dim) {{
      currentGranularityDim = dim;
      const dims = ['combos', 'sources', 'mediums', 'campaigns', 'contents', 'terms', 'subpages', 'tags'];
      dims.forEach(d => {{
        const btn = document.getElementById('dim-btn-' + d);
        if (btn) {{
          if (d === dim) {{
            btn.className = 'px-3.5 py-1.5 rounded-xl bg-purple-600 text-white font-bold text-xs transition shadow-sm';
          }} else if (d === 'tags') {{
            btn.className = 'px-3.5 py-1.5 rounded-xl bg-amber-100 text-amber-900 hover:bg-amber-200 border-2 border-amber-400 font-black text-xs transition shadow-sm flex items-center space-x-1';
          }} else {{
            btn.className = 'px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold text-xs transition';
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

      }} else if (currentGranularityDim === 'subpages') {{
        thead.innerHTML = `
          <tr>
            <th class="py-3 px-4">Посадочная страница</th>
            <th class="py-3 px-4 text-center">Всего заявок</th>
            <th class="py-3 px-4 text-center">Оплачено (Статус 142)</th>
            <th class="py-3 px-4 text-center">Конверсия (CR %)</th>
            <th class="py-3 px-4 text-right">Выручка (₸)</th>
            <th class="py-3 px-4 text-right">Средний чек (₸)</th>
          </tr>
        `;

        const sub = currentAggregates.subpages || {{}};
        let list = Object.keys(sub).map(k => ({{
          name: k,
          leads: sub[k].leads,
          won: sub[k].won,
          revenue: sub[k].rev,
          cr: sub[k].leads ? Math.round(sub[k].won / sub[k].leads * 1000) / 10 : 0,
          avgCheck: sub[k].won ? Math.round(sub[k].rev / sub[k].won) : 0
        }})).sort((a,b) => b.revenue - a.revenue || b.won - a.won);

        if (search) {{
          list = list.filter(item => item.name.toLowerCase().includes(search));
        }}

        if (countEl) countEl.innerText = 'Показано: ' + list.length + ' страниц';

        if (list.length === 0) {{
          tbody.innerHTML = '<tr><td colspan="6" class="py-8 text-center text-slate-400">Ничего не найдено</td></tr>';
          return;
        }}

        tbody.innerHTML = list.map(item => `
          <tr class="hover:bg-purple-50/30 transition">
            <td class="py-2.5 px-4 font-bold text-brand-700 code-font">${{item.name}}</td>
            <td class="py-2.5 px-4 text-center font-bold text-slate-800">${{item.leads.toLocaleString('ru-RU')}}</td>
            <td class="py-2.5 px-4 text-center font-black text-emerald-600">${{item.won}}</td>
            <td class="py-2.5 px-4 text-center font-bold ${{item.cr >= 5 ? 'text-emerald-700' : 'text-slate-700'}}">${{item.cr}}%</td>
            <td class="py-2.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${{item.revenue.toLocaleString('ru-RU')}} ₸</td>
            <td class="py-2.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${{item.avgCheck.toLocaleString('ru-RU')}} ₸</td>
          </tr>
        `).join('');

      }} else if (currentGranularityDim === 'contents') {{
        thead.innerHTML = `
          <tr>
            <th class="py-3 px-4">utm_content (Креатив / Блогер)</th>
            <th class="py-3 px-4 text-center">Кликов (Переходов)</th>
            <th class="py-3 px-4 text-center">Всего заявок</th>
            <th class="py-3 px-4 text-center">CR1 (Клик ➔ Лид)</th>
            <th class="py-3 px-4 text-center">Оплачено (142)</th>
            <th class="py-3 px-4 text-center">CR2 (Лид ➔ Оплата)</th>
            <th class="py-3 px-4 text-right">Выручка (₸)</th>
            <th class="py-3 px-4 text-right">Средний чек (₸)</th>
          </tr>
        `;

        const srcObj = currentAggregates.byContent || {{}};
        const allKeys = new Set([...Object.keys(srcObj), ...Object.keys(CLICK_COUNTS)]);
        let list = Array.from(allKeys).filter(k => k && k !== 'none').map(k => {{
          const item = srcObj[k] || {{ leads: 0, won: 0, rev: 0 }};
          const clicks = CLICK_COUNTS[k] || 0;
          const cr1 = clicks ? (Math.round(item.leads / clicks * 1000) / 10) + '%' : (item.leads ? '—' : '0%');
          const cr2 = item.leads ? (Math.round(item.won / item.leads * 1000) / 10) + '%' : '0%';
          return {{
            name: k,
            clicks: clicks,
            leads: item.leads,
            cr1: cr1,
            won: item.won,
            cr2: cr2,
            revenue: item.rev,
            avgCheck: item.won ? Math.round(item.rev / item.won) : 0
          }};
        }}).sort((a,b) => b.revenue - a.revenue || b.won - a.won || b.leads - a.leads || b.clicks - a.clicks);

        if (search) {{
          list = list.filter(item => item.name.toLowerCase().includes(search));
        }}

        if (countEl) countEl.innerText = 'Показано: ' + list.length + ' блогеров / креативов';

        if (list.length === 0) {{
          tbody.innerHTML = '<tr><td colspan="8" class="py-8 text-center text-slate-400">Ничего не найдено</td></tr>';
          return;
        }}

        tbody.innerHTML = list.map(item => `
          <tr class="hover:bg-purple-50/30 transition">
            <td class="py-2.5 px-4 font-bold text-brand-700 code-font">${{item.name}}</td>
            <td class="py-2.5 px-4 text-center font-bold text-purple-700">${{item.clicks ? item.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}}</td>
            <td class="py-2.5 px-4 text-center font-bold text-slate-800">${{item.leads.toLocaleString('ru-RU')}}</td>
            <td class="py-2.5 px-4 text-center font-semibold text-slate-600">${{item.cr1}}</td>
            <td class="py-2.5 px-4 text-center font-black text-emerald-600">${{item.won}}</td>
            <td class="py-2.5 px-4 text-center font-bold ${{item.leads && (item.won/item.leads >= 0.05) ? 'text-emerald-700' : 'text-slate-700'}}">${{item.cr2}}</td>
            <td class="py-2.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${{item.revenue.toLocaleString('ru-RU')}} ₸</td>
            <td class="py-2.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${{item.avgCheck.toLocaleString('ru-RU')}} ₸</td>
          </tr>
        `).join('');

      }} else {{
        const paramMap = {{
          'campaigns': currentAggregates.byCampaign,
          'contents': currentAggregates.byContent,
          'mediums': currentAggregates.byMedium,
          'terms': currentAggregates.byTerm,
          'sources': currentAggregates.bySource,
          'tags': currentAggregates.byTag
        }};
        const pNames = {{
          'campaigns': 'utm_campaign (Кампания)',
          'contents': 'utm_content (Креатив)',
          'mediums': 'utm_medium (Канал / Менеджер)',
          'terms': 'utm_term (Аудитория)',
          'sources': 'utm_source (Площадка / Блогер)',
          'tags': '🏷️ Тег AmoCRM'
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
        }})).sort((a,b) => b.revenue - a.revenue || b.won - a.won);

        if (search) {{
          list = list.filter(item => item.name.toLowerCase().includes(search));
        }}

        if (countEl) countEl.innerText = 'Показано: ' + list.length + ' значений';

        if (list.length === 0) {{
          tbody.innerHTML = '<tr><td colspan="6" class="py-8 text-center text-slate-400">Ничего не найдено</td></tr>';
          return;
        }}

        tbody.innerHTML = list.map(item => `
          <tr class="hover:bg-purple-50/30 transition">
            <td class="py-2.5 px-4 font-bold text-slate-900 code-font">${{item.name}}</td>
            <td class="py-2.5 px-4 text-center font-bold text-slate-800">${{item.leads.toLocaleString('ru-RU')}}</td>
            <td class="py-2.5 px-4 text-center font-black text-emerald-600">${{item.won}}</td>
            <td class="py-2.5 px-4 text-center font-bold ${{item.cr >= 5 ? 'text-emerald-700' : 'text-slate-700'}}">${{item.cr}}%</td>
            <td class="py-2.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${{item.revenue.toLocaleString('ru-RU')}} ₸</td>
            <td class="py-2.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${{item.avgCheck.toLocaleString('ru-RU')}} ₸</td>
          </tr>
        `).join('');
      }}
    }}

    // ============================================================
    // ЭКСПОРТ В CSV
    // ============================================================
    function exportGranularityCsv() {{
      let csv = '';
      let filename = 'utm_analytics_' + currentGranularityDim + '.csv';

      if (currentGranularityDim === 'combos') {{
        const combos = currentAggregates.combos || [];
        if (!combos.length) return alert('Нет данных для экспорта');
        csv = 'Посадочная страница,utm_source,utm_medium,utm_campaign,utm_content,utm_term,Лидов,Оплачено (142),CR %,Выручка (KZT),Средний чек\\n';
        combos.forEach(c => {{
          const row = [
            c.landing || c.path,
            c.src,
            c.med,
            c.cmp,
            c.cnt,
            c.trm,
            c.leads,
            c.won,
            c.cr + '%',
            c.revenue,
            c.avgCheck
          ].map(v => '"' + String(v).replace(/"/g, '""') + '"').join(',');
          csv += row + '\\n';
        }});
      }} else {{
        const paramMap = {{
          'campaigns': currentAggregates.byCampaign,
          'contents': currentAggregates.byContent,
          'mediums': currentAggregates.byMedium,
          'terms': currentAggregates.byTerm,
          'sources': currentAggregates.bySource,
          'tags': currentAggregates.byTag,
          'subpages': currentAggregates.subpages
        }};
        const pNames = {{
          'campaigns': 'utm_campaign',
          'contents': 'utm_content',
          'mediums': 'utm_medium',
          'terms': 'utm_term',
          'sources': 'utm_source',
          'tags': 'Тег AmoCRM',
          'subpages': 'Посадочная страница'
        }};
        const obj = paramMap[currentGranularityDim] || {{}};
        const keys = Object.keys(obj);
        if (!keys.length) return alert('Нет данных для экспорта');

        csv = (pNames[currentGranularityDim] || 'Параметр') + ',Лидов,Оплачено (142),CR %,Выручка (KZT),Средний чек\\n';
        keys.sort((a,b) => (obj[b].rev || obj[b].revenue || 0) - (obj[a].rev || obj[a].revenue || 0)).forEach(k => {{
          const item = obj[k];
          const l = item.leads || 0;
          const w = item.won || 0;
          const r = item.rev || item.revenue || 0;
          const cr = l ? (Math.round(w / l * 1000) / 10) + '%' : '0%';
          const avg = w ? Math.round(r / w) : 0;
          const row = [k, l, w, cr, r, avg].map(v => '"' + String(v).replace(/"/g, '""') + '"').join(',');
          csv += row + '\\n';
        }});
      }}

      const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    // ============================================================
    // SUPABASE REALTIME & ЖИВАЯ ПОДГРУЗКА
    // ============================================================
    const SUPABASE_URL = 'https://upeqrwqhdnmccyymugej.supabase.co';
    const SUPABASE_ANON_KEY = 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';
    let supabaseClient = null;

    try {{
      if (window.supabase) {{
        supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
      }}
    }} catch (e) {{
      console.warn('Supabase init error:', e);
    }}

    async function loadFreshDealsFromSupabase() {{
      if (!supabaseClient) return;
      try {{
        const {{ data, error }} = await supabaseClient
          .from('deals')
          .select('id, name, created_at, is_won, price, landing_page, utm_source, utm_medium, utm_campaign, utm_content, utm_term, tags')
          .order('created_at', {{ ascending: false }})
          .limit(1000);

        if (error || !data || !data.length) return;

        let addedCount = 0;
        const existingIds = new Set(ALL_LEADS.map(l => l.id));

        for (const d of data) {{
          if (!existingIds.has(d.id)) {{
            const ts = d.created_at ? Math.floor(new Date(d.created_at).getTime() / 1000) : 0;
            const dom = (d.landing_page && d.landing_page.includes('health')) ? 'janamenhealth.kz' : 'janamen1.kz';
            ALL_LEADS.unshift({{
              id: d.id,
              ts: ts,
              won: d.is_won ? 1 : 0,
              price: d.price || 0,
              dom: dom,
              path: d.landing_page || '/',
              page: d.landing_page || '/',
              src: d.utm_source || 'direct/none',
              med: d.utm_medium || 'none',
              cmp: d.utm_campaign || 'none',
              cnt: d.utm_content || 'none',
              trm: d.utm_term || 'none',
              stId: d.is_won ? 142 : 0,
              name: d.name || 'Сделка',
              tags: Array.isArray(d.tags) ? d.tags : []
            }});
            existingIds.add(d.id);
            addedCount++;
          }}
        }}

        if (addedCount > 0) {{
          console.log(`[Supabase] Подгружено ${{addedCount}} новых сделок в дашборд!`);
          onFilterChange();
          const live = document.getElementById('liveStatus');
          if (live) {{
            live.innerHTML = `🟢 Supabase Realtime (+${{addedCount}} новых)`;
          }}
        }}
      }} catch (err) {{
        console.warn('Load fresh deals err:', err);
      }}
    }}

    function initRealtime() {{
      if (!supabaseClient) return;
      supabaseClient
        .channel('public_deals')
        .on('postgres_changes', {{ event: '*', schema: 'public', table: 'deals' }}, payload => {{
          const d = payload.new;
          if (!d || !d.id) return;

          const existingIndex = ALL_LEADS.findIndex(l => l.id === d.id);
          const ts = d.created_at ? Math.floor(new Date(d.created_at).getTime() / 1000) : 0;
          const dom = (d.landing_page && d.landing_page.includes('health')) ? 'janamenhealth.kz' : 'janamen1.kz';

          const leadObj = {{
            id: d.id,
            ts: ts,
            won: d.is_won ? 1 : 0,
            price: d.price || 0,
            dom: dom,
            path: d.landing_page || '/',
            page: d.landing_page || '/',
            src: d.utm_source || 'direct/none',
            med: d.utm_medium || 'none',
            cmp: d.utm_campaign || 'none',
            cnt: d.utm_content || 'none',
            trm: d.utm_term || 'none',
            stId: d.is_won ? 142 : 0,
            name: d.name || 'Сделка',
            tags: Array.isArray(d.tags) ? d.tags : []
          }};

          if (existingIndex >= 0) {{
            ALL_LEADS[existingIndex] = leadObj;
          }} else {{
            ALL_LEADS.unshift(leadObj);
          }}

          onFilterChange();

          const live = document.getElementById('liveStatus');
          if (live) {{
            live.className = "hidden sm:inline-flex px-2.5 py-1 text-[11px] font-bold rounded-lg border bg-amber-50 text-amber-800 border-amber-300 animate-pulse";
            live.innerHTML = `⚡ Только что поступил лид: ${{d.utm_source || 'direct'}}!`;
            setTimeout(() => {{
              live.className = "hidden sm:inline-flex px-2.5 py-1 text-[11px] font-bold rounded-lg border bg-emerald-50 text-emerald-700 border-emerald-200";
              live.innerHTML = `🟢 Supabase Realtime (Живые данные)`;
            }}, 6000);
          }}
        }})
        .subscribe();
    }}

    // ============================================================
    // КЛИК-ТРЕКЕР И ГЕНЕРАТОР ССЫЛОК ДЛЯ БЛОГЕРОВ
    // ============================================================
    let CLICK_COUNTS = {{}};

    async function loadClickCounts() {{
      try {{
        const r = await fetch('/api/clicks-summary');
        const res = await r.json();
        if (res && res.byContent) {{
          CLICK_COUNTS = res.byContent;
          if (currentGranularityDim === 'contents') {{
            renderGranularityTable();
          }}
        }}
      }} catch (e) {{
        console.warn('Load clicks summary err:', e);
      }}
    }}

    function openLinkGeneratorModal() {{
      const m = document.getElementById('linkGenModal');
      if (m) {{
        m.classList.remove('hidden');
        updateGeneratedLink();
      }}
    }}

    function closeLinkGeneratorModal() {{
      const m = document.getElementById('linkGenModal');
      if (m) m.classList.add('hidden');
    }}

    function updateGeneratedLink() {{
      const bInput = document.getElementById('genBloggerName');
      const mSelect = document.getElementById('genManager');
      const pSelect = document.getElementById('genPage');
      const resInput = document.getElementById('genResultUrl');
      if (!bInput || !resInput) return;

      const blogger = (bInput.value || '').trim().replace(/\\s+/g, '_');
      const manager = mSelect ? mSelect.value : 'mpb2';
      const page = pSelect ? pSelect.value : '/organika';
      const origin = window.location.origin;

      if (!blogger) {{
        resInput.value = origin + '/api/go?b=blogger_name&m=' + manager + '&p=' + page;
      }} else {{
        resInput.value = origin + '/api/go?b=' + encodeURIComponent(blogger) + '&m=' + manager + '&p=' + page;
      }}
    }}

    function copyGeneratedLink() {{
      const resInput = document.getElementById('genResultUrl');
      if (!resInput) return;
      resInput.select();
      navigator.clipboard.writeText(resInput.value);
      const msg = document.getElementById('copySuccessMsg');
      if (msg) {{
        msg.classList.remove('hidden');
        setTimeout(() => msg.classList.add('hidden'), 3500);
      }}
    }}

    // ============================================================
    // СИНХРОНИЗАЦИЯ AMOCRM -> SUPABASE -> ДАШБОРД
    // ============================================================
    async function syncAmoCRM() {{
      const btn = document.getElementById('btnSyncCRM');
      const idle = btn.innerHTML;
      btn.innerHTML = '<span>⏳ Синхронизация AmoCRM...</span>';
      btn.disabled = true;

      try {{
        // Прямой опрос AmoCRM API через Vercel функцию (стягивает последние 200 сделок)
        const r = await fetch('/api/sync?limit=200');
        const res = await r.json();
        await loadFreshDealsFromSupabase();
        btn.innerHTML = `<span>✓ Синхронизировано (${{res.synced || 0}})</span>`;
      }} catch (err) {{
        await loadFreshDealsFromSupabase();
        btn.innerHTML = '<span>✓ Данные обновлены</span>';
      }} finally {{
        setTimeout(() => {{ btn.disabled = false; btn.innerHTML = idle; }}, 3000);
      }}
    }}

    // Автоматическая фоновая подтяжка при открытии страницы
    setTimeout(() => {{
      fetch('/api/sync?limit=50').then(() => loadFreshDealsFromSupabase()).catch(() => {{}});
    }}, 1500);

    // Инициализация
    onFilterChange();
    loadFreshDealsFromSupabase();
    loadClickCounts();
    initRealtime();
  </script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

with open('gas/Dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Generated simplified unified portal HTML with collapsible filters and clean single-view table!")
