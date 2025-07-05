from dataclasses import dataclass
from typing import Optional


@dataclass
class CompanyNullModel:
    country: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
