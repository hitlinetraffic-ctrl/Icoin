import docker
import time
import subprocess

def check_redis_manually():
    print("🔍 РУЧНАЯ ПРОВЕРКА REDIS CLUSTER...")
    
    client = docker.from_env()
    
    # Проверяем контейнеры
    containers = client.containers.list(all=True)
    redis_containers = [c for c in containers if 'redis-node' in c.name]
    
    print(f"📦 Найдено Redis контейнеров: {len(redis_containers)}")
    
    for container in redis_containers:
        print(f"\n🔎 Проверка {container.name}:")
        print(f"   Статус: {container.status}")
        
        if container.status == "running":
            # Пробуем пинговать каждый узел
            try:
                # Получаем IP контейнера
                inspect = client.api.inspect_container(container.id)
                ip = inspect['NetworkSettings']['Networks']['icoin_icoin-network']['IPAddress']
                port = 7000 if 'redis-node-1' in container.name else 7001 if 'redis-node-2' in container.name else 7002
                
                # Пинг через redis-cli
                cmd = f"docker exec {container.name} redis-cli -a icoin_redis_secure_password_2025_change_me -p {port} ping"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if "PONG" in result.stdout:
                    print(f"   ✅ Redis на порту {port} отвечает")
                else:
                    print(f"   ❌ Redis на порту {port} не отвечает: {result.stderr}")
                    
            except Exception as e:
                print(f"   ❌ Ошибка проверки: {e}")
    
    # Проверяем возможность создания кластера вручную
    print("\n🎯 ПОПЫТКА РУЧНОГО СОЗДАНИЯ КЛАСТЕРА...")
    try:
        cmd = 'docker exec icoin-redis-node-1-1 redis-cli -a icoin_redis_secure_password_2025_change_me --cluster create 172.20.0.2:7000 172.20.0.3:7001 172.20.0.4:7002 --cluster-replicas 0 --cluster-yes'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Кластер успешно создан!")
            print(result.stdout)
        else:
            print("❌ Ошибка создания кластера:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def get_redis_ips():
    """Получить IP адреса Redis контейнеров"""
    print("\n🌐 ПОЛУЧЕНИЕ IP АДРЕСОВ REDIS...")
    client = docker.from_env()
    
    containers = client.containers.list(filters={"name": "redis-node"})
    for container in containers:
        inspect = client.api.inspect_container(container.id)
        networks = inspect['NetworkSettings']['Networks']
        for network_name, network_settings in networks.items():
            if 'icoin' in network_name:
                ip = network_settings['IPAddress']
                print(f"   {container.name}: {ip}")

if __name__ == "__main__":
    get_redis_ips()
    check_redis_manually()