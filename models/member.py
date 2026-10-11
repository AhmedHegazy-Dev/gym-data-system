from datetime import date
from typing import List, Optional, Dict, Any
from models.person import Person
from models.membership import Membership
from models.attendance import Attendance


class Member(Person):

    def __init__(
        self,
        id: str,
        name: str,
        phone: str,
        email: str,
        join_date: Optional[date] = None,
        memberships: Optional[List[Membership]] = None,
        attendances: Optional[List[Attendance]] = None
    ) -> None:
        super().__init__(id, name, phone, email)
        self.__join_date: date = join_date if join_date is not None else date.today()
        self.__memberships: List[Membership] = memberships if memberships is not None else []
        self.__attendances: List[Attendance] = attendances if attendances is not None else []

    @property
    def join_date(self) -> date:
        return self.__join_date

    @property
    def memberships(self) -> List[Membership]:
        return self.__memberships

    @property
    def attendances(self) -> List[Attendance]:
        return self.__attendances

    @property
    def active_membership(self) -> Optional[Membership]:
        for m in self.__memberships:
            if m.is_active():
                return m
        return None

    def has_active_membership(self) -> bool:
        return self.active_membership is not None

    def get_active_membership(self) -> Optional[Membership]:
        return self.active_membership

    def add_membership(self, m: Membership) -> None:
        self.__memberships.append(m)

    def record_attendance(self, a: Attendance) -> None:
        self.__attendances.append(a)

    def get_role(self) -> str:
        return "Member"

    def display_info(self) -> str:
        status = "Active" if self.has_active_membership() else "Inactive/Expired"
        return f"Member [{self.id}] {self.name} | Phone: {self.phone} | Status: {status} | Joined: {self.join_date}"

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "join_date": self.__join_date.isoformat(),
            "memberships": [m.to_dict() for m in self.__memberships],
            "attendances": [a.to_dict() for a in self.__attendances],
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Member":
        raw_join_date = data.get("join_date")
        parsed_join_date = date.fromisoformat(raw_join_date) if raw_join_date else None

        memberships = [Membership.from_dict(m) for m in data.get("memberships", [])]
        attendances = [Attendance.from_dict(a) for a in data.get("attendances", [])]

        return cls(
            id=data["id"],
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
            join_date=parsed_join_date,
            memberships=memberships,
            attendances=attendances,
        )
