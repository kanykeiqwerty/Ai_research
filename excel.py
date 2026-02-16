import pandas as pd


def load_banks(file_path: str):
    df = pd.read_excel(file_path)
    return df["БАНК"].dropna().tolist()


def save_results(file_path: str, persons: list):
    data = []

    for p in persons:
        data.append({
            "Банк": p.bank,
            "ФИО": p.full_name if p.full_name else "",  # Пустая строка вместо None
            "Должность": p.position if p.position else "",
            "Телефон": p.phone if p.phone else "",
            "Email": p.email if p.email else "",
            "Соцсети": p.social_links if p.social_links else "",
            "Источник": p.source,
            "Дата сбора": p.date_collected,
            "Статус": p.status,
            "Комментарий": p.comment if p.comment else ""
        })

    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)


