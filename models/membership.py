from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from models.enums import MembershipType, MembershipStatus
from models.payment import Payment


class Membership:

    def __init__(
        self,
        id: str,
        member_id: str,
        type: MembershipType,
        start_date: date,
        end_date: date,
        price: float,
        status: MembershipStatus = MembershipStatus.ACTIVE,
        payments: Optional[List[Payment]] = None
    ) -> None:
        self.__id: str = id
        self.__member_id: str = member_id
        self.__type: MembershipType = type
        self.__start_date: date = start_date
        self.__end_date: date = end_date
        self.__price: float = float(price)
        self.__status: MembershipStatus = status
        self.__payments: List[Payment] = payments if payments is not None else []

    @property
    def id(self) -> str:
        return self.__id

    @property
    def member_id(self) -> str:
        return self.__member_id

    @property
    def type(self) -> MembershipType:
        return self.__type

    @property
    def start_date(self) -> date:
        return self.__start_date

    @property
    def end_date(self) -> date:
        return self.__end_date

    @property
    def price(self) -> float:
        return self.__price

    @property
    def status(self) -> MembershipStatus:
        return self.__status

    @status.setter
    def status(self, value: MembershipStatus) -> None:
        self.__status = value

    @property
    def payments(self) -> List[Payment]:
        return self.__payments

    def is_active(self) -> bool:
        today = date.today()
        return self.__status == MembershipStatus.ACTIVE and (self.__start_date <= today <= self.__end_date)

    def is_expired(self) -> bool:
        return self.__status == MembershipStatus.EXPIRED or date.today() > self.__end_date

    def renew(self, months: int) -> None:
        today = date.today()
        base_date = max(self.__end_date, today)
        self.__end_date = base_date + timedelta(days=months * 30)
        self.__status = MembershipStatus.ACTIVE

    def add_payment(self, payment: Payment) -> None:
        self.__payments.append(payment)

    def get_total_paid(self) -> float:
        return sum(p.amount for p in self.__payments)

    def get_remaining_balance(self) -> float:
        return max(0.0, self.__price - self.get_total_paid())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.__id,
            "member_id": self.__member_id,
            "type": self.__type.value,
            "start_date": self.__start_date.isoformat(),
            "end_date": self.__end_date.isoformat(),
            "price": self.__price,
            "status": self.__status.value,
            "payments": [p.to_dict() for p in self.__payments],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Membership":
        payments_data = [Payment.from_dict(p) for p in data.get("payments", [])]
        return cls(
            id=data["id"],
            member_id=data["member_id"],
            type=MembershipType(data["type"]),
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"]),
            price=float(data["price"]),
            status=MembershipStatus(data.get("status", MembershipStatus.ACTIVE.value)),
            payments=payments_data,
        )
