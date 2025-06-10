import { handleResponse } from './utils';

const API_BASE = 'http://127.0.0.1:5000/api/event_drafts';

/**
 * Создание черновика события
 */
export function createEventDraft(token, draftData) {
  return fetch(`${API_BASE}/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(draftData)
  }).then(handleResponse);
}

/**
 * Голосование за черновик (с поддержкой слотов)
 */
export function voteForDraft(token, draftId, voteData) {
  return fetch(`${API_BASE}/vote/${draftId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(voteData)
  }).then(handleResponse);
}

/**
 * Завершение голосования по черновику и попытка создать событие
 */
export function finalizeDraft(token, draftId) {
  return fetch(`${API_BASE}/finale/${draftId}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse);
}
