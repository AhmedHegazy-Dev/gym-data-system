from datetime import date
from typing import Dict, Any
from models.enums import PaymentMethod


class Payment:

    def __init__(
        self,
        id: str,
        membership_id: str,
        amount: float,
        payment_date: date,
        method: PaymentMethod
    ) -> None:
        self.__id: str = id
        self.__membership_id: str = membership_id
        self.__amount: float = float(amount)
        self.__payment_date: date = payment_date
        self.__method: PaymentMethod = method

    @property
    def id(self) -> str:
        return self.__id

    @property
    def membership_id(self) -> str:
        return self.__membership_id

    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def payment_date(self) -> date:
        return self.__payment_date

    @property
    def method(self) -> PaymentMethod:
        return self.__method

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.__id,
            "membership_id": self.__membership_id,
            "amount": self.__amount,
            "payment_date": self.__payment_date.isoformat(),
            "method": self.__method.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Payment":
        raw_date = data.get("payment_date") or data.get("date")
        parsed_date = date.fromisoformat(raw_date) if isinstance(raw_date, str) else raw_date
        return cls(
            id=data["id"],
            membership_id=data["membership_id"],
            amount=float(data["amount"]),
            payment_date=parsed_date,
            method=PaymentMethod(data["method"]),
        )
