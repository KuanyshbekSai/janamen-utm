/**
 * ============================================================
 * Config.js — Конфигурация Реестра UTM и Сквозной Аналитики Jana Men
 * ============================================================
 */

var CONFIG = {
  // Идентификатор Google Таблицы
  SPREADSHEET_ID: '1jBeeF8b_7CORi8Xf9Kjr9YN6c6ZrloQIljT2_-adcYs',

  // AmoCRM Настройки
  AMOCRM: {
    SUBDOMAIN: 'janamen',
    BASE_URL: 'https://janamen.amocrm.ru/api/v4',
    ACCESS_TOKEN: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImEwYjNmMDg0MzBmYjYyNzViMDE3YjUwMmMyMDM0OGUxNDdkZjkwZDUxNDljOTQxNWMyYjVmM2FjNzkwYWE5OGU5Mzk1OWNjYTI0NDBlNTIyIn0.eyJhdWQiOiIzZDE4ZGY5Ni1lNTEyLTRiZjQtYWYxZS0wOGY3YzNkODNhNWYiLCJqdGkiOiJhMGIzZjA4NDMwZmI2Mjc1YjAxN2I1MDJjMjAzNDhlMTQ3ZGY5MGQ1MTQ5Yzk0MTVjMmI1ZjNhYzc5MGFhOThlOTM5NTljY2EyNDQwZTUyMiIsImlhdCI6MTc4NzU1NTk3NCwibmJmIjoxNzg3NTU1OTc0LCJleHAiOjE4ODIyMjQwMDAsInN1YiI6IjExODA0NDc0IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMyMDc5NjU4LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJwdXNoX25vdGlmaWNhdGlvbnMiLCJmaWxlcyIsImNybSIsIm5vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiMjAwZTdmOWMtYTI5Ny00OTFlLWJjMWMtMmM3YjdiYmY3YmQ2IiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.kbK8E9uJ0JbpcS9NfkJ4UB8e-yE05c18raojZuhSrKT4VoEMqqFRz5cHOCYRRF7JI3uqIcyJywyN_yFAKzFnsMnRr-DH2rZ03GGBpMuiR1wgQ5wy4onDkRRYxohkLvEopCrTiEZu5Y3QKIRlsd85scGUV_BR3CAPc8IVuqEfN__9sVoWPwS-sa3m3fCIMOb9_BYyiH-FuW51mq6w5xlqliW5Ok7g1jOlY_KZZwgbHjCQy8z7cC_Allw0pYYQ_Z_YquyWl-4a7ATP8Q1Kv9JcjAxsna0vH5im-jbVPrkP0kvN_qvyOYRx9HUXv4QY6EseT8reFcChgM-LFDvYVwNGjw',
    CLIENT_ID: '3d18df96-e512-4bf4-af1e-08f7c3d83a5f',

    // Целевой статус подтверждения продажи: Этап 2, Воронка продаж — «Успешно реализовано» (Status ID 142)
    STATUS_WON_ID: 142,
    VERIFIED_STATUS_IDS: [
      142 // Успешно реализовано (Этап 2 / Воронка продаж)
    ],
    LOST_STATUS_IDS: [
      143 // Закрыто и не реализовано
    ],
    PAGE_LIMIT: 250,           // максимум AmoCRM API
    TIME_BUDGET_MS: 240000     // лимит одного запуска (GAS ~6 мин)
  },

  // Выделенный домен отдела маркетинга
  MARKETING_DOMAIN: 'janamen1.kz',

  // Имена листов
  SHEETS: {
    REGISTRY: '🎯 Реестр UTM',
    MARKETING_DASHBOARD: '📊 Отдел Маркетинга (janamen1.kz)',
    DASHBOARD: '📊 Сквозная Аналитика',
    DEALS: '📥 Сделки AmoCRM',
    TAXONOMY: '⚙️ Справочники'
  },

  // Базовые сайты и страницы отдела маркетинга (janamen1.kz)
  DEFAULT_LANDINGS: [
    { label: 'Jana Men Инфлюенс (janamen1.kz/influence)', url: 'https://janamen1.kz/influence' },
    { label: 'Jana Men Лидмагнит (janamen1.kz/lidmagnit)', url: 'https://janamen1.kz/lidmagnit' },
    { label: 'Jana Men Kaspi-форма (janamen1.kz/kaspiform)', url: 'https://janamen1.kz/kaspiform' },
    { label: 'Jana Men Воронка / Квиз (janamen1.kz/fun)', url: 'https://janamen1.kz/fun' },
    { label: 'Jana Men Inst Women (janamen1.kz/inst-women)', url: 'https://janamen1.kz/inst-women' },
    { label: 'Jana Men Inst Men (janamen1.kz/inst-men)', url: 'https://janamen1.kz/inst-men' },
    { label: 'Jana Men Главный (janamen1.kz)', url: 'https://janamen1.kz' },
    { label: 'Jana Men Health (janamenhealth.kz)', url: 'https://janamenhealth.kz' },
    { label: 'Jana Men Women Yakut (janamenhealth.kz/womens-yakut)', url: 'https://janamenhealth.kz/womens-yakut' },
    { label: 'Kaspi Landing (janamen.kz/kaspi)', url: 'https://janamen.kz/kaspi' }
  ],

  // Стандартные источники (utm_source)
  DEFAULT_SOURCES: [
    'instagram',
    'tiktok',
    'facebook',
    'telegram',
    'youtube',
    'google',
    'yandex',
    'kaspi',
    'whatsapp',
    'offline_qr',
    'partner'
  ],

  // Стандартные каналы (utm_medium)
  DEFAULT_MEDIUMS: [
    'influencer',   // Блогеры / инфлюенсеры
    'target_cpc',   // Таргетированная реклама (клики)
    'stories',      // Сториз
    'reels',        // Рилс
    'bio',          // Ссылка в шапке профиля
    'post',         // Пост / статья
    'tg_channel',   // Telegram канал
    'cpa',          // Оплата за действие
    'banner',       // Медийный баннер
    'qr',           // QR-код на упаковке / флаере
    'organic'       // Органический трафик
  ],

  // Теги / категории
  DEFAULT_TAGS: [
    'Инфлюенс / Блогеры',
    'Таргет FB/Insta',
    'TikTok Ads',
    'Telegram реклама',
    'Google Ads',
    'Kaspi продвижение',
    'Органика SMM',
    'Офлайн / Упаковка',
    'Партнерская программа'
  ]
};

function getSpreadsheet() {
  if (CONFIG.SPREADSHEET_ID) {
    try {
      return SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
    } catch (e) {
      return SpreadsheetApp.getActiveSpreadsheet();
    }
  }
  return SpreadsheetApp.getActiveSpreadsheet();
}
