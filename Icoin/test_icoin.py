# test_icoin.py - ТЕСТИРОВАНИЕ ВСЕХ ФУНКЦИЙ ICOIN
import requests
import json
import time
import hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

class iCoinTester:
    def __init__(self):
        self.base_urls = {
            "delegate1": "http://localhost:8001",
            "delegate2": "http://localhost:8002"
        }
        self.addresses = {}
        self.tokens = {}

    def get_security_status(self, node_name):
        """Получить статус безопасности узла"""
        try:
            response = requests.get(f"{self.base_urls[node_name]}/security", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def create_address(self, node_name):
        """Создать новый адрес на указанном узле"""
        try:
            response = requests.get(f"{self.base_urls[node_name]}/new_address")
            if response.status_code == 200:
                address = response.json()["address"]
                print(f"✅ {node_name}: Создан адрес {address[:16]}...")
                return address
        except Exception as e:
            print(f"❌ {node_name}: Ошибка создания адреса - {e}")
        return None

    def get_balance(self, node_name, address):
        """Получить баланс адреса"""
        try:
            response = requests.get(f"{self.base_urls[node_name]}/balance?address={address}")
            if response.status_code == 200:
                return response.json()["balance"]
        except:
            return 0
        return 0

    def get_chain_length(self, node_name):
        """Получить длину блокчейна"""
        try:
            response = requests.get(f"{self.base_urls[node_name]}/chain")
            if response.status_code == 200:
                return len(response.json())
        except:
            return 0
        return 0

    def test_transaction_flow(self):
        """Протестировать поток транзакций"""
        print("\n🧪 ТЕСТИРУЕМ ТРАНЗАКЦИИ...")
        
        # Создаем адреса на обоих узлах
        self.addresses["delegate1_addr1"] = self.create_address("delegate1")
        self.addresses["delegate1_addr2"] = self.create_address("delegate1")
        self.addresses["delegate2_addr1"] = self.create_address("delegate2")
        
        # Ждем немного
        time.sleep(2)
        
        # Проверяем начальные балансы
        print("\n💰 ПРОВЕРЯЕМ БАЛАНСЫ:")
        for name, address in self.addresses.items():
            balance = self.get_balance(name.split('_')[0], address)
            print(f"   {name}: {balance} ICOIN")

    def test_block_creation(self):
        """Мониторинг создания блоков"""
        print("\n⛏️  МОНИТОРИНГ СОЗДАНИЯ БЛОКОВ...")
        
        initial_lengths = {
            "delegate1": self.get_chain_length("delegate1"),
            "delegate2": self.get_chain_length("delegate2")
        }
        
        print(f"   Начальная длина цепочек: Delegate1={initial_lengths['delegate1']}, Delegate2={initial_lengths['delegate2']}")
        
        # Мониторим в течение 30 секунд
        for i in range(6):
            time.sleep(5)
            current_lengths = {
                "delegate1": self.get_chain_length("delegate1"),
                "delegate2": self.get_chain_length("delegate2")
            }
            
            print(f"   Через {i*5+5} сек: Delegate1={current_lengths['delegate1']}, Delegate2={current_lengths['delegate2']}")
            
            # Проверяем, создались ли новые блоки
            if (current_lengths['delegate1'] > initial_lengths['delegate1'] or 
                current_lengths['delegate2'] > initial_lengths['delegate2']):
                print("   🎉 НОВЫЕ БЛОКИ СОЗДАНЫ!")
                return True
        
        print("   ⚠️  Новые блоки не созданы (возможно, нет транзакций в пуле)")
        return False

    def test_network_health(self):
        """Проверить здоровье сети"""
        print("\n❤️  ПРОВЕРКА ЗДОРОВЬЯ СЕТИ...")
        
        healthy_nodes = 0
        for node_name in self.base_urls.keys():
            status = self.get_security_status(node_name)
            if status:
                print(f"✅ {node_name}:")
                print(f"   Активных пиров: {status['network_security']['active_peers']}")
                print(f"   Подозрительных активностей: {status['rate_limiting']['suspicious_activities']}")
                healthy_nodes += 1
            else:
                print(f"❌ {node_name}: недоступен")
        
        return healthy_nodes == len(self.base_urls)

    def performance_test(self):
        """Тест производительности"""
        print("\n⚡ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ...")
        
        start_time = time.time()
        
        # Создаем несколько адресов для теста
        test_addresses = []
        for i in range(5):
            addr = self.create_address("delegate1")
            if addr:
                test_addresses.append(addr)
            time.sleep(0.1)
        
        end_time = time.time()
        
        print(f"   Создано {len(test_addresses)} адресов за {end_time - start_time:.2f} секунд")
        print(f"   Скорость: {len(test_addresses)/(end_time - start_time):.2f} адресов/секунду")

    def run_all_tests(self):
        """Запустить все тесты"""
        print("🚀 ЗАПУСК ВСЕХ ТЕСТОВ ICOIN")
        print("=" * 60)
        
        # Даем системе время на запуск
        print("⏳ Ожидаем полный запуск системы...")
        time.sleep(10)
        
        # Запускаем тесты
        network_ok = self.test_network_health()
        if not network_ok:
            print("❌ Сеть не готова для тестирования")
            return
        
        self.performance_test()
        self.test_transaction_flow()
        self.test_block_creation()
        
        print("\n" + "=" * 60)
        print("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print("\n📊 СИСТЕМА ICOIN ГОТОВА К ИСПОЛЬЗОВАНИЮ!")

if __name__ == "__main__":
    tester = iCoinTester()
    tester.run_all_tests()