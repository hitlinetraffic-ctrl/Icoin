#!/bin/sh

# Ожидание готовности узлов Redis
echo "Ожидание запуска узлов Redis..."
sleep 20

# Попытка инициализации кластера
echo "Попытка инициализации кластера Redis..."
max_attempts=10
attempt=1

while [ $attempt -le $max_attempts ]
do
    echo "Попытка $attempt из $max_attempts..."
    redis-cli -a icoin_redis_secure_password_2025_change_me --cluster create redis-node-1:7000 redis-node-2:7001 redis-node-3:7002 --cluster-replicas 0 --cluster-yes
    
    if [ $? -eq 0 ]; then
        echo "Кластер Redis успешно создан!"
        exit 0
    fi
    
    echo "Ошибка при создании кластера. Повтор через 10 секунд..."
    sleep 10
    attempt=$((attempt+1))
done

echo "Не удалось создать кластер Redis после $max_attempts попыток."
exit 1