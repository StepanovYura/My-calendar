import { handleResponse } from './utils';

const API_BASE = 'http://127.0.0.1:5000/api/user';

/**
 * Получить свой профиль
 */
export function fetchUserProfile(token) { // ВОЗМОЖНО ПОНАДОБИТСЯ ПРОПИСАТЬ МЕТОД GET
  return fetch(`${API_BASE}/profile`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse);
}

/**
 * Обновить профиль
 */
export function updateUserProfile(token, updatedData) {
  return fetch(`${API_BASE}/profile`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(updatedData)
  }).then(handleResponse);
}

/**
 * Сменить пароль
 */
export function changePassword(token, currentPassword, newPassword) {
  return fetch(`${API_BASE}/change-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword
    })
  }).then(handleResponse);
}

/**
 * Удалить аккаунт
 */
export function deleteAccount(token) {
  return fetch(`${API_BASE}/delete`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse);
}

/**
 * Поиск пользователей по имени или email
 */
export function searchUsers(token, query) {
  return fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse);
}
