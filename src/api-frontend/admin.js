import { handleResponse } from './utils';

const API_BASE = '/api/admin';

/**
 * Получить список всех пользователей (только для админа)
 */
export function getAllUsers(token) {
  return fetch(`${API_BASE}/users`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Обновить данные пользователя (только для админа)
 */
export function updateUserByAdmin(token, userId, updatedData) {
  return fetch(`${API_BASE}/user/${userId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(updatedData),
  }).then(handleResponse);
}

/**
 * Удалить пользователя (только для админа)
 */
export function deleteUserByAdmin(token, userId) {
  return fetch(`${API_BASE}/user/${userId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}
