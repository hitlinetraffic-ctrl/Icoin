# check_containers.py 
import docker
import time
import sys

def check_containers():
    client = docker.from_env()
    
    print("🔍 Проверка состояния контейнеров...")
    
    containers = client.containers.list(all=True)
    
    for container in containers:
        print(f"📦 {container.name}: {container.status}")
        
        if container.status == "exited":
            print(f"   ❌ Контейнер завершился. Логи:")
            logs = container.logs(tail=20).decode('utf-8')
            print(f"   {logs}")
            
        elif container.status == "running":
            print(f"   ✅ Контейнер работает")

def check_redis_cluster():
    """Проверка Redis Cluster"""
    print("\n🔍 Проверка Redis Cluster...")
    try:
        client = docker.from_env()
        redis_container = client.containers.get('icoin-redis-node-1-1')
        
        # Проверяем, запущен ли Redis
        exec_result = redis_container.exec_run(
            "redis-cli -a icoin_redis_secure_password_2025_change_me -p 7000 ping"
        )
        
        if b"PONG" in exec_result.output:
            print("✅ Redis Node 1 работает")
        else:
            print("❌ Redis Node 1 не отвечает")
            
    except Exception as e:
        print(f"❌ Ошибка проверки Redis: {e}")

if __name__ == "__main__":
    check_containers()
    check_redis_cluster()