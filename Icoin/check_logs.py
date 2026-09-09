import docker
import time
import sys

def get_container_logs(container_name, follow=False, tail=100):
    """
    Получает и выводит логи указанного контейнера.

    :param container_name: Имя контейнера (например, 'icoin-icoin-delegate1-1')
    :param follow: Если True, выводит логи в реальном времени
    :param tail: Количество последних строк для вывода (по умолчанию 100)
    """
    try:
        # Подключаемся к Docker
        client = docker.from_client()

        # Находим контейнер по имени
        containers = client.containers.list(all=True)
        target_container = None
        for container in containers:
            if container_name in container.name:
                target_container = container
                break

        if not target_container:
            print(f"Контейнер с именем '{container_name}' не найден.")
            return

        # Получаем логи
        if follow:
            print(f"Следим за логами контейнера '{target_container.name}' в реальном времени (Ctrl+C для выхода)...")
            for line in target_container.logs(stream=True, follow=True, tail=tail):
                print(line.decode('utf-8').strip())
        else:
            logs = target_container.logs(tail=tail).decode('utf-8')
            print(f"Последние {tail} строк логов контейнера '{target_container.name}':")
            print(logs)

    except docker.errors.DockerException as e:
        print(f"Ошибка подключения к Docker: {e}")
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def list_containers():
    """Выводит список всех контейнеров из текущего проекта."""
    try:
        client = docker.from_client()
        containers = client.containers.list(all=True)
        print("Доступные контейнеры:")
        for container in containers:
            print(f"- {container.name} (статус: {container.status})")
    except docker.errors.DockerException as e:
        print(f"Ошибка подключения к Docker: {e}")

if __name__ == "__main__":
    # Примеры использования:
    # python check_logs.py icoin-icoin-delegate1-1          # Последние 100 строк
    # python check_logs.py icoin-icoin-delegate1-1 follow  # В реальном времени
    # python check_logs.py list                            # Список контейнеров

    if len(sys.argv) < 2:
        print("Использование:")
        print("  python check_logs.py <container_name> [follow] - получить логи контейнера")
        print("  python check_logs.py list - вывести список контейнеров")
        print("Примеры:")
        print("  python check_logs.py icoin-icoin-delegate1-1")
        print("  python check_logs.py icoin-icoin-delegate1-1 follow")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_containers()
    else:
        container_name = sys.argv[1]
        follow = len(sys.argv) > 2 and sys.argv[2] == "follow"
        get_container_logs(container_name, follow=follow)