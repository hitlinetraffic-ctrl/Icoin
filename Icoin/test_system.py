import requests
import time
import json

def test_node(node_url, node_name):
    print(f"🔍 Тестируем {node_name} ({node_url})...")
    
    try:
        # Пробуем получить security status
        response = requests.get(f"{node_url}/security", timeout=10)
        if response.status_code == 200:
            print(f"✅ {node_name}: Security API работает!")
            security_data = response.json()
            print(f"   Активные пиры: {security_data['network_security']['active_peers']}")
            print(f"   Черный список: {security_data['rate_limiting']['blacklisted']} адресов")
            return True
        elif response.status_code == 401:
            print(f"⚠️  {node_name}: Требуется аутентификация (но API доступен)")
            return True
        else:
            print(f"❌ {node_name}: Ошибка API - статус {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {node_name}: Не удалось подключиться")
        return False
    except Exception as e:
        print(f"❌ {node_name}: Ошибка - {e}")
        return False

def test_redis_cluster():
    print("\n🔍 Проверка Redis Cluster...")
    try:
        import subprocess
        # Проверяем состояние кластера через redis-cli
        cmd = "docker exec icoin-redis-node-1-1 redis-cli -a icoin_redis_secure_password_2025_change_me -p 7000 cluster info"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if "cluster_state:ok" in result.stdout:
            print("✅ Redis Cluster в состоянии 'ok'")
            # Парсим информацию о кластере
            for line in result.stdout.split('\n'):
                if 'cluster_' in line:
                    print(f"   {line}")
            return True
        else:
            print("❌ Redis Cluster не в состоянии 'ok'")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки Redis: {e}")
        return False

def main():
    print("🚀 ПОЛНАЯ ПРОВЕРКА СИСТЕМЫ ICOIN...")
    
    # Ждем немного для полного запуска
    print("⏳ Ожидаем полный запуск системы (30 секунд)...")
    time.sleep(30)
    
    # Проверяем Redis Cluster
    redis_ok = test_redis_cluster()
    
    # Проверяем узлы
    nodes = [
        ("http://localhost:8001", "Delegate1 (Шард 1)"),
        ("http://localhost:8002", "Delegate2 (Шард 2)")
    ]
    
    nodes_ok = True
    for url, name in nodes:
        if not test_node(url, name):
            nodes_ok = False
    
    print("\n" + "="*50)
    if redis_ok and nodes_ok:
        print("🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ КОРРЕКТНО!")
        print("\n📊 Следующие шаги:")
        print("   1. Проверить создание блоков")
        print("   2. Протестировать транзакции")
        print("   3. Проверить межшардовую коммуникацию")
        print("   4. Протестировать DPoS консенсус")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ!")
        if not redis_ok:
            print("   - Redis Cluster не работает")
        if not nodes_ok:
            print("   - Узлы не отвечают")
        
        print("\n🔧 Рекомендации:")
        print("   - Проверь логи: docker-compose logs delegate1")
        print("   - Перезапусти систему: docker-compose restart")
        print("   - Убедись, что порты 8001 и 8002 свободны")

if __name__ == "__main__":
    main()