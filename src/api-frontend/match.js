import { handleResponse } from './utils'

const API_BASE = 'http://127.0.0.1:5000/api'

/**
 * Получение совпадений по участникам за месяц
 * @param {string} token - JWT токен
 * @param {Array<number>} participantIds - ID участников
 * @param {number} year - Год
 * @param {number} month - Месяц (1-12)
 * @returns {Promise<Object>} - Результат с цветами и совпадениями
 */
export function getMatchDays(token, participantIds, year, month) {
  const query = new URLSearchParams({
    participants: participantIds.join(','),
    year: year.toString(),
    month: month.toString()
  })

  return fetch(`${API_BASE}/match?${query.toString()}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`
    }
  }).then(handleResponse)
}
