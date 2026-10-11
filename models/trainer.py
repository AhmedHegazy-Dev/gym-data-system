from typing import List, Dict, Any, Union
from models.person import Person


class Trainer(Person):

    def __init__(
        self,
        id: str,
        name: str,
        phone: str,
        email: str,
        specialty: str,
        salary: float,
        is_available: bool = True,
        assigned_members: Union[List[str], None] = None
    ) -> None:
        super().__init__(id, name, phone, email)
        self.__specialty: str = specialty
        self.__salary: float = float(salary)
        self.__is_available: bool = is_available
        self.__assigned_members: List[str] = assigned_members if assigned_members is not None else []

    @property
    def specialty(self) -> str:
        return self.__specialty

    @specialty.setter
    def specialty(self, value: str) -> None:
        self.__specialty = value

    @property
    def salary(self) -> float:
        return self.__salary

    @salary.setter
    def salary(self, value: float) -> None:
        self.__salary = float(value)

    @property
    def is_available(self) -> bool:
        return self.__is_available

    @is_available.setter
    def is_available(self, value: bool) -> None:
        self.__is_available = value

    @property
    def assigned_members(self) -> List[str]:
        return self.__assigned_members

    def assign_member(self, member_id: Union[str, Any]) -> None:
        m_id = member_id.id if hasattr(member_id, "id") else str(member_id)
        if m_id not in self.__assigned_members:
            self.__assigned_members.append(m_id)

    def unassign_member(self, member_id: Union[str, Any]) -> None:
        m_id = member_id.id if hasattr(member_id, "id") else str(member_id)
        if m_id in self.__assigned_members:
            self.__assigned_members.remove(m_id)

    def get_role(self) -> str:
        return "Trainer"

    def display_info(self) -> str:
        status = "Available" if self.__is_available else "Busy"
        return f"Trainer [{self.id}] {self.name} | Specialty: {self.__specialty} | Status: {status} | Salary: ${self.__salary:.2f}"

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "specialty": self.__specialty,
            "salary": self.__salary,
            "is_available": self.__is_available,
            "assigned_members": self.__assigned_members,
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trainer":
        return cls(
            id=data["id"],
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
            specialty=data["specialty"],
            salary=data["salary"],
            is_available=data.get("is_available", True),
            assigned_members=data.get("assigned_members", []),
        )
