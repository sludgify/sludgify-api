from dataclasses import dataclass
from typing import Optional


@dataclass
class CompanyNullModel:
    id: Optional[str] = None
    country: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
