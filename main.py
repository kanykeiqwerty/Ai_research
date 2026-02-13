from excel import load_banks, save_results
from pipeline import process_bank
import sys

def main():
    input_file = "Копия Проэкты.xlsx"
    output_file = "results1.xlsx"
    
    banks = load_banks(input_file)
    print(f"📋 Загружено банков: {len(banks)}")
    
    all_persons = []

    try:
        for bank in banks:
            persons = process_bank(bank)
            all_persons.extend(persons)
            print(f"✅ {bank}: найдено {len(persons)} человек(а)")
            
            # 💾 сохраняем после каждого банка (самый безопасный вариант)
            save_results(output_file, all_persons)

    except KeyboardInterrupt:
        print("\n⛔ Программа остановлена вручную!")

    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")

    finally:
        # 🔐 гарантированное сохранение при любом завершении
        if all_persons:
            save_results(output_file, all_persons)
            print(f"\n💾 Сохранено {len(all_persons)} записей в {output_file}")
        else:
            print("\n⚠️ Нет данных для сохранения")

if __name__ == "__main__":
    main()