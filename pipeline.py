# processor.py
from ai_clients import ai1, ai2
from merger import merge


def process_bank(bank_name: str):
    print(f"\n🔍 Обработка: {bank_name}")
    
    results_ai1 = ai1.search(bank_name)
    print(f"  AI-1: {len(results_ai1)} результатов")
    for p in results_ai1:
        print(f"    - {p.full_name} ({p.position})")
    
    results_ai2 = ai2.search(bank_name)
    print(f"  AI-2: {len(results_ai2)} результатов")
    for p in results_ai2:
        print(f"    - {p.full_name} ({p.position})")
    
    final_results = merge(results_ai1, results_ai2)
    print(f"  Итого после слияния: {len(final_results)} человек(а)")
    
    return final_results