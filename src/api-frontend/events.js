import { handleResponse } from './utils';

// const API_BASE = 'http://127.0.0.1:5000/api/events';
const API_BASE = `${import.meta.env.VITE_API_BASE_URL}/events`;
/**
 * Получение событий пользователя (по дню, неделе, месяцу, с возможностью указать user_id)
 * @param {string} token - JWT токен пользователя
 */
export function getUserEvents(token, filters = {}) {
  const url = new URL(`${API_BASE}/user`, window.location.origin);
  console.log('URL: ', url);
  // Добавляем фильтры в URL (date, week_start, week_end, month_start, month_end, user_id)
  Object.entries(filters).forEach(([key, val]) => {
    if (val) url.searchParams.append(key, val);
  });

  return fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json',
    },
  }).then(handleResponse);
}

/**
 * Получение информации о конкретном событии
 * @param {string} token - JWT токен пользователя
 * @param {number} eventId - ID события
 */
export function getEventDetail(token, eventId) {
  return fetch(`${API_BASE}/${eventId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json',
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
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json',
    },
  }).then(handleResponse);
}

/**
 * Получение всех участников конкретного события
 * @param {string} token - JWT токен пользователя
 * @param {number} eventId - ID события
 */
export function getEventParticipants(token, eventId) {
  return fetch(`${API_BASE}/${eventId}/participants`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json',
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
      'Authorization': `Bearer ${token}`,
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
  return fetch(`${API_BASE}/${eventId}/edit`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
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
  return fetch(`${API_BASE}/${eventId}/edit`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  }).then(handleResponse);
}


/**
 * Добавление участника к событию
 * @param {string} token - JWT токен пользователя
 * @param {number} eventId - ID события
 * @param {string} username - Name пользователя
 */
export function addParticipantToEvent(token, eventId, username) {
  return fetch(`${API_BASE}/${eventId}/add-participant`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username })
  }).then(handleResponse);
}