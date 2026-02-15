import json
from excel import load_banks, save_results
from ai_clients import ai1, ai2
from merger import merge

CHECKPOINT_FILE = "checkpoint.json"

def save_checkpoint(results):
    """Сохраняем текущие результаты в JSON."""
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({k: [p.__dict__ for p in v] for k, v in results.items()}, f, ensure_ascii=False)

def load_checkpoint():
    """Загружаем результаты из checkpoint, если он есть."""
    try:
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Восстановление объектов Person
        return {bank: [type('Person', (), p)() for p in persons] for bank, persons in data.items()}
    except FileNotFoundError:
        return {}

def process_bank(bank_name: str):
    """Обрабатываем банк через AI-1 и AI-2 и объединяем результаты."""
    return merge(ai1.search(bank_name) or [], ai2.search(bank_name) or [])

def main():
    banks = load_banks("Копия Проэкты.xlsx")
    
    results = load_checkpoint()  # продолжаем с checkpoint, если есть
    
    for bank in banks:
        if bank not in results:  # пропускаем уже обработанные
            results[bank] = process_bank(bank)
            save_checkpoint(results)  # сохраняем после каждого банка

    all_persons = [person for persons in results.values() for person in persons]
    save_results("results.xlsx", all_persons)

if __name__ == "__main__":
    main()
