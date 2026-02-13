from excel import load_banks, save_results
from pipeline import process_bank





def main():
    input_file = "Копия Проэкты.xlsx"  # файл со списком банков
    output_file = "results1.xlsx"  # файл для результатов
    
    # Загружаем список банков
    banks = load_banks(input_file)
    print(f"📋 Загружено банков: {len(banks)}")
    
    # Собираем все результаты
    all_persons = []
    
    for bank in banks[:5]:
        persons = process_bank(bank)
        all_persons.extend(persons)  # добавляем в общий список
        print(f"✅ {bank}: найдено {len(persons)} человек(а)")
    
    # Сохраняем все результаты
    save_results(output_file, all_persons)
    print(f"\n💾 Сохранено {len(all_persons)} записей в {output_file}")


if __name__ == "__main__":
    main()