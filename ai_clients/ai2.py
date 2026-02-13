from models import Person
from ai_clients.base import build_prompt, call_model


def search(bank_name: str):
    prompt = build_prompt(bank_name)
    data = call_model(prompt)

    persons = []
    for item in data:
        persons.append(
            Person(
                bank=bank_name,
                full_name=item.get("full_name"),
                position=item.get("position"),
                phone=item.get("phone"),
                email=item.get("email"),
                social_links=item.get("social_links"),
                source="AI-2"
            )
        )
    return persons
