# Jana Men — Реестр UTM-меток и Сквозная Аналитика

Система централизованного создания, регистрации и сквозной аналитики рекламных UTM-ссылок для компании Jana Men с интеграцией в Google Таблицы, AmoCRM и Tilda.

## 🔗 Быстрые ссылки проекта

- **Google Таблица**: [Открыть таблицу Jana Men UTM](https://docs.google.com/spreadsheets/d/1jBeeF8b_7CORi8Xf9Kjr9YN6c6ZrloQIljT2_-adcYs/edit)
- **Google Apps Script**: [Открыть проект скрипта](https://script.google.com/u/0/home/projects/1aSnl3HxjIBMKwCCc-xEsEZYCqY0XAr0Mw-CDU0BbH5Me3D6rW0GuRvL-/edit)
- **Веб-дашборд и генератор (Live Web App)**: [Открыть веб-портал](https://script.google.com/macros/s/AKfycbwV97KvjNwl_OCWbydMTd7DVFn6mDSRvjj6-z5nhdlQK8v9XliGC6JFW6NHZSY0p3Jz/exec)
- **Руководство по встраиванию в Tilda**: [TILDA_SETUP.md](TILDA_SETUP.md)

---

## 📁 Структура проекта

```text
├── gas/
│   ├── Config.js            # Настройки, токены AmoCRM, домены и справочники
│   ├── SheetInitializer.js  # Автогенерация и оформление 4 листов таблицы с формулами
│   ├── AmoCrmSync.js        # Синхронизация сделок и кастомных полей из AmoCRM v4
│   ├── RegistryService.js   # Валидация, транслит, дедупликация и запись UTM-меток
│   ├── WebApp.js            # Обработчики doGet / doPost (API и Tilda Webhooks)
│   ├── Menu.js              # Меню «🎯 Jana Men UTM & Аналитика» и триггеры
│   ├── Dashboard.html       # Адаптивный веб-интерфейс (SPA)
│   ├── appsscript.json      # Манифест Google Apps Script
│   └── Код.js               # Точки входа
├── index.html               # Автономная версия веб-портала (для браузера / Tilda)
├── utm_guide_light.html     # Образовательный гайд по UTM и сквозной аналитике
├── TILDA_SETUP.md           # Инструкция по настройке Tilda
└── .clasp.json              # Конфигурация Clasp для развертывания кода
```

---

## ⚡ Как запустить первый раз

1. Откройте [Google Таблицу](https://docs.google.com/spreadsheets/d/1jBeeF8b_7CORi8Xf9Kjr9YN6c6ZrloQIljT2_-adcYs/edit).
2. В верхнем меню появится пункт **🎯 Jana Men UTM & Аналитика**:
   - Нажмите **«🚀 1. Первоначальная настройка таблицы»** — создадутся и красиво оформятся все 4 листа:
     - `🎯 Реестр UTM` (с формулами оплат, лидов, выручки, CR, ROMI)
     - `📊 Сквозная Аналитика` (KPI и сводки по площадкам)
     - `📥 Сделки AmoCRM` (база сделок)
     - `⚙️ Справочники` (выпадающие списки и правила)
   - Нажмите **«⚡ 2. Синхронизировать сделки из AmoCRM»** — скрипт выгрузит свежие сделки и подтянет все UTM-метки.
   - Нажмите **«⏰ 4. Включить автообновление AmoCRM (каждые 2ч)»** — установится фоновый триггер автоматической синхронизации.
3. Откройте [Веб-дашборд](https://script.google.com/macros/s/AKfycbwV97KvjNwl_OCWbydMTd7DVFn6mDSRvjj6-z5nhdlQK8v9XliGC6JFW6NHZSY0p3Jz/exec) или встройте его на Tilda через блок `T123`.
