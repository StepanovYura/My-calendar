export async function handleResponse(response) {
  const contentType = response.headers.get("content-type");

  if (!response.ok) {
    const errorBody = contentType && contentType.includes("application/json")
      ? await response.json()
      : await response.text();
    throw new Error(errorBody.message || errorBody || 'Произошла ошибка запроса');
  }

  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }

  return response.text();
}

// ОПИСАТЬ КАЖДЫЙ ПАРАМЕТР ВО ВСЕХ JS И ПРОВЕРИТЬ МАРШРУТЫ !!!