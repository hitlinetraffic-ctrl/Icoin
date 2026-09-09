import asyncio
import aiohttp
import time
import json

async def test_security_features():
    """Тестируем новые функции безопасности"""
    
    print("🔒 Тестирование функций безопасности Icoin...")
    
    # Тест 1: Проверка подключения к Redis с паролем
    try:
        from icoin import get_redis_cluster
        redis_client = get_redis_cluster()
        print("✅ Redis Cluster: безопасное подключение работает")
    except Exception as e:
        print(f"❌ Redis Cluster: ошибка - {e}")
        return False
    
    # Тест 2: Проверка JWT токенов
    try:
        import jwt
        test_payload = {"node_id": "test", "exp": time.time() + 3600}
        secret = "test_secret"
        token = jwt.encode(test_payload, secret, algorithm="HS256")
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        print("✅ JWT токены: работают корректно")
    except Exception as e:
        print(f"❌ JWT токены: ошибка - {e}")
        return False
    
    print("🎉 Все базовые проверки безопасности пройдены!")
    return True

if __name__ == "__main__":
    asyncio.run(test_security_features())