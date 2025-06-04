import { handleResponse } from './utils';

const API_BASE = '/api/events';

/**
 * Получение событий пользователя (по дню, неделе, месяцу, с возможностью указать user_id)
 * @param {string} token - JWT токен пользователя
 */
export function getUserEvents(token, filters = {}) {
  const url = new URL(`${API_BASE}/user`, window.location.origin);

  // Добавляем фильтры в URL (date, week_start, week_end, month_start, month_end, user_id)
  Object.entries(filters).forEach(([key, val]) => {
    if (val) url.searchParams.append(key, val);
  });

  return fetch(url.toString(), {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Получение информации о конкретном событии
 * @param {string} token - JWT токен пользователя
 * @param {number} eventId - ID события
 */
export function getEventDetail(token, eventId) {
  return fetch(`${API_BASE}/detail/${eventId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Получение всех событий (доступно только администратору)
 * @param {string} token - JWT токен пользователя
 */
export function getAllEvents(token) {
  return fetch(`${API_BASE}/all`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Создание события
 * @param {string} token - JWT токен пользователя
 * @param {Object} eventData - { title, description, date_time, duration_minutes }
 */
export function createEvent(token, eventData) {
  return fetch(`${API_BASE}/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(eventData),
  }).then(handleResponse);
}

/**
 * Обновление события
 * @param {string} token - JWT токен пользователя
 * @param {number} eventId - ID события
 * @param {Object} updatedData - { title, description, date_time, duration_minutes }
 */
export function updateEvent(token, eventId, updatedData) {
  return fetch(`${API_BASE}/edit/${eventId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(updatedData),
  }).then(handleResponse);
}

/**
 * Удаление события
 * @param {string} token - JWT токен пользователя
 * @param {number} eventId - ID события
 */
export function deleteEvent(token, eventId) {
  return fetch(`${API_BASE}/edit/${eventId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}
