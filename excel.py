import pandas as pd


def load_banks(file_path: str):
    df = pd.read_excel(file_path)
    return df["БАНК"].dropna().tolist()


def save_results(file_path: str, persons: list):
    data = []

    for p in persons:
        data.append({
            "Банк": p.bank,
            "ФИО": p.full_name,
            "Должность": p.position,
            "Телефон": p.phone,
            "Email": p.email,
            "Соцсети": p.social_links,
            "Источник": p.source,
            "Дата сбора": p.date_collected,
            "Статус": p.status,
            "Комментарий": p.comment
        })

    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)