import { handleResponse } from './utils';

const API_BASE = '/api/event-drafts';

/**
 * Создание черновика события
 */
export function createEventDraft(token, draftData) {
  return fetch(`${API_BASE}`, {
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
  return fetch(`${API_BASE}/${draftId}/vote`, {
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
  return fetch(`${API_BASE}/${draftId}/finalize`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse);
}
