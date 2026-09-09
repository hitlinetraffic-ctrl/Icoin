import requests
import json
import time

def test_node_health(node_url, node_name):
    """Проверяем здоровье узла"""
    try:
        # Пробуем получить security status (нужен будет токен, но для начала проверим доступность)
        response = requests.get(f"{node_url}/security", timeout=5)
        if response.status_code == 200:
            print(f"✅ {node_name}: API работает, security status доступен")
            return True
        elif response.status_code == 401:
            print(f"⚠️  {node_name}: API работает, требуется аутентификация (это нормально)")
            return True
        else:
            print(f"❌ {node_name}: Ошибка API - статус {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {node_name}: Не удалось подключиться к API")
        return False
    except Exception as e:
        print(f"❌ {node_name}: Ошибка - {e}")
        return False

def main():
    print("🔍 ПРОВЕРКА СИСТЕМЫ ICOIN...")
    
    nodes = [
        ("http://localhost:8001", "Delegate1 (Шард 1)"),
        ("http://localhost:8002", "Delegate2 (Шард 2)")
    ]
    
    all_healthy = True
    for url, name in nodes:
        if not test_node_health(url, name):
            all_healthy = False
    
    if all_healthy:
        print("\n🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ КОРРЕКТНО!")
        print("📊 Следующие шаги:")
        print("   1. Проверить логи транзакций")
        print("   2. Протестировать создание блоков") 
        print("   3. Проверить межшардовую коммуникацию")
    else:
        print("\n⚠️  ЕСТЬ ПРОБЛЕМЫ! Проверьте логи контейнеров.")

if __name__ == "__main__":
    main()