import { handleResponse } from './utils';

const API_BASE = '/api/notifications';

/**
 * Получить все уведомления пользователя
 */
export function getAllNotifications(token) {
  return fetch(`${API_BASE}`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse);
}

/**
 * Получить только уведомления-приглашения
 */
export function getInvitationNotifications(token) {
  return fetch(`${API_BASE}/invitations`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse);
}

/**
 * Получить уведомления общего типа (результаты, обновления и т.п.)
 */
export function getGeneralNotifications(token) {
  return fetch(`${API_BASE}/general`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse);
}

/**
 * Отметить уведомление как прочитанное (или удалить его)
 */
export function markNotificationAsRead(token, notificationId) {
  return fetch(`${API_BASE}/read/${notificationId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse);
}
