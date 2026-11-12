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

  <!-- ШАПКА ПОРТАЛА (МИНИМАЛИСТИЧНАЯ ЭКЗЕКЬЮТИВ) -->
  <header class="bg-white border-b border-slate-200/80 sticky top-0 z-40 w-full shadow-2xs">
    <div class="w-full px-4 sm:px-6">
      <div class="flex justify-between items-center h-16">
        
        <!-- ЛОГОТИП И НАЗВАНИЕ -->
        <div class="flex items-center space-x-3">
          <div class="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center text-white font-black text-base shadow-xs tracking-tight">
            JM
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <h1 class="text-base font-extrabold tracking-tight text-slate-900 leading-none">Jana Men</h1>
              <span class="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 rounded-full">Аналитика</span>
            </div>
            <p class="text-[11px] text-slate-500 font-medium">Органика · Influence · Fan-отдел · Clicks & AmoCRM</p>
          </div>
        </div>

        <!-- КНОПКИ ДЕЙСТВИЙ (МИНИМАЛИЗМ) -->
        <div class="flex items-center space-x-2 sm:space-x-2.5">
          <button onclick="openAddBloggerModal()" class="inline-flex items-center space-x-1.5 px-3.5 py-2 text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 rounded-xl transition shadow-2xs cursor-pointer">
            <span>+ Добавить блогера</span>
          </button>

          <!-- АВТОРИЗАЦИЯ & ПРОФИЛЬ -->
          <div id="authWidget" class="flex items-center space-x-1.5 pl-2 border-l border-slate-200">
            <button id="btnUserManage" onclick="openUserManageModal()" class="hidden px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-xl border border-slate-200 transition cursor-pointer" title="Управление доступом сотрудников">
              👥 Доступы
            </button>
            <div id="userProfileBadge" onclick="openAuthModal()" class="cursor-pointer flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200/80 text-xs font-semibold text-slate-800 transition">
              <span>👤</span>
              <span id="userProfileName">Куанышбек</span>
            </div>
            <button id="btnAuthLogout" onclick="handleLogout()" class="text-xs text-slate-400 hover:text-slate-700 px-1 font-bold cursor-pointer" title="Выйти">
              ✕
            </button>
          </div>
        </div>

      </div>
    </div>
  </header>

  <!-- ОСНОВНОЙ КОНТЕНТ (СТРОГО ПО ЗАРИСОВКЕ РУКОВОДИТЕЛЯ) -->
  <main class="flex-1 w-full px-3 sm:px-6 py-4 space-y-3.5">

    <!-- 1. СТРОКА ПЕРИОДА (МИНИМАЛИЗМ: ПЕРИОДЫ ПО МЕСЯЦАМ + ВЫБОР ОТ ДАТЫ И ДО ДАТЫ) -->
    <div class="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-3 flex flex-wrap items-center justify-between gap-3">
      
      <!-- Левый блок: Быстрые пресеты периода -->
      <div class="flex items-center space-x-2 overflow-x-auto text-xs scrollbar-none py-0.5">
        <span class="font-extrabold text-slate-900 uppercase tracking-wider text-xs border-r border-slate-200 pr-3 whitespace-nowrap">Период</span>
        <div class="flex items-center space-x-1">
          <button onclick="setPeriodPreset('all')" id="period-btn-all" class="px-3 py-1.5 rounded-lg text-xs font-bold transition bg-slate-900 text-white shadow-2xs cursor-pointer">
            Весь период
          </button>
          <button onclick="setPeriodPreset('today')" id="period-btn-today" class="px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 transition cursor-pointer">
            Сегодня
          </button>
          <button onclick="setPeriodPreset('yesterday')" id="period-btn-yesterday" class="px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 transition cursor-pointer">
            Вчера
          </button>
          <button onclick="setPeriodPreset('last7')" id="period-btn-last7" class="px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 transition hidden sm:inline-block cursor-pointer">
            7 дней
          </button>
          <button onclick="setPeriodPreset('last30')" id="period-btn-last30" class="px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 transition hidden sm:inline-block cursor-pointer">
            30 дней
          </button>
        </div>

        <!-- Быстрые месяцы + Селектор по месяцам -->
        <div class="flex items-center space-x-1.5 pl-2 border-l border-slate-200">
          <button onclick="selectMonthPreset('2026-11')" id="period-btn-2026-11" class="px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 transition cursor-pointer">
            Ноябрь 2026
          </button>
          <button onclick="selectMonthPreset('2026-10')" id="period-btn-2026-10" class="px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 transition hidden md:inline-block cursor-pointer">
            Октябрь 2026
          </button>
          <select id="monthSelect" onchange="selectMonthPreset(this.value)" class="bg-slate-50 border border-slate-200 rounded-lg px-2 py-1.5 text-xs font-semibold text-slate-700 hover:border-slate-300 focus:outline-none focus:border-slate-900 cursor-pointer">
            <option value="">Другие месяцы...</option>
            <option value="2026-11">Ноябрь 2026</option>
            <option value="2026-10">Октябрь 2026</option>
            <option value="2026-09">Сентябрь 2026</option>
            <option value="2026-08">Август 2026</option>
            <option value="2026-07">Июль 2026</option>
            <option value="2026-06">Июнь 2026</option>
            <option value="2026-05">Май 2026</option>
            <option value="2026-04">Апрель 2026</option>
            <option value="2026-03">Март 2026</option>
            <option value="2026-02">Февраль 2026</option>
          </select>
        </div>
      </div>

      <!-- Правый блок: Выбор от даты и до даты + Поиск -->
      <div class="flex items-center space-x-2 flex-wrap">
        
        <!-- Функция выбора от даты и до даты (всегда на виду) -->
        <div class="flex items-center space-x-1.5 text-xs text-slate-500 font-medium bg-slate-50 px-2.5 py-1 rounded-xl border border-slate-200">
          <span class="text-slate-400">с</span>
          <input type="date" id="dateInputFrom" onchange="applyCustomDateRange()" class="bg-white border border-slate-200 rounded px-1.5 py-0.5 text-xs font-semibold text-slate-800 focus:outline-none focus:border-slate-900 cursor-pointer">
          <span class="text-slate-400">по</span>
          <input type="date" id="dateInputTo" onchange="applyCustomDateRange()" class="bg-white border border-slate-200 rounded px-1.5 py-0.5 text-xs font-semibold text-slate-800 focus:outline-none focus:border-slate-900 cursor-pointer">
          <button onclick="resetAllFilters()" title="Сбросить даты" class="text-slate-400 hover:text-slate-700 font-bold px-1 transition cursor-pointer">✕</button>
        </div>

        <!-- Поиск -->
        <div class="relative">
          <input type="text" id="filterSearchInput" oninput="onFilterChange()" placeholder="🔍 Поиск..." class="pl-3 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700 focus:bg-white focus:outline-none focus:border-slate-900 w-36 sm:w-48">
        </div>
      </div>
    </div>

    <!-- 2. БЛОК ОСНОВНЫХ ЦИФР (5 МИНИМАЛИСТИЧНЫХ БЕЛЫХ КАРТОЧЕК В ОДИН РЯД) -->
    <div id="kpiStandardGrid" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      
      <!-- 1. Всего заявок -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-col justify-between hover:border-slate-300 transition">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Всего заявок</span>
          <span id="kpiScopeBadge" class="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">Органика</span>
        </div>
        <div id="kpiTotalLeads" class="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-1.5 leading-none tracking-tight">—</div>
        <div class="text-xs text-slate-500 mt-2 flex items-center justify-between">
          <span id="kpiLeadsPeriod">за выбранный период</span>
          <span id="kpiClicksInline" class="font-medium text-slate-600">0 переходов</span>
        </div>
      </div>

      <!-- 2. Оплачено / CR % -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-col justify-between hover:border-slate-300 transition">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Оплачено</span>
          <span class="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">Статус 142</span>
        </div>
        <div id="kpiWonLeads" class="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-1.5 leading-none tracking-tight">—</div>
        <div id="kpiCr2" class="text-xs font-semibold text-slate-700 mt-2">CR: 0% (Лид ➔ Оплата)</div>
      </div>

      <!-- 3. Выручка -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-col justify-between hover:border-slate-300 transition">
        <div class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Выручка</div>
        <div id="kpiRevenue" class="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-1.5 leading-none tracking-tight whitespace-nowrap">—</div>
        <div id="kpiAvgCheck" class="text-xs font-medium text-slate-500 mt-2">Ср. чек: —</div>
      </div>

      <!-- 4. Расходы -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-col justify-between hover:border-slate-300 transition">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider" id="kpiExpenseLabel">Расходы</span>
        </div>
        <div id="kpiExpenses" class="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-1.5 leading-none tracking-tight whitespace-nowrap">0 ₸</div>
        <div id="kpiExpensesSub" class="text-xs text-slate-500 mt-2 truncate">затраты канала</div>
      </div>

      <!-- 5. Окупаемость -->
      <div class="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-2xs flex flex-col justify-between hover:border-slate-300 transition">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Окупаемость</span>
          <span id="kpiRomiBadge" class="text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/60">ROMI</span>
        </div>
        <div id="kpiRomi" class="text-2xl sm:text-3xl font-extrabold text-emerald-600 mt-1.5 leading-none tracking-tight whitespace-nowrap">—</div>
        <div id="kpiRomiSub" class="text-xs font-medium text-slate-500 mt-2 truncate">возврат инвестиций</div>
      </div>

    </div>

    <!-- Совместимость для скриптов -->
    <div class="hidden">
      <span id="kpiClicks">0</span>
      <span id="kpiCr1">CR1: —</span>
      <div id="kpiFanGrid"></div>
      <span id="fanKpiLeads">0</span>
      <span id="fanKpiClicks">0</span>
      <span id="fanKpiCr1">0%</span>
      <span id="fanKpiWon">0</span>
      <span id="fanKpiCr2">0%</span>
      <span id="fanKpiRevenue">0 ₸</span>
      <span id="fanKpiAvgCheck">Ср. чек: 0 ₸</span>
      <span id="activeFilterBadge">Весь период</span>
      <span id="toggleFilterText">Фильтры</span>
      <div id="filtersBody"></div>
    </div>

    <!-- 3. БЛОК: ВЫПОЛНЕНИЕ ПЛАНА (ТОЧНО ПО ЗАРИСОВКЕ: План, Факт, шкала Точка А ➔ Точка Б) -->
    <div class="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-4 sm:p-5">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100">
        <div class="flex items-center space-x-2 sm:space-x-3">
          <span class="text-sm font-extrabold text-slate-900 uppercase tracking-tight">Выполнение плана</span>
          <span class="text-slate-300 font-light text-base">|</span>
          <span id="planPercentBadge" class="px-2.5 py-0.5 text-xs font-bold rounded-full bg-slate-100 text-slate-800">
            0% выполнено
          </span>
        </div>
        <button onclick="openEditPlanModal()" class="px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-xl border border-slate-200 transition shadow-2xs flex items-center space-x-1.5 cursor-pointer">
          <span>✏️ Изменить план</span>
        </button>
      </div>

      <!-- Графические полосы План vs Факт -->
      <div class="mt-4 space-y-3.5">
        <!-- Полоса ПЛАН -->
        <div>
          <div class="flex items-center justify-between text-xs font-semibold text-slate-500 mb-1">
            <span class="flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-slate-400"></span>
              <span>План (Цель):</span>
            </span>
            <span id="planTargetDisplay" class="font-extrabold text-slate-800 text-sm">50 000 000 ₸</span>
          </div>
          <div class="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
            <div class="h-full bg-slate-300 rounded-full w-full"></div>
          </div>
        </div>

        <!-- Полоса ФАКТ -->
        <div>
          <div class="flex items-center justify-between text-xs font-semibold mb-1">
            <span class="flex items-center space-x-1.5 text-slate-800">
              <span class="w-2 h-2 rounded-full bg-slate-900"></span>
              <span>Факт (Выручка за период):</span>
            </span>
            <div class="flex items-center space-x-2">
              <span id="planFactDisplay" class="font-extrabold text-slate-900 text-sm">0 ₸</span>
              <span id="planFactPercent" class="text-xs font-bold text-slate-600">(0%)</span>
            </div>
          </div>
          <div class="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
            <div id="planFactBar" class="h-full bg-slate-900 rounded-full transition-all duration-500" style="width: 0%;"></div>
          </div>
        </div>

        <!-- Шкала от Точки А к Точке Б -->
        <div class="pt-2">
          <div class="relative w-full">
            <div class="h-1 bg-slate-200 w-full relative flex items-center justify-between rounded-full">
              <div class="w-1.5 h-1.5 bg-slate-600 rounded-full"></div>
              <div class="w-1 h-1 bg-slate-300 rounded-full"></div>
              <div class="w-1 h-1 bg-slate-300 rounded-full"></div>
              <div class="w-1 h-1 bg-slate-400 rounded-full"></div>
              <div class="w-1 h-1 bg-slate-300 rounded-full"></div>
              <div class="w-1 h-1 bg-slate-300 rounded-full"></div>
              <div class="w-1.5 h-1.5 bg-slate-600 rounded-full"></div>
            </div>

            <!-- Подписи Точка А и Точка Б -->
            <div class="flex items-center justify-between text-xs font-medium text-slate-600 mt-2.5">
              <div class="flex flex-col">
                <span class="text-[10px] text-slate-400 uppercase font-bold">Точка А (Старт)</span>
                <span class="font-extrabold text-slate-800 text-xs sm:text-sm">0 ₸</span>
              </div>
              <div id="planRemainingDisplay" class="text-center text-xs text-slate-500">
                Осталось до цели: <span class="font-bold text-slate-900" id="planRemainingVal">—</span>
              </div>
              <div class="flex flex-col items-end">
                <span class="text-[10px] text-slate-400 uppercase font-bold">Точка Б (Цель)</span>
                <span class="font-extrabold text-slate-900 text-xs sm:text-sm" id="planTargetVal">50 000 000 ₸</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 4. ТАБЫ ВЫБОРА КАНАЛОВ (МИНИМАЛИСТИЧНЫЙ SEGMENTED CONTROL НАД ТАБЛИЦЕЙ) -->
    <div class="bg-white rounded-2xl border border-slate-200/90 shadow-2xs p-1.5">
      <div class="bg-slate-100 p-1 rounded-xl flex items-center gap-1 overflow-x-auto scrollbar-none">
        
        <!-- РАЗДЕЛ 1: ОРГАНИКА -->
        <button onclick="switchMainChannel('organika')" id="main-tab-organika" class="px-3.5 py-2 rounded-lg bg-white text-slate-900 font-bold text-xs sm:text-sm flex items-center space-x-2 transition shadow-2xs whitespace-nowrap cursor-pointer">
          <span>🌿 Органика</span>
          <span id="tabBadgeOrganika" class="px-2 py-0.5 text-[10px] bg-slate-900 text-white rounded-full font-bold">18.4k</span>
        </button>

        <!-- РАЗДЕЛ 2: ИНФЛЮЕНС -->
        <button onclick="switchMainChannel('influence')" id="main-tab-influence" class="px-3.5 py-2 rounded-lg text-slate-600 hover:text-slate-900 font-semibold text-xs sm:text-sm flex items-center space-x-2 transition whitespace-nowrap cursor-pointer">
          <span>🌟 Инфлюенс</span>
          <span id="tabBadgeInfluence" class="px-2 py-0.5 text-[10px] bg-slate-200 text-slate-700 rounded-full font-semibold">4 мен.</span>
        </button>

        <!-- РАЗДЕЛ 3: ФАН -->
        <button onclick="switchMainChannel('fan')" id="main-tab-fan" class="px-3.5 py-2 rounded-lg text-slate-600 hover:text-slate-900 font-semibold text-xs sm:text-sm flex items-center space-x-2 transition whitespace-nowrap cursor-pointer">
          <span>🎬 Фан-отдел</span>
          <span id="tabBadgeFan" class="px-2 py-0.5 text-[10px] bg-slate-200 text-slate-700 rounded-full font-semibold">8 акк.</span>
        </button>

        <!-- ВСЕ КАНАЛЫ (СВОДКА) -->
        <button onclick="switchMainChannel('all')" id="main-tab-all" class="px-3.5 py-2 rounded-lg text-slate-600 hover:text-slate-900 font-semibold text-xs sm:text-sm flex items-center space-x-1.5 transition whitespace-nowrap ml-auto cursor-pointer">
          <span>📊 Все каналы</span>
        </button>

        <!-- ТЕГИ AMOCRM -->
        <button onclick="switchMainChannel('tags')" id="main-tab-tags" class="px-3 py-2 rounded-lg text-slate-600 hover:text-slate-900 font-semibold text-xs sm:text-sm flex items-center space-x-1.5 transition whitespace-nowrap cursor-pointer">
          <span>🏷️ Теги CRM</span>
        </button>

      </div>
    </div>

    <!-- 3. ГЛАВНАЯ ИНТЕРАКТИВНАЯ ТАБЛИЦА -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden space-y-0">
      
      <!-- ШАПКА ТАБЛИЦЫ: ЗАГОЛОВОК + ПОДЗАГОЛОВОК + ЭКСПОРТ -->
      <div class="p-4 sm:p-5 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div class="flex items-center space-x-2">
            <h2 id="tableMainTitle" class="text-base sm:text-lg font-black text-slate-900 tracking-tight">🌿 Органика: SMM (janamen1.kz/smm) & WhatsApp 9828</h2>
            <span id="tableBadgeTitle" class="px-2 py-0.5 text-[10px] font-black uppercase rounded bg-emerald-100 text-emerald-800">Канал 1</span>
          </div>
          <p id="tableMainSubtitle" class="text-xs text-slate-500 mt-0.5">6 официальных точек входа (шапка Instagram, YouTube, чат-бот Direct, Threads, TikTok и WhatsApp 9828)</p>
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

    <!-- 0. МОДАЛЬНОЕ ОКНО: ИЗМЕНИТЬ ПЛАН ВЫРУЧКИ (ТОЧКА Б) -->
    <div id="editPlanModal" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <h3 class="text-sm font-black text-slate-900 flex items-center space-x-2">
            <span>🎯</span>
            <span>Установить план по выручке (Точка Б)</span>
          </h3>
          <button onclick="closeEditPlanModal()" class="text-slate-400 hover:text-slate-600 font-bold text-sm cursor-pointer">✕</button>
        </div>
        <form onsubmit="event.preventDefault(); savePlanTarget();" class="p-6 space-y-4 text-xs font-semibold text-slate-700">
          <div>
            <label class="block text-[11px] uppercase tracking-wider text-slate-500 font-bold mb-1">Целевая выручка (₸):</label>
            <input type="number" id="inputPlanTarget" min="100000" step="500000" required class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-base font-black text-brand-700 focus:bg-white focus:outline-none focus:border-brand-500">
            <p class="text-[10px] text-slate-400 mt-1">Целевой ориентир для шкалы «Точка А ➔ Точка Б»</p>
          </div>

          <div class="grid grid-cols-3 gap-2 pt-1">
            <button type="button" onclick="setQuickPlan(30000000)" class="py-1.5 px-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-bold transition cursor-pointer">30 млн ₸</button>
            <button type="button" onclick="setQuickPlan(50000000)" class="py-1.5 px-2 bg-blue-50 hover:bg-blue-100 text-brand-800 rounded-lg text-xs font-bold transition border border-blue-200 cursor-pointer">50 млн ₸</button>
            <button type="button" onclick="setQuickPlan(100000000)" class="py-1.5 px-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-bold transition cursor-pointer">100 млн ₸</button>
          </div>

          <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
            <button type="button" onclick="closeEditPlanModal()" class="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl transition cursor-pointer">
              Отмена
            </button>
            <button type="submit" class="px-5 py-2 text-xs font-black text-white bg-brand-600 hover:bg-brand-700 rounded-xl transition shadow-md shadow-brand-500/20 cursor-pointer">
              ✓ Сохранить план
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 1. МОДАЛЬНОЕ ОКНО: ДОБАВИТЬ БЛОГЕРА & УСЛОВИЯ (ГОНОРАР, ДОСТАВКА, ВИТАМИНЫ) -->
      <!-- МОДАЛЬНОЕ ОКНО НАСТРОЙКИ ЗАРПЛАТ FAN-ОТДЕЛА -->
  <div id="editFanSalariesModal" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-3 sm:p-4">
    <div class="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-md w-full p-5 space-y-4">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h3 class="text-base font-extrabold text-slate-900">Зарплаты Fan-отдела</h3>
          <p class="text-xs text-slate-500 mt-0.5">Оклады сотрудников для точного расчёта окупаемости (ROMI)</p>
        </div>
        <button onclick="closeFanSalariesModal()" class="text-slate-400 hover:text-slate-700 text-lg font-bold p-1 cursor-pointer">✕</button>
      </div>

      <!-- Быстрая ставка всем -->
      <div class="bg-slate-50 p-3 rounded-xl border border-slate-200 flex items-center justify-between gap-2">
        <span class="text-xs font-semibold text-slate-700">Всем одинаково:</span>
        <div class="flex items-center space-x-1.5">
          <input type="number" id="inputFlatFanSalary" placeholder="150000" class="w-24 px-2 py-1 text-xs bg-white border border-slate-200 rounded-lg font-bold text-slate-800 focus:outline-none focus:border-slate-900">
          <span class="text-xs text-slate-500 font-bold">₸</span>
          <button onclick="applyFlatFanSalary()" class="px-2.5 py-1 text-xs font-bold bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition cursor-pointer">OK</button>
        </div>
      </div>

      <!-- Список сотрудников -->
      <div id="fanSalariesListContainer" class="max-h-60 overflow-y-auto space-y-2 pr-1 text-xs scrollbar-thin">
        <!-- Заполняется JS -->
      </div>

      <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
        <div class="text-xs text-slate-600">
          ФОТ в месяц: <span id="fanTotalSalaryPreview" class="font-extrabold text-slate-900 text-sm">0 ₸</span>
        </div>
        <div class="flex items-center space-x-2">
          <button onclick="closeFanSalariesModal()" class="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition cursor-pointer">Отмена</button>
          <button onclick="saveFanSalaries()" class="px-4 py-1.5 text-xs font-bold bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition shadow-xs cursor-pointer">Сохранить</button>
        </div>
      </div>
    </div>
  </div>

  <div id="addBloggerModal" class="hidden fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-xl w-full p-6 sm:p-7 shadow-2xl border border-slate-200 space-y-4">
        
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center space-x-2.5">
            <div class="w-9 h-9 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center text-lg font-black">🌟</div>
            <div>
              <h3 class="text-base font-black text-slate-900 leading-tight">Добавить блогера в Инфлюенс</h3>
              <p class="text-[11px] text-slate-400">Условия сотрудничества, отправленные витамины и авто-генерация UTM</p>
            </div>
          </div>
          <button onclick="closeAddBloggerModal()" class="text-slate-400 hover:text-slate-700 p-1 text-xl font-bold">✕</button>
        </div>

        <form onsubmit="event.preventDefault(); saveNewBlogger();" class="space-y-4 text-xs font-semibold text-slate-700">
          
          <!-- Менеджер & Instagram Handle -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-[11px] uppercase tracking-wider text-slate-500 font-bold mb-1">Менеджер (МПБ):</label>
              <select id="bloggerManager" onchange="updateBloggerUtmPreview()" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 font-bold text-slate-900">
                <option value="mpb1">Анельжан (mpb1)</option>
                <option value="mpb2">Алина (mpb2)</option>
                <option value="mpb3">Алуа (mpb3)</option>
                <option value="mpb4">Дарина (mpb4)</option>
              </select>
            </div>
            <div>
              <label class="block text-[11px] uppercase tracking-wider text-slate-500 font-bold mb-1">Instagram (@handle):</label>
              <input type="text" id="bloggerHandle" required oninput="updateBloggerUtmPreview()" placeholder="например: aishka_karimova" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 font-bold text-slate-900 font-mono">
            </div>
          </div>

          <!-- Имя блогера & Подписчики / Город -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="sm:col-span-1">
              <label class="block text-[11px] uppercase tracking-wider text-slate-500 font-bold mb-1">Имя / Псевдоним:</label>
              <input type="text" id="bloggerName" placeholder="Айша Каримова" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 font-bold text-slate-900">
            </div>
            <div>
              <label class="block text-[11px] uppercase tracking-wider text-slate-500 font-bold mb-1">Подписчиков:</label>
              <input type="text" id="bloggerSubs" placeholder="например: 45 тыс" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 text-slate-900">
            </div>
            <div>
              <label class="block text-[11px] uppercase tracking-wider text-slate-500 font-bold mb-1">Город:</label>
              <input type="text" id="bloggerCity" placeholder="Алматы" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-purple-500 text-slate-900">
            </div>
          </div>

          <!-- БЛОК РАСХОДОВ И ВИТАМИНОВ -->
          <div class="bg-purple-50/50 p-3.5 rounded-2xl border border-purple-100 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-black uppercase text-purple-900 tracking-wider">Условия: Оплата и отправленные витамины</span>
              <span class="text-[10px] text-purple-600 font-medium">учет себестоимости и доставки</span>
            </div>

            <!-- Деньги и Доставка -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] uppercase font-bold text-slate-600 mb-1">💵 Оплата деньгами (гонорар, ₸):</label>
                <input type="number" id="bloggerPaidCash" min="0" step="1000" placeholder="0" oninput="updateModalCalculatedCost()" class="w-full px-3 py-2 bg-white border border-purple-200 rounded-xl focus:outline-none focus:border-purple-500 font-bold text-slate-900">
              </div>
              <div>
                <label class="block text-[10px] uppercase font-bold text-slate-600 mb-1">🚚 Оплата за доставку (₸):</label>
                <input type="number" id="bloggerDeliveryCost" min="0" step="100" placeholder="0" oninput="updateModalCalculatedCost()" class="w-full px-3 py-2 bg-white border border-purple-200 rounded-xl focus:outline-none focus:border-purple-500 font-bold text-slate-900">
              </div>
            </div>

            <!-- Витамины (4 вида продукции) с фиксированными ценами: 62k / 72k -->
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <label class="block text-[10px] uppercase font-bold text-slate-600">🎁 Отправлено витаминов блогеру (кол-во, шт.):</label>
                <span class="text-[10px] text-purple-700 font-bold">Витамины по 62 000 ₸ · Аодзиру 72 000 ₸</span>
              </div>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <div class="bg-white p-2.5 rounded-xl border border-purple-100 text-center shadow-xs">
                  <div class="text-[10px] font-bold text-slate-700 leading-tight">Мужской</div>
                  <div class="text-[9px] text-purple-700 font-extrabold">62 000 ₸</div>
                  <input type="number" id="barterMan" min="0" max="20" value="0" oninput="updateModalCalculatedCost()" class="w-full text-center mt-1 font-black text-slate-900 border border-slate-200 rounded-lg py-1 text-sm focus:border-purple-500 focus:outline-none">
                </div>
                <div class="bg-white p-2.5 rounded-xl border border-purple-100 text-center shadow-xs">
                  <div class="text-[10px] font-bold text-slate-700 leading-tight">Женский</div>
                  <div class="text-[9px] text-purple-700 font-extrabold">62 000 ₸</div>
                  <input type="number" id="barterWoman" min="0" max="20" value="0" oninput="updateModalCalculatedCost()" class="w-full text-center mt-1 font-black text-slate-900 border border-slate-200 rounded-lg py-1 text-sm focus:border-purple-500 focus:outline-none">
                </div>
                <div class="bg-white p-2.5 rounded-xl border border-purple-100 text-center shadow-xs">
                  <div class="text-[10px] font-bold text-slate-700 leading-tight">Омега-3</div>
                  <div class="text-[9px] text-purple-700 font-extrabold">62 000 ₸</div>
                  <input type="number" id="barterOmega" min="0" max="20" value="0" oninput="updateModalCalculatedCost()" class="w-full text-center mt-1 font-black text-slate-900 border border-slate-200 rounded-lg py-1 text-sm focus:border-purple-500 focus:outline-none">
                </div>
                <div class="bg-white p-2.5 rounded-xl border border-purple-100 text-center shadow-xs">
                  <div class="text-[10px] font-bold text-slate-700 leading-tight">Аодзиру</div>
                  <div class="text-[9px] text-emerald-700 font-extrabold">72 000 ₸</div>
                  <input type="number" id="barterAojiru" min="0" max="20" value="0" oninput="updateModalCalculatedCost()" class="w-full text-center mt-1 font-black text-slate-900 border border-slate-200 rounded-lg py-1 text-sm focus:border-purple-500 focus:outline-none">
                </div>
              </div>
            </div>

            <!-- Итоговая расчетная себестоимость блогера -->
            <div class="mt-2 pt-2 border-t border-purple-200/60 flex items-center justify-between text-xs">
              <span class="text-slate-600 font-bold">Итого себестоимость условий:</span>
              <span id="modalTotalCalculatedCost" class="font-black text-rose-700 text-sm">0 ₸</span>
            </div>
          </div>

          <!-- Автоматическая трекинг-ссылка -->
          <div>
            <label class="block text-[11px] uppercase tracking-wider text-purple-800 font-bold mb-1">Персональная трекинг-ссылка:</label>
            <div class="relative">
              <input type="text" id="bloggerPreviewUrl" readonly class="w-full pl-3 pr-24 py-2.5 bg-slate-100 border border-slate-200 rounded-xl text-xs font-mono font-bold text-purple-950 select-all">
              <button type="button" onclick="copyBloggerPreviewUrl()" class="absolute right-1 top-1 bottom-1 px-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-xs font-bold transition">
                Копировать
              </button>
            </div>
          </div>

          <!-- Кнопки действий -->
          <div class="flex items-center justify-between pt-2 border-t border-slate-100">
            <div>
              <button type="button" id="btnDeleteBloggerModal" onclick="deleteCurrentBloggerFromModal()" class="hidden px-3.5 py-2 text-xs font-bold text-rose-600 hover:bg-rose-50 rounded-xl border border-rose-200 transition">
                🗑️ Удалить запись
              </button>
            </div>
            <div class="flex items-center space-x-2">
              <button type="button" onclick="closeAddBloggerModal()" class="px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl transition">
                Отмена
              </button>
              <button type="submit" id="btnSaveBlogger" class="px-5 py-2.5 text-xs font-black text-white bg-purple-600 hover:bg-purple-700 rounded-xl transition shadow-md shadow-purple-500/20">
                ✓ Сохранить блогера в базу
              </button>
            </div>
          </div>
        </form>

      </div>
    </div>

    <!-- 2. МОДАЛЬНОЕ ОКНО: ВХОД И РЕГИСТРАЦИЯ -->
    <div id="authModal" class="hidden fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 sm:p-7 shadow-2xl border border-slate-200 space-y-4">
        
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center space-x-2.5">
            <div class="w-9 h-9 rounded-xl bg-brand-100 text-brand-700 flex items-center justify-center text-lg font-black">🔐</div>
            <div>
              <h3 class="text-base font-black text-slate-900 leading-tight" id="authModalTitle">Вход в Аналитику Jana Men</h3>
              <p class="text-[11px] text-slate-400">Доступ к сквозным метрикам и отчетам</p>
            </div>
          </div>
          <button onclick="closeAuthModal()" class="text-slate-400 hover:text-slate-700 p-1 text-xl font-bold">✕</button>
        </div>

        <!-- Переключатель Вход / Регистрация -->
        <div class="flex rounded-xl bg-slate-100 p-1 text-xs font-bold">
          <button type="button" onclick="switchAuthTab('login')" id="tabAuthLogin" class="flex-1 py-1.5 rounded-lg bg-white shadow-sm text-slate-900">Вход</button>
          <button type="button" onclick="switchAuthTab('register')" id="tabAuthRegister" class="flex-1 py-1.5 rounded-lg text-slate-500 hover:text-slate-900">Регистрация</button>
        </div>

        <!-- Быстрый выбор роли для входа -->
        <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-xs">
          <div class="text-[10px] font-black uppercase text-slate-400 mb-1.5">Быстрый тестовый вход под ролью:</div>
          <div class="grid grid-cols-2 gap-1.5 text-[11px]">
            <button type="button" onclick="quickLoginRole('admin')" class="p-1.5 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 rounded-lg font-bold text-left">👑 Куанышбек (Владелец)</button>
            <button type="button" onclick="quickLoginRole('rom')" class="p-1.5 bg-blue-50 hover:bg-blue-100 text-blue-900 border border-blue-200 rounded-lg font-bold text-left">💼 РОМ (Маркетинг)</button>
            <button type="button" onclick="quickLoginRole('crm')" class="p-1.5 bg-slate-100 hover:bg-slate-200 text-slate-900 border border-slate-200 rounded-lg font-bold text-left">⚙️ CRM-интегратор</button>
            <button type="button" onclick="quickLoginRole('anelzhan')" class="p-1.5 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 rounded-lg font-bold text-left">🌟 Анельжан (mpb1)</button>
            <button type="button" onclick="quickLoginRole('alina')" class="p-1.5 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 rounded-lg font-bold text-left">🌟 Алина (mpb2)</button>
            <button type="button" onclick="quickLoginRole('alua')" class="p-1.5 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 rounded-lg font-bold text-left">🌟 Алуа (mpb3)</button>
          </div>
        </div>

        <form id="authForm" onsubmit="event.preventDefault(); submitAuthForm();" class="space-y-3 text-xs font-semibold text-slate-700">
          <div id="authNameField" class="hidden">
            <label class="block text-[11px] uppercase tracking-wider text-slate-500 font-bold mb-1">Ваше имя и фамилия:</label>
            <input type="text" id="authName" placeholder="например: Анельжан" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-bold text-slate-900">
          </div>

          <div>
            <label class="block text-[11px] uppercase tracking-wider text-slate-500 font-bold mb-1">Email / Логин:</label>
            <input type="text" id="authEmail" required placeholder="k.saidullayev@janamen.kz" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-bold text-slate-900">
          </div>

          <div>
            <label class="block text-[11px] uppercase tracking-wider text-slate-500 font-bold mb-1">Пароль:</label>
            <input type="password" id="authPassword" required placeholder="••••••••" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-bold text-slate-900">
          </div>

          <div id="authRoleField" class="hidden">
            <label class="block text-[11px] uppercase tracking-wider text-slate-500 font-bold mb-1">Отдел / Направление:</label>
            <select id="authRole" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:border-brand-500 font-bold text-slate-900">
              <option value="head_marketing">Руководитель отдела маркетинга (РОМ)</option>
              <option value="crm_integrator">CRM-интегратор</option>
              <option value="manager_mpb1">Менеджер: Анельжан (mpb1)</option>
              <option value="manager_mpb2">Менеджер: Алина (mpb2)</option>
              <option value="manager_mpb3">Менеджер: Алуа (mpb3)</option>
              <option value="manager_mpb4">Менеджер: Дарина (mpb4)</option>
              <option value="fan">Фан-аккаунты сетки</option>
            </select>
          </div>

          <div id="authFeedback" class="hidden text-xs p-2.5 rounded-xl font-medium"></div>

          <button type="submit" id="btnAuthSubmit" class="w-full py-2.5 mt-2 text-xs font-black text-white bg-brand-600 hover:bg-brand-700 rounded-xl transition shadow-md shadow-brand-500/20">
            Войти в систему
          </button>
        </form>

      </div>
    </div>

    <!-- 3. МОДАЛЬНОЕ ОКНО: УПРАВЛЕНИЕ ДОСТУПАМИ (ТОЛЬКО ДЛЯ SUPERADMIN) -->
    <div id="userManageModal" class="hidden fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-7 shadow-2xl border border-slate-200 space-y-4">
        
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center space-x-2.5">
            <div class="w-9 h-9 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center text-lg font-black">👥</div>
            <div>
              <h3 class="text-base font-black text-slate-900 leading-tight">Управление доступом сотрудников</h3>
              <p class="text-[11px] text-slate-400">Главный аккаунт: выдача прав, одобрение регистрации и блокировка</p>
            </div>
          </div>
          <button onclick="closeUserManageModal()" class="text-slate-400 hover:text-slate-700 p-1 text-xl font-bold">✕</button>
        </div>

        <!-- Кнопка быстрого добавления пользователя -->
        <div class="bg-slate-50 p-3.5 rounded-2xl border border-slate-200 space-y-2">
          <div class="text-[11px] font-black uppercase text-slate-600">Быстро создать доступ для сотрудника:</div>
          <div class="grid grid-cols-1 sm:grid-cols-4 gap-2">
            <input type="text" id="newUserName" placeholder="Имя" class="px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-bold text-slate-900">
            <input type="text" id="newUserEmail" placeholder="Email / логин" class="px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-bold text-slate-900">
            <input type="text" id="newUserPassword" placeholder="Пароль" class="px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-bold text-slate-900">
            <button onclick="createUserByAdmin()" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-black transition">
              + Выдать доступ
            </button>
          </div>
        </div>

        <!-- Таблица пользователей -->
        <div class="overflow-x-auto max-h-72 overflow-y-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-[10px] uppercase font-bold text-slate-400 border-b border-slate-100">
              <tr>
                <th class="py-2 px-3">Сотрудник</th>
                <th class="py-2 px-3">Email</th>
                <th class="py-2 px-3 text-center">Роль</th>
                <th class="py-2 px-3 text-center">Статус</th>
                <th class="py-2 px-3 text-right">Действия</th>
              </tr>
            </thead>
            <tbody id="userManageTableBody" class="divide-y divide-slate-100">
              <!-- Заполняется динамически -->
            </tbody>
          </table>
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

    // Полный реестр 93 блогеров из таблицы UGC Google Sheets
    const INFLUENCE_REGISTRY = [{"h": "frolova__kristina", "m": "mpb2", "mgr": "Алина", "n": "Левчук Кристина", "s": "4 582", "c": "Караганда", "p": "https://instagram.com/frolova__kristina?exln=Mnd0OTJlYXBpNXBj", "u": "https://janamen1.kz/influence?utm_source=frolova__kristina&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "asema_kotoraya_alel", "m": "mpb2", "mgr": "Алина", "n": "Акишева Асем", "s": "30,3 тыс", "c": "Караганда", "p": "https://instagram.com/asema_kotoraya_alel?obrf=MThhNWRkcWxnN2FjeQ%3D%3D", "u": "https://janamen1.kz/influence?utm_source=asema_kotoraya_alel&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "akhmoldinaa", "m": "mpb2", "mgr": "Алина", "n": "Ахмолдина Жансая", "s": "14,1 тыс", "c": "Караганда", "p": "https://instagram.com/akhmoldinaa?cplk=c2w2eWowZG5qY2ll", "u": "https://janamen1.kz/influence?utm_source=akhmoldinaa&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "ramazankyzy_dana", "m": "mpb2", "mgr": "Алина", "n": "Жагпарова Данагуль", "s": "12,9 тыс", "c": "Астана", "p": "https://instagram.com/ramazankyzy_dana?exln=eDJqM2NpNGI1d21z", "u": "https://janamen1.kz/influence?utm_source=ramazankyzy_dana&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "meruna_ll", "m": "mpb2", "mgr": "Алина", "n": "Меруна", "s": "17,7 тыс", "c": "Астана", "p": "https://www.instagram.com/meruna_ll?mdxt=MTAwZTVvdnR5ZTdlOQ==", "u": "https://janamen1.kz/influence?utm_source=meruna_ll&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "habataev.maksat", "m": "mpb2", "mgr": "Алина", "n": "Хабатаев Максат", "s": "75,7 тыс", "c": "Астана", "p": "https://www.instagram.com/habataev.maksat?cplk=MWFhZjk2aXFzN2dldg==", "u": "https://janamen1.kz/influence?utm_source=habataev.maksat&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "kazhmuratova_asiya", "m": "mpb2", "mgr": "Алина", "n": "Кажмуратова Асия", "s": "17,2 тыс", "c": "Щучинск", "p": "https://www.instagram.com/kazhmuratova_asiya?vrfl=NzdmdnJmcnhyZmRo&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=kazhmuratova_asiya&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "lukmanovna__", "m": "mpb2", "mgr": "Алина", "n": "Сагындык Онал", "s": "6 647", "c": "Караганда", "p": "https://www.instagram.com/lukmanovna__?cplk=dm5tM3hrbTc5emN0", "u": "https://janamen1.kz/influence?utm_source=lukmanovna__&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "bekzat_tunggysh", "m": "mpb2", "mgr": "Алина", "n": "Тунгышбаева Бекзат", "s": "8 217", "c": "Астана", "p": "https://www.instagram.com/bekzat_tunggysh?obrf=MXEyMTRqZmRkbXY2cQ%3D%3D&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=bekzat_tunggysh&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "zhuldyz_zaynulina", "m": "mpb2", "mgr": "Алина", "n": "Зайнулина Жулдыз", "s": "6 398", "c": "Актобе", "p": "https://www.instagram.com/zhuldyz_zaynulina?xtok=MTZ4Y3BmemlnMzQ2eg%3D%3D&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=zhuldyz_zaynulina&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "dinarakaltore", "m": "mpb2", "mgr": "Алина", "n": "Калторе Динара", "s": "38,4 тыс", "c": "Шымкент", "p": "https://www.instagram.com/dinarakaltore?rpxt=NGx2Y200YTRwendp&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=dinarakaltore&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "bika_mazhenova", "m": "mpb2", "mgr": "Алина", "n": "Маженова Бика", "s": "45,6 тыс", "c": "Астана", "p": "https://www.instagram.com/bika_mazhenova?xtok=YTBlYXgya3V6Mm5z", "u": "https://janamen1.kz/influence?utm_source=bika_mazhenova&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=stories"}, {"h": "orunkeeva_kz", "m": "mpb2", "mgr": "Алина", "n": "Нурмыханбет Гульсанат", "s": "21,9 тыс", "c": "Балхаш", "p": "https://www.instagram.com/orunkeeva_kz?vrfl=MTU5eXNxc2hsNmpvcg==", "u": "https://janamen1.kz/influence?utm_source=orunkeeva_kz&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "karima_turs", "m": "mpb2", "mgr": "Алина", "n": "Турсунханова Карима", "s": "40,8 тыс", "c": "Астана", "p": "https://www.instagram.com/karima_turs?srtk=NnZ4cmc0MHVwcXN0&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=karima_turs&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "kuzenbaikyzy___", "m": "mpb2", "mgr": "Алина", "n": "Шерехан Жания", "s": "7 339", "c": "Алматы", "p": "https://www.instagram.com/kuzenbaikyzy___?igsh=dzN5bWpncDF6c3Jr", "u": "https://janamen1.kz/influence?utm_source=kuzenbaikyzy___&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aknur_me", "m": "mpb2", "mgr": "Алина", "n": "Шынболатова Акнур", "s": "37,2 тыс", "c": "Шымкент", "p": "https://instagram.com/aknur_me", "u": "https://janamen1.kz/influence?utm_source=aknur_me&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "dankarti", "m": "mpb2", "mgr": "Алина", "n": "Артыкбай Дана", "s": "12,2 тыс", "c": "Туркестан", "p": "https://www.instagram.com/dankarti?igsh=MWhybXAwbDRhdGExaA%3D%3D&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=dankarti&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "almaznyi__", "m": "mpb2", "mgr": "Алина", "n": "Илесов Алмас", "s": "3 899", "c": "Шымкент", "p": "https://www.instagram.com/almaznyi__?rpxt=MTVzbHNhbTRyajdtbQ==", "u": "https://janamen1.kz/influence?utm_source=almaznyi__&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "sharipova_zhannat", "m": "mpb2", "mgr": "Алина", "n": "Шарипова Жанат", "s": "9 863", "c": "Астана", "p": "https://www.instagram.com/sharipova_zhannat?obrf=MWdtamw5a3l0ODE5eg==", "u": "https://janamen1.kz/influence?utm_source=sharipova_zhannat&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "zar1nka", "m": "mpb3", "mgr": "Алуа", "n": "Касымова Зарина", "s": "9 884", "c": "Алматы", "p": "https://www.instagram.com/zar1nka?dlrf=MXJjNG9xeTN5dHU5", "u": "https://janamen1.kz/influence?utm_source=zar1nka&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels"}, {"h": "kanatkyzyy___", "m": "mpb3", "mgr": "Алуа", "n": "Төлеубек Жаннұр", "s": "12,8 тыс", "c": "Караганда", "p": "https://www.instagram.com/kanatkyzyy___?dlrf=MXNnYTRpZGFndzA0NA%3D%3D", "u": "https://janamen1.kz/influence?utm_source=kanatkyzyy___&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "yrysgul.abdukarimova", "m": "mpb3", "mgr": "Алуа", "n": "Абдукаримова Ирисгул", "s": "32,8 тыс", "c": "Шымкент", "p": "https://instagram.com/yrysgul.abdukarimova?obrf=ZWNsb3R5aXp2emhl", "u": "https://janamen1.kz/influence?utm_source=yrysgul.abdukarimova&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "gulnur_zhumagul", "m": "mpb3", "mgr": "Алуа", "n": "Жумагул Гулнур", "s": "21,9 тыс", "c": "Алматы", "p": "https://www.instagram.com/gulnur_zhumagul?dlrf=MWw1Z2picWsxeDAyNw%3D%3D", "u": "https://janamen1.kz/influence?utm_source=gulnur_zhumagul&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "indira_nyrbekkyzyy", "m": "mpb3", "mgr": "Алуа", "n": "Еркебек Индира", "s": "28,2 тыс", "c": "Алматы", "p": "https://www.instagram.com/indira_nyrbekkyzyy?obrf=YTRvY2xhMHNtYW9w", "u": "https://janamen1.kz/influence?utm_source=indira_nyrbekkyzyy&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aselqyzdan", "m": "mpb3", "mgr": "Алуа", "n": "Рымбаева Асел", "s": "40,6 тыс", "c": "Жанаозен", "p": "https://www.instagram.com/aselqyzdan/", "u": "https://janamen1.kz/influence?utm_source=aselqyzdan&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "anar_aitzhanova_", "m": "mpb3", "mgr": "Алуа", "n": "Айтжанова Анар", "s": "9 059", "c": "Астана", "p": "https://www.instagram.com/anar_aitzhanova_/", "u": "https://janamen1.kz/influence?utm_source=anar_aitzhanova_&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "timon_bmw", "m": "mpb3", "mgr": "Алуа", "n": "Айтжанов Тимур", "s": "5 586", "c": "Астана", "p": "https://www.instagram.com/timon_bmw/", "u": "https://janamen1.kz/influence?utm_source=timon_bmw&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "dr.nazerke_kuatkyzy", "m": "mpb3", "mgr": "Алуа", "n": "Шакенова Назерке", "s": "13,1 тыс", "c": "Астана", "p": "https://www.instagram.com/dr.nazerke_kuatkyzy/", "u": "https://janamen1.kz/influence?utm_source=dr.nazerke_kuatkyzy&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aya_bainiyet", "m": "mpb3", "mgr": "Алуа", "n": "Байниет Аягоз", "s": "33,3 тыс", "c": "Алматы", "p": "https://www.instagram.com/aya_bainiyet/", "u": "https://janamen1.kz/influence?utm_source=aya_bainiyet&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "damirusha__", "m": "mpb2", "mgr": "Алина", "n": "Толепова Дамира", "s": "10,2 тыс", "c": "Актобе", "p": "https://www.instagram.com/damirusha__?igsh=MXFieWg3ZDQxM3M4MQ%3D%3D&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=damirusha__&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "elon.rasulovna", "m": "mpb3", "mgr": "Алуа", "n": "Азиева Эльмира", "s": "14,5 тыс", "c": "Шымкент", "p": "https://www.instagram.com/elon.rasulovna/", "u": "https://janamen1.kz/influence?utm_source=elon.rasulovna&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "sanimka.off", "m": "mpb3", "mgr": "Алуа", "n": "Тузелбай Сымбат", "s": "59,8 тыс", "c": "Алматы", "p": "https://www.instagram.com/sanimka.off/", "u": "https://janamen1.kz/influence?utm_source=sanimka.off&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "_zzhuldyzbaeva", "m": "mpb3", "mgr": "Алуа", "n": "Алимкулова Жансая", "s": "30,1 тыс", "c": "Талгар", "p": "https://www.instagram.com/_zzhuldyzbaeva/", "u": "https://janamen1.kz/influence?utm_source=_zzhuldyzbaeva&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "alua_toltayeva", "m": "mpb3", "mgr": "Алуа", "n": "Төлтаева Алуа", "s": "37,5 тыс", "c": "Шымкент", "p": "https://www.instagram.com/alua_toltayeva/", "u": "https://janamen1.kz/influence?utm_source=alua_toltayeva&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "saule_kuralbaevna", "m": "mpb1", "mgr": "Анельжан", "n": "Сауле", "s": "12 100", "c": "Шымкент", "p": "https://www.instagram.com/saule_kuralbaevna?stkn=MXg1bzZscWkwdTRjag==", "u": "https://janamen1.kz/influence?utm_source=saule_kuralbaevna&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "ainykshaaa", "m": "mpb1", "mgr": "Анельжан", "n": "Айныкша", "s": "12 300", "c": "Шымкент", "p": "https://www.instagram.com/ainykshaaa?stkn=MTZhMXp5am5neHlrbA==", "u": "https://janamen1.kz/influence?utm_source=ainykshaaa&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "asylzat_erbolatovnaa", "m": "mpb1", "mgr": "Анельжан", "n": "Асылзат", "s": "18300", "c": "Астана", "p": "https://www.instagram.com/asylzat_erbolatovnaa?vrfl=ajZrbjY3NHZjazY0", "u": "https://janamen1.kz/influence?utm_source=asylzat_erbolatovnaa&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "arailym_zhak", "m": "mpb1", "mgr": "Анельжан", "n": "Арайлым", "s": "20200", "c": "Астана", "p": "https://www.instagram.com/arailym_zhak?stkn=MTAzcmRqNTFuanJ2bA==", "u": "https://janamen1.kz/influence?utm_source=arailym_zhak&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aliyaestet", "m": "mpb1", "mgr": "Анельжан", "n": "Алия", "s": "1411", "c": "Астана", "p": "https://www.instagram.com/aliyaestet?mdxt=NW55czE4andyZGNq", "u": "https://janamen1.kz/influence?utm_source=aliyaestet&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "madina.dreams", "m": "mpb1", "mgr": "Анельжан", "n": "Мадина", "s": "23700", "c": "Алматы", "p": "https://www.instagram.com/madina.dreams?cplk=a2JwYmE3ZHRhbnQ4", "u": "https://janamen1.kz/influence?utm_source=madina.dreams&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "qura1aikaa", "m": "mpb1", "mgr": "Анельжан", "n": "Куралай", "s": "14500", "c": "Шымкент", "p": "https://www.instagram.com/qura1aikaa?cplk=emIyYWRteWpnbWQ5", "u": "https://janamen1.kz/influence?utm_source=qura1aikaa&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "dr_diana.erlanovna", "m": "mpb1", "mgr": "Анельжан", "n": "Диана", "s": "11000", "c": "Шымкент", "p": "https://www.instagram.com/dr_diana.erlanovna?dlrf=MTcxOW50eXl5OGdqdw==", "u": "https://janamen1.kz/influence?utm_source=dr_diana.erlanovna&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "hayrinis_aa", "m": "mpb1", "mgr": "Анельжан", "n": "Хайринис", "s": "4883", "c": "Алматы", "p": "https://www.instagram.com/hayrinis_aa?vrfl=azUzOHAyOWh4N3E4", "u": "https://janamen1.kz/influence?utm_source=hayrinis_aa&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aknur_ydyrys", "m": "mpb1", "mgr": "Анельжан", "n": "Акнур", "s": "15200", "c": "Алматы", "p": "https://www.instagram.com/aknur_ydyrys?srtk=ODVvdWV4eXNpN3lh", "u": "https://janamen1.kz/influence?utm_source=aknur_ydyrys&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "bota_abdualii", "m": "mpb1", "mgr": "Анельжан", "n": "Бота", "s": "52600", "c": "Астана", "p": "https://www.instagram.com/bota_abdualii?dlrf=MXFzZ3JnY2dodTBsNA==", "u": "https://janamen1.kz/influence?utm_source=bota_abdualii&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "zhansokk__", "m": "mpb1", "mgr": "Анельжан", "n": "Жансая", "s": "8468", "c": "Шымкент", "p": "https://www.instagram.com/zhansokk__?psln=MW9lcHc4MnlwYTh1ag==", "u": "https://janamen1.kz/influence?utm_source=zhansokk__&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "gaukhar_taktarbekova", "m": "mpb1", "mgr": "Анельжан", "n": "Гаухар", "s": "27000", "c": "Тараз", "p": "https://www.instagram.com/gaukhar_taktarbekova", "u": "https://janamen1.kz/influence?utm_source=gaukhar_taktarbekova&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "amirovva_m", "m": "mpb1", "mgr": "Анельжан", "n": "Макпал", "s": "4270", "c": "Астана", "p": "https://www.instagram.com/amirovva_m?rpxt=MTNxZTVjenVlczN4dw==", "u": "https://janamen1.kz/influence?utm_source=amirovva_m&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "araika.mom", "m": "mpb1", "mgr": "Анельжан", "n": "Арай", "s": "13500", "c": "Талдыкорган", "p": "https://www.instagram.com/araika.mom?exln=MWFldWlqdG1reTAzNA==", "u": "https://janamen1.kz/influence?utm_source=araika.mom&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aishka_karimova", "m": "mpb1", "mgr": "Анельжан", "n": "Аиша", "s": "219000", "c": "Астана", "p": "https://www.instagram.com/aishka_karimova?vrfl=bGpzY2cwbXA2ZW5m", "u": "https://janamen1.kz/influence?utm_source=aishka_karimova&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "gulayan.keneshbaeva", "m": "mpb1", "mgr": "Анельжан", "n": "Гулаян", "s": "8690", "c": "Алматы", "p": "https://www.instagram.com/gulayan.keneshbaeva?mdxt=aHF5YWtkNGtndmk3", "u": "https://janamen1.kz/influence?utm_source=gulayan.keneshbaeva&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "maliqa.sultan", "m": "mpb1", "mgr": "Анельжан", "n": "Малика", "s": "2179", "c": "Алматы", "p": "https://www.instagram.com/maliqa.sultan?", "u": "https://janamen1.kz/influence?utm_source=maliqa.sultan&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aizadaalnur", "m": "mpb1", "mgr": "Анельжан", "n": "Айзада", "s": "71400", "c": "Алматы", "p": "https://www.instagram.com/aizadaalnur?xtok=MWU1MGRqNHdhdXhrcg==", "u": "https://janamen1.kz/influence?utm_source=aizadaalnur&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "lyazzka001", "m": "mpb1", "mgr": "Анельжан", "n": "Лязат", "s": "9020", "c": "Алматы", "p": "https://www.instagram.com/lyazzka001?vrfl=MTdpdmdweG82a2txbg==", "u": "https://janamen1.kz/influence?utm_source=lyazzka001&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "adina_tolegenova", "m": "mpb1", "mgr": "Анельжан", "n": "Адина", "s": "6535", "c": "Алматы", "p": "https://www.instagram.com/adina_tolegenova?mdxt=MmxmdXU1anhyNnhs", "u": "https://janamen1.kz/influence?utm_source=adina_tolegenova&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "sitora_sidelnikova", "m": "mpb1", "mgr": "Анельжан", "n": "Ситора", "s": "6 880", "c": "Тараз", "p": "https://www.instagram.com/sitora_sidelnikova?vrfl=MXgyaHNqZmF2ZHJqcw==", "u": "https://janamen1.kz/influence?utm_source=sitora_sidelnikova&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "d.guldanaa", "m": "mpb1", "mgr": "Анельжан", "n": "Гульдана", "s": "1 407", "c": "Астана", "p": "https://www.instagram.com/d.guldanaa?srtk=b2FkMXA3MGRodWIy", "u": "https://janamen1.kz/influence?utm_source=d.guldanaa&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "gauhar_diary", "m": "mpb1", "mgr": "Анельжан", "n": "Гаухар", "s": "9 798", "c": "Алматы", "p": "https://www.instagram.com/gauhar_diary?mdxt=ZHV3dnlvajhteHl6", "u": "https://janamen1.kz/influence?utm_source=gauhar_diary&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "_arailym.14", "m": "mpb2", "mgr": "Алина", "n": "Арайлым", "s": "98,9 тыс", "c": "Балхаш", "p": "https://www.instagram.com/_arailym.14?dlrf=MXhsYnd4bTBxbXp3Ng==", "u": "https://janamen1.kz/influence?utm_source=_arailym.14&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "xamida_iles", "m": "mpb3", "mgr": "Алуа", "n": "Илесова Хамида", "s": "8 280", "c": "Шымкент", "p": "https://www.instagram.com/xamida_iles/", "u": "https://janamen1.kz/influence?utm_source=xamida_iles&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "uais0va", "m": "mpb2", "mgr": "Алина", "n": "Алтынай", "s": "19,6 тыс", "c": "Алмата", "p": "https://www.instagram.com/uais0va?cplk=MTFpdXFjZ2tydHo1MQ==", "u": "https://janamen1.kz/influence?utm_source=uais0va&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aruzhan_zhuzbay", "m": "mpb3", "mgr": "Алуа", "n": "Аружан Жүзбай", "s": "9 590", "c": "Каскелен", "p": "https://www.instagram.com/aruzhan_zhuzbay/", "u": "https://janamen1.kz/influence?utm_source=aruzhan_zhuzbay&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "bibinur.maratova9500nv", "m": "mpb3", "mgr": "Алуа", "n": "Ахметова Бибинур", "s": "8 286", "c": "Алматы", "p": "https://www.instagram.com/bibinur.maratova9500nv/", "u": "https://janamen1.kz/influence?utm_source=bibinur.maratova9500nv&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "armana_fitness_trainer", "m": "mpb3", "mgr": "Алуа", "n": "Хамзина Арман", "s": "61,9 тыс", "c": "Астана", "p": "https://www.instagram.com/armana_fitness_trainer/", "u": "https://janamen1.kz/influence?utm_source=armana_fitness_trainer&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "taubaeva.bayan", "m": "mpb3", "mgr": "Алуа", "n": "Таубай Баян", "s": "41,2 тыс", "c": "Шымкент", "p": "https://www.instagram.com/taubaeva.bayan/", "u": "https://janamen1.kz/influence?utm_source=taubaeva.bayan&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "raushan_ismail", "m": "mpb3", "mgr": "Алуа", "n": "Исмайл Раушан", "s": "20,2 тым", "c": "Рудный", "p": "https://www.instagram.com/raushan_ismail/", "u": "https://janamen1.kz/influence?utm_source=raushan_ismail&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "_ttomika_", "m": "mpb2", "mgr": "Алина", "n": "Абдирашит Тогжан", "s": "41,7 тыс", "c": "Астана", "p": "https://www.instagram.com/_ttomika_?dlrf=MXNvaG55c2FqaXl1aA%3D%3D&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=_ttomika_&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=stories"}, {"h": "abbaz.meruert", "m": "mpb2", "mgr": "Алина", "n": "Аббаз Меруерт", "s": "25,4 тыс", "c": "Туркестан", "p": "https://www.instagram.com/abbaz.meruert?mdxt=MXd1cDl1YnMwYXl5MA%3D%3D&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=abbaz.meruert&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "sarsssembaeva", "m": "mpb2", "mgr": "Алина", "n": "Сатыбай Дария", "s": "72 тыс", "c": "Астана", "p": "https://www.instagram.com/sarsssembaeva?obrf=aWFodXdvNDdid3Np", "u": "https://janamen1.kz/influence?utm_source=sarsssembaeva&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=stories"}, {"h": "seel.anzh", "m": "mpb1", "mgr": "Анельжан", "n": "seel.anzh", "s": "8 966", "c": "Алматы", "p": "https://www.instagram.com/seel.anzh?xtok=MTJlcGNhcWU3NXY1cQ==", "u": "https://janamen1.kz/influence?utm_source=seel.anzh&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "nazeka.altynbek", "m": "mpb1", "mgr": "Анельжан", "n": "nazeka.altynbek", "s": "4 403", "c": "Алматы", "p": "https://www.instagram.com/nazeka.altynbek?exln=MWUxN25hdjVsaHRxcg==", "u": "https://janamen1.kz/influence?utm_source=nazeka.altynbek&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "kuanysheva.dii", "m": "mpb2", "mgr": "Алина", "n": "Куанышева Дильназ", "s": "74,8 тыс", "c": "Астана", "p": "https://www.instagram.com/kuanysheva.dii?obrf=b3luYzdzczM1Ym15", "u": "https://janamen1.kz/influence?utm_source=kuanysheva.dii&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "anarayerikovna", "m": "mpb2", "mgr": "Алина", "n": "Анара", "s": "7 000", "c": "Астана", "p": "https://www.instagram.com/anarayerikovna?cplk=MWdzbjZwZ2NpMTdydg==", "u": "https://janamen1.kz/influence?utm_source=anarayerikovna&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "askhatovna_g", "m": "mpb3", "mgr": "Алуа", "n": "Гульжаннат Асхатовна", "s": "5 529", "c": "Алматы", "p": "https://www.instagram.com/askhatovna_g/", "u": "https://janamen1.kz/influence?utm_source=askhatovna_g&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aidana_adilkassym", "m": "mpb3", "mgr": "Алуа", "n": "Айдана Адилкасымова", "s": "72,6 тыс", "c": "Астана", "p": "https://www.instagram.com/aidana_adilkassym/", "u": "https://janamen1.kz/influence?utm_source=aidana_adilkassym&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "inabattan01", "m": "mpb2", "mgr": "Алина", "n": "Амантай Инабат", "s": "37,4 тыс", "c": "Астана", "p": "https://www.instagram.com/inabattan01?xtok=OWJibWkzY2tscmR4", "u": "https://janamen1.kz/influence?utm_source=inabattan01&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aminkamn04", "m": "mpb2", "mgr": "Алина", "n": "Манезова Амина", "s": "10,1 тыс", "c": "Караганда", "p": "https://www.instagram.com/aminkamn04?exln=MTNxaHFieHk0aThvbw==", "u": "https://janamen1.kz/influence?utm_source=aminkamn04&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "nazdossanova", "m": "mpb2", "mgr": "Алина", "n": "Карибаева Назерке", "s": "12,8 тыс", "c": "Алмата", "p": "https://www.instagram.com/nazdossanova?srtk=MTRhbzlkN2MxbW5yaw==", "u": "https://janamen1.kz/influence?utm_source=nazdossanova&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "diva_boni", "m": "mpb2", "mgr": "Алина", "n": "Момышева Балнур", "s": "119 тыс", "c": "Алмата", "p": "https://www.instagram.com/diva_boni?rpxt=MWx4ZnFiNTg5dmxwdg==", "u": "https://janamen1.kz/influence?utm_source=diva_boni&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=stories"}, {"h": "erke_expert", "m": "mpb2", "mgr": "Алина", "n": "Назерке", "s": "38,8 тыс", "c": "Шымкент", "p": "https://www.instagram.com/erke_expert?xtok=OWw3NXVnNTd0ZXBy&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=erke_expert&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "aiymka.krg", "m": "mpb3", "mgr": "Алуа", "n": "Мурат Айым", "s": "38,9 тыс", "c": "Караганда", "p": "https://www.instagram.com/aiymka.krg/", "u": "https://janamen1.kz/influence?utm_source=aiymka.krg&utm_medium=mpb3&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "alipbayeva.raikhan", "m": "mpb1", "mgr": "Анельжан", "n": "Алипбаева Райхан", "s": "20,4 тыс", "c": "Атырау", "p": "https://www.instagram.com/alipbayeva.raikhan?obrf=MXV4OTd1Y25qd2c1Nw%3D%3D", "u": "https://janamen1.kz/influence?utm_source=alipbayeva.raikhan&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "zainolda_aktan", "m": "mpb2", "mgr": "Алина", "n": "Зайнолда Актан", "s": "71,7 тыс", "c": "Алматы", "p": "https://www.instagram.com/zainolda_aktan?rpxt=MTZ3MmE2anhzMTZ6Nw==", "u": "https://janamen1.kz/influence?utm_source=zainolda_aktan&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "_akbayan_", "m": "mpb2", "mgr": "Алина", "n": "Карымбай Акбаян", "s": "6 257", "c": "Алматы", "p": "https://www.instagram.com/_akbayan_?xtok=MXRjdXd5OHlhZ3ZlaQ%3D%3D&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=_akbayan_&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "mayabassova", "m": "mpb2", "mgr": "Алина", "n": "Кумисай Маябасова", "s": "101 тыс", "c": "Шымкент", "p": "https://www.instagram.com/mayabassova?obrf=eTZjcGUzYzhsNXlu", "u": "https://janamen1.kz/influence?utm_source=mayabassova&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=stories"}, {"h": "akmaral_k.k", "m": "mpb2", "mgr": "Алина", "n": "Қабанбаева Ақмарал", "s": "32,1 тыс", "c": "Усть-каменогорск", "p": "https://www.instagram.com/akmaral_k.k?vrfl=aWJuZzVmZWxiMGl0&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=akmaral_k.k&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "kuanyshevna15", "m": "mpb2", "mgr": "Алина", "n": "Жангазинова Малика", "s": "8 780", "c": "Сарань", "p": "https://www.instagram.com/kuanyshevna15?cplk=MWtoenJwMnpydmlleQ==", "u": "https://janamen1.kz/influence?utm_source=kuanyshevna15&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "batyrhanovna.creator", "m": "mpb2", "mgr": "Алина", "n": "Толеу Томирис", "s": "9 568", "c": "Караганда", "p": "https://www.instagram.com/batyrhanovna.creator?psln=N3hiNDl0ajVpdGhp&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=batyrhanovna.creator&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "korkemdiary", "m": "mpb2", "mgr": "Алина", "n": "Әзімханова Көркем", "s": "9 759", "c": "Астана", "p": "https://www.instagram.com/korkemdiary?cplk=NHJodGkzcmJidmw1", "u": "https://janamen1.kz/influence?utm_source=korkemdiary&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "fariza_zhomartovna", "m": "mpb2", "mgr": "Алина", "n": "Мырзабаева Фариза", "s": "", "c": "Астана", "p": "https://www.instagram.com/fariza_zhomartovna?obrf=MTc4NmFkYXRqd2xpbA%3D%3D&utm_source=qr", "u": "https://janamen1.kz/influence?utm_source=fariza_zhomartovna&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=reels_stories"}, {"h": "withlovemika1", "m": "mpb1", "mgr": "Анельжан", "n": "Садыкова Меруерт", "s": "23", "c": "Астана", "p": "https://www.instagram.com/withlovemika1/", "u": "https://janamen1.kz/influence?utm_source=withlovemika1&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=stories"}, {"h": "qulbek_galiya", "m": "mpb1", "mgr": "Анельжан", "n": "Қүлбек Ғалия", "s": "", "c": "", "p": "https://instagram.com/qulbek_galiya", "u": "https://janamen1.kz/influence?utm_source=qulbek_galiya&utm_medium=mpb1&utm_campaign=ugc_barter&utm_content=stories"}, {"h": "k.saidullayev", "m": "mpb2", "mgr": "Алина", "n": "Куанышбек Сайдуллаев", "s": "", "c": "", "p": "https://www.instagram.com/k.saidullayev/", "u": "https://janamen1.kz/influence?utm_source=k.saidullayev&utm_medium=mpb2&utm_campaign=ugc_barter&utm_content=stories"}];


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
    const expandedAccordions = new Set(['all_section_organika', 'all_section_influence', 'all_section_fan', 'org_wa', 'org_smm', 'org_site', 'mpb1', 'mpb2', 'mpb3', 'mpb4', 'bekezhanova_dilnaz', 'doskazhanova_ainagul', 'kenzhebaeva_aisulu_1', 'kenzhebaeva_aisulu_2', 'gaisina_kamila', 'kenzhebaeva_aida', 'adina_khaidarova_1', 'adina_khaidarova_2']);
    let CLICK_BY_CAMPAIGN = {};

    // Данные кликов из Supabase
    // Блогеры, добавленные вручную / из базы данных
    let CUSTOM_BLOGGERS = [];

    // Авторизация и текущий пользователь
    let CURRENT_USER = null;

    let RAW_CLICKS = [];
    let CLICK_COUNTS = {};
    let CLICK_BY_CONTENT = {};
    let CLICK_BY_MEDIUM = {};
    let CLICK_BY_PAGE = {};
    let CLICK_BY_SOURCE = {};
    let CLICK_BY_BLOGGER = {};
    let CLICK_BY_CAMPAIGN_SOURCE = {};

    // Агрегированные данные текущей выборки
    let currentChannelData = {};

    // ============================================================
    // ПЕРЕКЛЮЧЕНИЕ ГЛАВНЫХ КАНАЛОВ
    // ============================================================
    function switchMainChannel(channel) {
      currentMainChannel = channel;

      // Минималистичное обновление сегментированных вкладок (Apple / Linear style)
      const tabs = ['organika', 'influence', 'fan', 'all', 'tags'];
      tabs.forEach(t => {
        const btn = document.getElementById('main-tab-' + t);
        const badge = document.getElementById('tabBadge' + t.charAt(0).toUpperCase() + t.slice(1));
        if (!btn) return;

        const isRightAligned = (t === 'all');
        const mlClass = isRightAligned ? 'ml-auto' : '';

        if (t === channel) {
          btn.className = `px-3.5 py-2 rounded-lg bg-white text-slate-900 font-bold text-xs sm:text-sm flex items-center space-x-2 transition shadow-2xs whitespace-nowrap cursor-pointer ${mlClass}`;
          if (badge) badge.className = 'px-2 py-0.5 text-[10px] bg-slate-900 text-white rounded-full font-bold';
        } else {
          btn.className = `px-3.5 py-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-white/60 font-semibold text-xs sm:text-sm flex items-center space-x-2 transition whitespace-nowrap cursor-pointer ${mlClass}`;
          if (badge) badge.className = 'px-2 py-0.5 text-[10px] bg-slate-200 text-slate-700 rounded-full font-semibold';
        }
      });

      // Показ/скрытие кнопок разворачивания
      const actionBtns = document.getElementById('channelActionButtons');
      const allSubTabs = document.getElementById('allChannelsSubTabs');
      if (channel === 'influence' || channel === 'fan' || channel === 'organika') {
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
    // ФИЛЬТРАЦИЯ ПО ПЕРИОДУ (БЫСТРЫЕ ДНИ, МЕСЯЦЫ, ОТ ДАТЫ И ДО ДАТЫ)
    // ============================================================
    function selectMonthPreset(val) {
      if (!val) {
        setPeriodPreset('all');
        return;
      }
      const parts = val.split('-');
      const y = parseInt(parts[0], 10);
      const m = parseInt(parts[1], 10); // 1-12
      
      const startDate = new Date(Date.UTC(y, m - 1, 1, 0, 0, 0));
      const lastDay = new Date(y, m, 0).getDate();
      const endDate = new Date(Date.UTC(y, m - 1, lastDay, 23, 59, 59));

      filterDateFrom = Math.floor(startDate.getTime() / 1000);
      filterDateTo = Math.floor(endDate.getTime() / 1000);

      const startIso = `${y}-${String(m).padStart(2, '0')}-01`;
      const endIso = `${y}-${String(m).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;

      const inFrom = document.getElementById('dateInputFrom');
      const inTo = document.getElementById('dateInputTo');
      if (inFrom) inFrom.value = startIso;
      if (inTo) inTo.value = endIso;

      const monthSelect = document.getElementById('monthSelect');
      if (monthSelect) monthSelect.value = val;

      const buttons = document.querySelectorAll('[id^="period-btn-"]');
      buttons.forEach(b => {
        if (b.id === 'period-btn-' + val) {
          b.className = 'px-2.5 py-1.5 rounded-lg text-xs font-bold transition bg-slate-900 text-white shadow-2xs cursor-pointer';
        } else {
          b.className = 'px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 transition cursor-pointer';
        }
      });

      currentPeriod = 'month_' + val;
      onFilterChange();
    }

    function setPeriodPreset(preset) {
      currentPeriod = preset;
      const now = new Date();
      const nowTs = Math.floor(now.getTime() / 1000);

      const buttons = document.querySelectorAll('[id^="period-btn-"]');
      buttons.forEach(b => {
        if (b.id === 'period-btn-' + preset) {
          b.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition bg-slate-900 text-white shadow-2xs cursor-pointer';
        } else {
          b.className = 'px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 transition cursor-pointer';
        }
      });

      const monthSelect = document.getElementById('monthSelect');
      if (monthSelect) monthSelect.value = '';

      const inFrom = document.getElementById('dateInputFrom');
      const inTo = document.getElementById('dateInputTo');

      const fmt = (d) => {
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
      };

      if (preset === 'all') {
        filterDateFrom = null;
        filterDateTo = null;
        if (inFrom) inFrom.value = '';
        if (inTo) inTo.value = '';
      } else if (preset === 'today') {
        const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
        filterDateFrom = Math.floor(start.getTime() / 1000);
        filterDateTo = null;
        if (inFrom) inFrom.value = fmt(now);
        if (inTo) inTo.value = fmt(now);
      } else if (preset === 'yesterday') {
        const yDay = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 0, 0, 0);
        const yEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 23, 59, 59);
        filterDateFrom = Math.floor(yDay.getTime() / 1000);
        filterDateTo = Math.floor(yEnd.getTime() / 1000);
        if (inFrom) inFrom.value = fmt(yDay);
        if (inTo) inTo.value = fmt(yDay);
      } else if (preset === 'last7') {
        filterDateFrom = nowTs - 7 * 86400;
        filterDateTo = null;
        if (inFrom) inFrom.value = fmt(new Date((nowTs - 7 * 86400) * 1000));
        if (inTo) inTo.value = fmt(now);
      } else if (preset === 'last30') {
        filterDateFrom = nowTs - 30 * 86400;
        filterDateTo = null;
        if (inFrom) inFrom.value = fmt(new Date((nowTs - 30 * 86400) * 1000));
        if (inTo) inTo.value = fmt(now);
      }

      onFilterChange();
    }

    function applyCustomDateRange() {
      const fromVal = document.getElementById('dateInputFrom')?.value;
      const toVal = document.getElementById('dateInputTo')?.value;
      if (!fromVal && !toVal) return;

      currentPeriod = 'custom';
      if (fromVal) {
        const parts = fromVal.split('-');
        const dt = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10), 0, 0, 0);
        filterDateFrom = Math.floor(dt.getTime() / 1000);
      } else {
        filterDateFrom = null;
      }

      if (toVal) {
        const parts = toVal.split('-');
        const dt = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10), 23, 59, 59);
        filterDateTo = Math.floor(dt.getTime() / 1000);
      } else {
        filterDateTo = null;
      }

      const buttons = document.querySelectorAll('[id^="period-btn-"]');
      buttons.forEach(b => {
        b.className = 'px-2.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 transition cursor-pointer';
      });

      const monthSelect = document.getElementById('monthSelect');
      if (monthSelect) monthSelect.value = '';

      onFilterChange();
    }

    function resetAllFilters() {
      currentPeriod = 'all';
      filterDateFrom = null;
      filterDateTo = null;
      const inFrom = document.getElementById('dateInputFrom');
      const inTo = document.getElementById('dateInputTo');
      if (inFrom) inFrom.value = '';
      if (inTo) inTo.value = '';
      const search = document.getElementById('filterSearchInput');
      if (search) search.value = '';
      const monthSelect = document.getElementById('monthSelect');
      if (monthSelect) monthSelect.value = '';
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

      // Официальные 6 точек входа Органики (janamen1.kz/smm + WhatsApp 9828)
      const organikaItems = {
        'smm_bio': {
          id: 'smm_bio',
          name: '📸 Шапка профиля Instagram (Bio)',
          placement: 'Instagram Bio',
          source: 'instagram',
          medium: 'bio',
          campaign: 'main_profile',
          url: 'https://janamen1.kz/smm?utm_source=instagram&utm_medium=bio&utm_campaign=main_profile',
          leads: 0, won: 0, rev: 0, clicks: 0
        },
        'smm_youtube': {
          id: 'smm_youtube',
          name: '▶️ YouTube канал (Шапка и описание)',
          placement: 'YouTube канал',
          source: 'youtube',
          medium: 'channel',
          campaign: 'smm_video',
          url: 'https://janamen1.kz/smm?utm_source=youtube&utm_medium=channel&utm_campaign=smm_video',
          leads: 0, won: 0, rev: 0, clicks: 0
        },
        'smm_chatbot': {
          id: 'smm_chatbot',
          name: '🤖 Чат-бот из основного профиля Direct',
          placement: 'Instagram Bot / Direct',
          source: 'chatbot',
          medium: 'direct_bot',
          campaign: 'welcome_bot',
          url: 'https://janamen1.kz/smm?utm_source=chatbot&utm_medium=direct_bot&utm_campaign=welcome_bot',
          leads: 0, won: 0, rev: 0, clicks: 0
        },
        'smm_threads': {
          id: 'smm_threads',
          name: '🧵 Threads ссылка (В профиле и постах)',
          placement: 'Threads профиль',
          source: 'threads',
          medium: 'post',
          campaign: 'threads_bio',
          url: 'https://janamen1.kz/smm?utm_source=threads&utm_medium=post&utm_campaign=threads_bio',
          leads: 0, won: 0, rev: 0, clicks: 0
        },
        'smm_tiktok': {
          id: 'smm_tiktok',
          name: '🎵 TikTok (Шапка основного аккаунта)',
          placement: 'TikTok Bio',
          source: 'tiktok',
          medium: 'bio',
          campaign: 'tiktok_main',
          url: 'https://janamen1.kz/smm?utm_source=tiktok&utm_medium=bio&utm_campaign=tiktok_main',
          leads: 0, won: 0, rev: 0, clicks: 0
        },
        'wa_9828': {
          id: 'wa_9828',
          name: '📱 WhatsApp Айтыма Бериковича (9828)',
          placement: 'WhatsApp 77083779828',
          source: 'whatsapp',
          medium: 'direct',
          campaign: 'wa9828',
          url: 'https://janamen1.kz/iwa-9828?utm_source=whatsapp&utm_medium=direct&utm_campaign=wa9828',
          leads: 0, won: 0, rev: 0, clicks: 0
        },
        'smm_other': {
          id: 'smm_other',
          name: '🌐 Прямые заходы на /smm и заявки',
          placement: 'Сайт /smm',
          source: 'smm',
          medium: 'direct',
          campaign: 'other',
          url: 'https://janamen1.kz/smm',
          leads: 0, won: 0, rev: 0, clicks: 0
        }
      };

      const influenceManagers = {
        'mpb1': { code: 'mpb1', name: 'Анельжан (mpb1)', leads: 0, won: 0, rev: 0, clicks: 0, bloggers: {} },
        'mpb2': { code: 'mpb2', name: 'Алина (mpb2)', leads: 0, won: 0, rev: 0, clicks: 0, bloggers: {} },
        'mpb3': { code: 'mpb3', name: 'Алуа (mpb3)', leads: 0, won: 0, rev: 0, clicks: 0, bloggers: {} },
        'mpb4': { code: 'mpb4', name: 'Дарина (mpb4)', leads: 0, won: 0, rev: 0, clicks: 0, bloggers: {} },
        'other': { code: 'other', name: 'Другие / Без менеджера', leads: 0, won: 0, rev: 0, clicks: 0, bloggers: {} }
      };

      // Предзагрузка блогеров из реестра таблицы Google Sheets (с учетом удаленных владельцем)
      let deletedBloggersList = [];
      try {
        deletedBloggersList = JSON.parse(localStorage.getItem('janamen_deleted_bloggers') || '[]');
      } catch(e) {}

      const bloggerMap = {};
      if (typeof INFLUENCE_REGISTRY !== 'undefined' && Array.isArray(INFLUENCE_REGISTRY)) {
        INFLUENCE_REGISTRY.forEach(b => {
          if (!b.h || deletedBloggersList.includes(b.h.toLowerCase())) return;
          const hLower = b.h.toLowerCase();
          bloggerMap[hLower] = b;
          if (b.n) bloggerMap[b.n.toLowerCase()] = b;
          const mKey = b.m || 'mpb1';
          if (influenceManagers[mKey]) {
            influenceManagers[mKey].bloggers[b.h] = {
              handle: b.h,
              name: b.n || b.h,
              manager: mKey,
              subs: b.s || '—',
              city: b.c || '—',
              profile: b.p || ('https://instagram.com/' + b.h),
              utm: b.u || `https://janamen1.kz/influence?utm_source=${b.h}&utm_medium=${mKey}&utm_campaign=ugc_barter&utm_content=reels_stories`,
              leads: 0,
              won: 0,
              rev: 0,
              clicks: 0,
              isPreloaded: true
            };
          }
        });
      }

      // Предзагрузка блогеров из базы данных Supabase / сохраненных локально
      if (typeof CUSTOM_BLOGGERS !== 'undefined' && Array.isArray(CUSTOM_BLOGGERS)) {
        CUSTOM_BLOGGERS.forEach(cb => {
          if (!cb.handle || deletedBloggersList.includes(cb.handle.toLowerCase())) return;
          const hLower = cb.handle.toLowerCase().trim();
          const mKey = cb.manager || 'mpb1';
          if (influenceManagers[mKey]) {
            const existing = influenceManagers[mKey].bloggers[cb.handle] || influenceManagers[mKey].bloggers[hLower];
            if (existing) {
              existing.name = cb.name || existing.name;
              existing.subs = cb.subs || existing.subs;
              existing.city = cb.city || existing.city;
              existing.paid_cash = cb.paid_cash || 0;
              existing.delivery_cost = cb.delivery_cost || 0;
              existing.barter_man = cb.barter_man || 0;
              existing.barter_woman = cb.barter_woman || 0;
              existing.barter_omega = cb.barter_omega || 0;
              existing.barter_aojiru = cb.barter_aojiru || 0;
            } else {
              influenceManagers[mKey].bloggers[cb.handle] = {
                handle: cb.handle,
                name: cb.name || cb.handle,
                manager: mKey,
                subs: cb.subs || '—',
                city: cb.city || '—',
                profile: cb.profile || ('https://instagram.com/' + cb.handle),
                utm: cb.utm_url || `https://janamen1.kz/influence?utm_source=${cb.handle}&utm_medium=${mKey}&utm_campaign=ugc_barter&utm_content=reels_stories`,
                paid_cash: cb.paid_cash || 0,
                delivery_cost: cb.delivery_cost || 0,
                barter_man: cb.barter_man || 0,
                barter_woman: cb.barter_woman || 0,
                barter_omega: cb.barter_omega || 0,
                barter_aojiru: cb.barter_aojiru || 0,
                leads: 0,
                won: 0,
                rev: 0,
                clicks: 0,
                isCustom: true
              };
            }
          }
          bloggerMap[hLower] = { h: cb.handle, n: cb.name, m: mKey, s: cb.subs, c: cb.city };
        });
      }

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
      fanAccounts['fan_4516'] = { id: 'fan_4516', name: 'Кампания 4516 (Архив)', leads: 0, won: 0, rev: 0, clicks: 0, spend: 0, isOfficial: false, platforms: {} };
      fanAccounts['fan_2427'] = { id: 'fan_2427', name: 'Кампания 2427-2431 (Архив)', leads: 0, won: 0, rev: 0, clicks: 0, spend: 0, isOfficial: false, platforms: {} };
      fanAccounts['fan_other'] = { id: 'fan_other', name: 'Другие фан-сделки', leads: 0, won: 0, rev: 0, clicks: 0, spend: 0, isOfficial: false, platforms: {} };

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

        const lCmp = (l.cmp || '').toLowerCase();
        const lCnt = (l.cnt || '').toLowerCase();
        const lMed = (l.med || '').toLowerCase();
        const lSrc = (l.src || '').toLowerCase();

        // Определение каналов
        const isWa9828 = l.path === '/iwa-9828' || (l.med && l.med.includes('Айтым')) || (l.tags && l.tags.some(t => t.includes('9828') || t.includes('77083779828')));
        const isSmm = l.path === '/smm' || l.med === 'social' || lCmp.includes('smm') || lSrc.includes('smm');
        const isOrganikaSite = l.path === '/organika' || (currentMainChannel === 'organika' && l.path === '/');
        const isOrganika = isWa9828 || isSmm || isOrganikaSite;

        let matchedFanId = null;
        for (let fi = 0; fi < FAN_REGISTRY.length; fi++) {
          const f = FAN_REGISTRY[fi];
          if (lCmp.includes(f.id) || lCnt.includes(f.id) || lSrc.includes(f.id)) {
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

        const isInfluence = !isFan && (l.path === '/influence' || lMed.startsWith('mpb') || lCmp.includes('influence') || (l.src && bloggerMap[lSrc]) || (l.cnt && bloggerMap[lCnt]));

        if (isOrganika) countOrganika++;
        if (isInfluence) countInfluence++;
        if (isFan) countFan++;

        // Фильтр главного канала
        if (currentMainChannel === 'organika' && !isOrganika) continue;
        if (currentMainChannel === 'influence' && !isInfluence) continue;
        if (currentMainChannel === 'fan' && !isFan) continue;

        // Поисковый фильтр (с расширенным поиском по имени блогера и его нику)
        if (textSearch) {
          const tagStr = (l.tags || []).join(' ');
          let bloggerFullName = '';
          const bMatch = bloggerMap[lSrc] || bloggerMap[lCnt] || bloggerMap[lCmp];
          if (bMatch) {
            bloggerFullName = (bMatch.n || '') + ' ' + (bMatch.h || '');
          }
          const hay = (l.src + ' ' + l.med + ' ' + l.cmp + ' ' + l.cnt + ' ' + l.trm + ' ' + l.path + ' ' + l.name + ' ' + tagStr + ' ' + bloggerFullName).toLowerCase();
          if (!hay.includes(textSearch)) continue;
        }

        leads++;
        if (l.won) {
          won++;
          rev += l.price;
        }

        // Агрегация для Органики (6 официальных точек janamen1.kz/smm + WhatsApp 9828)
        if (isOrganika) {
          let orgKey = 'smm_other';
          if (isWa9828) {
            orgKey = 'wa_9828';
          } else if (lSrc === 'chatbot' || lMed === 'direct_bot' || lCmp.includes('bot')) {
            orgKey = 'smm_chatbot';
          } else if (lSrc === 'youtube' || lMed === 'channel' || lCmp.includes('youtube')) {
            orgKey = 'smm_youtube';
          } else if (lSrc === 'threads' || lMed === 'post' || lCmp.includes('threads')) {
            orgKey = 'smm_threads';
          } else if (lSrc === 'tiktok' || lCmp.includes('tiktok')) {
            orgKey = 'smm_tiktok';
          } else if (lSrc === 'instagram' || lMed === 'bio' || lCmp.includes('bio') || lCmp.includes('profile')) {
            orgKey = 'smm_bio';
          }

          if (organikaItems[orgKey]) {
            organikaItems[orgKey].leads++;
            if (l.won) {
              organikaItems[orgKey].won++;
              organikaItems[orgKey].rev += l.price;
            }
          }
        }
        // Агрегация для Influence (Два источника: Таблица Реестра + AmoCRM)
        if (currentMainChannel === 'influence') {
          let mKey = (l.med && l.med.startsWith('mpb')) ? l.med : null;
          let bKey = null;
          let regMatch = null;

          // 1. Поиск в реестре по utm_source (в UGC-ссылках имя блогера передается в utm_source!)
          if (l.src && bloggerMap[lSrc]) {
            regMatch = bloggerMap[lSrc];
            bKey = regMatch.h;
            if (!mKey) mKey = regMatch.m;
          } else if (l.cnt && bloggerMap[lCnt]) {
            regMatch = bloggerMap[lCnt];
            bKey = regMatch.h;
            if (!mKey) mKey = regMatch.m;
          } else if (l.cmp && bloggerMap[lCmp]) {
            regMatch = bloggerMap[lCmp];
            bKey = regMatch.h;
            if (!mKey) mKey = regMatch.m;
          }

          if (!mKey) mKey = (l.med && l.med.startsWith('mpb')) ? l.med : 'other';
          if (!influenceManagers[mKey]) mKey = 'other';
          const mgr = influenceManagers[mKey];
          mgr.leads++;
          if (l.won) { mgr.won++; mgr.rev += l.price; }

          if (!bKey) {
            // Динамический блогер из сделок CRM
            if (l.src && !['direct', 'instagram', 'tiktok', 'facebook', 'none', 'smm', 'whatsapp', 'influence'].includes(lSrc)) {
              bKey = l.src;
            } else if (l.cnt && !['reels_stories', 'stories', 'reels', 'none', 'barter'].includes(lCnt)) {
              bKey = l.cnt;
            } else if (l.cmp && !['ugc_barter', 'none', 'leads'].includes(lCmp)) {
              bKey = l.cmp;
            } else {
              bKey = (l.cnt && l.cnt !== 'none') ? l.cnt : ((l.src && l.src !== 'direct') ? l.src : 'не_указан');
            }
          }

          let b = mgr.bloggers[bKey];
          if (!b) {
            b = mgr.bloggers[bKey] = {
              handle: bKey,
              name: bKey,
              manager: mKey,
              subs: '—',
              city: '—',
              profile: `https://instagram.com/${bKey}`,
              utm: `https://janamen1.kz/influence?utm_source=${bKey}&utm_medium=${mKey}&utm_campaign=ugc_barter&utm_content=reels_stories`,
              leads: 0,
              won: 0,
              rev: 0,
              clicks: 0,
              isPreloaded: false
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
          else if (lSrc.includes('facebook') || lSrc.includes('fb')) pKey = 'facebook';
          else if (lSrc.includes('telegram') || lSrc.includes('tg')) pKey = 'telegram';
          else pKey = l.src || 'other';

          if (!fa.platforms[pKey]) {
            fa.platforms[pKey] = {
              name: pKey.charAt(0).toUpperCase() + pKey.slice(1),
              icon: pKey === 'tiktok' ? '🎵' : (pKey === 'instagram' ? '📸' : (pKey === 'youtube' ? '▶️' : (pKey === 'facebook' ? '👥' : (pKey === 'telegram' ? '✈️' : '🌐')))),
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

      // Привязка кликов
      // Подсчет кликов для 6 точек Органики
      let orgTotalClicks = 0;
      if (Array.isArray(RAW_CLICKS) && RAW_CLICKS.length > 0) {
        RAW_CLICKS.forEach(c => {
          const p = (c.landing_page || '').toLowerCase();
          const src = (c.utm_source || '').toLowerCase();
          const med = (c.utm_medium || '').toLowerCase();
          const cmp = (c.utm_campaign || '').toLowerCase();

          if (p === '/iwa-9828' || src === 'whatsapp' || cmp.includes('wa9828')) {
            organikaItems['wa_9828'].clicks++;
          } else if (src === 'youtube' || cmp === 'smm_video' || (p.includes('smm') && (src === 'youtube' || med === 'channel' || cmp.includes('youtube')))) {
            organikaItems['smm_youtube'].clicks++;
          } else if (src === 'chatbot' || med === 'direct_bot' || cmp.includes('welcome_bot') || cmp.includes('bot')) {
            organikaItems['smm_chatbot'].clicks++;
          } else if (src === 'threads' || med === 'post' || cmp.includes('threads')) {
            organikaItems['smm_threads'].clicks++;
          } else if (src === 'tiktok' || cmp.includes('tiktok')) {
            organikaItems['smm_tiktok'].clicks++;
          } else if (src === 'instagram' || med === 'bio' || cmp.includes('profile') || (p.includes('smm') && med === 'bio')) {
            organikaItems['smm_bio'].clicks++;
          } else if (p.includes('smm')) {
            organikaItems['smm_other'].clicks++;
          }
        });
      }
      Object.values(organikaItems).forEach(item => orgTotalClicks += item.clicks);
      if (currentMainChannel === 'organika') {
        clicks = orgTotalClicks;
      } else if (currentMainChannel === 'influence') {
        // 1. Динамическая регистрация блогеров из RAW_CLICKS (клики без лидов)
        if (Array.isArray(RAW_CLICKS)) {
          RAW_CLICKS.forEach(c => {
            const cMed = (c.utm_medium || '').toLowerCase();
            const cPage = (c.landing_page || '').toLowerCase();
            const cSrc = (c.utm_source || '').trim();
            const cCmp = (c.utm_campaign || '').trim();
            const cBlg = (c.blogger || '').trim();

            const isInfClick = cMed.startsWith('mpb') || cPage.includes('influence') || cCmp.includes('ugc') || cCmp.includes('influence');
            if (!isInfClick) return;

            let mKey = cMed.startsWith('mpb') ? cMed : 'mpb1';
            let bKey = cBlg || cSrc;
            if (!bKey || ['direct', 'instagram', 'tiktok', 'facebook', 'none'].includes(bKey.toLowerCase())) {
              bKey = cCmp || 'blogger_link';
            }

            if (bloggerMap[bKey.toLowerCase()]) {
              const regB = bloggerMap[bKey.toLowerCase()];
              bKey = regB.h;
              if (regB.m) mKey = regB.m;
            }

            if (!influenceManagers[mKey]) mKey = 'other';
            const mgr = influenceManagers[mKey];

            if (!mgr.bloggers[bKey]) {
              mgr.bloggers[bKey] = {
                handle: bKey,
                name: bKey,
                manager: mKey,
                subs: '—',
                city: '—',
                profile: `https://instagram.com/${bKey}`,
                utm: `https://janamen1.kz/influence?utm_source=${bKey}&utm_medium=${mKey}&utm_campaign=ugc_barter&utm_content=reels_stories`,
                leads: 0,
                won: 0,
                rev: 0,
                clicks: 0,
                isPreloaded: false
              };
            }
          });
        }

        // 2. Распределение кликов по каждому менеджеру и блогеру
        Object.values(influenceManagers).forEach(mgr => {
          let mClicks = 0;
          Object.values(mgr.bloggers).forEach(b => {
            let bClicks = 0;
            if (Array.isArray(RAW_CLICKS) && RAW_CLICKS.length > 0) {
              bClicks = RAW_CLICKS.filter(c => {
                const cBlg = (c.blogger || '').toLowerCase();
                const cSrc = (c.utm_source || '').toLowerCase();
                const cCnt = (c.utm_content || '').toLowerCase();
                const cMed = (c.utm_medium || '').toLowerCase();
                const isBlogger = (cBlg === b.handle.toLowerCase() || cSrc === b.handle.toLowerCase() || cCnt === b.handle.toLowerCase());
                return isBlogger;
              }).length;
            } else {
              bClicks = (CLICK_BY_BLOGGER && CLICK_BY_BLOGGER[b.handle] ? CLICK_BY_BLOGGER[b.handle] : 0) +
                        (CLICK_BY_SOURCE && CLICK_BY_SOURCE[b.handle] ? CLICK_BY_SOURCE[b.handle] : 0) +
                        (CLICK_BY_CONTENT && CLICK_BY_CONTENT[b.handle] ? CLICK_BY_CONTENT[b.handle] : 0);
            }
            b.clicks = bClicks;
            mClicks += bClicks;
          });
          mgr.clicks = mClicks;
          clicks += mClicks;
        });
      } else if (currentMainChannel === 'fan') {
        clicks = 0;
        Object.keys(fanAccounts).forEach(fKey => {
          const fa = fanAccounts[fKey];
          const fKeyLower = fKey.toLowerCase();

          // Клики конкретного сотрудника
          let empClicks = 0;
          if (Array.isArray(RAW_CLICKS) && RAW_CLICKS.length > 0) {
            empClicks = RAW_CLICKS.filter(c => {
              const cmp = (c.utm_campaign || '').toLowerCase();
              const blg = (c.blogger || '').toLowerCase();
              return cmp === fKeyLower || blg === fKeyLower;
            }).length;
          } else {
            empClicks = (CLICK_BY_CAMPAIGN[fKey] || 0) + (CLICK_COUNTS[fKey] || 0);
          }

          fa.clicks = empClicks;
          clicks += empClicks;

          // Клики по каждой платформе СТРОГО для данного сотрудника
          Object.keys(fa.platforms).forEach(pKey => {
            let platClicks = 0;
            const pKeyLower = pKey.toLowerCase();

            if (Array.isArray(RAW_CLICKS) && RAW_CLICKS.length > 0) {
              platClicks = RAW_CLICKS.filter(c => {
                const cmp = (c.utm_campaign || '').toLowerCase();
                const blg = (c.blogger || '').toLowerCase();
                const src = (c.utm_source || '').toLowerCase();
                const isEmp = cmp === fKeyLower || blg === fKeyLower;
                const isPlat = src.includes(pKeyLower);
                return isEmp && isPlat;
              }).length;
            } else {
              const comboKey = `${fKeyLower}:::${pKeyLower}`;
              platClicks = CLICK_BY_CAMPAIGN_SOURCE[comboKey] || 0;
            }

            fa.platforms[pKey].clicks = platClicks;
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
        organikaItems,
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
    // БЛОК: УПРАВЛЕНИЕ ПЛАНОМ ВЫРУЧКИ (ТОЧКА А ➔ ТОЧКА Б)
    // ============================================================
    let TARGET_SALES_PLAN = Number(localStorage.getItem('janamen_sales_plan') || 50000000);

    function openEditPlanModal() {
      const modal = document.getElementById('editPlanModal');
      const input = document.getElementById('inputPlanTarget');
      if (input) input.value = TARGET_SALES_PLAN;
      if (modal) modal.classList.remove('hidden');
    }

    function closeEditPlanModal() {
      const modal = document.getElementById('editPlanModal');
      if (modal) modal.classList.add('hidden');
    }

    function setQuickPlan(val) {
      const input = document.getElementById('inputPlanTarget');
      if (input) input.value = val;
    }

    function savePlanTarget() {
      const input = document.getElementById('inputPlanTarget');
      const val = Number(input?.value);
      if (val && val > 0) {
        TARGET_SALES_PLAN = val;
        localStorage.setItem('janamen_sales_plan', String(val));
        closeEditPlanModal();
        updateKpis();
      }
    }

    function updatePlanProgress(factRev) {
      const target = TARGET_SALES_PLAN || 50000000;
      const fact = Number(factRev) || 0;
      const pct = Math.round(fact / target * 100);
      const clampedPct = Math.min(100, Math.max(0, pct));

      const targetDisplay = document.getElementById('planTargetDisplay');
      const targetVal = document.getElementById('planTargetVal');
      const factDisplay = document.getElementById('planFactDisplay');
      const factPercent = document.getElementById('planFactPercent');
      const factBar = document.getElementById('planFactBar');
      const badge = document.getElementById('planPercentBadge');
      const remainingVal = document.getElementById('planRemainingVal');

      if (targetDisplay) targetDisplay.innerText = target.toLocaleString('ru-RU') + ' ₸';
      if (targetVal) targetVal.innerText = target.toLocaleString('ru-RU') + ' ₸';
      if (factDisplay) factDisplay.innerText = fact.toLocaleString('ru-RU') + ' ₸';
      if (factPercent) factPercent.innerText = `(${pct}%)`;
      if (factBar) factBar.style.width = clampedPct + '%';
      
      if (badge) {
        badge.innerText = `${pct}% выполнено`;
        badge.className = `px-2.5 py-0.5 text-xs font-black rounded-full ${pct >= 100 ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-brand-800'}`;
      }

      if (remainingVal) {
        const remaining = Math.max(0, target - fact);
        remainingVal.innerText = remaining > 0 ? (remaining.toLocaleString('ru-RU') + ' ₸') : '🎉 План выполнен!';
      }
    }

    // ============================================================
    // УПРАВЛЕНИЕ ЗАРПЛАТАМИ FAN-ОТДЕЛА (ДЛЯ РАСЧЕТА РАСХОДОВ И ROMI)
    // ============================================================
    const DEFAULT_FAN_SALARY = 150000; // 150 000 ₸ / месяц на каждого сотрудника по умолчанию

    function getFanSalariesMap() {
      try {
        return JSON.parse(localStorage.getItem('janamen_fan_salaries') || '{}');
      } catch (e) {
        return {};
      }
    }

    function getFanSalary(fanId) {
      const map = getFanSalariesMap();
      if (map[fanId] !== undefined) return Number(map[fanId]);
      return DEFAULT_FAN_SALARY;
    }

    function getFanTotalMonthlySalary() {
      let total = 0;
      FAN_REGISTRY.forEach(f => {
        total += getFanSalary(f.id);
      });
      return total;
    }

    function getFanPeriodExpenses() {
      const monthlyTotal = getFanTotalMonthlySalary();
      if (!filterDateFrom && !filterDateTo) {
        return monthlyTotal; // Если весь период, отображаем месячный бюджет ФОТ
      }
      if (filterDateFrom && filterDateTo) {
        const days = Math.max(1, Math.round((filterDateTo - filterDateFrom) / 86400));
        const months = days / 30.4;
        return Math.round(monthlyTotal * months);
      }
      if (filterDateFrom && !filterDateTo) {
        const nowTs = Math.floor(Date.now() / 1000);
        const days = Math.max(1, Math.round((nowTs - filterDateFrom) / 86400));
        const months = days / 30.4;
        return Math.round(monthlyTotal * months);
      }
      return monthlyTotal;
    }

    function openFanSalariesModal() {
      const modal = document.getElementById('editFanSalariesModal');
      const container = document.getElementById('fanSalariesListContainer');
      const preview = document.getElementById('fanTotalSalaryPreview');
      if (!container || !modal) return;

      container.innerHTML = '';
      let total = 0;
      FAN_REGISTRY.forEach(f => {
        const sal = getFanSalary(f.id);
        total += sal;
        const row = document.createElement('div');
        row.className = 'flex items-center justify-between p-2 rounded-xl bg-slate-50 border border-slate-200';
        row.innerHTML = `
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-700 text-xs">🎬</span>
            <span class="font-bold text-slate-800 text-xs">${f.name}</span>
          </div>
          <div class="flex items-center space-x-1">
            <input type="number" id="fan_sal_${f.id}" value="${sal}" oninput="recalcFanSalariesPreview()" class="w-24 px-2 py-1 text-xs bg-white border border-slate-200 rounded font-bold text-slate-800 focus:outline-none focus:border-slate-900 text-right">
            <span class="text-xs text-slate-500 font-bold">₸</span>
          </div>
        `;
        container.appendChild(row);
      });

      if (preview) preview.innerText = total.toLocaleString('ru-RU') + ' ₸';
      modal.classList.remove('hidden');
    }

    function closeFanSalariesModal() {
      const modal = document.getElementById('editFanSalariesModal');
      if (modal) modal.classList.add('hidden');
    }

    function recalcFanSalariesPreview() {
      let total = 0;
      FAN_REGISTRY.forEach(f => {
        const input = document.getElementById('fan_sal_' + f.id);
        total += Number(input?.value || 0);
      });
      const preview = document.getElementById('fanTotalSalaryPreview');
      if (preview) preview.innerText = total.toLocaleString('ru-RU') + ' ₸';
    }

    function applyFlatFanSalary() {
      const flat = Number(document.getElementById('inputFlatFanSalary')?.value);
      if (!flat || flat <= 0) return;
      FAN_REGISTRY.forEach(f => {
        const input = document.getElementById('fan_sal_' + f.id);
        if (input) input.value = flat;
      });
      recalcFanSalariesPreview();
    }

    function saveFanSalaries() {
      const map = {};
      FAN_REGISTRY.forEach(f => {
        const input = document.getElementById('fan_sal_' + f.id);
        map[f.id] = Number(input?.value || DEFAULT_FAN_SALARY);
      });
      localStorage.setItem('janamen_fan_salaries', JSON.stringify(map));
      closeFanSalariesModal();
      updateKpis();
      renderMainTable();
    }

    // ============================================================
    // ОБНОВЛЕНИЕ KPI КАРТОЧЕК
    // ============================================================
    function updateKpis() {
      const d = currentChannelData;
      const userRole = CURRENT_USER?.role || 'superadmin';
      const userMgrCode = CURRENT_USER?.manager_code;

      // Все каналы используют единый чистый ряд из 5 карточек (#kpiStandardGrid)
      const stdGrid = document.getElementById('kpiStandardGrid');
      if (stdGrid) stdGrid.classList.remove('hidden');

      let displayLeads = d.leads;
      let displayWon = d.won;
      let displayRev = d.rev;
      let displayClicks = d.clicks;
      let displayAvgCheck = displayWon ? Math.round(displayRev / displayWon) : 0;

      // Если вошел конкретный менеджер (например Анельжан mpb1) — изолируем метрики strictly под нее
      if (currentMainChannel === 'influence' && userRole === 'manager' && userMgrCode) {
        const myMgr = d.influenceManagers?.[userMgrCode] || { leads: 0, won: 0, rev: 0, clicks: 0 };
        displayLeads = myMgr.leads;
        displayWon = myMgr.won;
        displayRev = myMgr.rev;
        displayClicks = myMgr.clicks;
        displayAvgCheck = displayWon ? Math.round(displayRev / displayWon) : 0;
      }

      document.getElementById('kpiTotalLeads').innerText = displayLeads.toLocaleString('ru-RU');
      document.getElementById('kpiWonLeads').innerText = displayWon.toLocaleString('ru-RU');
      document.getElementById('kpiRevenue').innerText = displayRev.toLocaleString('ru-RU') + ' ₸';
      document.getElementById('kpiAvgCheck').innerText = 'Ср. чек: ' + (displayAvgCheck || 0).toLocaleString('ru-RU') + ' ₸';
      
      const inlineClicks = document.getElementById('kpiClicksInline');
      if (inlineClicks) {
        if (displayClicks > 0) {
          inlineClicks.innerText = `${displayClicks.toLocaleString('ru-RU')} переходов`;
        } else {
          inlineClicks.innerText = '0 переходов';
        }
      }
      
      const cr2Pct = displayLeads ? (Math.round(displayWon / displayLeads * 1000) / 10) + '%' : '0%';
      const cr2El = document.getElementById('kpiCr2');
      if (cr2El) cr2El.innerText = 'CR: ' + cr2Pct + ' (Лид ➔ Оплата)';

      // Обновляем блок Выполнения Плана (Точка А ➔ Точка Б)
      updatePlanProgress(displayRev);

      const scopeBadge = document.getElementById('kpiScopeBadge');
      const expenseEl = document.getElementById('kpiExpenses');
      const expenseSubEl = document.getElementById('kpiExpensesSub');
      const expenseLabelEl = document.getElementById('kpiExpenseLabel');
      const romiEl = document.getElementById('kpiRomi');
      const romiSubEl = document.getElementById('kpiRomiSub');
      const romiBadgeEl = document.getElementById('kpiRomiBadge');

      if (currentMainChannel === 'organika') {
        if (scopeBadge) {
          scopeBadge.innerText = 'Органика SMM';
          scopeBadge.className = 'text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700';
        }
        if (expenseEl) expenseEl.innerText = '0 ₸';
        if (expenseSubEl) expenseSubEl.innerText = 'SMM / Соцсети (0 ₸ затрат)';
        if (expenseLabelEl) expenseLabelEl.innerText = 'Расходы SMM';
        
        if (romiEl) {
          romiEl.innerText = '∞ (Органика)';
          romiEl.className = 'text-2xl sm:text-3xl font-extrabold text-emerald-600 mt-1.5 leading-none tracking-tight whitespace-nowrap';
        }
        if (romiSubEl) romiSubEl.innerText = '100% чистый доход (0 ₸ затрат)';
        if (romiBadgeEl) {
          romiBadgeEl.innerText = '100% ЧИСТО';
          romiBadgeEl.className = 'text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/60';
        }

      } else if (currentMainChannel === 'influence') {
        let totalInfExpenses = 0;
        let mgrList = Object.values(d.influenceManagers || {});
        if (userRole === 'manager' && userMgrCode) {
          mgrList = [d.influenceManagers?.[userMgrCode]].filter(Boolean);
          if (scopeBadge) scopeBadge.innerText = `Менеджер ${userMgrCode.toUpperCase()}`;
        } else {
          if (scopeBadge) scopeBadge.innerText = 'Influence';
        }
        if (scopeBadge) scopeBadge.className = 'text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700';

        mgrList.forEach(m => {
          const bList = Object.values(m.bloggers || {});
          bList.forEach(b => {
            const manCost = (b.barter_man || 0) * 62000;
            const womanCost = (b.barter_woman || 0) * 62000;
            const omegaCost = (b.barter_omega || 0) * 62000;
            const aojiruCost = (b.barter_aojiru || 0) * 72000;
            const delCost = b.delivery || 0;
            const feeCost = b.fee || 0;
            totalInfExpenses += (manCost + womanCost + omegaCost + aojiruCost + delCost + feeCost);
          });
        });

        if (expenseLabelEl) expenseLabelEl.innerText = 'Расходы на блогеров';
        if (expenseEl) expenseEl.innerText = totalInfExpenses.toLocaleString('ru-RU') + ' ₸';
        if (expenseSubEl) expenseSubEl.innerText = 'бартер 62k/72k + доставка + фикс';

        if (romiEl) {
          if (totalInfExpenses > 0) {
            const romiVal = Math.round((displayRev - totalInfExpenses) / totalInfExpenses * 100);
            const romiMult = (displayRev / totalInfExpenses).toFixed(1) + 'x';
            romiEl.innerText = (romiVal >= 0 ? '+' : '') + romiVal + '%';
            romiEl.className = `text-2xl sm:text-3xl font-extrabold ${romiVal >= 0 ? 'text-emerald-600' : 'text-rose-600'} mt-1.5 leading-none tracking-tight whitespace-nowrap`;
            if (romiSubEl) romiSubEl.innerText = 'Окупаемость ' + romiMult + ' (выручка vs блогеры)';
            if (romiBadgeEl) {
              romiBadgeEl.innerText = romiVal >= 0 ? 'ПРИБЫЛЬ' : 'УБЫТОК';
              romiBadgeEl.className = `text-[9px] font-bold uppercase px-2 py-0.5 rounded-full ${romiVal >= 0 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200/60' : 'bg-rose-50 text-rose-700 border border-rose-200/60'}`;
            }
          } else {
            romiEl.innerText = '—';
            romiEl.className = 'text-2xl sm:text-3xl font-extrabold text-slate-400 mt-1.5 leading-none tracking-tight whitespace-nowrap';
            if (romiSubEl) romiSubEl.innerText = 'Нет расходов на блогеров';
            if (romiBadgeEl) {
              romiBadgeEl.innerText = 'ROMI';
              romiBadgeEl.className = 'text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700';
            }
          }
        }

      } else if (currentMainChannel === 'fan') {
        if (scopeBadge) {
          scopeBadge.innerText = 'Fan-отдел';
          scopeBadge.className = 'text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700';
        }

        const fanPeriodExpenses = getFanPeriodExpenses();
        if (expenseLabelEl) expenseLabelEl.innerText = 'Расходы на зарплаты';
        if (expenseEl) expenseEl.innerText = fanPeriodExpenses.toLocaleString('ru-RU') + ' ₸';
        if (expenseSubEl) expenseSubEl.innerHTML = `${FAN_REGISTRY.length} сотр. • <button onclick="openFanSalariesModal()" class="font-bold underline text-slate-700 hover:text-slate-900 cursor-pointer">✏️ Настроить ЗП</button>`;

        if (romiEl) {
          if (fanPeriodExpenses > 0) {
            const romiVal = Math.round((displayRev - fanPeriodExpenses) / fanPeriodExpenses * 100);
            const romiMult = (displayRev / fanPeriodExpenses).toFixed(1) + 'x';
            romiEl.innerText = (romiVal >= 0 ? '+' : '') + romiVal + '%';
            romiEl.className = `text-2xl sm:text-3xl font-extrabold ${romiVal >= 0 ? 'text-emerald-600' : 'text-rose-600'} mt-1.5 leading-none tracking-tight whitespace-nowrap`;
            if (romiSubEl) romiSubEl.innerText = 'Окупаемость ' + romiMult + ' (выручка vs ФОТ)';
            if (romiBadgeEl) {
              romiBadgeEl.innerText = romiVal >= 0 ? 'ПРИБЫЛЬ' : 'УБЫТОК';
              romiBadgeEl.className = `text-[9px] font-bold uppercase px-2 py-0.5 rounded-full ${romiVal >= 0 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200/60' : 'bg-rose-50 text-rose-700 border border-rose-200/60'}`;
            }
          } else {
            romiEl.innerText = '—';
            romiEl.className = 'text-2xl sm:text-3xl font-extrabold text-slate-400 mt-1.5 leading-none tracking-tight whitespace-nowrap';
            if (romiSubEl) romiSubEl.innerText = 'ФОТ не задан';
            if (romiBadgeEl) {
              romiBadgeEl.innerText = 'ФОТ';
              romiBadgeEl.className = 'text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700';
            }
          }
        }

      } else if (currentMainChannel === 'all') {
        if (scopeBadge) {
          scopeBadge.innerText = 'Все каналы';
          scopeBadge.className = 'text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700';
        }

        let totalInfExpenses = 0;
        Object.values(d.influenceManagers || {}).forEach(m => {
          Object.values(m.bloggers || {}).forEach(b => {
            const manCost = (b.barter_man || 0) * 62000;
            const womanCost = (b.barter_woman || 0) * 62000;
            const omegaCost = (b.barter_omega || 0) * 62000;
            const aojiruCost = (b.barter_aojiru || 0) * 72000;
            const delCost = b.delivery || 0;
            const feeCost = b.fee || 0;
            totalInfExpenses += (manCost + womanCost + omegaCost + aojiruCost + delCost + feeCost);
          });
        });

        const fanSalaries = getFanPeriodExpenses();
        const totalExpenses = totalInfExpenses + fanSalaries;

        if (expenseLabelEl) expenseLabelEl.innerText = 'Общие расходы';
        if (expenseEl) expenseEl.innerText = totalExpenses.toLocaleString('ru-RU') + ' ₸';
        if (expenseSubEl) expenseSubEl.innerText = 'Блогеры + ФОТ Fan-отдела';

        if (romiEl) {
          if (totalExpenses > 0) {
            const romiVal = Math.round((displayRev - totalExpenses) / totalExpenses * 100);
            const romiMult = (displayRev / totalExpenses).toFixed(1) + 'x';
            romiEl.innerText = (romiVal >= 0 ? '+' : '') + romiVal + '%';
            romiEl.className = `text-2xl sm:text-3xl font-extrabold ${romiVal >= 0 ? 'text-emerald-600' : 'text-rose-600'} mt-1.5 leading-none tracking-tight whitespace-nowrap`;
            if (romiSubEl) romiSubEl.innerText = 'Окупаемость ' + romiMult + ' суммарно';
            if (romiBadgeEl) {
              romiBadgeEl.innerText = romiVal >= 0 ? 'ПРИБЫЛЬ' : 'УБЫТОК';
              romiBadgeEl.className = `text-[9px] font-bold uppercase px-2 py-0.5 rounded-full ${romiVal >= 0 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200/60' : 'bg-rose-50 text-rose-700 border border-rose-200/60'}`;
            }
          } else {
            romiEl.innerText = '—';
            romiEl.className = 'text-2xl sm:text-3xl font-extrabold text-slate-400 mt-1.5 leading-none tracking-tight whitespace-nowrap';
            if (romiSubEl) romiSubEl.innerText = '0 ₸ общих расходов';
          }
        }

      } else if (currentMainChannel === 'tags') {
        if (scopeBadge) {
          scopeBadge.innerText = 'Теги CRM';
          scopeBadge.className = 'text-[9px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-700';
        }
        if (expenseLabelEl) expenseLabelEl.innerText = 'Расходы';
        if (expenseEl) expenseEl.innerText = '0 ₸';
        if (expenseSubEl) expenseSubEl.innerText = 'Теги без прямых затрат';
        if (romiEl) {
          romiEl.innerText = '—';
          romiEl.className = 'text-2xl sm:text-3xl font-extrabold text-slate-400 mt-1.5 leading-none tracking-tight whitespace-nowrap';
        }
        if (romiSubEl) romiSubEl.innerText = 'Маркетинг тегов';
      }
    }

    function renderMainTable() {
      const thead = document.getElementById('mainTableHead');
      const tbody = document.getElementById('mainTableBody');
      const rowBadge = document.getElementById('rowCountBadge');
      const mainTitle = document.getElementById('tableMainTitle');
      const badgeTitle = document.getElementById('tableBadgeTitle');
      const subTitle = document.getElementById('tableMainSubtitle');
      const textSearch = (document.getElementById('filterSearchInput')?.value || '').toLowerCase().trim();

      if (currentMainChannel === 'organika') {
        mainTitle.innerText = '🌿 Органика: SMM (janamen1.kz/smm) & WhatsApp 9828';
        badgeTitle.innerText = 'Канал 1';
        badgeTitle.className = 'px-2 py-0.5 text-[10px] font-black uppercase rounded bg-emerald-100 text-emerald-800';
        subTitle.innerText = 'Официальные UTM-метки: Шапка профиля Instagram, YouTube канал, Чат-бот Direct, Threads, TikTok и WhatsApp 9828';

        thead.innerHTML = `
          <tr>
            <th class="py-3 px-4">Точка входа / Размещение</th>
            <th class="py-3 px-4 text-center">Площадка</th>
            <th class="py-3 px-4 text-center">Кликов (Переходов)</th>
            <th class="py-3 px-4 text-center">Всего заявок (Лидов)</th>
            <th class="py-3 px-4 text-center">CR1 (Клик➔Лид)</th>
            <th class="py-3 px-4 text-center">Оплачено (142)</th>
            <th class="py-3 px-4 text-center">CR2 (Лид➔Оплата)</th>
            <th class="py-3 px-4 text-right">Выручка (₸)</th>
            <th class="py-3 px-4 text-right">Ср. чек (₸)</th>
            <th class="py-3 px-4 text-center">Готовая UTM-ссылка</th>
          </tr>
        `;

        const items = currentChannelData.organikaItems || {};
        let totalRows = 0;
        let html = '';

        const order = ['smm_bio', 'smm_youtube', 'smm_chatbot', 'smm_threads', 'smm_tiktok', 'wa_9828', 'smm_other'];

        order.forEach(k => {
          const item = items[k];
          if (!item) return;

          if (textSearch) {
            const hay = (item.name + ' ' + item.placement + ' ' + item.source + ' ' + item.medium + ' ' + item.campaign).toLowerCase();
            if (!hay.includes(textSearch)) return;
          }

          totalRows++;
          const cr1 = item.clicks ? (Math.round(item.leads / item.clicks * 1000) / 10) + '%' : (item.leads ? '—' : '0%');
          const cr2 = item.leads ? (Math.round(item.won / item.leads * 1000) / 10) + '%' : '0%';
          const avg = item.won ? Math.round(item.rev / item.won) : 0;

          html += `
            <tr class="hover:bg-emerald-50/40 transition text-xs border-b border-slate-100">
              <td class="py-3 px-4 font-bold text-slate-900 flex items-center space-x-2">
                <span>${item.name}</span>
                ${item.leads > 0 ? `<span class="px-2 py-0.5 text-[10px] font-black rounded-full bg-emerald-100 text-emerald-800">${item.leads} лид.</span>` : ''}
              </td>
              <td class="py-3 px-4 text-center">
                <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-slate-100 text-slate-700">${item.placement}</span>
              </td>
              <td class="py-3 px-4 text-center font-bold text-purple-700">${item.clicks ? item.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
              <td class="py-3 px-4 text-center font-black ${item.leads > 0 ? 'text-slate-900 bg-emerald-100/70 rounded' : 'text-slate-400'}">${item.leads.toLocaleString('ru-RU')}</td>
              <td class="py-3 px-4 text-center font-semibold text-slate-600">${cr1}</td>
              <td class="py-3 px-4 text-center font-black ${item.won > 0 ? 'text-emerald-600' : 'text-slate-400'}">${item.won}</td>
              <td class="py-3 px-4 text-center font-semibold ${item.won > 0 ? 'text-emerald-700' : 'text-slate-400'}">${cr2}</td>
              <td class="py-3 px-4 text-right font-black ${item.rev > 0 ? 'text-slate-900' : 'text-slate-400'} whitespace-nowrap">${item.rev.toLocaleString('ru-RU')} ₸</td>
              <td class="py-3 px-4 text-right font-semibold text-slate-600 whitespace-nowrap">${avg ? avg.toLocaleString('ru-RU') + ' ₸' : '—'}</td>
              <td class="py-3 px-4 text-center">
                <div class="inline-flex items-center space-x-1">
                  <button onclick="copyDirectUrl('${item.url}')" title="Скопировать ссылку с UTM" class="px-2.5 py-1 text-[11px] font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-600 hover:text-white rounded-lg border border-emerald-300 transition shadow-2xs">
                    📋 Копировать UTM
                  </button>
                  <a href="${item.url}" target="_blank" title="Открыть ссылку" class="px-1.5 py-1 text-[11px] font-bold text-slate-500 hover:text-slate-800 bg-slate-100 rounded-lg border border-slate-200 transition">
                    ↗
                  </a>
                </div>
              </td>
            </tr>
          `;
        });

        rowBadge.innerText = 'Показано: ' + totalRows + ' точек входа';
        tbody.innerHTML = html;
      } else if (currentMainChannel === 'influence') {
        mainTitle.innerText = '🌟 Influence (Инфлюенс-маркетинг): Менеджеры МПБ & Блогеры';
        badgeTitle.innerText = 'Канал 2';
        badgeTitle.className = 'px-2 py-0.5 text-[10px] font-black uppercase rounded bg-purple-100 text-purple-800';
        subTitle.innerText = 'Свертка по 4 менеджерам МПБ с разворачиванием до каждого блогера из таблицы Google Sheets (93+) и сделок AmoCRM';

        thead.innerHTML = `
          <tr>
            <th class="py-3 px-4">Менеджер / Блогер</th>
            <th class="py-3 px-4 text-center">Площадка / Подписчики / Город</th>
            <th class="py-3 px-4 text-center">Условия / Отправлено</th>
            <th class="py-3 px-4 text-right cursor-pointer select-none group" onclick="toggleExpenseDetails()" title="Нажмите, чтобы свернуть/развернуть детализацию расходов">
              <div class="inline-flex items-center space-x-1.5 justify-end">
                <span class="group-hover:text-purple-700 transition">Расход (₸)</span>
                <span id="expenseToggleBtn" class="text-[9px] px-1.5 py-0.5 rounded font-black ${showExpenseDetails ? 'bg-purple-600 text-white' : 'bg-purple-100 text-purple-800'}">
                  ${showExpenseDetails ? '▲ Свернуть' : '▼ Детали'}
                </span>
              </div>
            </th>
            <th class="py-3 px-4 text-center">Кликов</th>
            <th class="py-3 px-4 text-center">Всего лидов</th>
            <th class="py-3 px-4 text-center">CR1 (Клик➔Лид)</th>
            <th class="py-3 px-4 text-center">Оплачено</th>
            <th class="py-3 px-4 text-center">CR2 (Лид➔Оплата)</th>
            <th class="py-3 px-4 text-right">Выручка (₸)</th>
            <th class="py-3 px-4 text-center">Окупаемость (ROMI)</th>
            <th class="py-3 px-4 text-right">Ср. чек (₸)</th>
            <th class="py-3 px-4 text-center">Instagram & Ссылка</th>
          </tr>
        `;

        const mgrs = currentChannelData.influenceManagers || {};
        let totalRows = 0;
        let html = '';

        const userRole = CURRENT_USER?.role || 'superadmin';
        const userMgrCode = CURRENT_USER?.manager_code;

        let order = ['mpb1', 'mpb2', 'mpb3', 'mpb4', 'other'];
        // Изоляция менеджеров: если вошла Анельжан (mpb1), видит ТОЛЬКО mpb1
        if (userRole === 'manager' && userMgrCode) {
          order = [userMgrCode];
        }

        order.forEach(mCode => {
          const m = mgrs[mCode];
          if (!m) return;

          let bloggersList = Object.values(m.bloggers || {}).sort((a,b) => {
            if (b.leads !== a.leads) return b.leads - a.leads;
            if (b.rev !== a.rev) return b.rev - a.rev;
            return a.name.localeCompare(b.name);
          });

          // ФИЛЬТРАЦИЯ БЛОГЕРОВ ПО ПОИСКОВОМУ ЗАПРОСУ
          if (textSearch) {
            const mHay = (m.name + ' ' + m.code).toLowerCase();
            const managerMatches = mHay.includes(textSearch);

            bloggersList = bloggersList.filter(b => {
              const bHay = [
                b.handle || '',
                b.name || '',
                b.city || '',
                b.subs || '',
                b.manager || ''
              ].join(' ').toLowerCase();
              return managerMatches || bHay.includes(textSearch);
            });

            // Если у менеджера есть совпадения, автоматически раскрываем его список
            if (bloggersList.length > 0) {
              expandedAccordions.add(mCode);
            } else if (!managerMatches) {
              // Если ни менеджер, ни блогеры не совпали — скрываем менеджера
              return;
            }
          }

          const isExpanded = expandedAccordions.has(mCode);
          const bCount = bloggersList.length;
          const activeCount = bloggersList.filter(b => b.leads > 0).length;

          // Расчет расходов команды менеджера
          let mTotalExpense = 0;
          bloggersList.forEach(b => {
            const exp = calculateBloggerExpenses(b);
            mTotalExpense += exp.totalExpense;
          });

          const mCr1 = m.clicks ? (Math.round(m.leads / m.clicks * 1000) / 10) + '%' : (m.leads ? '—' : '0%');
          const mCr2 = m.leads ? (Math.round(m.won / m.leads * 1000) / 10) + '%' : '0%';
          const mAvg = m.won ? Math.round(m.rev / m.won) : 0;

          let mExpDisplay = '';
          if (mTotalExpense > 0) {
            mExpDisplay = `<div class="font-black text-rose-800 text-xs whitespace-nowrap">${mTotalExpense.toLocaleString('ru-RU')} ₸</div>`;
            if (m.rev > 0) {
              const romi = Math.round((m.rev - mTotalExpense) / mTotalExpense * 100);
              mExpDisplay += `<div class="text-[9px] font-black ${romi >= 0 ? 'text-emerald-700' : 'text-rose-600'}">${romi >= 0 ? '+' : ''}${romi}% ROMI</div>`;
            }
          } else {
            mExpDisplay = `<span class="text-slate-400 font-normal">0 ₸</span>`;
          }

          totalRows++;

          // Строка менеджера (Level 1)
          html += `
            <tr onclick="toggleAccordion('${mCode}')" class="bg-purple-50/70 hover:bg-purple-100/70 cursor-pointer transition font-bold border-t-2 border-purple-200">
              <td class="py-3.5 px-4 text-purple-950 flex items-center space-x-2">
                <span class="w-5 h-5 rounded-md bg-purple-600 text-white flex items-center justify-center text-xs transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}">
                  ▶
                </span>
                <span class="text-sm font-black">${m.name}</span>
                <span class="px-2 py-0.5 text-[10px] font-extrabold rounded-full bg-purple-200 text-purple-900">
                  ${bCount} блогеров ${activeCount > 0 ? `(${activeCount} активных)` : ''}
                </span>
              </td>
              <td class="py-3.5 px-4 text-center text-xs text-slate-500 font-medium">Отдел блогеров</td>
              <td class="py-3.5 px-4 text-center text-[10px] text-purple-800 font-bold">Сводка МПБ</td>
              <td class="py-3.5 px-4 text-right">${mExpDisplay}</td>
              <td class="py-3.5 px-4 text-center font-black text-purple-700">${m.clicks ? m.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
              <td class="py-3.5 px-4 text-center font-black text-slate-900">${m.leads.toLocaleString('ru-RU')}</td>
              <td class="py-3.5 px-4 text-center font-bold text-slate-700">${mCr1}</td>
              <td class="py-3.5 px-4 text-center font-black text-emerald-600">${m.won}</td>
              <td class="py-3.5 px-4 text-center font-bold ${m.won > 0 ? 'text-emerald-700 bg-emerald-100/70 rounded' : 'text-slate-400'}">${mCr2}</td>
              <td class="py-3.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${m.rev.toLocaleString('ru-RU')} ₸</td>
              <td class="py-3.5 px-4 text-center font-black whitespace-nowrap">
                ${mTotalExpense > 0 ? `
                  <span class="px-2 py-0.5 rounded-full font-black text-xs ${m.rev >= mTotalExpense ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                    ${m.rev >= mTotalExpense ? '+' : ''}${Math.round((m.rev - mTotalExpense) / mTotalExpense * 100)}% (${(m.rev / mTotalExpense).toFixed(1)}x)
                  </span>
                ` : (m.rev > 0 ? `<span class="px-2 py-0.5 rounded-full font-bold text-xs bg-emerald-100 text-emerald-800">100% (Без затрат)</span>` : `<span class="text-slate-300 font-semibold">—</span>`)}
              </td>
              <td class="py-3.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${mAvg.toLocaleString('ru-RU')} ₸</td>
              <td class="py-3.5 px-4 text-center">
                <button onclick="event.stopPropagation(); copyInfluenceManagerLink('${mCode}')" class="px-2.5 py-1 text-[11px] font-bold text-purple-700 bg-white hover:bg-purple-200 rounded-lg border border-purple-300 transition">
                  📋 Ссылка МПБ
                </button>
              </td>
            </tr>
          `;

          // Дочерние строки блогеров (Level 2)
          if (isExpanded) {
            if (bCount === 0) {
              html += `
                <tr class="bg-white">
                  <td colspan="12" class="py-3 px-8 text-xs text-slate-400 italic">У данного менеджера пока нет лидов/блогеров в базе</td>
                </tr>
              `;
            } else {
              bloggersList.forEach(b => {
                totalRows++;
                const exp = calculateBloggerExpenses(b);
                const bCr1 = b.clicks ? (Math.round(b.leads / b.clicks * 1000) / 10) + '%' : (b.leads ? '—' : '0%');
                const bCr2 = b.leads ? (Math.round(b.won / b.leads * 1000) / 10) + '%' : '0%';
                const bAvg = b.won ? Math.round(b.rev / b.won) : 0;
                const isTested = b.handle === 'aishka_karimova';
                const rowBg = isTested ? 'bg-amber-50/60 hover:bg-amber-100/70' : (b.leads > 0 ? 'bg-emerald-50/30 hover:bg-emerald-100/40' : 'hover:bg-slate-50');

                // Форматирование условий сотрудничества
                const dealBadges = [];
                if (b.paid_cash > 0) dealBadges.push(`<span class="inline-block px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-800 font-bold border border-emerald-200">💵 ${Number(b.paid_cash).toLocaleString('ru-RU')} ₸</span>`);
                const barters = [];
                if (b.barter_man > 0) barters.push(`${b.barter_man} муж.`);
                if (b.barter_woman > 0) barters.push(`${b.barter_woman} жен.`);
                if (b.barter_omega > 0) barters.push(`${b.barter_omega} омега`);
                if (b.barter_aojiru > 0) barters.push(`${b.barter_aojiru} аодз.`);
                if (barters.length > 0) dealBadges.push(`<span class="inline-block px-1.5 py-0.5 rounded bg-purple-50 text-purple-900 font-bold border border-purple-200">🎁 ${barters.join(' + ')}</span>`);
                if (b.delivery_cost > 0) dealBadges.push(`<span class="inline-block px-1.5 py-0.5 rounded bg-blue-50 text-blue-800 font-bold border border-blue-200">🚚 ${Number(b.delivery_cost).toLocaleString('ru-RU')} ₸</span>`);

                const dealHtml = dealBadges.length > 0 ? dealBadges.join('<div class="mt-0.5"></div>') : `<button onclick="event.stopPropagation(); editBloggerExpenses('${b.handle}', '${mCode}')" class="text-[10px] text-purple-600 hover:text-purple-800 underline font-semibold">+ Указать</button>`;

                // Столбец Расход (₸) с детализацией
                let expHtml = '';
                if (exp.totalExpense > 0) {
                  expHtml = `<div class="font-black text-rose-800 whitespace-nowrap text-xs">${exp.totalExpense.toLocaleString('ru-RU')} ₸</div>`;
                  if (showExpenseDetails) {
                    const details = [];
                    if (exp.paidCash > 0) details.push(`💵 гонорар: ${exp.paidCash.toLocaleString('ru-RU')} ₸`);
                    if (exp.deliveryCost > 0) details.push(`🚚 доставка: ${exp.deliveryCost.toLocaleString('ru-RU')} ₸`);
                    if (exp.bMan > 0) details.push(`мужской (${exp.bMan}×62k): ${(exp.bMan * 62000).toLocaleString('ru-RU')} ₸`);
                    if (exp.bWoman > 0) details.push(`женский (${exp.bWoman}×62k): ${(exp.bWoman * 62000).toLocaleString('ru-RU')} ₸`);
                    if (exp.bOmega > 0) details.push(`омега (${exp.bOmega}×62k): ${(exp.bOmega * 62000).toLocaleString('ru-RU')} ₸`);
                    if (exp.bAojiru > 0) details.push(`аодзиру (${exp.bAojiru}×72k): ${(exp.bAojiru * 72000).toLocaleString('ru-RU')} ₸`);
                    expHtml += `
                      <div class="mt-1 text-[9px] text-slate-600 font-medium bg-slate-50 border border-slate-200 rounded p-1.5 text-right space-y-0.5 shadow-2xs">
                        ${details.join('<br>')}
                      </div>
                    `;
                  }
                  if (b.rev > 0) {
                    const diff = b.rev - exp.totalExpense;
                    expHtml += `<div class="text-[9px] font-black ${diff >= 0 ? 'text-emerald-700' : 'text-rose-600'} mt-0.5">${diff >= 0 ? '+' : ''}${diff.toLocaleString('ru-RU')} ₸</div>`;
                  }
                } else {
                  expHtml = `<span class="text-slate-300 font-mono">—</span>`;
                }

                html += `
                  <tr class="${rowBg} transition text-xs border-b border-slate-100">
                    <td class="py-2.5 px-4 pl-10 font-bold text-slate-800 flex items-center space-x-2">
                      <span class="text-slate-300 font-mono">└─</span>
                      <a href="${b.profile || ('https://instagram.com/' + b.handle)}" target="_blank" class="text-purple-700 hover:text-purple-900 font-black hover:underline flex items-center space-x-1">
                        <span>📸</span>
                        <span>@${b.handle}</span>
                      </a>
                      ${b.name && b.name !== b.handle ? `<span class="text-slate-500 font-medium text-[11px]">(${b.name})</span>` : ''}
                      ${isTested ? '<span class="px-1.5 py-0.2 text-[9px] font-black rounded-full bg-amber-200 text-amber-900 animate-pulse">Тестовый лид</span>' : ''}
                      ${b.leads > 0 && !isTested ? `<span class="px-1.5 py-0.2 text-[9px] font-black rounded-full bg-emerald-100 text-emerald-800">${b.leads} лид.</span>` : ''}
                    </td>
                    <td class="py-2.5 px-4 text-center">
                      <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-slate-100 text-slate-700">${b.subs || '—'}</span>
                      ${b.city && b.city !== '—' ? `<span class="text-[10px] text-slate-400 block">${b.city}</span>` : ''}
                    </td>
                    <td class="py-2.5 px-4 text-center text-[10px] font-bold text-slate-700 leading-tight">
                      ${dealHtml}
                    </td>
                    <td class="py-2.5 px-4 text-right">
                      ${expHtml}
                    </td>
                    <td class="py-2.5 px-4 text-center font-bold text-purple-700">${b.clicks ? b.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
                    <td class="py-2.5 px-4 text-center font-black ${b.leads > 0 ? 'text-slate-900 bg-emerald-100/70 rounded' : 'text-slate-400'}">${b.leads.toLocaleString('ru-RU')}</td>
                    <td class="py-2.5 px-4 text-center font-semibold text-slate-600">${bCr1}</td>
                    <td class="py-2.5 px-4 text-center font-black ${b.won > 0 ? 'text-emerald-600' : 'text-slate-400'}">${b.won}</td>
                    <td class="py-2.5 px-4 text-center font-semibold ${b.won > 0 ? 'text-emerald-700' : 'text-slate-400'}">${bCr2}</td>
                    <td class="py-2.5 px-4 text-right font-black ${b.rev > 0 ? 'text-slate-900' : 'text-slate-400'} whitespace-nowrap">${b.rev.toLocaleString('ru-RU')} ₸</td>
                    <td class="py-2.5 px-4 text-center whitespace-nowrap">
                      ${exp.totalExpense > 0 ? `
                        <span class="px-1.5 py-0.5 rounded text-[11px] font-black ${b.rev >= exp.totalExpense ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                          ${b.rev >= exp.totalExpense ? '+' : ''}${Math.round((b.rev - exp.totalExpense) / exp.totalExpense * 100)}%
                        </span>
                        <span class="text-[10px] text-slate-400 font-medium ml-0.5">${(b.rev / exp.totalExpense).toFixed(1)}x</span>
                      ` : (b.rev > 0 ? `<span class="px-1.5 py-0.5 rounded text-[11px] font-bold bg-emerald-50 text-emerald-700">100%</span>` : `<span class="text-slate-300 font-semibold">—</span>`)}
                    </td>
                    <td class="py-2.5 px-4 text-right font-semibold text-slate-600 whitespace-nowrap">${bAvg ? bAvg.toLocaleString('ru-RU') + ' ₸' : '—'}</td>
                    <td class="py-2.5 px-4 text-center">
                      <div class="flex items-center justify-center space-x-1">
                        <button onclick="editBloggerExpenses('${b.handle}', '${mCode}')" title="Редактировать условия и витамины" class="px-2 py-0.5 text-[10px] font-bold text-purple-700 hover:text-white bg-purple-50 hover:bg-purple-600 rounded border border-purple-200 transition">
                          ✏️ Условия
                        </button>
                        <button onclick="copyBloggerDirectLink('${b.handle}', '${mCode}')" title="Скопировать трекинг-ссылку блогера" class="px-2 py-0.5 text-[10px] font-bold text-purple-700 hover:text-white bg-purple-50 hover:bg-purple-600 rounded border border-purple-200 transition">
                          🔗 Ссылка
                        </button>
                        ${(CURRENT_USER && (CURRENT_USER.role === 'superadmin' || (CURRENT_USER.email && (CURRENT_USER.email.includes('saidullayev') || CURRENT_USER.email === 'admin')))) ? `
                          <button onclick="event.stopPropagation(); deleteBloggerByAdmin('${b.handle}')" title="Удалить блогера (только для владельца)" class="px-2 py-0.5 text-[10px] font-bold text-rose-600 hover:text-white bg-rose-50 hover:bg-rose-600 rounded border border-rose-200 transition">
                            🗑️
                          </button>
                        ` : ''}
                      </div>
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
        mainTitle.innerText = '🎬 Fan-отдел: Сквозная аналитика & Зарплаты';
        badgeTitle.innerText = 'Канал 3';
        badgeTitle.className = 'px-2 py-0.5 text-[10px] font-bold uppercase rounded-full bg-slate-100 text-slate-700';
        subTitle.innerText = 'Сотрудники Fan-команды, площадки TikTok / Instagram / YouTube, оклады и расчет окупаемости (ROMI)';

        thead.innerHTML = `
          <tr class="text-[11px] font-bold text-slate-500 uppercase tracking-wider bg-slate-50/80 border-b border-slate-200">
            <th class="py-3 px-4 text-left">МЕНЕДЖЕР / СОТРУДНИК</th>
            <th class="py-3 px-4 text-center">ПЛОЩАДКА</th>
            <th class="py-3 px-4 text-center">КЛИКОВ</th>
            <th class="py-3 px-4 text-center">ЗАЯВОК</th>
            <th class="py-3 px-4 text-center">ОПЛАЧЕНО</th>
            <th class="py-3 px-4 text-center">CR (ЛИД➔ОПЛАТА)</th>
            <th class="py-3 px-4 text-right">ВЫРУЧКА (₸)</th>
            <th class="py-3 px-4 text-right">ЗАРПЛАТА (₸)</th>
            <th class="py-3 px-4 text-center">ОКУПАЕМОСТЬ</th>
            <th class="py-3 px-4 text-center">UTM & ССЫЛКИ</th>
          </tr>
        `;

        const fans = currentChannelData.fanAccounts || {};
        let totalRows = 0;
        let html = '';

        // 8 официальных сотрудников команды
        FAN_REGISTRY.forEach(fReg => {
          const f = fans[fReg.id];
          if (!f) return;

          if (textSearch) {
            const fHay = (fReg.name + ' ' + fReg.id + ' ' + fReg.platforms.map(p => p.name + ' ' + p.url + ' ' + p.profile).join(' ')).toLowerCase();
            if (!fHay.includes(textSearch)) return;
            expandedAccordions.add(fReg.id);
          }

          const isExpanded = expandedAccordions.has(fReg.id);
          const platformsList = fReg.platforms;
          const pCount = platformsList.length;

          const fCr2 = f.leads ? (Math.round(f.won / f.leads * 1000) / 10) + '%' : '0%';
          const salary = getFanSalary(fReg.id);
          
          let romiBadgeHtml = '<span class="text-slate-400 text-xs">—</span>';
          if (salary > 0) {
            if (f.rev > 0) {
              const rVal = Math.round((f.rev - salary) / salary * 100);
              const rMult = (f.rev / salary).toFixed(1) + 'x';
              romiBadgeHtml = `<span class="px-2 py-0.5 text-[10px] font-bold rounded-full ${rVal >= 0 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200/60' : 'bg-rose-50 text-rose-700 border border-rose-200/60'}">${rMult} (${rVal >= 0 ? '+' : ''}${rVal}%)</span>`;
            } else {
              romiBadgeHtml = '<span class="text-[11px] font-medium text-slate-400">0x (0 ₸)</span>';
            }
          }

          totalRows++;

          // Строка сотрудника (Level 1)
          html += `
            <tr onclick="toggleAccordion('${fReg.id}')" class="bg-slate-50/70 hover:bg-slate-100/70 cursor-pointer transition font-bold border-t border-slate-200">
              <td class="py-3 px-4 text-slate-900 flex items-center space-x-2">
                <span class="w-5 h-5 rounded-md bg-slate-200 text-slate-700 flex items-center justify-center text-xs transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}">
                  ▶
                </span>
                <span class="text-sm font-extrabold text-slate-900">${f.name}</span>
                <span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-slate-200 text-slate-700">
                  ${pCount} площ.
                </span>
              </td>
              <td class="py-3 px-4 text-center text-xs text-slate-500 font-semibold">Все площадки</td>
              <td class="py-3 px-4 text-center font-bold text-slate-700">${f.clicks ? f.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
              <td class="py-3 px-4 text-center font-extrabold text-slate-900">${f.leads.toLocaleString('ru-RU')}</td>
              <td class="py-3 px-4 text-center font-extrabold text-slate-900">${f.won}</td>
              <td class="py-3 px-4 text-center font-semibold text-slate-700">${fCr2}</td>
              <td class="py-3 px-4 text-right font-extrabold text-slate-900 whitespace-nowrap">${f.rev.toLocaleString('ru-RU')} ₸</td>
              <td class="py-3 px-4 text-right font-extrabold text-slate-800 whitespace-nowrap">
                <span>${salary.toLocaleString('ru-RU')} ₸</span>
                <button onclick="event.stopPropagation(); openFanSalariesModal()" title="Изменить оклад" class="ml-1 text-[11px] text-slate-400 hover:text-slate-700 cursor-pointer">✏️</button>
              </td>
              <td class="py-3 px-4 text-center">${romiBadgeHtml}</td>
              <td class="py-3 px-4 text-center">
                <button onclick="event.stopPropagation(); copyFanAllLinks('${fReg.id}')" class="px-2.5 py-1 text-[11px] font-semibold text-slate-700 bg-white hover:bg-slate-100 rounded-lg border border-slate-200 transition shadow-2xs cursor-pointer">
                  📋 Ссылки
                </button>
              </td>
            </tr>
          `;

          // Дочерние площадки
          if (isExpanded) {
            platformsList.forEach(p => {
              totalRows++;
              const pData = f.platforms[p.name.toLowerCase()] || { leads: 0, won: 0, rev: 0, clicks: 0 };
              const pCr2 = pData.leads ? (Math.round(pData.won / pData.leads * 1000) / 10) + '%' : '0%';
              const hasProfile = p.profile && p.profile.startsWith('http');

              html += `
                <tr class="hover:bg-slate-50 transition text-xs border-b border-slate-100">
                  <td class="py-2.5 px-4 pl-10 font-bold text-slate-800 flex items-center space-x-2">
                    <span class="text-slate-300 font-mono">└─</span>
                    <span class="text-sm leading-none">${p.icon}</span>
                    <span class="text-slate-800 font-semibold">${p.name}</span>
                  </td>
                  <td class="py-2.5 px-4 text-center text-xs font-mono text-slate-600 font-medium">${p.name.toLowerCase()}</td>
                  <td class="py-2.5 px-4 text-center font-semibold text-slate-600">${pData.clicks ? pData.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
                  <td class="py-2.5 px-4 text-center font-bold text-slate-800">${pData.leads.toLocaleString('ru-RU')}</td>
                  <td class="py-2.5 px-4 text-center font-bold text-slate-900">${pData.won}</td>
                  <td class="py-2.5 px-4 text-center font-semibold text-slate-600">${pCr2}</td>
                  <td class="py-2.5 px-4 text-right font-bold text-slate-900 whitespace-nowrap">${pData.rev.toLocaleString('ru-RU')} ₸</td>
                  <td class="py-2.5 px-4 text-center text-slate-300">—</td>
                  <td class="py-2.5 px-4 text-center text-slate-300">—</td>
                  <td class="py-2.5 px-4 text-center flex items-center justify-center space-x-1.5">
                    ${hasProfile ? `<a href="${p.profile}" target="_blank" title="Открыть профиль" class="px-2 py-0.5 text-[10px] font-medium text-slate-600 hover:text-slate-900 bg-white rounded border border-slate-200 transition">👤 Профиль</a>` : ''}
                    <button onclick="copyFanPlatformLink('${p.url}')" title="Скопировать готовую ссылку с меткой" class="px-2 py-0.5 text-[10px] font-semibold text-slate-700 hover:text-slate-900 bg-white hover:bg-slate-50 rounded border border-slate-200 transition shadow-2xs cursor-pointer">
                      📋 UTM
                    </button>
                  </td>
                </tr>
              `;
            });
          }
        });
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
        // ============================================================
        // ВСЕ КАНАЛЫ (СВОДКА В ТОЧНО ТАКОМ ЖЕ ВИДЕ: ОРГАНИКА + INFLUENCE + FAN)
        // ============================================================
        mainTitle.innerText = '📊 Все каналы (Сквозная аналитика): Органика · Инфлюенс · Фан-сетка';
        badgeTitle.innerText = 'Все каналы';
        badgeTitle.className = 'px-2 py-0.5 text-[10px] font-black uppercase rounded bg-brand-100 text-brand-900 border border-brand-300';
        subTitle.innerText = 'Единый сквозной срез по всем источникам трафика Jana Men в единой иерархической структуре';

        thead.innerHTML = `
          <tr>
            <th class="py-3 px-4">Канал / Направление / Менеджер / Блогер</th>
            <th class="py-3 px-4 text-center">Тип / Площадка</th>
            <th class="py-3 px-4 text-center">Условия / Расход</th>
            <th class="py-3 px-4 text-center">Кликов</th>
            <th class="py-3 px-4 text-center">Лидов</th>
            <th class="py-3 px-4 text-center">CR1 (Клик➔Лид)</th>
            <th class="py-3 px-4 text-center">Оплачено (142)</th>
            <th class="py-3 px-4 text-center">CR2 (Лид➔Оплата)</th>
            <th class="py-3 px-4 text-right">Выручка (₸)</th>
            <th class="py-3 px-4 text-center">Окупаемость (ROMI)</th>
            <th class="py-3 px-4 text-right">Ср. чек (₸)</th>
            <th class="py-3 px-4 text-center">Ссылка / Действие</th>
          </tr>
        `;

        let totalRows = 0;
        let html = '';

        // -------------------------------------------------------------
        // РАЗДЕЛ 1: ОРГАНИКА (SMM & WA 9828)
        // -------------------------------------------------------------
        const orgItems = currentChannelData.organikaItems || {};
        let orgLeads = 0, orgWon = 0, orgRev = 0, orgClicks = 0;
        Object.values(orgItems).forEach(i => {
          orgLeads += i.leads; orgWon += i.won; orgRev += i.rev; orgClicks += i.clicks;
        });
        const orgCr1 = orgClicks ? (Math.round(orgLeads / orgClicks * 1000) / 10) + '%' : (orgLeads ? '—' : '0%');
        const orgCr2 = orgLeads ? (Math.round(orgWon / orgLeads * 1000) / 10) + '%' : '0%';
        const orgAvg = orgWon ? Math.round(orgRev / orgWon) : 0;
        const isOrgExpanded = expandedAccordions.has('all_section_organika');

        totalRows++;
        html += `
          <tr onclick="toggleAccordion('all_section_organika')" class="bg-emerald-50/80 hover:bg-emerald-100/80 cursor-pointer transition font-bold border-t-2 border-emerald-300">
            <td class="py-3.5 px-4 text-emerald-950 flex items-center space-x-2">
              <span class="w-5 h-5 rounded-md bg-emerald-600 text-white flex items-center justify-center text-xs transition-transform duration-200 ${isOrgExpanded ? 'rotate-90' : ''}">▶</span>
              <span class="text-sm font-black">🌿 КАНАЛ 1: Органика (SMM /smm & WhatsApp 9828)</span>
              <span class="px-2 py-0.5 text-[10px] font-extrabold rounded-full bg-emerald-200 text-emerald-900">6 точек входа</span>
            </td>
            <td class="py-3.5 px-4 text-center text-xs font-semibold text-emerald-800">Соцсети & WA</td>
            <td class="py-3.5 px-4 text-center text-xs text-slate-400 font-medium">Бесплатно (SMM)</td>
            <td class="py-3.5 px-4 text-center font-black text-purple-700">${orgClicks ? orgClicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
            <td class="py-3.5 px-4 text-center font-black text-slate-900">${orgLeads.toLocaleString('ru-RU')}</td>
            <td class="py-3.5 px-4 text-center font-bold text-slate-700">${orgCr1}</td>
            <td class="py-3.5 px-4 text-center font-black text-emerald-600">${orgWon}</td>
            <td class="py-3.5 px-4 text-center font-bold ${orgWon > 0 ? 'text-emerald-700 bg-emerald-100/70 rounded' : 'text-slate-400'}">${orgCr2}</td>
            <td class="py-3.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${orgRev.toLocaleString('ru-RU')} ₸</td>
            <td class="py-3.5 px-4 text-center font-black">
              <span class="px-2 py-0.5 text-xs font-black rounded-full bg-emerald-100 text-emerald-800">∞ (Органика 100%)</span>
            </td>
            <td class="py-3.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${orgAvg.toLocaleString('ru-RU')} ₸</td>
            <td class="py-3.5 px-4 text-center">
              <button onclick="event.stopPropagation(); switchMainChannel('organika')" class="px-2.5 py-1 text-[11px] font-bold text-emerald-800 bg-white hover:bg-emerald-100 rounded-lg border border-emerald-300 transition">
                Перейти в канал
              </button>
            </td>
          </tr>
        `;

        if (isOrgExpanded) {
          ['smm_bio', 'smm_youtube', 'smm_chatbot', 'smm_threads', 'smm_tiktok', 'wa_9828', 'smm_other'].forEach(k => {
            const item = orgItems[k];
            if (!item) return;
            totalRows++;
            const cr1 = item.clicks ? (Math.round(item.leads / item.clicks * 1000) / 10) + '%' : (item.leads ? '—' : '0%');
            const cr2 = item.leads ? (Math.round(item.won / item.leads * 1000) / 10) + '%' : '0%';
            const avg = item.won ? Math.round(item.rev / item.won) : 0;
            html += `
              <tr class="hover:bg-slate-50 transition text-xs border-b border-slate-100">
                <td class="py-2.5 px-4 pl-10 font-bold text-slate-800 flex items-center space-x-2">
                  <span class="text-slate-300 font-mono">└─</span>
                  <span>${item.name}</span>
                </td>
                <td class="py-2.5 px-4 text-center text-[10px] text-slate-500 font-medium">${item.placement}</td>
                <td class="py-2.5 px-4 text-center text-slate-400 font-mono text-[10px]">—</td>
                <td class="py-2.5 px-4 text-center font-bold text-purple-700">${item.clicks ? item.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
                <td class="py-2.5 px-4 text-center font-black ${item.leads > 0 ? 'text-slate-900 bg-emerald-100/70 rounded' : 'text-slate-400'}">${item.leads.toLocaleString('ru-RU')}</td>
                <td class="py-2.5 px-4 text-center font-semibold text-slate-600">${cr1}</td>
                <td class="py-2.5 px-4 text-center font-black ${item.won > 0 ? 'text-emerald-600' : 'text-slate-400'}">${item.won}</td>
                <td class="py-2.5 px-4 text-center font-semibold ${item.won > 0 ? 'text-emerald-700' : 'text-slate-400'}">${cr2}</td>
                <td class="py-2.5 px-4 text-right font-black ${item.rev > 0 ? 'text-slate-900' : 'text-slate-400'} whitespace-nowrap">${item.rev.toLocaleString('ru-RU')} ₸</td>
                <td class="py-2.5 px-4 text-center font-medium text-emerald-700 text-xs">100% (Без затрат)</td>
                <td class="py-2.5 px-4 text-right font-semibold text-slate-600 whitespace-nowrap">${avg ? avg.toLocaleString('ru-RU') + ' ₸' : '—'}</td>
                <td class="py-2.5 px-4 text-center">
                  <button onclick="copyDirectUrl('${item.url}')" class="px-2 py-0.5 text-[10px] font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-600 hover:text-white rounded border border-emerald-300 transition">
                    📋 UTM
                  </button>
                </td>
              </tr>
            `;
          });
        }

        // -------------------------------------------------------------
        // РАЗДЕЛ 2: INFLUENCE (МЕНЕДЖЕРЫ МПБ & БЛОГЕРЫ)
        // -------------------------------------------------------------
        const infMgrs = currentChannelData.influenceManagers || {};
        let infLeads = 0, infWon = 0, infRev = 0, infClicks = 0, infExpenses = 0, infBloggersCount = 0;
        Object.values(infMgrs).forEach(m => {
          infLeads += m.leads; infWon += m.won; infRev += m.rev; infClicks += m.clicks;
          const bList = Object.values(m.bloggers || {});
          infBloggersCount += bList.length;
          bList.forEach(b => {
            const exp = calculateBloggerExpenses(b);
            infExpenses += exp.totalExpense;
          });
        });
        const infCr1 = infClicks ? (Math.round(infLeads / infClicks * 1000) / 10) + '%' : (infLeads ? '—' : '0%');
        const infCr2 = infLeads ? (Math.round(infWon / infLeads * 1000) / 10) + '%' : '0%';
        const infAvg = infWon ? Math.round(infRev / infWon) : 0;
        const isInfExpanded = expandedAccordions.has('all_section_influence');

        totalRows++;
        html += `
          <tr onclick="toggleAccordion('all_section_influence')" class="bg-purple-50/80 hover:bg-purple-100/80 cursor-pointer transition font-bold border-t-2 border-purple-300">
            <td class="py-3.5 px-4 text-purple-950 flex items-center space-x-2">
              <span class="w-5 h-5 rounded-md bg-purple-600 text-white flex items-center justify-center text-xs transition-transform duration-200 ${isInfExpanded ? 'rotate-90' : ''}">▶</span>
              <span class="text-sm font-black">🌟 КАНАЛ 2: Influence (Менеджеры МПБ & Блогеры)</span>
              <span class="px-2 py-0.5 text-[10px] font-extrabold rounded-full bg-purple-200 text-purple-900">${infBloggersCount} блогеров</span>
            </td>
            <td class="py-3.5 px-4 text-center text-xs font-semibold text-purple-800">4 менеджера МПБ</td>
            <td class="py-3.5 px-4 text-center font-black text-rose-800 text-xs">${infExpenses > 0 ? (infExpenses.toLocaleString('ru-RU') + ' ₸') : '—'}</td>
            <td class="py-3.5 px-4 text-center font-black text-purple-700">${infClicks ? infClicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
            <td class="py-3.5 px-4 text-center font-black text-slate-900">${infLeads.toLocaleString('ru-RU')}</td>
            <td class="py-3.5 px-4 text-center font-bold text-slate-700">${infCr1}</td>
            <td class="py-3.5 px-4 text-center font-black text-emerald-600">${infWon}</td>
            <td class="py-3.5 px-4 text-center font-bold ${infWon > 0 ? 'text-emerald-700 bg-emerald-100/70 rounded' : 'text-slate-400'}">${infCr2}</td>
            <td class="py-3.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${infRev.toLocaleString('ru-RU')} ₸</td>
            <td class="py-3.5 px-4 text-center font-black">
              ${infExpenses > 0 ? `
                <span class="px-2 py-0.5 text-xs font-black rounded-full ${infRev >= infExpenses ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                  ${infRev >= infExpenses ? '+' : ''}${Math.round((infRev - infExpenses) / infExpenses * 100)}% (${(infRev / infExpenses).toFixed(1)}x)
                </span>
              ` : (infRev > 0 ? `<span class="px-2 py-0.5 text-xs font-bold rounded-full bg-emerald-100 text-emerald-800">100%</span>` : `<span class="text-slate-300 font-semibold">—</span>`)}
            </td>
            <td class="py-3.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${infAvg.toLocaleString('ru-RU')} ₸</td>
            <td class="py-3.5 px-4 text-center">
              <button onclick="event.stopPropagation(); switchMainChannel('influence')" class="px-2.5 py-1 text-[11px] font-bold text-purple-700 bg-white hover:bg-purple-100 rounded-lg border border-purple-300 transition">
                Перейти в канал
              </button>
            </td>
          </tr>
        `;

        if (isInfExpanded) {
          // Если залогинен конкретный менеджер — показываем только его отдел
          const userRole = CURRENT_USER?.role || 'superadmin';
          const userMgrCode = CURRENT_USER?.manager_code;
          let mgrOrder = ['mpb1', 'mpb2', 'mpb3', 'mpb4', 'other'];
          if (userRole === 'manager' && userMgrCode) {
            mgrOrder = [userMgrCode];
          }

          mgrOrder.forEach(mCode => {
            const m = infMgrs[mCode];
            if (!m) return;
            const bList = Object.values(m.bloggers || {});
            let mExp = 0;
            bList.forEach(b => { mExp += calculateBloggerExpenses(b).totalExpense; });
            const mCr1 = m.clicks ? (Math.round(m.leads / m.clicks * 1000) / 10) + '%' : (m.leads ? '—' : '0%');
            const mCr2 = m.leads ? (Math.round(m.won / m.leads * 1000) / 10) + '%' : '0%';
            const mAvg = m.won ? Math.round(m.rev / m.won) : 0;
            const isMgrExp = expandedAccordions.has('all_mgr_' + mCode);

            totalRows++;
            html += `
              <tr onclick="toggleAccordion('all_mgr_${mCode}')" class="bg-purple-50/40 hover:bg-purple-100/40 cursor-pointer transition text-xs border-b border-purple-100 font-bold">
                <td class="py-2.5 px-4 pl-8 flex items-center space-x-2 text-purple-900">
                  <span class="w-4 h-4 rounded bg-purple-200 text-purple-800 flex items-center justify-center text-[10px] ${isMgrExp ? 'rotate-90' : ''}">▶</span>
                  <span class="font-extrabold">${m.name}</span>
                  <span class="text-[10px] text-purple-600">(${bList.length} блог.)</span>
                </td>
                <td class="py-2.5 px-4 text-center text-slate-500 font-medium">Менеджер МПБ</td>
                <td class="py-2.5 px-4 text-center font-bold text-rose-700">${mExp > 0 ? (mExp.toLocaleString('ru-RU') + ' ₸') : '—'}</td>
                <td class="py-2.5 px-4 text-center font-bold text-purple-700">${m.clicks ? m.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
                <td class="py-2.5 px-4 text-center font-black text-slate-900">${m.leads.toLocaleString('ru-RU')}</td>
                <td class="py-2.5 px-4 text-center font-semibold text-slate-600">${mCr1}</td>
                <td class="py-2.5 px-4 text-center font-black ${m.won > 0 ? 'text-emerald-600' : 'text-slate-400'}">${m.won}</td>
                <td class="py-2.5 px-4 text-center font-semibold ${m.won > 0 ? 'text-emerald-700' : 'text-slate-400'}">${mCr2}</td>
                <td class="py-2.5 px-4 text-right font-black text-slate-900">${m.rev.toLocaleString('ru-RU')} ₸</td>
                <td class="py-2.5 px-4 text-center font-bold whitespace-nowrap">
                  ${mExp > 0 ? `
                    <span class="px-1.5 py-0.5 rounded text-[11px] font-black ${m.rev >= mExp ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                      ${m.rev >= mExp ? '+' : ''}${Math.round((m.rev - mExp) / mExp * 100)}% (${(m.rev / mExp).toFixed(1)}x)
                    </span>
                  ` : (m.rev > 0 ? `<span class="px-1.5 py-0.5 rounded text-[11px] font-bold bg-emerald-50 text-emerald-700">100%</span>` : `<span class="text-slate-300 font-semibold">—</span>`)}
                </td>
                <td class="py-2.5 px-4 text-right font-semibold text-slate-600">${mAvg ? mAvg.toLocaleString('ru-RU') + ' ₸' : '—'}</td>
                <td class="py-2.5 px-4 text-center">
                  <button onclick="event.stopPropagation(); copyInfluenceManagerLink('${mCode}')" class="px-2 py-0.5 text-[10px] font-bold text-purple-700 bg-white rounded border border-purple-200">
                    📋 Ссылка
                  </button>
                </td>
              </tr>
            `;

            if (isMgrExp) {
              bList.forEach(b => {
                totalRows++;
                const exp = calculateBloggerExpenses(b);
                const bCr1 = b.clicks ? (Math.round(b.leads / b.clicks * 1000) / 10) + '%' : (b.leads ? '—' : '0%');
                const bCr2 = b.leads ? (Math.round(b.won / b.leads * 1000) / 10) + '%' : '0%';
                const bAvg = b.won ? Math.round(b.rev / b.won) : 0;
                html += `
                  <tr class="hover:bg-slate-50 transition text-xs border-b border-slate-100">
                    <td class="py-2 px-4 pl-14 font-medium text-slate-800 flex items-center space-x-1.5">
                      <span class="text-slate-300 font-mono">└─</span>
                      <a href="${b.profile || ('https://instagram.com/' + b.handle)}" target="_blank" class="font-bold text-purple-700 hover:underline">@${b.handle}</a>
                      ${b.name && b.name !== b.handle ? `<span class="text-slate-400 text-[10px]">(${b.name})</span>` : ''}
                    </td>
                    <td class="py-2 px-4 text-center text-slate-500 text-[10px]">${b.subs || '—'} · ${b.city || '—'}</td>
                    <td class="py-2 px-4 text-center text-rose-700 font-bold text-[10px]">${exp.totalExpense > 0 ? (exp.totalExpense.toLocaleString('ru-RU') + ' ₸') : '—'}</td>
                    <td class="py-2 px-4 text-center font-bold text-purple-700">${b.clicks ? b.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
                    <td class="py-2 px-4 text-center font-black ${b.leads > 0 ? 'text-slate-900 bg-emerald-100/70 rounded' : 'text-slate-400'}">${b.leads.toLocaleString('ru-RU')}</td>
                    <td class="py-2 px-4 text-center font-semibold text-slate-600">${bCr1}</td>
                    <td class="py-2 px-4 text-center font-black ${b.won > 0 ? 'text-emerald-600' : 'text-slate-400'}">${b.won}</td>
                    <td class="py-2 px-4 text-center font-semibold ${b.won > 0 ? 'text-emerald-700' : 'text-slate-400'}">${bCr2}</td>
                    <td class="py-2 px-4 text-right font-black ${b.rev > 0 ? 'text-slate-900' : 'text-slate-400'}">${b.rev.toLocaleString('ru-RU')} ₸</td>
                    <td class="py-2 px-4 text-center whitespace-nowrap">
                      ${exp.totalExpense > 0 ? `
                        <span class="px-1.5 py-0.5 rounded text-[10px] font-black ${b.rev >= exp.totalExpense ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                          ${b.rev >= exp.totalExpense ? '+' : ''}${Math.round((b.rev - exp.totalExpense) / exp.totalExpense * 100)}%
                        </span>
                        <span class="text-[10px] text-slate-400 font-medium ml-0.5">${(b.rev / exp.totalExpense).toFixed(1)}x</span>
                      ` : (b.rev > 0 ? `<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700">100%</span>` : `<span class="text-slate-300 font-semibold">—</span>`)}
                    </td>
                    <td class="py-2 px-4 text-right font-semibold text-slate-600">${bAvg ? bAvg.toLocaleString('ru-RU') + ' ₸' : '—'}</td>
                    <td class="py-2 px-4 text-center">
                      <button onclick="copyBloggerDirectLink('${b.handle}', '${mCode}')" class="px-2 py-0.5 text-[10px] font-bold text-purple-700 bg-purple-50 rounded border border-purple-200">
                        🔗 Ссылка
                      </button>
                    </td>
                  </tr>
                `;
              });
            }
          });
        }

        // -------------------------------------------------------------
        // РАЗДЕЛ 3: FAN (ФАН-АККАУНТЫ СЕТКИ)
        // -------------------------------------------------------------
        const fanAccs = currentChannelData.fanAccounts || {};
        let fanLeads = 0, fanWon = 0, fanRev = 0, fanClicks = 0;
        Object.values(fanAccs).forEach(f => {
          fanLeads += f.leads; fanWon += f.won; fanRev += f.rev; fanClicks += f.clicks;
        });
        const fanCr1 = fanClicks ? (Math.round(fanLeads / fanClicks * 1000) / 10) + '%' : (fanLeads ? '—' : '0%');
        const fanCr2 = fanLeads ? (Math.round(fanWon / fanLeads * 1000) / 10) + '%' : '0%';
        const fanAvg = fanWon ? Math.round(fanRev / fanWon) : 0;
        const isFanExpanded = expandedAccordions.has('all_section_fan');

        totalRows++;
        html += `
          <tr onclick="toggleAccordion('all_section_fan')" class="bg-indigo-50/80 hover:bg-indigo-100/80 cursor-pointer transition font-bold border-t-2 border-indigo-300">
            <td class="py-3.5 px-4 text-indigo-950 flex items-center space-x-2">
              <span class="w-5 h-5 rounded-md bg-indigo-600 text-white flex items-center justify-center text-xs transition-transform duration-200 ${isFanExpanded ? 'rotate-90' : ''}">▶</span>
              <span class="text-sm font-black">🎬 КАНАЛ 3: Fan (Фан-аккаунты сетки)</span>
              <span class="px-2 py-0.5 text-[10px] font-extrabold rounded-full bg-indigo-200 text-indigo-900">8 аккаунтов</span>
            </td>
            <td class="py-3.5 px-4 text-center text-xs font-semibold text-indigo-800">TikTok · Insta · YouTube</td>
            <td class="py-3.5 px-4 text-center text-xs text-slate-400 font-medium">Контент-сетка</td>
            <td class="py-3.5 px-4 text-center font-black text-indigo-700">${fanClicks ? fanClicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
            <td class="py-3.5 px-4 text-center font-black text-slate-900">${fanLeads.toLocaleString('ru-RU')}</td>
            <td class="py-3.5 px-4 text-center font-bold text-slate-700">${fanCr1}</td>
            <td class="py-3.5 px-4 text-center font-black text-emerald-600">${fanWon}</td>
            <td class="py-3.5 px-4 text-center font-bold ${fanWon > 0 ? 'text-emerald-700 bg-emerald-100/70 rounded' : 'text-slate-400'}">${fanCr2}</td>
            <td class="py-3.5 px-4 text-right font-black text-slate-900 whitespace-nowrap">${fanRev.toLocaleString('ru-RU')} ₸</td>
            <td class="py-3.5 px-4 text-center font-black">
              <span class="px-2 py-0.5 text-xs font-black rounded-full bg-emerald-100 text-emerald-800">∞ (Органика 100%)</span>
            </td>
            <td class="py-3.5 px-4 text-right font-semibold text-slate-700 whitespace-nowrap">${fanAvg.toLocaleString('ru-RU')} ₸</td>
            <td class="py-3.5 px-4 text-center">
              <button onclick="event.stopPropagation(); switchMainChannel('fan')" class="px-2.5 py-1 text-[11px] font-bold text-indigo-700 bg-white hover:bg-indigo-100 rounded-lg border border-indigo-300 transition">
                Перейти в канал
              </button>
            </td>
          </tr>
        `;

        if (isFanExpanded) {
          FAN_REGISTRY.forEach(fReg => {
            const f = fanAccs[fReg.id];
            if (!f) return;
            const isFExp = expandedAccordions.has('all_fan_' + fReg.id);
            const fCr1 = f.clicks ? (Math.round(f.leads / f.clicks * 1000) / 10) + '%' : (f.leads ? '—' : '0%');
            const fCr2 = f.leads ? (Math.round(f.won / f.leads * 1000) / 10) + '%' : '0%';
            const fAvg = f.won ? Math.round(f.rev / f.won) : 0;
            totalRows++;
            html += `
              <tr onclick="toggleAccordion('all_fan_${fReg.id}')" class="bg-indigo-50/40 hover:bg-indigo-100/40 cursor-pointer transition text-xs border-b border-indigo-100 font-bold">
                <td class="py-2.5 px-4 pl-8 flex items-center space-x-2 text-indigo-900">
                  <span class="w-4 h-4 rounded bg-indigo-200 text-indigo-800 flex items-center justify-center text-[10px] ${isFExp ? 'rotate-90' : ''}">▶</span>
                  <span class="font-extrabold">${f.name}</span>
                </td>
                <td class="py-2.5 px-4 text-center text-slate-500 font-medium">Фан-аккаунт</td>
                <td class="py-2.5 px-4 text-center text-slate-400 font-mono text-[10px]">—</td>
                <td class="py-2.5 px-4 text-center font-bold text-indigo-700">${f.clicks ? f.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
                <td class="py-2.5 px-4 text-center font-black text-slate-900">${f.leads.toLocaleString('ru-RU')}</td>
                <td class="py-2.5 px-4 text-center font-semibold text-slate-600">${fCr1}</td>
                <td class="py-2.5 px-4 text-center font-black ${f.won > 0 ? 'text-emerald-600' : 'text-slate-400'}">${f.won}</td>
                <td class="py-2.5 px-4 text-center font-semibold ${f.won > 0 ? 'text-emerald-700' : 'text-slate-400'}">${fCr2}</td>
                <td class="py-2.5 px-4 text-right font-black text-slate-900">${f.rev.toLocaleString('ru-RU')} ₸</td>
                <td class="py-2.5 px-4 text-center font-medium text-emerald-700 text-xs">100% (Без затрат)</td>
                <td class="py-2.5 px-4 text-right font-semibold text-slate-600">${fAvg ? fAvg.toLocaleString('ru-RU') + ' ₸' : '—'}</td>
                <td class="py-2.5 px-4 text-center">
                  <button onclick="event.stopPropagation(); copyFanAllLinks('${fReg.id}')" class="px-2 py-0.5 text-[10px] font-bold text-indigo-700 bg-white rounded border border-indigo-200">
                    📋 Ссылки
                  </button>
                </td>
              </tr>
            `;

            if (isFExp) {
              fReg.platforms.forEach(p => {
                const pKey = p.name.toLowerCase();
                const pData = f.platforms[pKey] || { leads: 0, won: 0, rev: 0, clicks: 0 };
                const pCr1 = pData.clicks ? (Math.round(pData.leads / pData.clicks * 1000) / 10) + '%' : (pData.leads ? '—' : '0%');
                const pCr2 = pData.leads ? (Math.round(pData.won / pData.leads * 1000) / 10) + '%' : '0%';
                const pAvg = pData.won ? Math.round(pData.rev / pData.won) : 0;
                totalRows++;
                html += `
                  <tr class="hover:bg-slate-50 transition text-xs border-b border-slate-100">
                    <td class="py-2 px-4 pl-14 font-medium text-slate-700 flex items-center space-x-1.5">
                      <span class="text-slate-300 font-mono">└─</span>
                      <span>${p.icon} ${p.name}</span>
                    </td>
                    <td class="py-2 px-4 text-center text-slate-500 text-[10px]">${p.name}</td>
                    <td class="py-2 px-4 text-center text-slate-400 font-mono text-[10px]">—</td>
                    <td class="py-2 px-4 text-center font-bold text-indigo-700">${pData.clicks ? pData.clicks.toLocaleString('ru-RU') : '<span class="text-slate-300">—</span>'}</td>
                    <td class="py-2 px-4 text-center font-black ${pData.leads > 0 ? 'text-slate-900 bg-emerald-100/70 rounded' : 'text-slate-400'}">${pData.leads.toLocaleString('ru-RU')}</td>
                    <td class="py-2 px-4 text-center font-semibold text-slate-600">${pCr1}</td>
                    <td class="py-2 px-4 text-center font-black ${pData.won > 0 ? 'text-emerald-600' : 'text-slate-400'}">${pData.won}</td>
                    <td class="py-2 px-4 text-center font-semibold ${pData.won > 0 ? 'text-emerald-700' : 'text-slate-400'}">${pCr2}</td>
                    <td class="py-2 px-4 text-right font-black ${pData.rev > 0 ? 'text-slate-900' : 'text-slate-400'}">${pData.rev.toLocaleString('ru-RU')} ₸</td>
                    <td class="py-2 px-4 text-center font-medium text-emerald-700 text-xs">100%</td>
                    <td class="py-2 px-4 text-right font-semibold text-slate-600">${pAvg ? pAvg.toLocaleString('ru-RU') + ' ₸' : '—'}</td>
                    <td class="py-2 px-4 text-center">
                      <button onclick="copyFanPlatformLink('${p.url}')" class="px-2 py-0.5 text-[10px] font-bold text-indigo-700 bg-indigo-50 rounded border border-indigo-200">
                        🔗 Ссылка
                      </button>
                    </td>
                  </tr>
                `;
              });
            }
          });
        }

        rowBadge.innerText = 'Показано: ' + totalRows + ' строк (3 канала)';
        tbody.innerHTML = html;
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

            function copyDirectUrl(url) {
      if (!url) return;
      navigator.clipboard.writeText(url);
      alert('✓ Ссылка с UTM-меткой скопирована в буфер обмена:\n' + url);
    }
    function copyOrganikaBaseLink(secKey) {
      let url = 'https://janamen1.kz/smm';
      let title = 'SMM / Соцсети';
      if (secKey === 'org_wa') {
        url = 'https://janamen1.kz/iwa-9828';
        title = 'WhatsApp Айтыма Бериковича (77083779828)';
      } else if (secKey === 'org_site') {
        url = 'https://janamen1.kz/organika';
        title = 'Органика сайта';
      }
      navigator.clipboard.writeText(url);
      alert('✓ Скопирована ссылка направления ' + title + ':\n\n' + url);
    }

    function copyOrganikaItemLink(path, src, cmp, cnt) {
      let url = 'https://janamen1.kz' + (path.startsWith('/') ? path : '/' + path);
      const params = [];
      if (src && src !== 'none') params.push('utm_source=' + encodeURIComponent(src));
      params.push('utm_medium=social');
      if (cmp && cmp !== 'none') params.push('utm_campaign=' + encodeURIComponent(cmp));
      if (cnt && cnt !== 'none') params.push('utm_content=' + encodeURIComponent(cnt));
      if (params.length) url += '?' + params.join('&');

      navigator.clipboard.writeText(url);
      alert('✓ Скопирована ссылка с UTM:\n\n' + url);
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
    function copyBloggerDirectLink(b, m, u) { return copyBloggerLinkDirect(b, m, u); }
    function copyBloggerLinkDirect(blogger, manager, customUrl) {
      const url = customUrl || ('https://janamen1.kz/influence?utm_source=' + encodeURIComponent(blogger) + '&utm_medium=' + manager + '&utm_campaign=ugc_barter&utm_content=reels_stories');
      navigator.clipboard.writeText(url);
      alert('✓ Персональная UTM-ссылка для блогера @' + blogger + ' скопирована:\n' + url);
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
          if (Array.isArray(res.clicks)) RAW_CLICKS = res.clicks;
          if (res.byCampaignSource) CLICK_BY_CAMPAIGN_SOURCE = res.byCampaignSource;
          if (res.byContent) { CLICK_COUNTS = res.byContent; CLICK_BY_CONTENT = res.byContent; }
          if (res.byMedium) CLICK_BY_MEDIUM = res.byMedium;
          if (res.byPage) CLICK_BY_PAGE = res.byPage;
          if (res.bySource) CLICK_BY_SOURCE = res.bySource;
          if (res.byCampaign) CLICK_BY_CAMPAIGN = res.byCampaign;
          if (res.byBlogger) CLICK_BY_BLOGGER = res.byBlogger;
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

      // Живая подписка на входящие клики
      supabaseClient
        .channel('public_clicks')
        .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'clicks' }, payload => {
          const c = payload.new;
          if (!c) return;
          RAW_CLICKS.unshift(c);

          const cnt = (c.utm_content || '').trim();
          const med = (c.utm_medium || '').trim();
          const p = (c.landing_page || '').trim();
          const src = (c.utm_source || '').trim();
          const cmp = (c.utm_campaign || '').trim();
          const blg = (c.blogger || '').trim();

          if (cnt && cnt !== 'none') CLICK_BY_CONTENT[cnt] = (CLICK_BY_CONTENT[cnt] || 0) + 1;
          if (med && med !== 'none') CLICK_BY_MEDIUM[med] = (CLICK_BY_MEDIUM[med] || 0) + 1;
          if (p && p !== 'none') CLICK_BY_PAGE[p] = (CLICK_BY_PAGE[p] || 0) + 1;
          if (src && src !== 'none') CLICK_BY_SOURCE[src] = (CLICK_BY_SOURCE[src] || 0) + 1;
          if (cmp && cmp !== 'none') CLICK_BY_CAMPAIGN[cmp] = (CLICK_BY_CAMPAIGN[cmp] || 0) + 1;
          if (blg && blg !== 'none') CLICK_BY_BLOGGER[blg] = (CLICK_BY_BLOGGER[blg] || 0) + 1;
          if (cmp && src && cmp !== 'none' && src !== 'none') {
            const csKey = `${cmp.toLowerCase()}:::${src.toLowerCase()}`;
            CLICK_BY_CAMPAIGN_SOURCE[csKey] = (CLICK_BY_CAMPAIGN_SOURCE[csKey] || 0) + 1;
          }

          onFilterChange();

          const live = document.getElementById('liveStatus');
          if (live) {
            live.className = "hidden sm:inline-flex px-2.5 py-1 text-[11px] font-bold rounded-lg border bg-purple-50 text-purple-800 border-purple-300 animate-pulse";
            live.innerHTML = `⚡ Клик: ${src} (${p})`;
            setTimeout(() => {
              live.className = "hidden sm:inline-flex px-2.5 py-1 text-[11px] font-bold rounded-lg border bg-emerald-50 text-emerald-700 border-emerald-200";
              live.innerHTML = `🟢 Supabase Realtime (Живые данные)`;
            }, 5000);
          }
        })
        .subscribe();
    }

    // ============================================================
    // ============================================================
    // ЦЕНЫ НА ВИТАМИНЫ И РАСЧЕТ СЕБЕСТОИМОСТИ БЛОГЕРОВ
    // ============================================================
    const VITAMIN_PRICES = {
      man: 62000,    // Мужской комплекс
      woman: 62000,  // Женский комплекс
      omega: 62000,  // Омега-3
      aojiru: 72000  // Аодзиро (Аодзиру)
    };

    let showExpenseDetails = false;

    function toggleExpenseDetails() {
      showExpenseDetails = !showExpenseDetails;
      renderPortalTables();
    }

    function calculateBloggerExpenses(b) {
      const paidCash = Number(b.paid_cash) || 0;
      const deliveryCost = Number(b.delivery_cost) || 0;
      const bMan = Number(b.barter_man) || 0;
      const bWoman = Number(b.barter_woman) || 0;
      const bOmega = Number(b.barter_omega) || 0;
      const bAojiru = Number(b.barter_aojiru) || 0;

      const manCost = bMan * VITAMIN_PRICES.man;
      const womanCost = bWoman * VITAMIN_PRICES.woman;
      const omegaCost = bOmega * VITAMIN_PRICES.omega;
      const aojiruCost = bAojiru * VITAMIN_PRICES.aojiru;
      const vitaminsCost = manCost + womanCost + omegaCost + aojiruCost;

      const totalExpense = paidCash + deliveryCost + vitaminsCost;

      return {
        paidCash,
        deliveryCost,
        bMan, bWoman, bOmega, bAojiru,
        manCost, womanCost, omegaCost, aojiruCost,
        vitaminsCost,
        totalExpense
      };
    }

    function updateModalCalculatedCost() {
      const cash = parseFloat(document.getElementById('bloggerPaidCash')?.value) || 0;
      const delivery = parseFloat(document.getElementById('bloggerDeliveryCost')?.value) || 0;
      const bMan = parseInt(document.getElementById('barterMan')?.value) || 0;
      const bWoman = parseInt(document.getElementById('barterWoman')?.value) || 0;
      const bOmega = parseInt(document.getElementById('barterOmega')?.value) || 0;
      const bAojiru = parseInt(document.getElementById('barterAojiru')?.value) || 0;

      const vitCost = (bMan * VITAMIN_PRICES.man) + (bWoman * VITAMIN_PRICES.woman) + (bOmega * VITAMIN_PRICES.omega) + (bAojiru * VITAMIN_PRICES.aojiru);
      const total = cash + delivery + vitCost;

      const label = document.getElementById('modalTotalCalculatedCost');
      if (label) {
        label.innerText = total.toLocaleString('ru-RU') + ' ₸';
      }
    }

    function editBloggerExpenses(handle, manager) {
      openAddBloggerModal();
      const cleanH = String(handle).replace(/^@/, '').trim().toLowerCase();
      const hInput = document.getElementById('bloggerHandle');
      const mInput = document.getElementById('bloggerManager');
      const nInput = document.getElementById('bloggerName');
      const sInput = document.getElementById('bloggerSubs');
      const cInput = document.getElementById('bloggerCity');
      const cashInput = document.getElementById('bloggerPaidCash');
      const delInput = document.getElementById('bloggerDeliveryCost');
      const manInput = document.getElementById('barterMan');
      const womInput = document.getElementById('barterWoman');
      const omgInput = document.getElementById('barterOmega');
      const aojInput = document.getElementById('barterAojiru');

      if (hInput) hInput.value = cleanH;
      if (mInput) mInput.value = manager || 'mpb1';

      // Поиск существующего блогера в базе
      const custom = CUSTOM_BLOGGERS.find(b => (b.handle || '').toLowerCase() === cleanH);
      if (custom) {
        if (nInput) nInput.value = custom.name || cleanH;
        if (sInput) sInput.value = custom.subs || '';
        if (cInput) cInput.value = custom.city || '';
        if (cashInput) cashInput.value = custom.paid_cash || 0;
        if (delInput) delInput.value = custom.delivery_cost || 0;
        if (manInput) manInput.value = custom.barter_man || 0;
        if (womInput) womInput.value = custom.barter_woman || 0;
        if (omgInput) omgInput.value = custom.barter_omega || 0;
        if (aojInput) aojInput.value = custom.barter_aojiru || 0;
      } else {
        const reg = (typeof INFLUENCE_REGISTRY !== 'undefined') ? INFLUENCE_REGISTRY.find(b => (b.h || '').toLowerCase() === cleanH) : null;
        if (reg) {
          if (nInput) nInput.value = reg.n || cleanH;
          if (sInput) sInput.value = reg.s || '';
          if (cInput) cInput.value = reg.c || '';
        } else {
          if (nInput) nInput.value = cleanH;
        }
        if (cashInput) cashInput.value = 0;
        if (delInput) delInput.value = 0;
        if (manInput) manInput.value = 0;
        if (womInput) womInput.value = 0;
        if (omgInput) omgInput.value = 0;
        if (aojInput) aojInput.value = 0;
      }

      updateBloggerUtmPreview();
      updateModalCalculatedCost();

      // Показываем кнопку удаления ТОЛЬКО если вошел супер-админ (владелец)
      const btnDel = document.getElementById('btnDeleteBloggerModal');
      const isMaster = CURRENT_USER && (
        CURRENT_USER.role === 'superadmin' ||
        (CURRENT_USER.email && (CURRENT_USER.email.includes('saidullayev') || CURRENT_USER.email === 'admin'))
      );
      if (btnDel) {
        if (isMaster) btnDel.classList.remove('hidden');
        else btnDel.classList.add('hidden');
      }
    }

    // УПРАВЛЕНИЕ БЛОГЕРАМИ (ДОБАВЛЕНИЕ, ВИТАМИНЫ, УСЛОВИЯ, UTM)
    // ============================================================
    // ============================================================
    // УДАЛЕНИЕ ЗАПИСЕЙ БЛОГЕРОВ (СТРОГО ТОЛЬКО ДЛЯ ВЛАДЕЛЬЦА)
    // ============================================================
    async function deleteBloggerByAdmin(handle) {
      const isMaster = CURRENT_USER && (
        CURRENT_USER.role === 'superadmin' ||
        (CURRENT_USER.email && (CURRENT_USER.email.includes('saidullayev') || CURRENT_USER.email === 'admin'))
      );

      if (!isMaster) {
        alert('Доступ запрещен. Только владелец (Куанышбек Сайдуллаев) имеет право удалять записи!');
        return;
      }

      const cleanH = String(handle).replace(/^@/, '').trim().toLowerCase();
      if (!confirm(`Вы действительно хотите безвозвратно удалить блогера @${cleanH} из базы данных?`)) {
        return;
      }

      try {
        const res = await fetch(`/api/bloggers?handle=${encodeURIComponent(cleanH)}&admin_email=${encodeURIComponent(CURRENT_USER.email)}`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            handle: cleanH,
            admin_email: CURRENT_USER.email
          })
        });

        if (res.status === 403) {
          alert('Доступ запрещен сервером: удалять записи может только владелец.');
          return;
        }

        // Фиксируем удаление локально
        let deletedList = [];
        try {
          deletedList = JSON.parse(localStorage.getItem('janamen_deleted_bloggers') || '[]');
        } catch(e) {}
        if (!deletedList.includes(cleanH)) {
          deletedList.push(cleanH);
          localStorage.setItem('janamen_deleted_bloggers', JSON.stringify(deletedList));
        }

        // Удаляем из CUSTOM_BLOGGERS
        CUSTOM_BLOGGERS = CUSTOM_BLOGGERS.filter(b => (b.handle || '').toLowerCase() !== cleanH);
        localStorage.setItem('janamen_custom_bloggers', JSON.stringify(CUSTOM_BLOGGERS));

        closeAddBloggerModal();
        onFilterChange();
        alert(`✓ Блогер @${cleanH} успешно удален из базы.`);
      } catch (err) {
        alert('Ошибка при удалении: ' + err.message);
      }
    }

    function deleteCurrentBloggerFromModal() {
      const handle = (document.getElementById('bloggerHandle')?.value || '').trim();
      if (!handle) return;
      deleteBloggerByAdmin(handle);
    }

    function openAddBloggerModal() {
      const modal = document.getElementById('addBloggerModal');
      if (modal) modal.classList.remove('hidden');
      const btnDel = document.getElementById('btnDeleteBloggerModal');
      if (btnDel) btnDel.classList.add('hidden');

      const mgrSelect = document.getElementById('bloggerManager');
      const userRole = CURRENT_USER?.role || 'superadmin';
      const userMgrCode = CURRENT_USER?.manager_code;

      if (mgrSelect && userRole === 'manager' && userMgrCode) {
        mgrSelect.value = userMgrCode;
        mgrSelect.disabled = true; // заблокировано для менеджера
      } else if (mgrSelect) {
        mgrSelect.disabled = false;
      }

      updateBloggerUtmPreview();
      updateModalCalculatedCost();
    }

    function closeAddBloggerModal() {
      const modal = document.getElementById('addBloggerModal');
      if (modal) modal.classList.add('hidden');
    }

    function updateBloggerUtmPreview() {
      const handleInput = document.getElementById('bloggerHandle');
      const mgrInput = document.getElementById('bloggerManager');
      const previewInput = document.getElementById('bloggerPreviewUrl');
      if (!handleInput || !previewInput) return;

      let handle = (handleInput.value || '').trim().replace(/^@/, '').toLowerCase();
      if (!handle) handle = 'blogger_handle';
      const mgr = (mgrInput ? mgrInput.value : 'mpb1') || 'mpb1';

      const url = `https://janamen1.kz/influence?utm_source=${handle}&utm_medium=${mgr}&utm_campaign=ugc_barter&utm_content=reels_stories`;
      previewInput.value = url;
    }

    function copyBloggerPreviewUrl() {
      const previewInput = document.getElementById('bloggerPreviewUrl');
      if (!previewInput) return;
      previewInput.select();
      navigator.clipboard.writeText(previewInput.value);
      alert('✓ Ссылка для блогера скопирована в буфер обмена!');
    }

    async function loadCustomBloggers() {
      try {
        // Сначала берем из localStorage для мгновенной загрузки
        const local = localStorage.getItem('janamen_custom_bloggers');
        if (local) {
          CUSTOM_BLOGGERS = JSON.parse(local);
          onFilterChange();
        }

        // Синхронизируем с Supabase через /api/bloggers
        const res = await fetch('/api/bloggers');
        if (res.ok) {
          const data = await res.json();
          if (data && data.bloggers && Array.isArray(data.bloggers)) {
            CUSTOM_BLOGGERS = data.bloggers;
            localStorage.setItem('janamen_custom_bloggers', JSON.stringify(CUSTOM_BLOGGERS));
            onFilterChange();
          }
        }
      } catch (err) {
        console.warn('Could not load bloggers from API:', err);
      }
    }

    async function saveNewBlogger() {
      const handleRaw = (document.getElementById('bloggerHandle').value || '').trim().replace(/^@/, '').toLowerCase();
      if (!handleRaw) {
        alert('Пожалуйста, укажите Instagram никнейм блогера (@handle)');
        return;
      }

      let mgr = document.getElementById('bloggerManager').value;
      const userRole = CURRENT_USER?.role || 'superadmin';
      const userMgrCode = CURRENT_USER?.manager_code;
      if (userRole === 'manager' && userMgrCode) {
        mgr = userMgrCode;
      }
      const name = (document.getElementById('bloggerName').value || '').trim() || handleRaw;
      const subs = (document.getElementById('bloggerSubs').value || '').trim() || '—';
      const city = (document.getElementById('bloggerCity').value || '').trim() || '—';
      const paidCash = parseFloat(document.getElementById('bloggerPaidCash').value) || 0;
      const deliveryCost = parseFloat(document.getElementById('bloggerDeliveryCost').value) || 0;
      const bMan = parseInt(document.getElementById('barterMan').value) || 0;
      const bWoman = parseInt(document.getElementById('barterWoman').value) || 0;
      const bOmega = parseInt(document.getElementById('barterOmega').value) || 0;
      const bAojiru = parseInt(document.getElementById('barterAojiru').value) || 0;
      const utmUrl = `https://janamen1.kz/influence?utm_source=${handleRaw}&utm_medium=${mgr}&utm_campaign=ugc_barter&utm_content=reels_stories`;

      const bloggerObj = {
        manager: mgr,
        handle: handleRaw,
        name: name,
        subs: subs,
        city: city,
        profile: `https://instagram.com/${handleRaw}`,
        utm_url: utmUrl,
        paid_cash: paidCash,
        delivery_cost: deliveryCost,
        barter_man: bMan,
        barter_woman: bWoman,
        barter_omega: bOmega,
        barter_aojiru: bAojiru,
        created_at: new Date().toISOString()
      };

      const btn = document.getElementById('btnSaveBlogger');
      const originalText = btn.innerHTML;
      btn.disabled = true;
      btn.innerText = 'Сохранение...';

      // 1. Локально добавляем/обновляем
      const existingIdx = CUSTOM_BLOGGERS.findIndex(b => (b.handle || '').toLowerCase() === handleRaw);
      if (existingIdx >= 0) {
        CUSTOM_BLOGGERS[existingIdx] = bloggerObj;
      } else {
        CUSTOM_BLOGGERS.unshift(bloggerObj);
      }
      localStorage.setItem('janamen_custom_bloggers', JSON.stringify(CUSTOM_BLOGGERS));

      // 2. Отправляем в Supabase через /api/bloggers
      try {
        await fetch('/api/bloggers', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(bloggerObj)
        });
      } catch (e) {
        console.warn('API error when saving blogger:', e);
      }

      btn.disabled = false;
      btn.innerHTML = originalText;
      closeAddBloggerModal();

      // Переключаем на вкладку influence если не на ней, и разворачиваем менеджера
      if (currentMainChannel !== 'influence') {
        switchMainChannel('influence');
      }
      expandedAccordions.add(mgr);
      onFilterChange();

      alert(`✓ Блогер @${handleRaw} успешно добавлен в отдел ${mgr.toUpperCase()}!\nСсылка скопирована:\n${utmUrl}`);
      navigator.clipboard.writeText(utmUrl);
    }

    // ============================================================
    // АВТОРИЗАЦИЯ, РЕГИСТРАЦИЯ И УПРАВЛЕНИЕ ДОСТУПОМ (RBAC)
    // ============================================================
    let authCurrentTab = 'login';

    function initAuth() {
      const savedUser = localStorage.getItem('janamen_auth_user');
      if (savedUser) {
        try {
          CURRENT_USER = JSON.parse(savedUser);
        } catch(e) {
          CURRENT_USER = null;
        }
      }

      if (!CURRENT_USER) {
        // По умолчанию главный аккаунт (владелец / супервайзер)
        CURRENT_USER = {
          name: 'Куанышбек Сайдуллаев',
          email: 'k.saidullayev@janamen.kz',
          role: 'superadmin',
          status: 'active'
        };
        localStorage.setItem('janamen_auth_user', JSON.stringify(CURRENT_USER));
      }

      renderUserBadge();
    }

    function renderUserBadge() {
      const badge = document.getElementById('userProfileName');
      const btnManage = document.getElementById('btnUserManage');
      if (badge && CURRENT_USER) {
        let roleTitle = 'Пользователь';
        if (CURRENT_USER.role === 'superadmin') roleTitle = '👑 Владелец';
        else if (CURRENT_USER.role === 'head_marketing') roleTitle = '💼 РОМ';
        else if (CURRENT_USER.role === 'crm_integrator') roleTitle = '⚙️ CRM';
        else if (CURRENT_USER.role === 'manager') roleTitle = `🌟 ${CURRENT_USER.manager_code ? CURRENT_USER.manager_code.toUpperCase() : 'Менеджер'}`;
        else if (CURRENT_USER.role === 'fan') roleTitle = '🎬 Фан-сетка';

        badge.innerHTML = `<span>${CURRENT_USER.name || CURRENT_USER.email.split('@')[0]}</span> <span class="text-[10px] text-slate-400 font-normal">(${roleTitle})</span>`;
      }
      if (btnManage) {
        // Только Superadmin видит кнопку "Доступы"
        if (CURRENT_USER && (CURRENT_USER.role === 'superadmin' || CURRENT_USER.email === 'k.saidullayev@janamen.kz')) {
          btnManage.classList.remove('hidden');
        } else {
          btnManage.classList.add('hidden');
        }
      }
    }

    function openAuthModal() {
      const modal = document.getElementById('authModal');
      if (modal) modal.classList.remove('hidden');
      switchAuthTab('login');
      const fb = document.getElementById('authFeedback');
      if (fb) fb.classList.add('hidden');
    }

    function closeAuthModal() {
      const modal = document.getElementById('authModal');
      if (modal) modal.classList.add('hidden');
    }

    function switchAuthTab(tab) {
      authCurrentTab = tab;
      const tabLog = document.getElementById('tabAuthLogin');
      const tabReg = document.getElementById('tabAuthRegister');
      const nameFld = document.getElementById('authNameField');
      const roleFld = document.getElementById('authRoleField');
      const btnSub = document.getElementById('btnAuthSubmit');
      const title = document.getElementById('authModalTitle');

      if (tab === 'login') {
        tabLog.className = "flex-1 py-1.5 rounded-lg bg-white shadow-sm text-slate-900 font-bold";
        tabReg.className = "flex-1 py-1.5 rounded-lg text-slate-500 hover:text-slate-900 font-bold";
        nameFld.classList.add('hidden');
        roleFld.classList.add('hidden');
        btnSub.innerText = "Войти в систему";
        if (title) title.innerText = "Вход в Аналитику Jana Men";
      } else {
        tabReg.className = "flex-1 py-1.5 rounded-lg bg-white shadow-sm text-slate-900 font-bold";
        tabLog.className = "flex-1 py-1.5 rounded-lg text-slate-500 hover:text-slate-900 font-bold";
        nameFld.classList.remove('hidden');
        roleFld.classList.remove('hidden');
        btnSub.innerText = "Зарегистрироваться";
        if (title) title.innerText = "Регистрация нового сотрудника";
      }
    }

    async function quickLoginRole(roleKey) {
      const emailInput = document.getElementById('authEmail');
      const passInput = document.getElementById('authPassword');
      if (emailInput && passInput) {
        emailInput.value = roleKey;
        passInput.value = 'janamen2026';
        await submitAuthForm();
      }
    }
    async function submitAuthForm() {
      const email = (document.getElementById('authEmail').value || '').trim();
      const pass = (document.getElementById('authPassword').value || '').trim();
      const name = (document.getElementById('authName').value || '').trim();
      const role = document.getElementById('authRole').value;
      const fb = document.getElementById('authFeedback');

      fb.className = "text-xs p-2.5 rounded-xl font-medium";
      fb.classList.remove('hidden');

      try {
        const res = await fetch('/api/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: authCurrentTab,
            email: email,
            password: pass,
            name: name,
            role: role
          })
        });
        const data = await res.json();

        if (!data.ok && !data.success) {
          fb.classList.add('bg-rose-50', 'text-rose-700', 'border', 'border-rose-200');
          fb.innerText = data.error || 'Ошибка входа / регистрации';
          return;
        }

        if (authCurrentTab === 'register' && data.user.status === 'pending') {
          fb.classList.add('bg-amber-50', 'text-amber-800', 'border', 'border-amber-200');
          fb.innerText = '✓ Регистрация принята! Ожидайте подтверждения от Куанышбека.';
          return;
        }

        CURRENT_USER = data.user;
        localStorage.setItem('janamen_auth_user', JSON.stringify(CURRENT_USER));
        renderUserBadge();
        fb.classList.add('bg-emerald-50', 'text-emerald-700', 'border', 'border-emerald-200');
        fb.innerText = '✓ Успешно!';
        setTimeout(() => {
          closeAuthModal();
        }, 1000);

      } catch(err) {
        // Fallback если локально без API
        if (email.includes('saidullayev') || email === 'admin') {
          CURRENT_USER = { name: name || 'Куанышбек Сайдуллаев', email: email, role: 'superadmin', status: 'active' };
          localStorage.setItem('janamen_auth_user', JSON.stringify(CURRENT_USER));
          renderUserBadge();
          closeAuthModal();
        } else {
          fb.classList.add('bg-rose-50', 'text-rose-700', 'border', 'border-rose-200');
          fb.innerText = 'Ошибка сети. Проверьте подключение.';
        }
      }
    }

    function handleLogout() {
      if (confirm('Вы уверены, что хотите выйти из профиля?')) {
        localStorage.removeItem('janamen_auth_user');
        CURRENT_USER = null;
        initAuth();
      }
    }

    // ============================================================
    // УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (ТОЛЬКО SUPERADMIN)
    // ============================================================
    let ALL_USERS_LIST = [];

    async function openUserManageModal() {
      if (!CURRENT_USER || CURRENT_USER.role !== 'superadmin') {
        alert('Доступ запрещен. Только владелец (Куанышбек) может управлять правами.');
        return;
      }
      const modal = document.getElementById('userManageModal');
      if (modal) modal.classList.remove('hidden');
      await loadUsersList();
    }

    function closeUserManageModal() {
      const modal = document.getElementById('userManageModal');
      if (modal) modal.classList.add('hidden');
    }

    async function loadUsersList() {
      const tbody = document.getElementById('userManageTableBody');
      if (!tbody) return;
      tbody.innerHTML = '<tr><td colspan="5" class="py-4 text-center text-slate-400">Загрузка списка сотрудников...</td></tr>';

      try {
        const res = await fetch('/api/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'list_users',
            admin_email: CURRENT_USER.email
          })
        });
        const data = await res.json();
        if ((data.ok || data.success) && Array.isArray(data.users)) {
          ALL_USERS_LIST = data.users;
        } else {
          ALL_USERS_LIST = [
            { id: 1, name: 'Куанышбек Сайдуллаев', email: 'k.saidullayev@janamen.kz', role: 'superadmin', status: 'active' },
            { id: 2, name: 'Анельжан (mpb1)', email: 'mpb1@janamen.kz', role: 'manager', status: 'active' },
            { id: 3, name: 'Алина (mpb2)', email: 'mpb2@janamen.kz', role: 'manager', status: 'active' },
            { id: 4, name: 'Алуа (mpb3)', email: 'mpb3@janamen.kz', role: 'manager', status: 'active' },
            { id: 5, name: 'Дарина (mpb4)', email: 'mpb4@janamen.kz', role: 'manager', status: 'active' }
          ];
        }
      } catch (e) {
        ALL_USERS_LIST = [
          { id: 1, name: 'Куанышбек Сайдуллаев', email: 'k.saidullayev@janamen.kz', role: 'superadmin', status: 'active' },
          { id: 2, name: 'Анельжан (mpb1)', email: 'mpb1@janamen.kz', role: 'manager', status: 'active' }
        ];
      }

      renderUserManageTable();
    }

    function renderUserManageTable() {
      const tbody = document.getElementById('userManageTableBody');
      if (!tbody) return;

      if (ALL_USERS_LIST.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="py-4 text-center text-slate-400">Нет сотрудников в базе</td></tr>';
        return;
      }

      let html = '';
      ALL_USERS_LIST.forEach(u => {
        const isMaster = (u.email === 'k.saidullayev@janamen.kz' || u.role === 'superadmin');
        const statusBadge = u.status === 'active' 
          ? '<span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-100 text-emerald-700">Активен</span>'
          : (u.status === 'pending'
            ? '<span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-100 text-amber-700 animate-pulse">Ожидает</span>'
            : '<span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-rose-100 text-rose-700">Заблокирован</span>');

        html += `
          <tr class="hover:bg-slate-50 transition border-b border-slate-100">
            <td class="py-2.5 px-3 font-bold text-slate-900">
              ${u.name || 'Без имени'}
              ${isMaster ? ' <span class="text-[10px] text-amber-600 font-black">👑 Владелец</span>' : ''}
            </td>
            <td class="py-2.5 px-3 font-mono text-slate-600">${u.email}</td>
            <td class="py-2.5 px-3 text-center">
              ${isMaster ? '<span class="font-bold text-amber-700">Супервайзер</span>' : `
                <select onchange="updateUserRole('${u.id}', this.value)" class="text-xs bg-slate-100 border border-slate-200 rounded px-1.5 py-0.5 font-bold text-slate-700">
                  <option value="superadmin" ${u.role === 'superadmin' ? 'selected' : ''}>Администратор (Владелец)</option>
                  <option value="head_marketing" ${u.role === 'head_marketing' ? 'selected' : ''}>Руководитель маркетинга (РОМ)</option>
                  <option value="crm_integrator" ${u.role === 'crm_integrator' ? 'selected' : ''}>CRM-интегратор</option>
                  <option value="manager_mpb1" ${(u.role === 'manager' && u.manager_code === 'mpb1') || u.role === 'manager_mpb1' ? 'selected' : ''}>Менеджер Анельжан (mpb1)</option>
                  <option value="manager_mpb2" ${(u.role === 'manager' && u.manager_code === 'mpb2') || u.role === 'manager_mpb2' ? 'selected' : ''}>Менеджер Алина (mpb2)</option>
                  <option value="manager_mpb3" ${(u.role === 'manager' && u.manager_code === 'mpb3') || u.role === 'manager_mpb3' ? 'selected' : ''}>Менеджер Алуа (mpb3)</option>
                  <option value="manager_mpb4" ${(u.role === 'manager' && u.manager_code === 'mpb4') || u.role === 'manager_mpb4' ? 'selected' : ''}>Менеджер Дарина (mpb4)</option>
                  <option value="fan" ${u.role === 'fan' ? 'selected' : ''}>Фан-аккаунты</option>
                </select>
              `}
            </td>
            <td class="py-2.5 px-3 text-center">${statusBadge}</td>
            <td class="py-2.5 px-3 text-right space-x-1">
              ${!isMaster ? `
                ${u.status !== 'active' ? `
                  <button onclick="toggleUserStatus('${u.id}', 'active')" class="px-2 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold rounded text-[11px] border border-emerald-200">
                    Одобрить
                  </button>
                ` : `
                  <button onclick="toggleUserStatus('${u.id}', 'blocked')" class="px-2 py-1 bg-slate-100 hover:bg-rose-50 text-slate-600 hover:text-rose-600 font-bold rounded text-[11px] border border-slate-200">
                    Блок
                  </button>
                `}
                <button onclick="deleteUser('${u.id}', '${u.email}')" class="px-2 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold rounded text-[11px] border border-rose-200">
                  Удалить
                </button>
              ` : '<span class="text-[11px] text-slate-400 font-medium">Главный</span>'}
            </td>
          </tr>
        `;
      });

      tbody.innerHTML = html;
    }

    async function createUserByAdmin() {
      const name = (document.getElementById('newUserName').value || '').trim();
      const email = (document.getElementById('newUserEmail').value || '').trim();
      const pass = (document.getElementById('newUserPassword').value || '').trim();

      if (!email || !pass) {
        alert('Укажите email и пароль');
        return;
      }

      try {
        await fetch('/api/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'register',
            name: name,
            email: email,
            password: pass,
            role: 'manager'
          })
        });

        // сразу активируем
        await fetch('/api/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'update_user',
            admin_email: CURRENT_USER.email,
            email: email,
            status: 'active'
          })
        });

        document.getElementById('newUserName').value = '';
        document.getElementById('newUserEmail').value = '';
        document.getElementById('newUserPassword').value = '';
        await loadUsersList();
        alert(`✓ Доступ для ${email} успешно создан!`);
      } catch (e) {
        alert('Ошибка при создании пользователя: ' + e.message);
      }
    }

    async function updateUserRole(userId, newRole) {
      try {
        await fetch('/api/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'update_user',
            admin_email: CURRENT_USER.email,
            id: userId,
            role: newRole
          })
        });
      } catch (e) {}
    }

    async function toggleUserStatus(userId, newStatus) {
      try {
        await fetch('/api/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'update_user',
            admin_email: CURRENT_USER.email,
            id: userId,
            status: newStatus
          })
        });
        await loadUsersList();
      } catch (e) {}
    }

    async function deleteUser(userId, email) {
      if (!confirm(`Удалить доступ для сотрудника ${email}?`)) return;
      try {
        await fetch('/api/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'delete_user',
            admin_email: CURRENT_USER.email,
            id: userId
          })
        });
        await loadUsersList();
      } catch (e) {}
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
    initAuth();
    loadCustomBloggers();
    onFilterChange();
    loadFreshDealsFromSupabase();
    loadClickCounts();
    initRealtime();

    // Автообновление кликов и сделок в реальном времени (каждые 8 сек и при фокусе)
    setInterval(() => {
      loadClickCounts();
      loadFreshDealsFromSupabase();
    }, 8000);
    window.addEventListener('focus', () => {
      loadClickCounts();
      loadFreshDealsFromSupabase();
    });
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
