import json

with open('gas/marketing_analytics_summary.json', 'r', encoding='utf-8') as f:
    analytics_json = f.read()

with open('gas/utm_granularity_data.json', 'r', encoding='utf-8') as f:
    granularity_json = f.read()

with open('gas/compact_leads_dict.json', 'r', encoding='utf-8') as f:
    leads_dict_json = f.read()

html_template = r'''<!DOCTYPE html>
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
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#eff6ff',
              100: '#dbeafe',
              500: '#3b82f6',
              600: '#2563eb',
              700: '#1d4ed8',
              800: '#1e40af',
              900: '#1e3a8a',
            }
          }
        }
      }
    }
  </script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .code-font { font-family: 'JetBrains Mono', monospace; }
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
            <p class="text-[11px] text-slate-500 font-medium">Органика · Influence (МПБ) · Fan-аккаунты · Clicks & AmoCRM</p>
          </div>
        </div>

        <!-- КНОПКИ ДЕЙСТВИЙ -->
        <div class="flex items-center space-x-2 sm:space-x-2.5">
          <span id="liveStatus" class="hidden sm:inline-flex px-2.5 py-1 text-[11px] font-bold rounded-lg border bg-emerald-50 text-emerald-700 border-emerald-200">🟢 Supabase Realtime (Живые данные)</span>
          <button onclick="openLinkGeneratorModal()" class="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-bold text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg transition border border-purple-200 shadow-sm">
            <span>🔗 Ссылка для блогера</span>
          </button>
          <button onclick="syncAmoCRM()" id="btnSyncCRM" class="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition border border-slate-200">
            <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <span class="hidden sm:inline">Синхронизировать</span> AmoCRM
          </button>
          <a href="https://docs.google.com/spreadsheets/d/1jBeeF8b_7CORi8Xf9Kjr9YN6c6ZrloQIljT2_-adcYs/edit" target="_blank" class="hidden md:inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-lg transition shadow-sm">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
            <span>Google Таблица</span>
          </a>
        </div>

      </div>
    </div>
  </header>

  <!-- ОСНОВНОЙ КОНТЕНТ (FULL WIDTH НА ВЕСЬ ЭКРАН) -->
  <main class="flex-1 w-full px-3 sm:px-6 py-4 space-y-4">

    <!-- 0. ГЛАВНЫЕ КАНАЛЫ (ПЕРВИЧНЫЕ РАЗДЕЛЫ ВЕРХНЕГО УРОВНЯ) -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-2 sm:p-2.5">
      <div class="flex items-center gap-1.5 sm:gap-2 overflow-x-auto text-xs font-bold scrollbar-none">
        
        <!-- РАЗДЕЛ 1: ОРГАНИКА -->
        <button onclick="switchMainChannel('organika')" id="main-tab-organika" class="px-4 py-2.5 rounded-xl bg-emerald-600 text-white font-black text-xs sm:text-sm flex items-center space-x-2 transition shadow-sm whitespace-nowrap">
          <span>🌿 1. Органика (/smm + WA Айтыма)</span>
          <span id="tabBadgeOrganika" class="px-2 py-0.5 text-[10px] bg-white/20 text-white rounded-full font-black">18.4k</span>
        </button>

        <!-- РАЗДЕЛ 2: INFLUENCE (МПБ) -->
        <button onclick="switchMainChannel('influence')" id="main-tab-influence" class="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-purple-100 text-slate-700 hover:text-purple-900 font-black text-xs sm:text-sm flex items-center space-x-2 transition whitespace-nowrap">
          <span>🌟 2. Influence (Менеджеры МПБ)</span>
          <span id="tabBadgeInfluence" class="px-2 py-0.5 text-[10px] bg-purple-200 text-purple-900 rounded-full font-black">4 мен.</span>
        </button>

        <!-- РАЗДЕЛ 3: FAN (ФАН-АККАУНТЫ) -->
        <button onclick="switchMainChannel('fan')" id="main-tab-fan" class="px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-indigo-100 text-slate-700 hover:text-indigo-900 font-black text-xs sm:text-sm flex items-center space-x-2 transition whitespace-nowrap">
          <span>🎬 3. Fan (Фан-аккаунты сетки)</span>
          <span id="tabBadgeFan" class="px-2 py-0.5 text-[10px] bg-indigo-200 text-indigo-900 rounded-full font-black">8 акк.</span>
        </button>

        <!-- ВСЕ КАНАЛЫ (СВОДКА) -->
        <button onclick="switchMainChannel('all')" id="main-tab-all" class="px-3.5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs sm:text-sm flex items-center space-x-1.5 transition whitespace-nowrap ml-auto">
          <span>📊 Все каналы (Сводка)</span>
        </button>

        <!-- ТЕГИ AMOCRM -->
        <button onclick="switchMainChannel('tags')" id="main-tab-tags" class="px-3.5 py-2.5 rounded-xl bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 font-bold text-xs sm:text-sm flex items-center space-x-1.5 transition whitespace-nowrap">
          <span>🏷️ ТЕГИ AmoCRM</span>
        </button>

      </div>
    </div>

    <!-- 1. ПОЛОСА КЛЮЧЕВЫХ KPI КАРТОЧЕК (ПЕРЕСЧИТЫВАЕТСЯ ПОД ВЫБРАННЫЙ РАЗДЕЛ НА ЛЕТУ) -->
    <div class="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
      
      <!-- Лиды -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Всего заявок (лидов)</span>
          <span id="kpiScopeBadge" class="text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">Органика</span>
        </div>
        <div id="kpiTotalLeads" class="text-xl sm:text-3xl font-black text-slate-900 mt-1">—</div>
        <div class="text-[11px] text-slate-500 mt-0.5" id="kpiLeadsPeriod">за выбранный период</div>
      </div>

      <!-- Клики -->
      <div class="bg-white p-4 rounded-2xl border border-purple-200 shadow-sm bg-gradient-to-br from-white to-purple-50/30">
        <div class="text-[11px] font-bold text-purple-700 uppercase tracking-wider">Кликов (Переходов)</div>
        <div id="kpiClicks" class="text-xl sm:text-3xl font-black text-purple-700 mt-1">0</div>
        <div id="kpiCr1" class="text-[11px] font-bold text-purple-800 mt-0.5">CR1 (Клик ➔ Лид): —</div>
      </div>

      <!-- Оплачено -->
      <div class="bg-white p-4 rounded-2xl border border-emerald-200 shadow-sm bg-gradient-to-br from-white to-emerald-50/40">
        <div class="text-[11px] font-bold text-emerald-700 uppercase tracking-wider">Оплачено (Статус 142)</div>
        <div id="kpiWonLeads" class="text-xl sm:text-3xl font-black text-emerald-600 mt-1">—</div>
        <div id="kpiCr2" class="text-[11px] font-bold text-emerald-700 mt-0.5">CR2 (Лид ➔ Оплата): —</div>
      </div>

      <!-- Выручка -->
      <div class="bg-white p-4 rounded-2xl border border-blue-200 shadow-sm bg-gradient-to-br from-white to-blue-50/40">
        <div class="text-[11px] font-bold text-brand-700 uppercase tracking-wider">Подтвержденная Выручка</div>
        <div id="kpiRevenue" class="text-xl sm:text-3xl font-black text-brand-700 mt-1">—</div>
        <div id="kpiAvgCheck" class="text-[11px] font-semibold text-slate-600 mt-0.5">Средний чек: —</div>
      </div>

      <!-- Активных сущностей -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm col-span-2 lg:col-span-1">
        <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wider" id="kpiEntityLabel">Активных блогеров/связок</div>
        <div id="kpiEntitiesCount" class="text-xl sm:text-3xl font-black text-slate-800 mt-1">—</div>
        <div class="text-[11px] text-slate-400 mt-0.5">в текущей выборке</div>
      </div>

    </div>

    <!-- 2. СВОРАЧИВАЕМЫЙ БЛОК ФИЛЬТРАЦИИ ПО ПЕРИОДУ И ПОИСКА -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      
      <!-- ШАПКА ФИЛЬТРОВ: АКТИВНЫЙ БЕЙДЖ + КНОПКА СВЕРНУТЬ/РАЗВЕРНУТЬ -->
      <div class="px-4 py-2.5 bg-slate-50/70 border-b border-slate-200/80 flex items-center justify-between gap-3">
        <div class="flex items-center space-x-2 overflow-hidden text-xs">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="font-black text-slate-800 uppercase tracking-wider whitespace-nowrap">Период:</span>
          <span id="activeFilterBadge" class="font-bold px-2.5 py-0.5 rounded-lg bg-blue-100 text-brand-800 border border-blue-200 truncate">
            Весь период · Органика
          </span>
        </div>

        <div class="flex items-center space-x-2">
          <button onclick="resetAllFilters()" class="text-xs font-semibold text-slate-500 hover:text-slate-800 px-2 py-1 rounded-lg hover:bg-slate-200/60 transition flex items-center space-x-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            <span>Сбросить</span>
          </button>
          <button onclick="toggleFilters()" id="btnToggleFilters" class="px-3 py-1 text-xs font-bold rounded-xl bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 transition flex items-center space-x-1.5 shadow-sm">
            <span id="toggleFilterText">Свернуть фильтры</span>
            <svg id="toggleFilterIcon" class="w-3.5 h-3.5 text-slate-500 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </button>
        </div>
      </div>

      <!-- ТЕЛО ФИЛЬТРОВ -->
      <div id="filtersBody" class="p-4 sm:p-5 space-y-3.5 transition-all">
        
        <!-- СТРОКА 1: БЫСТРЫЕ ПЕРИОДЫ -->
        <div class="flex flex-wrap items-center gap-1.5">
          <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1">Быстрый период:</span>
          <button onclick="setPeriodPreset('all')" id="period-btn-all" class="px-2.5 py-1 text-xs font-bold rounded-lg bg-slate-900 text-white transition shadow-sm">Весь период</button>
          <button onclick="setPeriodPreset('today')" id="period-btn-today" class="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Сегодня (11 ноя)</button>
          <button onclick="setPeriodPreset('yesterday')" id="period-btn-yesterday" class="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition">Вчера (10 ноя)</button>
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

        <!-- СТРОКА 2: ПОИСК ПО ТАБЛИЦЕ -->
        <div class="pt-2 border-t border-slate-100 flex items-center justify-between gap-3">
          <div class="relative flex-1 max-w-lg">
            <input type="text" id="filterSearchInput" oninput="onFilterChange()" placeholder="Поиск по блогеру, креативу, кампании, ссылке или тегу..." class="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-medium text-slate-800 transition">
            <svg class="w-4 h-4 text-slate-400 absolute left-3 top-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </div>
          <div id="channelActionButtons" class="flex items-center space-x-2">
            <!-- Кнопки разворачивания для Influence и Fan -->
            <button onclick="expandAllAccordion()" id="btnExpandAll" class="px-3 py-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition border border-slate-200">
              [+] Развернуть всех
            </button>
            <button onclick="collapseAllAccordion()" id="btnCollapseAll" class="px-3 py-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition border border-slate-200">
              [-] Свернуть всех
            </button>
          </div>
        </div>

      </div>

    </div>

    <!-- 3. ГЛАВНАЯ ИНТЕРАКТИВНАЯ ТАБЛИЦА -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden space-y-0">
      
      <!-- ШАПКА ТАБЛИЦЫ: ЗАГОЛОВОК + ПОДЗАГОЛОВОК + ЭКСПОРТ -->
      <div class="p-4 sm:p-5 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div class="flex items-center space-x-2">
            <h2 id="tableMainTitle" class="text-base sm:text-lg font-black text-slate-900 tracking-tight">🌿 Органика: SMM и WhatsApp Айтыма Бериковича</h2>
            <span id="tableBadgeTitle" class="px-2 py-0.5 text-[10px] font-black uppercase rounded bg-emerald-100 text-emerald-800">Канал 1</span>
          </div>
          <p id="tableMainSubtitle" class="text-xs text-slate-500 mt-0.5">Прямая прозрачная таблица без вложенности: все клики, заявки и подтвержденные оплаты</p>
        </div>

        <div class="flex items-center space-x-2">
          <span id="rowCountBadge" class="text-xs font-bold text-slate-500 whitespace-nowrap">Показано: 0 строк</span>
          <button onclick="exportCurrentTableCsv()" class="px-3 py-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition border border-slate-200 flex items-center space-x-1.5">
            <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            <span>Экспорт в CSV</span>
          </button>
        </div>
      </div>

      <!-- ПОД-ВКЛАДКИ ДЛЯ РЕЖИМА "ВСЕ КАНАЛЫ" (ПОКАЗЫВАЮТСЯ ТОЛЬКО ПРИ ALL) -->
      <div id="allChannelsSubTabs" class="hidden px-4 py-2.5 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center gap-1.5 overflow-x-auto text-xs">
        <button onclick="setAllChannelDim('combos')" id="dim-btn-combos" class="px-3 py-1.5 rounded-xl bg-purple-600 text-white font-bold transition shadow-sm">Полные связки (Combo)</button>
        <button onclick="setAllChannelDim('sources')" id="dim-btn-sources" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold transition">utm_source</button>
        <button onclick="setAllChannelDim('mediums')" id="dim-btn-mediums" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold transition">utm_medium</button>
        <button onclick="setAllChannelDim('campaigns')" id="dim-btn-campaigns" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold transition">utm_campaign</button>
        <button onclick="setAllChannelDim('contents')" id="dim-btn-contents" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold transition">utm_content</button>
        <button onclick="setAllChannelDim('subpages')" id="dim-btn-subpages" class="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold transition">Посадочные страницы</button>
      </div>

      <!-- ТАБЛИЦА НА ВСЮ ШИРИНУ -->
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead id="mainTableHead" class="bg-slate-50 border-b border-slate-200 text-slate-700 uppercase font-bold text-[11px] tracking-wider">
            <!-- Заполняется динамически -->
          </thead>
          <tbody id="mainTableBody" class="divide-y divide-slate-100">
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
            <label class="block text-[11px] uppercase tracking-wider text-slate-400 font-bold mb-1">Ник блогера (utm_content):</label>
            <input type="text" id="genBloggerName" oninput="updateGeneratedLink()" placeholder="например: bika_mazhenova, frolova_kristina, aliyakairatkyzy" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 font-bold text-slate-900">
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-[11px] uppercase tracking-wider text-slate-400 font-bold mb-1">Менеджер / Кампания:</label>
              <select id="genManager" onchange="updateGeneratedLink()" class="w-full px-2.5 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 font-bold text-slate-900">
                <optgroup label="🌟 Менеджеры Influence (МПБ)">
                  <option value="mpb2">Алина (mpb2)</option>
                  <option value="mpb1">Анельжан (mpb1)</option>
                  <option value="mpb3">Алуа (mpb3)</option>
                  <option value="mpb4">Дарина (mpb4)</option>
                </optgroup>
                <optgroup label="🎬 8 Фан-аккаунтов">
                  <option value="bekezhanova_dilnaz">Бекежанова Дильназ (fan)</option>
                  <option value="doskazhanova_ainagul">Доскажанова Айнагуль (fan)</option>
                  <option value="kenzhebaeva_aisulu_1">Кенжебаева Айсулу 1 (fan)</option>
                  <option value="kenzhebaeva_aisulu_2">Кенжебаева Айсулу 2 (fan)</option>
                  <option value="gaisina_kamila">Гайсина Камила (fan)</option>
                  <option value="kenzhebaeva_aida">Кенжебаева Аида (fan)</option>
                  <option value="adina_khaidarova_1">Адина Хайдарова 1 (fan)</option>
                  <option value="adina_khaidarova_2">Адина Хайдарова 2 (fan)</option>
                </optgroup>
                <optgroup label="Органика">
                  <option value="organic">Органика / SMM</option>
                </optgroup>
              </select>
            </div>

            <div>
              <label class="block text-[11px] uppercase tracking-wider text-slate-400 font-bold mb-1">Посадочная страница:</label>
              <select id="genPage" onchange="updateGeneratedLink()" class="w-full px-2.5 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 font-bold text-slate-900">
                <option value="/influence">/influence (Инфлюенс)</option>
                <option value="/smm">/smm (Соцсети)</option>
                <option value="/organika">/organika (Форма заявки)</option>
                <option value="/lidmagnit">/lidmagnit (Лид-магнит)</option>
                <option value="/">/ (Главная)</option>
              </select>
            </div>
          </div>

          <div class="pt-2">
            <label class="block text-[11px] uppercase tracking-wider text-purple-700 font-bold mb-1">Готовая ссылка для блогера (с авто-кликом):</label>
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
    // Встроенный компактный датасет для мгновенной фильтрации за любые периоды
    const COMPACT_PAYLOAD = __LEADS_DICT_JSON__;
    const S = COMPACT_PAYLOAD.strings;
    const ALL_LEADS = COMPACT_PAYLOAD.rows.map(r => ({
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
    }));

    // Менеджеры Influence
    const INFLUENCE_MANAGERS = {
      'mpb1': { code: 'mpb1', name: 'Анельжан', role: 'Менеджер по блогерам' },
      'mpb2': { code: 'mpb2', name: 'Алина', role: 'Менеджер по блогерам' },
      'mpb3': { code: 'mpb3', name: 'Алуа', role: 'Менеджер по блогерам' },
      'mpb4': { code: 'mpb4', name: 'Дарина', role: 'Менеджер по блогерам' }
    };

    // 8 Официальных фан-аккаунтов из реестра
    const FAN_REGISTRY = [
      {
        id: 'bekezhanova_dilnaz',
        name: 'Бекежанова Дильназ',
        platforms: [
          { name: 'TikTok', icon: '🎵', url: 'https://janamen1.kz/fun?utm_source=tiktok&utm_medium=video&utm_campaign=bekezhanova_dilnaz', profile: 'https://www.tiktok.com/@janamen_fans?_r=1&_t=ZS-97265Roj4pl' },
          { name: 'Instagram', icon: '📸', url: 'https://janamen1.kz/fun?utm_source=instagram&utm_medium=video&utm_campaign=bekezhanova_dilnaz', profile: 'https://www.instagram.com/janamen_fans?igsh=MTBrdWd4cHZ2NnBvdw==' },
          { name: 'YouTube', icon: '▶️', url: 'https://janamen1.kz/fun?utm_source=youtube&utm_medium=video&utm_campaign=bekezhanova_dilnaz', profile: 'https://youtube.com/@janamen_fanss?si=gcBCvNEGz3eiZzuY' }
        ]
      },
      {
        id: 'doskazhanova_ainagul',
        name: 'Доскажанова Айнагуль',
        platforms: [
          { name: 'Instagram', icon: '📸', url: 'https://janamen1.kz/fun?utm_source=instagram&utm_medium=video&utm_campaign=doskazhanova_ainagul', profile: 'https://www.instagram.com/janamenfun?igsh=anFyaHZyM21yNDg1' },
          { name: 'YouTube', icon: '▶️', url: 'https://janamen1.kz/fun?utm_source=youtube&utm_medium=video&utm_campaign=doskazhanova_ainagul', profile: 'https://youtube.com/@janamenfun?si=mivEknbjZKm7etIU' }
        ]
      },
      {
        id: 'kenzhebaeva_aisulu_1',
        name: 'Кенжебаева Айсулу (1)',
        platforms: [
          { name: 'TikTok', icon: '🎵', url: 'https://janamen1.kz/fun?utm_source=tiktok&utm_medium=video&utm_campaign=kenzhebaeva_aisulu_1', profile: 'https://www.tiktok.com/@janamennfans' },
          { name: 'Instagram', icon: '📸', url: 'https://janamen1.kz/fun?utm_source=instagram&utm_medium=video&utm_campaign=kenzhebaeva_aisulu_1', profile: 'https://www.instagram.com/janamen.aitymfan?igsh=MXB2amxyMzZ0ODVyMw==' },
          { name: 'YouTube', icon: '▶️', url: 'https://janamen1.kz/fun?utm_source=youtube&utm_medium=video&utm_campaign=kenzhebaeva_aisulu_1', profile: 'https://youtube.com/@janamenaitymfan?si=XBChM5eOBOngD0Vy' }
        ]
      },
      {
        id: 'kenzhebaeva_aisulu_2',
        name: 'Кенжебаева Айсулу (2)',
        platforms: [
          { name: 'TikTok', icon: '🎵', url: 'https://janamen1.kz/fun?utm_source=tiktok&utm_medium=video&utm_campaign=kenzhebaeva_aisulu_2', profile: 'https://www.tiktok.com/@janamen.edit' },
          { name: 'Instagram', icon: '📸', url: 'https://janamen1.kz/fun?utm_source=instagram&utm_medium=video&utm_campaign=kenzhebaeva_aisulu_2', profile: 'https://www.instagram.com/janamen.edit?igsh=MWp6dnFmcW42enQzMQ==' },
          { name: 'YouTube', icon: '▶️', url: 'https://janamen1.kz/fun?utm_source=youtube&utm_medium=video&utm_campaign=kenzhebaeva_aisulu_2', profile: 'https://youtube.com/@janamenedit?si=MQAZq4ijlN6Sml1' }
        ]
      },
      {
        id: 'gaisina_kamila',
        name: 'Гайсина Камила',
        platforms: [
          { name: 'TikTok', icon: '🎵', url: 'https://janamen1.kz/fun?utm_source=tiktok&utm_medium=video&utm_campaign=gaisina_kamila', profile: 'https://www.tiktok.com/@aitym.fanclub' },
          { name: 'Instagram', icon: '📸', url: 'https://janamen1.kz/fun?utm_source=instagram&utm_medium=video&utm_campaign=gaisina_kamila', profile: 'https://www.instagram.com/aitym.fanclub?igsh=MTN0aXI4eG03ejF5dw==' },
          { name: 'YouTube', icon: '▶️', url: 'https://janamen1.kz/fun?utm_source=youtube&utm_medium=video&utm_campaign=gaisina_kamila', profile: 'https://youtube.com/@aitymfanclub?si=1Rcj4IJ_6SRLKvxK' }
        ]
      },
      {
        id: 'kenzhebaeva_aida',
        name: 'Кенжебаева Аида',
        platforms: [
          { name: 'TikTok', icon: '🎵', url: 'https://janamen1.kz/fun?utm_source=tiktok&utm_medium=video&utm_campaign=kenzhebaeva_aida', profile: 'https://www.tiktok.com/@janamennn.fan' },
          { name: 'Instagram', icon: '📸', url: 'https://janamen1.kz/fun?utm_source=instagram&utm_medium=video&utm_campaign=kenzhebaeva_aida', profile: 'https://www.instagram.com/janamennnfan?igsh=eG5tMTJvcnRtamg1' },
          { name: 'YouTube', icon: '▶️', url: 'https://janamen1.kz/fun?utm_source=youtube&utm_medium=video&utm_campaign=kenzhebaeva_aida', profile: 'https://youtube.com/@janamennnfan?si=sNhTX4xyMPbNtQVQ' }
        ]
      },
      {
        id: 'adina_khaidarova_1',
        name: 'Адина Хайдарова (1)',
        platforms: [
          { name: 'TikTok', icon: '🎵', url: 'https://janamen1.kz/fun?utm_source=tiktok&utm_medium=video&utm_campaign=adina_khaidarova_1', profile: 'https://www.tiktok.com/@jana.men68' },
          { name: 'Instagram', icon: '📸', url: 'https://janamen1.kz/fun?utm_source=instagram&utm_medium=video&utm_campaign=adina_khaidarova_1', profile: 'https://www.instagram.com/aitymzhakupovfanacc?igsh=OWdjZXNpaGE3eGJn' },
          { name: 'YouTube', icon: '▶️', url: 'https://janamen1.kz/fun?utm_source=youtube&utm_medium=video&utm_campaign=adina_khaidarova_1', profile: 'https://youtube.com/@janamen-q4x?si=i2KdBr5w2SndINSW' }
        ]
      },
      {
        id: 'adina_khaidarova_2',
        name: 'Адина Хайдарова (2)',
        platforms: [
          { name: 'TikTok', icon: '🎵', url: 'https://janamen1.kz/fun?utm_source=tiktok&utm_medium=video&utm_campaign=adina_khaidarova_2', profile: 'https://www.tiktok.com/@jana.menfan' },
          { name: 'Instagram', icon: '📸', url: 'https://janamen1.kz/fun?utm_source=instagram&utm_medium=video&utm_campaign=adina_khaidarova_2', profile: 'https://www.instagram.com/janamen_fan?igsh=Y2w2YXEwbTlnc3ow' },
          { name: 'YouTube', icon: '▶️', url: 'https://janamen1.kz/fun?utm_source=youtube&utm_medium=video&utm_campaign=adina_khaidarova_2', profile: 'https://youtube.com/channel/UC88OJTRuSzamH0hWRg8qmVQ' }
        ]
      }
    ];

    // Состояние фильтров
    let currentMainChannel = 'organika'; // 'organika' | 'influence' | 'fan' | 'all' | 'tags'
    let currentPeriod = 'all';
    let filterDateFrom = null; // unix timestamp in seconds
    let filterDateTo = null;   // unix timestamp in seconds
    let filtersCollapsed = false;
    let currentAllDim = 'combos';

    // Состояние развернутых аккордеонов
    const expandedAccordions = new Set(['mpb1', 'mpb2', 'mpb3', 'mpb4', 'bekezhanova_dilnaz', 'doskazhanova_ainagul', 'kenzhebaeva_aisulu_1', 'kenzhebaeva_aisulu_2', 'gaisina_kamila', 'kenzhebaeva_aida', 'adina_khaidarova_1', 'adina_khaidarova_2']);
    let CLICK_BY_CAMPAIGN = {};

    // Данные кликов из Supabase
    let CLICK_COUNTS = {};
    let CLICK_BY_MEDIUM = {};
    let CLICK_BY_PAGE = {};
    let CLICK_BY_SOURCE = {};

    // Агрегированные данные текущей выборки
    let currentChannelData = {};

    // ============================================================
    // ПЕРЕКЛЮЧЕНИЕ ГЛАВНЫХ КАНАЛОВ
    // ============================================================
    function switchMainChannel(channel) {
      currentMainChannel = channel;

      // Обновление вкладок
      const tabs = ['organika', 'influence', 'fan', 'all', 'tags'];
      tabs.forEach(t => {
        const btn = document.getElementById('main-tab-' + t);
        if (!btn) return;
        if (t === channel) {
          if (t === 'organika') btn.className = 'px-4 py-2.5 rounded-xl bg-emerald-600 text-white font-black text-xs sm:text-sm flex items-center space-x-2 transition shadow-sm whitespace-nowrap';
          else if (t === 'influence') btn.className = 'px-4 py-2.5 rounded-xl bg-purple-600 text-white font-black text-xs sm:text-sm flex items-center space-x-2 transition shadow-sm whitespace-nowrap';
          else if (t === 'fan') btn.className = 'px-4 py-2.5 rounded-xl bg-indigo-600 text-white font-black text-xs sm:text-sm flex items-center space-x-2 transition shadow-sm whitespace-nowrap';
          else if (t === 'tags') btn.className = 'px-3.5 py-2.5 rounded-xl bg-amber-500 text-white font-black text-xs sm:text-sm flex items-center space-x-1.5 transition shadow-sm whitespace-nowrap';
          else btn.className = 'px-3.5 py-2.5 rounded-xl bg-slate-900 text-white font-black text-xs sm:text-sm flex items-center space-x-1.5 transition shadow-sm whitespace-nowrap ml-auto';
        } else {
          if (t === 'tags') btn.className = 'px-3.5 py-2.5 rounded-xl bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 font-bold text-xs sm:text-sm flex items-center space-x-1.5 transition whitespace-nowrap';
          else if (t === 'all') btn.className = 'px-3.5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs sm:text-sm flex items-center space-x-1.5 transition whitespace-nowrap ml-auto';
          else btn.className = 'px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-black text-xs sm:text-sm flex items-center space-x-2 transition whitespace-nowrap';
        }
      });

      // Показ/скрытие кнопок разворачивания
      const actionBtns = document.getElementById('channelActionButtons');
      const allSubTabs = document.getElementById('allChannelsSubTabs');
      if (channel === 'influence' || channel === 'fan') {
        if (actionBtns) actionBtns.classList.remove('hidden');
      } else {
        if (actionBtns) actionBtns.classList.add('hidden');
      }

      if (channel === 'all') {
        if (allSubTabs) allSubTabs.classList.remove('hidden');
      } else {
        if (allSubTabs) allSubTabs.classList.add('hidden');
      }

      onFilterChange();
    }

    // ============================================================
    // СВОРАЧИВАНИЕ / РАЗВОРАЧИВАНИЕ ФИЛЬТРОВ
    // ============================================================
    function toggleFilters() {
      filtersCollapsed = !filtersCollapsed;
      const body = document.getElementById('filtersBody');
      const txt = document.getElementById('toggleFilterText');
      const icon = document.getElementById('toggleFilterIcon');
      if (filtersCollapsed) {
        body.classList.add('hidden');
        txt.innerText = 'Развернуть фильтры';
        icon.style.transform = 'rotate(180deg)';
      } else {
        body.classList.remove('hidden');
        txt.innerText = 'Свернуть фильтры';
        icon.style.transform = 'rotate(0deg)';
      }
    }

    // ============================================================
    // ФИЛЬТРАЦИЯ ПО ПЕРИОДУ
    // ============================================================
    function setPeriodPreset(preset) {
      currentPeriod = preset;
      const now = new Date();
      const nowTs = Math.floor(now.getTime() / 1000);

      const buttons = document.querySelectorAll('[id^="period-btn-"]');
      buttons.forEach(b => {
        if (b.id === 'period-btn-' + preset) {
          b.className = 'px-2.5 py-1 text-xs font-bold rounded-lg bg-slate-900 text-white transition shadow-sm';
        } else {
          b.className = 'px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
        }
      });

      if (preset === 'all') {
        filterDateFrom = null;
        filterDateTo = null;
      } else if (preset === 'today') {
        const start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        filterDateFrom = Math.floor(start.getTime() / 1000);
        filterDateTo = null;
      } else if (preset === 'yesterday') {
        const start = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
        const end = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        filterDateFrom = Math.floor(start.getTime() / 1000);
        filterDateTo = Math.floor(end.getTime() / 1000);
      } else if (preset === 'last7') {
        filterDateFrom = nowTs - 7 * 86400;
        filterDateTo = null;
      } else if (preset === 'last30') {
        filterDateFrom = nowTs - 30 * 86400;
        filterDateTo = null;
      } else if (preset === 'nov2026') {
        filterDateFrom = Math.floor(new Date('2026-11-01T00:00:00Z').getTime() / 1000);
        filterDateTo = Math.floor(new Date('2026-12-01T00:00:00Z').getTime() / 1000);
      } else if (preset === 'oct2026') {
        filterDateFrom = Math.floor(new Date('2026-10-01T00:00:00Z').getTime() / 1000);
        filterDateTo = Math.floor(new Date('2026-11-01T00:00:00Z').getTime() / 1000);
      }

      onFilterChange();
    }

    function applyCustomDateRange() {
      const fromVal = document.getElementById('dateInputFrom').value;
      const toVal = document.getElementById('dateInputTo').value;
      if (!fromVal && !toVal) return;

      currentPeriod = 'custom';
      filterDateFrom = fromVal ? Math.floor(new Date(fromVal + 'T00:00:00Z').getTime() / 1000) : null;
      filterDateTo = toVal ? Math.floor(new Date(toVal + 'T23:59:59Z').getTime() / 1000) : null;

      const buttons = document.querySelectorAll('[id^="period-btn-"]');
      buttons.forEach(b => {
        b.className = 'px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
      });

      onFilterChange();
    }

    function resetAllFilters() {
      currentPeriod = 'all';
      filterDateFrom = null;
      filterDateTo = null;
      document.getElementById('dateInputFrom').value = '';
      document.getElementById('dateInputTo').value = '';
      document.getElementById('filterSearchInput').value = '';
      setPeriodPreset('all');
    }

    // ============================================================
    // ОСНОВНОЙ ПЕРЕСЧЕТ И АГРЕГАЦИЯ ДАННЫХ
    // ============================================================
    function onFilterChange() {
      updateActiveFilterBadge();
      computeChannelData();
      updateKpis();
      renderMainTable();
    }

    function updateActiveFilterBadge() {
      const badge = document.getElementById('activeFilterBadge');
      let pLabel = 'Весь период';
      if (currentPeriod === 'today') pLabel = 'Сегодня';
      else if (currentPeriod === 'yesterday') pLabel = 'Вчера';
      else if (currentPeriod === 'last7') pLabel = '7 дней';
      else if (currentPeriod === 'last30') pLabel = '30 дней';
      else if (currentPeriod === 'nov2026') pLabel = 'Ноябрь 2026';
      else if (currentPeriod === 'oct2026') pLabel = 'Октябрь 2026';
      else if (currentPeriod === 'custom') pLabel = 'Точные даты';

      let cLabel = 'Органика';
      if (currentMainChannel === 'influence') cLabel = 'Influence (МПБ)';
      else if (currentMainChannel === 'fan') cLabel = 'Fan-аккаунты';
      else if (currentMainChannel === 'all') cLabel = 'Все каналы';
      else if (currentMainChannel === 'tags') cLabel = 'Теги AmoCRM';

      badge.innerText = pLabel + ' · ' + cLabel;
    }

    function computeChannelData() {
      const textSearch = (document.getElementById('filterSearchInput').value || '').toLowerCase().trim();

      let leads = 0;
      let won = 0;
      let rev = 0;
      let clicks = 0;

      // Структуры для каждого режима
      const organikaGroups = {};
      const influenceManagers = {
        'mpb1': { code: 'mpb1', name: 'Анельжан (mpb1)', leads: 0, won: 0, rev: 0, clicks: 0, bloggers: {} },
        'mpb2': { code: 'mpb2', name: 'Алина (mpb2)', leads: 0, won: 0, rev: 0, clicks: 0, bloggers: {} },
        'mpb3': { code: 'mpb3', name: 'Алуа (mpb3)', leads: 0, won: 0, rev: 0, clicks: 0, bloggers: {} },
        'mpb4': { code: 'mpb4', name: 'Дарина (mpb4)', leads: 0, won: 0, rev: 0, clicks: 0, bloggers: {} },
        'other': { code: 'other', name: 'Другие / Без менеджера', leads: 0, won: 0, rev: 0, clicks: 0, bloggers: {} }
      };

      const fanAccounts = {};
      FAN_REGISTRY.forEach(f => {
        fanAccounts[f.id] = {
          id: f.id,
          name: f.name,
          leads: 0,
          won: 0,
          rev: 0,
          clicks: 0,
          isOfficial: true,
          platforms: {}
        };
        f.platforms.forEach(p => {
          fanAccounts[f.id].platforms[p.name.toLowerCase()] = {
            name: p.name,
            icon: p.icon,
            url: p.url,
            profile: p.profile,
            leads: 0,
            won: 0,
            rev: 0,
            clicks: 0
          };
        });
      });

      // Исторические группы
      fanAccounts['fan_4516'] = { id: 'fan_4516', name: 'Кампания 4516 (Архив)', leads: 0, won: 0, rev: 0, clicks: 0, isOfficial: false, platforms: {} };
      fanAccounts['fan_2427'] = { id: 'fan_2427', name: 'Кампания 2427-2431 (Архив)', leads: 0, won: 0, rev: 0, clicks: 0, isOfficial: false, platforms: {} };
      fanAccounts['fan_other'] = { id: 'fan_other', name: 'Другие фан-сделки', leads: 0, won: 0, rev: 0, clicks: 0, isOfficial: false, platforms: {} };

      const allCombos = {};
      const allSources = {};
      const allMediums = {};
      const allCampaigns = {};
      const allContents = {};
      const allSubpages = {};
      const allTags = {};

      let len = ALL_LEADS.length;
      let countOrganika = 0;
      let countInfluence = 0;
      let countFan = 0;

      for (let i = 0; i < len; i++) {
        const l = ALL_LEADS[i];

        // 1. Фильтр дат
        if (filterDateFrom && l.ts < filterDateFrom) continue;
        if (filterDateTo && l.ts > filterDateTo) continue;

        // Определение принадлежности к каналам
        const isWa9828 = l.path === '/iwa-9828' || (l.med && l.med.includes('Айтым')) || (l.tags && l.tags.some(t => t.includes('9828') || t.includes('77083779828')));
        const isSmm = l.path === '/smm' || l.med === 'social' || (l.cmp && l.cmp.toLowerCase().includes('smm')) || (l.src && l.src.toLowerCase().includes('smm'));
        const isOrganikaSite = l.path === '/organika' || (currentMainChannel === 'organika' && l.path === '/');
        const isOrganika = isWa9828 || isSmm || isOrganikaSite;

        const isInfluence = l.path === '/influence' || (l.med && l.med.startsWith('mpb')) || (l.cmp && l.cmp.toLowerCase().includes('influence'));
                const lCmp = (l.cmp || '').toLowerCase();
        const lCnt = (l.cnt || '').toLowerCase();
        const lMed = (l.med || '').toLowerCase();
        const lSrc = (l.src || '').toLowerCase();

        let matchedFanId = null;
        for (let fi = 0; fi < FAN_REGISTRY.length; fi++) {
          const f = FAN_REGISTRY[fi];
          if (lCmp.includes(f.id) || lCnt.includes(f.id)) {
            matchedFanId = f.id;
            break;
          }
        }

        if (!matchedFanId) {
          if (lCmp.includes('4516')) matchedFanId = 'fan_4516';
          else if (lCmp.includes('2427') || lCmp.includes('2428') || lCmp.includes('2429') || lCmp.includes('2430') || lCmp.includes('2431')) matchedFanId = 'fan_2427';
          else if (lMed === 'fan' || lMed === 'video' || l.path === '/fun' || l.path.startsWith('/fan') || lSrc.includes('fan')) {
            matchedFanId = 'fan_other';
          }
        }

        const isFan = matchedFanId !== null;

        if (isOrganika) countOrganika++;
        if (isInfluence) countInfluence++;
        if (isFan) countFan++;

        // Фильтр главного канала
        if (currentMainChannel === 'organika' && !isOrganika) continue;
        if (currentMainChannel === 'influence' && !isInfluence) continue;
        if (currentMainChannel === 'fan' && !isFan) continue;

        // Поисковый фильтр
        if (textSearch) {
          const tagStr = (l.tags || []).join(' ');
          const hay = (l.src + ' ' + l.med + ' ' + l.cmp + ' ' + l.cnt + ' ' + l.trm + ' ' + l.path + ' ' + l.name + ' ' + tagStr).toLowerCase();
          if (!hay.includes(textSearch)) continue;
        }

        leads++;
        if (l.won) {
          won++;
          rev += l.price;
        }

        // Агрегация для Органики
        if (currentMainChannel === 'organika') {
          let gKey = '';
          let gType = '';
          if (isWa9828) {
            gKey = '📱 WhatsApp Айтыма Бериковича (77083779828)';
            gType = 'wa';
          } else if (isSmm) {
            gKey = '📸 /smm (Соцсети)';
            gType = 'smm';
          } else {
            gKey = '🌐 ' + (l.path || '/');
            gType = 'site';
          }

          const itemKey = gKey + ' | ' + (l.src || 'direct') + ' | ' + (l.cmp || 'none') + ' | ' + (l.cnt || 'none');
          let g = organikaGroups[itemKey];
          if (!g) {
            g = organikaGroups[itemKey] = {
              title: gKey,
              type: gType,
              path: l.path,
              src: l.src,
              cmp: l.cmp,
              cnt: l.cnt,
              leads: 0,
              won: 0,
              rev: 0,
              clicks: 0
            };
          }
          g.leads++;
          if (l.won) { g.won++; g.rev += l.price; }
        }

        // Агрегация для Influence
        if (currentMainChannel === 'influence') {
          let mKey = (l.med && l.med.startsWith('mpb')) ? l.med : 'other';
          if (!influenceManagers[mKey]) mKey = 'other';
          const mgr = influenceManagers[mKey];
          mgr.leads++;
          if (l.won) { mgr.won++; mgr.rev += l.price; }

          const bKey = (l.cnt && l.cnt !== 'none') ? l.cnt : 'не_указан';
          let b = mgr.bloggers[bKey];
          if (!b) {
            b = mgr.bloggers[bKey] = {
              name: bKey,
              manager: mKey,
              leads: 0,
              won: 0,
              rev: 0,
              clicks: 0
            };
          }
          b.leads++;
          if (l.won) { b.won++; b.rev += l.price; }
        }

        // Агрегация для Fan
        if (currentMainChannel === 'fan' && matchedFanId && fanAccounts[matchedFanId]) {
          const fa = fanAccounts[matchedFanId];
          fa.leads++;
          if (l.won) { fa.won++; fa.rev += l.price; }

          let pKey = 'other';
          if (lSrc.includes('tiktok')) pKey = 'tiktok';
          else if (lSrc.includes('instagram') || lSrc.includes('ig')) pKey = 'instagram';
          else if (lSrc.includes('youtube') || lSrc.includes('yt')) pKey = 'youtube';
          else pKey = l.src || 'other';

          if (!fa.platforms[pKey]) {
            fa.platforms[pKey] = {
              name: pKey,
              icon: pKey === 'tiktok' ? '🎵' : (pKey === 'instagram' ? '📸' : (pKey === 'youtube' ? '▶️' : '🌐')),
              url: `https://janamen1.kz/fun?utm_source=${pKey}&utm_medium=video&utm_campaign=${matchedFanId}`,
              profile: '',
              leads: 0,
              won: 0,
              rev: 0,
              clicks: 0
            };
          }
          fa.platforms[pKey].leads++;
          if (l.won) { fa.platforms[pKey].won++; fa.platforms[pKey].rev += l.price; }
        }

        // Агрегация для Всех каналов & Тегов
        const ck = (l.path || '/') + '|' + l.src + '|' + l.med + '|' + l.cmp + '|' + l.cnt + '|' + l.trm;
        if (!allCombos[ck]) {
          allCombos[ck] = { landing: 'janamen1.kz' + l.path, path: l.path, src: l.src, med: l.med, cmp: l.cmp, cnt: l.cnt, trm: l.trm, leads: 0, won: 0, rev: 0 };
        }
        allCombos[ck].leads++;
        if (l.won) { allCombos[ck].won++; allCombos[ck].rev += l.price; }

        function incDim(dict, key) {
          if (!dict[key]) dict[key] = { name: key, leads: 0, won: 0, rev: 0 };
          dict[key].leads++;
          if (l.won) { dict[key].won++; dict[key].rev += l.price; }
        }
        incDim(allSources, l.src);
        incDim(allMediums, l.med);
        incDim(allCampaigns, l.cmp);
        incDim(allContents, l.cnt);
        incDim(allSubpages, l.path);
        if (l.tags && l.tags.length) {
          for (let ti = 0; ti < l.tags.length; ti++) {
            if (l.tags[ti]) incDim(allTags, l.tags[ti]);
          }
        }
      }

      // Обновление счетчиков на вкладках
      const bOrg = document.getElementById('tabBadgeOrganika');
      if (bOrg) bOrg.innerText = countOrganika >= 1000 ? (Math.round(countOrganika / 100) / 10) + 'k' : countOrganika;

      const bInf = document.getElementById('tabBadgeInfluence');
      if (bInf) bInf.innerText = countInfluence + ' лид.';

      const bFan = document.getElementById('tabBadgeFan');
      if (bFan) bFan.innerText = countFan + ' лид.';

      // Привязка кликов из CLICK_COUNTS
      if (currentMainChannel === 'organika') {
        const smmClicks = (CLICK_BY_PAGE['/smm'] || 0) + (CLICK_COUNTS['smm'] || 0) + (CLICK_BY_MEDIUM['social'] || 0);
        clicks += smmClicks;
        Object.values(organikaGroups).forEach(g => {
          if (g.type === 'smm') g.clicks = smmClicks;
        });
      } else if (currentMainChannel === 'influence') {
        Object.keys(influenceManagers).forEach(mCode => {
          const mgr = influenceManagers[mCode];
          let mgrClicks = (CLICK_BY_MEDIUM[mCode] || 0);
          Object.values(mgr.bloggers).forEach(b => {
            const bClicks = CLICK_COUNTS[b.name] || 0;
            b.clicks = bClicks;
            mgrClicks += bClicks;
          });
          mgr.clicks = mgrClicks;
          clicks += mgrClicks;
        });
      } else if (currentMainChannel === 'fan') {
        Object.keys(fanAccounts).forEach(fKey => {
          const fa = fanAccounts[fKey];
          const fClicks = (CLICK_BY_CAMPAIGN[fKey] || 0) + (CLICK_COUNTS[fKey] || 0);
          fa.clicks = fClicks;
          clicks += fClicks;

          Object.keys(fa.platforms).forEach(pKey => {
            fa.platforms[pKey].clicks = CLICK_BY_SOURCE[pKey] || 0;
          });
        });
      } else {
        clicks = Object.values(CLICK_COUNTS).reduce((a, b) => a + b, 0);
      }

      currentChannelData = {
        leads, won, rev, clicks,
        cr1: clicks ? (won ? (leads / clicks) : 0) : 0,
        cr2: leads ? (won / leads) : 0,
        avgCheck: won ? Math.round(rev / won) : 0,
        organikaGroups: Object.values(organikaGroups).sort((a,b) => b.leads - a.leads),
        influenceManagers,
        fanAccounts,
        allCombos: Object.values(allCombos).sort((a,b) => b.rev - a.rev || b.leads - a.leads),
        allSources: Object.values(allSources).sort((a,b) => b.rev - a.rev || b.leads - a.leads),
        allMediums: Object.values(allMediums).sort((a,b) => b.rev - a.rev || b.leads - a.leads),
        allCampaigns: Object.values(allCampaigns).sort((a,b) => b.rev - a.rev || b.leads - a.leads),
        allContents: Object.values(allContents).sort((a,b) => b.rev - a.rev || b.leads - a.leads),
        allSubpages: Object.values(allSubpages).sort((a,b) => b.rev - a.rev || b.leads - a.leads),
        allTags: Object.values(allTags).sort((a,b) => b.leads - a.leads)
      };
    }

    // ============================================================
    // ОБНОВЛЕНИЕ KPI КАРТОЧЕК
    // ============================================================
    function updateKpis() {
      const d = currentChannelData;
      document.getElementById('kpiTotalLeads').innerText = d.leads.toLocaleString('ru-RU');
      document.getElementById('kpiWonLeads').innerText = d.won.toLocaleString('ru-RU');
      document.getElementById('kpiRevenue').innerText = d.rev.toLocaleString('ru-RU') + ' ₸';
      document.getElementById('kpiAvgCheck').innerText = 'Средний чек: ' + (d.avgCheck || 0).toLocaleString('ru-RU') + ' ₸';
      document.getElementById('kpiClicks').innerText = d.clicks.toLocaleString('ru-RU');
      
      const cr1Pct = d.clicks ? (Math.round(d.leads / d.clicks * 1000) / 10) + '%' : (d.leads ? '—' : '0%');
      document.getElementById('kpiCr1').innerText = 'CR1 (Клик ➔ Лид): ' + cr1Pct;
      
      const cr2Pct = d.leads ? (Math.round(d.won / d.leads * 1000) / 10) + '%' : '0%';
      document.getElementById('kpiCr2').innerText = 'CR2 (Лид ➔ Оплата): ' + cr2Pct;

      const scopeBadge = document.getElementById('kpiScopeBadge');
      const entityLabel = document.getElementById('kpiEntityLabel');
      const entitiesCount = document.getElementById('kpiEntitiesCount');

      if (currentMainChannel === 'organika') {
        scopeBadge.innerText = 'Органика';
        scopeBadge.className = 'text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800';
        entityLabel.innerText = 'Связок и точек входа';
        entitiesCount.innerText = d.organikaGroups.length;
      } else if (currentMainChannel === 'influence') {
        scopeBadge.innerText = 'Influence';
        scopeBadge.className = 'text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-purple-100 text-purple-800';
        entityLabel.innerText = 'Блогеров в базе';
        let bCount = 0;
        Object.values(d.influenceManagers).forEach(m => bCount += Object.keys(m.bloggers).length);
        entitiesCount.innerText = bCount;
      } else if (currentMainChannel === 'fan') {
        scopeBadge.innerText = 'Fan-аккаунты';
        scopeBadge.className = 'text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-800';
        entityLabel.innerText = 'Фан-аккаунтов';
        entitiesCount.innerText = FAN_REGISTRY.length + ' аккаунтов';
      } else if (currentMainChannel === 'tags') {
        scopeBadge.innerText = 'Теги CRM';
        scopeBadge.className = 'text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-amber-100 text-amber-800';
        entityLabel.innerText = 'Тегов AmoCRM';
        entitiesCount.innerText = d.allTags.length;
      } else {
        scopeBadge.innerText = 'Все каналы';
        scopeBadge.className = 'text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-800';
        entityLabel.innerText = 'Активных UTM-связок';
        entitiesCount.innerText = d.allCombos.length;
      }
    }

    // ============================================================
    // УПРАВЛЕНИЕ АККОРДЕОНАМИ (РАЗВЕРНУТЬ / СВЕРНУТЬ)
    // ============================================================
    function toggleAccordion(id) {
      if (expandedAccordions.has(id)) {
        expandedAccordions.delete(id);
      } else {
        expandedAccordions.add(id);
      }
      renderMainTable();
    }

    function expandAllAccordion() {
      Object.keys(currentChannelData.influenceManagers || {}).forEach(k => expandedAccordions.add(k));
      FAN_REGISTRY.forEach(f => expandedAccordions.add(f.id)); Object.keys(currentChannelData.fanAccounts || {}).forEach(k => expandedAccordions.add(k));
      renderMainTable();
    }

    function collapseAllAccordion() {
      expandedAccordions.clear();
      renderMainTable();
    }

    // ============================================================
    // ОТРИСОВКА ГЛАВНОЙ ТАБЛИЦЫ
    // ============================================================
    function renderMainTable() {
      const thead = document.getElementById('mainTableHead');
      const tbody = document.getElementById('mainTableBody');
      const rowBadge = document.getElementById('rowCountBadge');
      const mainTitle = document.getElementById('tableMainTitle');
      const badgeTitle = document.getElementById('tableBadgeTitle');
      const subTitle = document.getElementById('tableMainSubtitle');

      if (currentMainChannel === 'organika') {
        mainTitle.innerText = '🌿 Органика: SMM и WhatsApp Айтыма Бериковича';
        badgeTitle.innerText = 'Канал 1';
        badgeTitle.className = 'px-2 py-0.5 text-[10px] font-black uppercase rounded bg-emerald-100 text-emerald-800';
        subTitle.innerText = 'Прямая прозрачная таблица без вложенности: клики, заявки и подтвержденные оплаты';

        thead.innerHTML = `
          <tr>
            <th class="py-3 px-4">Канал / Посадочная страница</th>
            <th class="py-3 px-4">utm_source (Источник)</th>
            <th class="py-3 px-4">utm_campaign</th>
            <th class="py-3 px-4">utm_content</th>
            <th class="py-3 px-4 text-center">Кликов</th>
            <th class="py-3 px-4 text-center">Лидов всего</th>
            <th class="py-3 px-4 text-center">CR1 (Клик➔Лид)</th>
            <th class="py-3 px-4 text-center">Оплачено (142)</th>
            <th class="py-3 px-4 text-center">CR2 (Лид➔Оплата)</th>
            <th class="py-3 px-4 text-right">Выручка (₸)</th>
            <th class="py-3 px-4 text-right">Ср. чек (₸)</th>
          </tr>
        `;

        const list = currentChannelData.organikaGroups || [];
        rowBadge.innerText = 'Показано: ' + list.length + ' связок';

        if (list.length === 0) {
          tbody.innerHTML = '<tr><td colspan="11" class="py-8 text-center text-slate-400">Ничего не найдено за выбранный период</td></tr>';
          return;
        }

        tbody.innerHTML = list.map(item => {
          const cr1 = item.clicks ? (Math.round(item.leads / item.clicks * 1000) / 10) + '%' : (item.leads ? '—' : '0%');
          const cr2 = item.leads ? (Math.round(item.won / item.leads * 1000) / 10) + '%' : '0%';
          const avg = item.won ? Math.round(item.rev / item.won) : 0;
          return `
            <tr class="hover:bg-emerald-50/30 transition">
              <td class="py-3 px-4 font-bold text-slate-900 code-font whitespace-nowrap">${item.title}</td>
              <td class="py-3 px-4 font-bold text-slate-700 code-font">${item.src}</td>
              <td class="py-3 px-4 text-slate-600 code-font">${item.cmp}</td>
              <td class="py-3 px-4 text-slate-500 code-font text-[11px]">${item.cnt}</td>
              <td class="py-3 px-4 text-center font-bold text-purple-700">${item.clicks ? item.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
              <td class="py-3 px-4 text-center font-black text-slate-900">${item.leads.toLocaleString('ru-RU')}</td>
              <td class="py-3 px-4 text-center font-semibold text-slate-600">${cr1}</td>
              <td class="py-3 px-4 text-center font-black text-emerald-600">${item.won}</td>
              <td class="py-3 px-4 text-center font-bold ${item.won > 0 ? 'text-emerald-700 bg-emerald-50/60 rounded' : 'text-slate-400'}">${cr2}</td>
              <td class="py-3 px-4 text-right font-black text-slate-900 whitespace-nowrap">${item.rev.toLocaleString('ru-RU')} ₸</td>
              <td class="py-3 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${avg.toLocaleString('ru-RU')} ₸</td>
            </tr>
          `;
        }).join('');

      } else if (currentMainChannel === 'influence') {
        mainTitle.innerText = '🌟 Influence (Инфлюенс-маркетинг): Менеджеры МПБ & Блогеры';
        badgeTitle.innerText = 'Канал 2';
        badgeTitle.className = 'px-2 py-0.5 text-[10px] font-black uppercase rounded bg-purple-100 text-purple-800';
        subTitle.innerText = 'Свертка по менеджерам (клики, лиды, продажи) с разворачиванием до каждого блогера';

        thead.innerHTML = `
          <tr>
            <th class="py-3 px-4">Менеджер / Блогер (utm_content)</th>
            <th class="py-3 px-4 text-center">Кликов (Переходов)</th>
            <th class="py-3 px-4 text-center">Всего заявок (Лидов)</th>
            <th class="py-3 px-4 text-center">CR1 (Клик➔Лид)</th>
            <th class="py-3 px-4 text-center">Оплачено (142)</th>
            <th class="py-3 px-4 text-center">CR2 (Лид➔Оплата)</th>
            <th class="py-3 px-4 text-right">Выручка (₸)</th>
            <th class="py-3 px-4 text-right">Ср. чек (₸)</th>
            <th class="py-3 px-4 text-center">Быстрая ссылка</th>
          </tr>
        `;

        const mgrs = currentChannelData.influenceManagers || {};
        let totalRows = 0;
        let html = '';

        // Порядок отображения 4 менеджеров
        const order = ['mpb1', 'mpb2', 'mpb3', 'mpb4', 'other'];

        order.forEach(mCode => {
          const m = mgrs[mCode];
          if (!m) return;
          const isExpanded = expandedAccordions.has(mCode);
          const bloggersList = Object.values(m.bloggers || {}).sort((a,b) => b.rev - a.rev || b.leads - a.leads);
          const bCount = bloggersList.length;

          const mCr1 = m.clicks ? (Math.round(m.leads / m.clicks * 1000) / 10) + '%' : (m.leads ? '—' : '0%');
          const mCr2 = m.leads ? (Math.round(m.won / m.leads * 1000) / 10) + '%' : '0%';
          const mAvg = m.won ? Math.round(m.rev / m.won) : 0;

          totalRows++;

          // Строка Менеджера (Level 1)
          html += `
            <tr onclick="toggleAccordion('${mCode}')" class="bg-purple-50/60 hover:bg-purple-100/60 cursor-pointer transition font-bold border-t-2 border-purple-200">
              <td class="py-3.5 px-4 text-slate-900 flex items-center space-x-2">
                <span class="w-5 h-5 rounded-md bg-purple-600 text-white flex items-center justify-center text-xs transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}">
                  ▶
                </span>
                <span class="text-sm font-black text-purple-950">${m.name}</span>
                <span class="px-2 py-0.5 text-[10px] font-extrabold rounded-full bg-purple-200 text-purple-900">
                  ${bCount} блогеров
                </span>
              </td>
              <td class="py-3.5 px-4 text-center font-black text-purple-700">${m.clicks ? m.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
              <td class="py-3.5 px-4 text-center font-black text-slate-900">${m.leads.toLocaleString('ru-RU')}</td>
              <td class="py-3.5 px-4 text-center font-bold text-slate-700">${mCr1}</td>
              <td class="py-3.5 px-4 text-center font-black text-emerald-600">${m.won}</td>
              <td class="py-3.5 px-4 text-center font-bold ${m.won > 0 ? 'text-emerald-700 bg-emerald-100/70 rounded' : 'text-slate-400'}">${mCr2}</td>
              <td class="py-3.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${m.rev.toLocaleString('ru-RU')} ₸</td>
              <td class="py-3.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${mAvg.toLocaleString('ru-RU')} ₸</td>
              <td class="py-3.5 px-4 text-center">
                <button onclick="event.stopPropagation(); openGenForManager('${mCode}')" class="px-2 py-1 text-[11px] font-bold text-purple-700 bg-white hover:bg-purple-200 rounded-lg border border-purple-300 transition">
                  + Ссылка
                </button>
              </td>
            </tr>
          `;

          // Дочерние строки блогеров (Level 2)
          if (isExpanded) {
            if (bCount === 0) {
              html += `
                <tr class="bg-white">
                  <td colspan="9" class="py-3 px-8 text-xs text-slate-400 italic">У данного менеджера пока нет лидов/блогеров за выбранный период</td>
                </tr>
              `;
            } else {
              bloggersList.forEach(b => {
                totalRows++;
                const bCr1 = b.clicks ? (Math.round(b.leads / b.clicks * 1000) / 10) + '%' : (b.leads ? '—' : '0%');
                const bCr2 = b.leads ? (Math.round(b.won / b.leads * 1000) / 10) + '%' : '0%';
                const bAvg = b.won ? Math.round(b.rev / b.won) : 0;
                html += `
                  <tr class="hover:bg-slate-50 transition text-xs border-b border-slate-100">
                    <td class="py-2.5 px-4 pl-10 font-bold text-slate-800 code-font flex items-center space-x-1.5">
                      <span class="text-slate-300 font-mono">└─</span>
                      <span class="text-brand-700 font-bold">@${b.name}</span>
                    </td>
                    <td class="py-2.5 px-4 text-center font-bold text-purple-700">${b.clicks ? b.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
                    <td class="py-2.5 px-4 text-center font-bold text-slate-800">${b.leads.toLocaleString('ru-RU')}</td>
                    <td class="py-2.5 px-4 text-center font-semibold text-slate-600">${bCr1}</td>
                    <td class="py-2.5 px-4 text-center font-black text-emerald-600">${b.won}</td>
                    <td class="py-2.5 px-4 text-center font-bold ${b.won > 0 ? 'text-emerald-700' : 'text-slate-400'}">${bCr2}</td>
                    <td class="py-2.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${b.rev.toLocaleString('ru-RU')} ₸</td>
                    <td class="py-2.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${bAvg.toLocaleString('ru-RU')} ₸</td>
                    <td class="py-2.5 px-4 text-center">
                      <button onclick="copyBloggerLinkDirect('${b.name}', '${mCode}')" title="Скопировать ссылку" class="px-2 py-0.5 text-[11px] font-bold text-slate-600 hover:text-purple-700 bg-slate-100 hover:bg-purple-100 rounded border border-slate-200 transition">
                        📋 Ссылка
                      </button>
                    </td>
                  </tr>
                `;
              });
            }
          }
        });

        rowBadge.innerText = 'Показано: ' + totalRows + ' строк';
        tbody.innerHTML = html;

      } else if (currentMainChannel === 'fan') {
        mainTitle.innerText = '🎬 Fan (Фан-аккаунты сетки): 8 аккаунтов команды & каналы';
        badgeTitle.innerText = 'Канал 3';
        badgeTitle.className = 'px-2 py-0.5 text-[10px] font-black uppercase rounded bg-indigo-100 text-indigo-800';
        subTitle.innerText = 'Свертка по 8 сотрудникам сетки с детализацией по TikTok, Instagram, YouTube, готовыми ссылками и переходами на профили';

        thead.innerHTML = `
          <tr>
            <th class="py-3 px-4">Сотрудник / Площадка</th>
            <th class="py-3 px-4 text-center">Кликов (Переходов)</th>
            <th class="py-3 px-4 text-center">Всего заявок (Лидов)</th>
            <th class="py-3 px-4 text-center">CR1 (Клик➔Лид)</th>
            <th class="py-3 px-4 text-center">Оплачено (142)</th>
            <th class="py-3 px-4 text-center">CR2 (Лид➔Оплата)</th>
            <th class="py-3 px-4 text-right">Выручка (₸)</th>
            <th class="py-3 px-4 text-right">Ср. чек (₸)</th>
            <th class="py-3 px-4 text-center">UTM-ссылка & Профиль</th>
          </tr>
        `;

        const fans = currentChannelData.fanAccounts || {};
        let totalRows = 0;
        let html = '';

        // Сначала отображаем 8 официальных сотрудников команды
        FAN_REGISTRY.forEach(fReg => {
          const f = fans[fReg.id];
          if (!f) return;
          const isExpanded = expandedAccordions.has(fReg.id);
          const platformsList = fReg.platforms;
          const pCount = platformsList.length;

          const fCr1 = f.clicks ? (Math.round(f.leads / f.clicks * 1000) / 10) + '%' : (f.leads ? '—' : '0%');
          const fCr2 = f.leads ? (Math.round(f.won / f.leads * 1000) / 10) + '%' : '0%';
          const fAvg = f.won ? Math.round(f.rev / f.won) : 0;

          totalRows++;

          // Строка сотрудника (Level 1)
          html += `
            <tr onclick="toggleAccordion('${fReg.id}')" class="bg-indigo-50/60 hover:bg-indigo-100/60 cursor-pointer transition font-bold border-t-2 border-indigo-200">
              <td class="py-3.5 px-4 text-slate-900 flex items-center space-x-2">
                <span class="w-5 h-5 rounded-md bg-indigo-600 text-white flex items-center justify-center text-xs transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}">
                  ▶
                </span>
                <span class="text-sm font-black text-indigo-950">${f.name}</span>
                <span class="px-2 py-0.5 text-[10px] font-extrabold rounded-full bg-indigo-200 text-indigo-900">
                  ${pCount} площадки
                </span>
                ${f.leads === 0 ? '<span class="px-2 py-0.2 text-[9px] font-bold rounded-full bg-slate-200/70 text-slate-600">Готов к трафику</span>' : ''}
              </td>
              <td class="py-3.5 px-4 text-center font-black text-indigo-700">${f.clicks ? f.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
              <td class="py-3.5 px-4 text-center font-black text-slate-900">${f.leads.toLocaleString('ru-RU')}</td>
              <td class="py-3.5 px-4 text-center font-bold text-slate-700">${fCr1}</td>
              <td class="py-3.5 px-4 text-center font-black text-emerald-600">${f.won}</td>
              <td class="py-3.5 px-4 text-center font-bold ${f.won > 0 ? 'text-emerald-700 bg-emerald-100/70 rounded' : 'text-slate-400'}">${fCr2}</td>
              <td class="py-3.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${f.rev.toLocaleString('ru-RU')} ₸</td>
              <td class="py-3.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${fAvg.toLocaleString('ru-RU')} ₸</td>
              <td class="py-3.5 px-4 text-center">
                <button onclick="event.stopPropagation(); copyFanAllLinks('${fReg.id}')" class="px-2.5 py-1 text-[11px] font-bold text-indigo-700 bg-white hover:bg-indigo-200 rounded-lg border border-indigo-300 transition">
                  📋 Ссылки
                </button>
              </td>
            </tr>
          `;

          // Дочерние строки площадок (Level 2)
          if (isExpanded) {
            platformsList.forEach(p => {
              totalRows++;
              const pData = f.platforms[p.name.toLowerCase()] || { leads: 0, won: 0, rev: 0, clicks: 0 };
              const pCr1 = pData.clicks ? (Math.round(pData.leads / pData.clicks * 1000) / 10) + '%' : (pData.leads ? '—' : '0%');
              const pCr2 = pData.leads ? (Math.round(pData.won / pData.leads * 1000) / 10) + '%' : '0%';
              const pAvg = pData.won ? Math.round(pData.rev / pData.won) : 0;
              const hasProfile = p.profile && p.profile.startsWith('http');

              html += `
                <tr class="hover:bg-slate-50 transition text-xs border-b border-slate-100">
                  <td class="py-2.5 px-4 pl-10 font-bold text-slate-800 code-font flex items-center space-x-2">
                    <span class="text-slate-300 font-mono">└─</span>
                    <span class="text-base leading-none">${p.icon}</span>
                    <span class="text-slate-900 font-black">${p.name}</span>
                    ${p.profile && !hasProfile ? '<span class="text-[10px] text-slate-400 font-normal">(' + p.profile + ')</span>' : ''}
                  </td>
                  <td class="py-2.5 px-4 text-center font-bold text-indigo-700">${pData.clicks ? pData.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
                  <td class="py-2.5 px-4 text-center font-bold text-slate-800">${pData.leads.toLocaleString('ru-RU')}</td>
                  <td class="py-2.5 px-4 text-center font-semibold text-slate-600">${pCr1}</td>
                  <td class="py-2.5 px-4 text-center font-black text-emerald-600">${pData.won}</td>
                  <td class="py-2.5 px-4 text-center font-bold ${pData.won > 0 ? 'text-emerald-700' : 'text-slate-400'}">${pCr2}</td>
                  <td class="py-2.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${pData.rev.toLocaleString('ru-RU')} ₸</td>
                  <td class="py-2.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${pAvg.toLocaleString('ru-RU')} ₸</td>
                  <td class="py-2.5 px-4 text-center flex items-center justify-center space-x-1.5">
                    <button onclick="copyFanUtmDirect('${p.url}', '${f.name}', '${p.name}')" title="Скопировать готовую UTM-ссылку" class="px-2 py-0.5 text-[11px] font-bold text-indigo-700 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 rounded border border-indigo-200 transition">
                      📋 UTM
                    </button>
                    ${hasProfile ? `
                      <a href="${p.profile}" target="_blank" title="Открыть соцсеть" class="px-2 py-0.5 text-[11px] font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded border border-slate-200 transition">
                        🔗 Профиль
                      </a>
                    ` : ''}
                  </td>
                </tr>
              `;
            });
          }
        });

        // Исторические архивные фан-кампании
        const histKeys = ['fan_4516', 'fan_2427', 'fan_other'];
        histKeys.forEach(hKey => {
          const h = fans[hKey];
          if (!h || h.leads === 0) return;
          const isExpanded = expandedAccordions.has(hKey);
          const pList = Object.values(h.platforms || {});
          totalRows++;
          html += `
            <tr onclick="toggleAccordion('${hKey}')" class="bg-slate-100/70 hover:bg-slate-200/60 cursor-pointer transition font-bold border-t border-slate-200 text-slate-700">
              <td class="py-3 px-4 flex items-center space-x-2">
                <span class="w-4 h-4 rounded bg-slate-400 text-white flex items-center justify-center text-[10px] transition-transform ${isExpanded ? 'rotate-90' : ''}">▶</span>
                <span class="text-xs font-bold text-slate-800">${h.name}</span>
                <span class="px-1.5 py-0.2 text-[9px] font-semibold rounded bg-slate-200 text-slate-600">Архив</span>
              </td>
              <td class="py-3 px-4 text-center text-slate-400">—</td>
              <td class="py-3 px-4 text-center font-bold text-slate-800">${h.leads.toLocaleString('ru-RU')}</td>
              <td class="py-3 px-4 text-center text-slate-400">—</td>
              <td class="py-3 px-4 text-center font-bold text-emerald-600">${h.won}</td>
              <td class="py-3 px-4 text-center font-semibold text-slate-600">${h.leads ? (Math.round(h.won/h.leads*1000)/10)+'%' : '0%'}</td>
              <td class="py-3 px-4 text-right font-bold text-slate-800">${h.rev.toLocaleString('ru-RU')} ₸</td>
              <td class="py-3 px-4 text-right text-slate-600">${(h.won ? Math.round(h.rev/h.won) : 0).toLocaleString('ru-RU')} ₸</td>
              <td class="py-3 px-4 text-center text-slate-400 text-[10px]">Архивные сделки</td>
            </tr>
          `;
          if (isExpanded) {
            pList.forEach(p => {
              totalRows++;
              html += `
                <tr class="hover:bg-slate-50 transition text-xs border-b border-slate-100 text-slate-600">
                  <td class="py-2 px-4 pl-10 code-font">└─ ${p.name}</td>
                  <td class="py-2 px-4 text-center text-slate-400">—</td>
                  <td class="py-2 px-4 text-center font-semibold">${p.leads}</td>
                  <td class="py-2 px-4 text-center text-slate-400">—</td>
                  <td class="py-2 px-4 text-center font-bold text-emerald-600">${p.won}</td>
                  <td class="py-2 px-4 text-center">${p.leads ? (Math.round(p.won/p.leads*1000)/10)+'%' : '0%'}</td>
                  <td class="py-2 px-4 text-right">${p.rev.toLocaleString('ru-RU')} ₸</td>
                  <td class="py-2 px-4 text-right">${(p.won ? Math.round(p.rev/p.won) : 0).toLocaleString('ru-RU')} ₸</td>
                  <td class="py-2 px-4 text-center text-slate-300">—</td>
                </tr>
              `;
            });
          }
        });

        rowBadge.innerText = 'Показано: ' + totalRows + ' строк';
        tbody.innerHTML = html;

      } else if (currentMainChannel === 'tags') {
        mainTitle.innerText = '🏷️ ТЕГИ AmoCRM: Полный срез всех тегов сделок';
        badgeTitle.innerText = 'Теги CRM';
        badgeTitle.className = 'px-2 py-0.5 text-[10px] font-black uppercase rounded bg-amber-100 text-amber-900 border border-amber-300';
        subTitle.innerText = 'Точный учет всех телефонных тегов, номеров WhatsApp и меток воронок из AmoCRM';

        thead.innerHTML = `
          <tr>
            <th class="py-3 px-4">🏷️ Название тега AmoCRM</th>
            <th class="py-3 px-4 text-center">Всего заявок (Лидов)</th>
            <th class="py-3 px-4 text-center">Оплачено (Статус 142)</th>
            <th class="py-3 px-4 text-center">Конверсия (CR %)</th>
            <th class="py-3 px-4 text-right">Выручка (₸)</th>
            <th class="py-3 px-4 text-right">Средний чек (₸)</th>
          </tr>
        `;

        const list = currentChannelData.allTags || [];
        rowBadge.innerText = 'Показано: ' + list.length + ' тегов';

        tbody.innerHTML = list.map(item => {
          const cr = item.leads ? Math.round(item.won / item.leads * 1000) / 10 : 0;
          const avg = item.won ? Math.round(item.rev / item.won) : 0;
          return `
            <tr class="hover:bg-amber-50/40 transition">
              <td class="py-2.5 px-4 font-bold text-slate-900 code-font">${item.name}</td>
              <td class="py-2.5 px-4 text-center font-bold text-slate-800">${item.leads.toLocaleString('ru-RU')}</td>
              <td class="py-2.5 px-4 text-center font-black text-emerald-600">${item.won}</td>
              <td class="py-2.5 px-4 text-center font-bold ${cr >= 5 ? 'text-emerald-700' : 'text-slate-700'}">${cr}%</td>
              <td class="py-2.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${item.rev.toLocaleString('ru-RU')} ₸</td>
              <td class="py-2.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${avg.toLocaleString('ru-RU')} ₸</td>
            </tr>
          `;
        }).join('');

      } else {
        // ALL CHANNELS
        mainTitle.innerText = '📊 Сводная таблица связок и эффективности UTM';
        badgeTitle.innerText = 'Все каналы';
        badgeTitle.className = 'px-2 py-0.5 text-[10px] font-black uppercase rounded bg-slate-100 text-slate-800';
        subTitle.innerText = 'Оценка переходов, конверсии в оплату и подтвержденной выручки по всем параметрам';

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

        const list = currentChannelData.allCombos || [];
        rowBadge.innerText = 'Показано: ' + list.length + ' связок';

        tbody.innerHTML = list.map(c => {
          const cr = c.leads ? Math.round(c.won / c.leads * 1000) / 10 : 0;
          const avg = c.won ? Math.round(c.rev / c.won) : 0;
          return `
            <tr class="hover:bg-purple-50/30 transition">
              <td class="py-2 px-3 font-bold text-brand-700 code-font whitespace-nowrap">${c.landing || c.path}</td>
              <td class="py-2 px-3 font-bold text-slate-800 code-font">${c.src}</td>
              <td class="py-2 px-3 text-slate-600 code-font">${c.med}</td>
              <td class="py-2 px-3 font-semibold text-slate-800 code-font">${c.cmp}</td>
              <td class="py-2 px-3 text-slate-500 code-font text-[11px]">${c.cnt}</td>
              <td class="py-2 px-3 text-slate-500 code-font text-[11px]">${c.trm}</td>
              <td class="py-2 px-3 text-center font-bold text-slate-800">${c.leads.toLocaleString('ru-RU')}</td>
              <td class="py-2 px-3 text-center font-black text-emerald-600">${c.won}</td>
              <td class="py-2 px-3 text-center font-bold ${cr >= 5 ? 'text-emerald-700 bg-emerald-50 rounded' : 'text-slate-600'}">${cr}%</td>
              <td class="py-2 px-3 text-right font-black text-slate-900 whitespace-nowrap">${c.rev.toLocaleString('ru-RU')} ₸</td>
              <td class="py-2 px-3 text-right font-semibold text-slate-700 whitespace-nowrap">${avg.toLocaleString('ru-RU')} ₸</td>
            </tr>
          `;
        }).join('');
      }
    }

    // ============================================================
    // БЫСТРЫЕ ДЕЙСТВИЯ СО ССЫЛКАМИ БЛОГЕРОВ
    // ============================================================
    function openGenForManager(mCode) {
      openLinkGeneratorModal();
      const mSel = document.getElementById('genManager');
      if (mSel) {
        mSel.value = mCode;
        updateGeneratedLink();
      }
    }

        function copyFanUtmDirect(url, name, platform) {
      navigator.clipboard.writeText(url);
      alert('✓ Скопирована UTM-ссылка для ' + name + ' (' + platform + '):\n\n' + url + '\n\nКлики автоматически фиксируются в Supabase, а UTM передаются в AmoCRM!');
    }

    function copyFanAllLinks(fanId) {
      const f = FAN_REGISTRY.find(x => x.id === fanId);
      if (!f) return;
      const text = f.name + ' — UTM-ссылки:\n' + f.platforms.map(p => p.name + ': ' + p.url).join('\n');
      navigator.clipboard.writeText(text);
      alert('✓ Скопированы все UTM-ссылки для ' + f.name + ':\n\n' + text);
    }
    function copyBloggerLinkDirect(blogger, manager) {
      const origin = window.location.origin;
      const url = origin + '/r/' + encodeURIComponent(blogger) + '?m=' + manager + '&p=/influence';
      navigator.clipboard.writeText(url);
      alert('✓ Ссылка для блогера @' + blogger + ' скопирована:\n' + url);
    }

    function openLinkGeneratorModal() {
      const m = document.getElementById('linkGenModal');
      if (m) {
        m.classList.remove('hidden');
        updateGeneratedLink();
      }
    }

    function closeLinkGeneratorModal() {
      const m = document.getElementById('linkGenModal');
      if (m) m.classList.add('hidden');
    }

    function updateGeneratedLink() {
      const bInput = document.getElementById('genBloggerName');
      const mSelect = document.getElementById('genManager');
      const pSelect = document.getElementById('genPage');
      const resInput = document.getElementById('genResultUrl');
      if (!bInput || !resInput) return;

      const blogger = (bInput.value || '').trim().replace(/\\s+/g, '_');
      const manager = mSelect ? mSelect.value : 'mpb2';
      const page = pSelect ? pSelect.value : '/influence';
      const origin = window.location.origin;

      if (!blogger) {
        resInput.value = origin + '/r/blogger_name?m=' + manager + '&p=' + page;
      } else {
        resInput.value = origin + '/r/' + encodeURIComponent(blogger) + '?m=' + manager + '&p=' + page;
      }
    }

    function copyGeneratedLink() {
      const resInput = document.getElementById('genResultUrl');
      if (!resInput) return;
      resInput.select();
      navigator.clipboard.writeText(resInput.value);
      const msg = document.getElementById('copySuccessMsg');
      if (msg) {
        msg.classList.remove('hidden');
        setTimeout(() => msg.classList.add('hidden'), 3500);
      }
    }

    // ============================================================
    // ЭКСПОРТ В CSV
    // ============================================================
    function exportCurrentTableCsv() {
      let csv = '';
      const filename = 'janamen_' + currentMainChannel + '.csv';

      if (currentMainChannel === 'organika') {
        csv = 'Канал / Посадочная,utm_source,utm_campaign,utm_content,Кликов,Лидов,CR1,Оплачено,CR2,Выручка (₸),Ср. чек\\n';
        currentChannelData.organikaGroups.forEach(g => {
          const cr1 = g.clicks ? (Math.round(g.leads / g.clicks * 1000) / 10) + '%' : '0%';
          const cr2 = g.leads ? (Math.round(g.won / g.leads * 1000) / 10) + '%' : '0%';
          const avg = g.won ? Math.round(g.rev / g.won) : 0;
          csv += [g.title, g.src, g.cmp, g.cnt, g.clicks, g.leads, cr1, g.won, cr2, g.rev, avg]
            .map(v => '"' + String(v).replace(/"/g, '""') + '"').join(',') + '\\n';
        });
      } else if (currentMainChannel === 'influence') {
        csv = 'Менеджер,Блогер,Кликов,Лидов,CR1,Оплачено,CR2,Выручка (₸),Ср. чек\\n';
        Object.values(currentChannelData.influenceManagers).forEach(m => {
          Object.values(m.bloggers).forEach(b => {
            const cr1 = b.clicks ? (Math.round(b.leads / b.clicks * 1000) / 10) + '%' : '0%';
            const cr2 = b.leads ? (Math.round(b.won / b.leads * 1000) / 10) + '%' : '0%';
            const avg = b.won ? Math.round(b.rev / b.won) : 0;
            csv += [m.name, b.name, b.clicks, b.leads, cr1, b.won, cr2, b.rev, avg]
              .map(v => '"' + String(v).replace(/"/g, '""') + '"').join(',') + '\\n';
          });
        });
      } else {
        csv = 'Посадочная,utm_source,utm_medium,utm_campaign,utm_content,Лидов,Оплачено,Выручка\\n';
        (currentChannelData.allCombos || []).forEach(c => {
          csv += [c.landing || c.path, c.src, c.med, c.cmp, c.cnt, c.leads, c.won, c.rev]
            .map(v => '"' + String(v).replace(/"/g, '""') + '"').join(',') + '\\n';
        });
      }

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    // ============================================================
    // SUPABASE & СИНХРОНИЗАЦИЯ AMOCRM
    // ============================================================
    const SUPABASE_URL = 'https://upeqrwqhdnmccyymugej.supabase.co';
    const SUPABASE_ANON_KEY = 'sb_publishable_bhEfs-Ej7u-1_MAytAp-eg_bvEnTuwi';
    let supabaseClient = null;

    try {
      if (window.supabase) {
        supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
      }
    } catch (e) {
      console.warn('Supabase init err:', e);
    }

    async function loadFreshDealsFromSupabase() {
      if (!supabaseClient) return;
      try {
        const { data, error } = await supabaseClient
          .from('deals')
          .select('id, name, created_at, is_won, price, landing_page, utm_source, utm_medium, utm_campaign, utm_content, utm_term, tags')
          .order('created_at', { ascending: false })
          .limit(1000);

        if (error || !data || !data.length) return;

        let addedCount = 0;
        const existingIds = new Set(ALL_LEADS.map(l => l.id));

        for (const d of data) {
          if (!existingIds.has(d.id)) {
            const ts = d.created_at ? Math.floor(new Date(d.created_at).getTime() / 1000) : 0;
            const dom = (d.landing_page && d.landing_page.includes('health')) ? 'janamenhealth.kz' : 'janamen1.kz';
            ALL_LEADS.unshift({
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
              status_id: d.is_won ? 142 : 0,
              name: d.name || 'Сделка',
              tags: Array.isArray(d.tags) ? d.tags : []
            });
            existingIds.add(d.id);
            addedCount++;
          }
        }

        if (addedCount > 0) {
          onFilterChange();
          const live = document.getElementById('liveStatus');
          if (live) live.innerHTML = `🟢 Supabase Realtime (+${addedCount} новых)`;
        }
      } catch (err) {
        console.warn('Load fresh deals err:', err);
      }
    }

    async function loadClickCounts() {
      try {
        const r = await fetch('/api/clicks-summary');
        const res = await r.json();
        if (res) {
          if (res.byContent) CLICK_COUNTS = res.byContent;
          if (res.byMedium) CLICK_BY_MEDIUM = res.byMedium;
          if (res.byPage) CLICK_BY_PAGE = res.byPage;
          if (res.bySource) CLICK_BY_SOURCE = res.bySource;
          if (res.byCampaign) CLICK_BY_CAMPAIGN = res.byCampaign;
          onFilterChange();
        }
      } catch (e) {
        console.warn('Load clicks summary err:', e);
      }
    }

    function initRealtime() {
      if (!supabaseClient) return;
      supabaseClient
        .channel('public_deals')
        .on('postgres_changes', { event: '*', schema: 'public', table: 'deals' }, payload => {
          const d = payload.new;
          if (!d || !d.id) return;

          const existingIndex = ALL_LEADS.findIndex(l => l.id === d.id);
          const ts = d.created_at ? Math.floor(new Date(d.created_at).getTime() / 1000) : 0;
          const dom = (d.landing_page && d.landing_page.includes('health')) ? 'janamenhealth.kz' : 'janamen1.kz';

          const leadObj = {
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
            status_id: d.is_won ? 142 : 0,
            name: d.name || 'Сделка',
            tags: Array.isArray(d.tags) ? d.tags : []
          };

          if (existingIndex >= 0) {
            ALL_LEADS[existingIndex] = leadObj;
          } else {
            ALL_LEADS.unshift(leadObj);
          }

          onFilterChange();

          const live = document.getElementById('liveStatus');
          if (live) {
            live.className = "hidden sm:inline-flex px-2.5 py-1 text-[11px] font-bold rounded-lg border bg-amber-50 text-amber-800 border-amber-300 animate-pulse";
            live.innerHTML = `⚡ Новый лид: ${d.utm_source || 'direct'} (${d.landing_page || '/'})!`;
            setTimeout(() => {
              live.className = "hidden sm:inline-flex px-2.5 py-1 text-[11px] font-bold rounded-lg border bg-emerald-50 text-emerald-700 border-emerald-200";
              live.innerHTML = `🟢 Supabase Realtime (Живые данные)`;
            }, 6000);
          }
        })
        .subscribe();
    }

    async function syncAmoCRM() {
      const btn = document.getElementById('btnSyncCRM');
      const idle = btn.innerHTML;
      btn.innerHTML = '<span>⏳ Синхронизация...</span>';
      btn.disabled = true;

      try {
        const r = await fetch('/api/sync?limit=200');
        const res = await r.json();
        await loadFreshDealsFromSupabase();
        btn.innerHTML = `<span>✓ Синхронизировано (${res.synced || 0})</span>`;
      } catch (err) {
        await loadFreshDealsFromSupabase();
        btn.innerHTML = '<span>✓ Данные обновлены</span>';
      } finally {
        setTimeout(() => { btn.disabled = false; btn.innerHTML = idle; }, 3000);
      }
    }

    // Инициализация
    onFilterChange();
    loadFreshDealsFromSupabase();
    loadClickCounts();
    initRealtime();
  </script>
</body>
</html>'''

# Заменяем плейсхолдер реальным JSON
final_html = html_template.replace('__LEADS_DICT_JSON__', leads_dict_json)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

with open('gas/Dashboard.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f"Successfully generated index.html ({len(final_html):,} bytes) and gas/Dashboard.html!")
