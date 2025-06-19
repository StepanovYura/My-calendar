// src/api/friends.js

import { handleResponse } from './utils';

// const API_BASE = 'http://127.0.0.1:5000/api/friends';
const API_BASE = `${import.meta.env.VITE_API_BASE_URL}/friends`;

/**
 * Отправка запроса на дружбу
 * @param {string} token - JWT токен
 * @param {number} userId - ID пользователя, которому отправляется заявка
 */
export function sendFriendRequest(token, userId) {
  return fetch(`${API_BASE}/request`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ user_id: userId }),
  }).then(handleResponse);
}

/**
 * Ответ на заявку в друзья
 * @param {string} token - JWT токен
 * @param {number} requestId - ID заявки
 * @param {'accept' | 'decline'} action - ответ пользователя
 */
export function respondToFriendRequest(token, requestId, action) {
  return fetch(`${API_BASE}/request/${requestId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ action }),
  }).then(handleResponse);
}

/**
 * Получение всех друзей и заявок
 * @param {string} token - JWT токен
 */
export function getFriendList(token) {
  return fetch(`${API_BASE}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Получение информации о конкретном друге
 * @param {string} token - JWT токен
 * @param {number} friendId - ID друга
 */
export function getFriendDetail(token, friendId) {
  return fetch(`${API_BASE}/${friendId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Удаление из друзей
 * @param {string} token - JWT токен
 * @param {number} friendId - ID друга
 */
export function removeFriend(token, friendId) {
  return fetch(`${API_BASE}/${friendId}/remove`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}
