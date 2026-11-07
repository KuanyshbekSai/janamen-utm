/**
 * ============================================================
 * Код.js — Главная точка входа Google Apps Script
 * ============================================================
 */

function initialSetup() {
  return setupSpreadsheet();
}

function runAmoSync() {
  return syncAmoCrmDeals();
}
