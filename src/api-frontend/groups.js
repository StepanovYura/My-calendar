import { handleResponse } from './utils';

const API_BASE = 'http://127.0.0.1:5000/api/groups';

/**
 * Создание группы
 */
export function createGroup(token, groupData) {
  return fetch(API_BASE, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: groupData,
  }).then(handleResponse);
}

/**
 * Вступить в группу
 */
export function joinGroup(token, groupId) {
  return fetch(`${API_BASE}/${groupId}/join`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Выйти из группы
 */
export function leaveGroup(token, groupId) {
  return fetch(`${API_BASE}/${groupId}/leave`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Удалить группу
 */
export function deleteGroup(token, groupId) {
  return fetch(`${API_BASE}/${groupId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Редактировать группу
 */
export function editGroup(token, groupId, updatedData) {
  return fetch(`${API_BASE}/${groupId}`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: updatedData,
  }).then(handleResponse);
}

/**
 * Пригласить пользователя в группу
 */
export function inviteToGroup(token, groupId, userId) {
  return fetch(`${API_BASE}/${groupId}/invite`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ user_id: userId }),
  }).then(handleResponse);
}

/**
 * Получить список групп текущего пользователя
 */
export function getMyGroups(token) {
  return fetch(`${API_BASE}/my`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Получить подробную информацию о группе
 */
export function getGroupDetail(token, groupId) {
  return fetch(`${API_BASE}/${groupId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}

/**
 * Получить список событий группы
 */
export function getGroupSchedule(token, groupId) {
  return fetch(`${API_BASE}/${groupId}/schedule`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then(handleResponse);
}


/**
 * Получить список участников группы
 */
export function getGroupMembers(token, groupId) {
  return fetch(`${API_BASE}/${groupId}/members`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse)
}

/**
 * ответ на invite
 */
export function respondToGroupInvitation(token, groupId, action) {
  return fetch(`${API_BASE}/${groupId}/invite-response`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ action })
  }).then(handleResponse);
}