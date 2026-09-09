# iCoin (исправленная версия)

## Что исправлено (критичное)
- Привязка адреса к public_key: `from == sha256(public_key_pem)[:40]`
- Replay-защита: `nonce` должен увеличиваться последовательно по адресу
- Валидация блоков: проверка hash/previous_hash + полная проверка транзакций на временном state
- Синхронизация цепочки: пересбор state из цепочки без “накрутки” балансов
- Добавлен endpoint для получения токена: `POST /auth/token`
- Добавлен endpoint `GET /account` (balance + next_nonce)
- Награда за блок теперь идёт на `node_address` (адрес узла), а не на `node_id`

## Быстрый старт (Docker)
1) Создай `.env`:
- Скопируй `.env.example` -> `.env`
- Заполни `JWT_SECRET`, `API_PASSWORD`, `REDIS_PASSWORD`
- Обязательно заполни `GENESIS_PRIVATE_KEY_B64` (одинаково для всех нод)

2) Запуск:
```bash
docker compose up --build
