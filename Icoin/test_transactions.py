# test_transactions.py
import requests
import json
import time

def test_transaction_flow():
    print("🧪 Тестируем поток транзакций...")
    
    # Создаем адреса
    response = requests.get("http://localhost:8001/new_address")
    address1 = response.json()["address"]
    
    response = requests.get("http://localhost:8002/new_address") 
    address2 = response.json()["address"]
    
    print(f"📍 Созданы адреса: {address1[:8]}... и {address2[:8]}...")
    
    # TODO: Добавить логику подписи транзакций
    # Это потребует JWT токен и подписание
    
test_transaction_flow()