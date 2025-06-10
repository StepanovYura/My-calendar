import { handleResponse } from './utils';
const API_BASE = 'http://127.0.0.1:5000/api/auth';

/**
 * Регистрация нового пользователя
 * @param {Object} userData - { name, email, password, privacy_setting? }
 */
export function registerUser(userData) {
  return fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  }).then(handleResponse);
}

/**
 * Авторизация пользователя
 * @param {Object} userData - { email, password }
 */
export function loginUser(userData) {
  return fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  }).then(handleResponse);
}

/**
 * Выход из системы
 * @param {string} token - JWT токен пользователя
 */
export function logoutUser(token) {
  return fetch(`${API_BASE}/logout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Проверка авторизации (используется при входе на сайт или обновлении страницы)
 * @param {string} token - JWT токен
 */
export function checkAuth(token) {
  return fetch(`${API_BASE}/check`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}
