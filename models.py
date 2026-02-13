from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Person:
    bank: str
    full_name: str
    position: str
    phone: Optional[str]=None
    email: Optional[str]=None
    social_links: Optional[str]=None
    source: str = ""
    date_collected: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    status: str = "Найдено"
    comment: str = ""
