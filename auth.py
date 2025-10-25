from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional

# Ваш секретный ключ API
API_KEY = "secret-api-key-12345"

# Определяем, что ключ будет браться из заголовка с именем X-API-Key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Проверка API ключа, переданного в заголовке X-API-Key.
    Если ключ неверный, возвращается ошибка 403 Forbidden.
    """
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный API ключ. Требуется заголовок X-API-Key с правильным значением."
        )
    return api_key
