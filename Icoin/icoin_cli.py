# icoin_cli.py - КОМАНДНЫЙ ИНТЕРФЕЙС ДЛЯ ICOIN
import requests
import json
import sys
import time

class iCoinCLI:
    def __init__(self):
        self.nodes = {
            "1": "http://localhost:8001",
            "2": "http://localhost:8002"
        }
        self.current_node = "1"

    def get_node_url(self):
        return self.nodes[self.current_node]

    def print_status(self):
        """Показать статус системы"""
        print("\n📊 СТАТУС СИСТЕМЫ ICOIN:")
        print("=" * 40)
        
        for node_id, url in self.nodes.items():
            try:
                response = requests.get(f"{url}/security", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"🟢 Узел {node_id}:")
                    print(f"   Цепочка: {len(requests.get(f'{url}/chain').json())} блоков")
                    print(f"   Пиры: {data['network_security']['active_peers']}")
                    print(f"   Безопасность: ✅")
                else:
                    print(f"🔴 Узел {node_id}: недоступен")
            except:
                print(f"🔴 Узел {node_id}: недоступен")

    def create_address(self):
        """Создать новый адрес"""
        try:
            response = requests.get(f"{self.get_node_url()}/new_address")
            if response.status_code == 200:
                address = response.json()["address"]
                print(f"✅ Создан новый адрес: {address}")
                return address
            else:
                print("❌ Ошибка при создании адреса")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def check_balance(self, address):
        """Проверить баланс"""
        try:
            response = requests.get(f"{self.get_node_url()}/balance?address={address}")
            if response.status_code == 200:
                balance = response.json()["balance"]
                print(f"💰 Баланс адреса {address[:16]}...: {balance} ICOIN")
                return balance
            else:
                print("❌ Адрес не найден")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def show_blockchain(self):
        """Показать блокчейн"""
        try:
            response = requests.get(f"{self.get_node_url()}/chain")
            if response.status_code == 200:
                chain = response.json()
                print(f"\n⛓️  БЛОКЧЕЙН (всего {len(chain)} блоков):")
                print("-" * 50)
                
                for i, block in enumerate(chain[-5:]):  # Показываем последние 5 блоков
                    print(f"Блок #{block['index']}:")
                    print(f"  Хеш: {block['hash'][:16]}...")
                    print(f"  Время: {time.ctime(block['timestamp'])}")
                    print(f"  Транзакций: {len(block['transactions'])}")
                    print(f"  Майнер: {block['miner']}")
                    print(f"  Шард: {block['shard_id']}")
                    print()
                
                if len(chain) > 5:
                    print(f"... и еще {len(chain) - 5} блоков")
            else:
                print("❌ Ошибка при получении цепочки")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def switch_node(self, node_id):
        """Переключиться на другой узел"""
        if node_id in self.nodes:
            self.current_node = node_id
            print(f"✅ Переключен на узел {node_id}")
        else:
            print("❌ Неверный ID узла")

    def show_help(self):
        """Показать справку"""
        print("\n📖 КОМАНДЫ ICOIN CLI:")
        print("  status       - Показать статус системы")
        print("  address      - Создать новый адрес")
        print("  balance <адрес> - Проверить баланс")
        print("  blockchain   - Показать блокчейн")
        print("  switch <id>  - Переключиться на узел (1 или 2)")
        print("  help         - Показать эту справку")
        print("  exit         - Выйти")

    def run(self):
        """Запустить CLI"""
        print("🚀 ICOIN COMMAND LINE INTERFACE")
        print("Введите 'help' для списка команд")
        
        while True:
            try:
                command = input(f"\nicoin[node-{self.current_node}]> ").strip().split()
                
                if not command:
                    continue
                    
                cmd = command[0].lower()
                
                if cmd == "exit":
                    print("👋 До свидания!")
                    break
                elif cmd == "status":
                    self.print_status()
                elif cmd == "address":
                    self.create_address()
                elif cmd == "balance" and len(command) > 1:
                    self.check_balance(command[1])
                elif cmd == "blockchain":
                    self.show_blockchain()
                elif cmd == "switch" and len(command) > 1:
                    self.switch_node(command[1])
                elif cmd == "help":
                    self.show_help()
                else:
                    print("❌ Неизвестная команда. Введите 'help' для справки.")
                    
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    cli = iCoinCLI()
    cli.run()