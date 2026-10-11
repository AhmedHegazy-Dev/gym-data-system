from datetime import datetime
from typing import Dict, Any, Optional


class Attendance:

    def __init__(
        self,
        id: str,
        member_id: str,
        trainer_id: Optional[str] = None,
        check_in: Optional[datetime] = None,
        check_out: Optional[datetime] = None
    ) -> None:
        self.__id: str = id
        self.__member_id: str = member_id
        self.__trainer_id: Optional[str] = trainer_id
        self.__check_in: datetime = check_in if check_in is not None else datetime.now()
        self.__check_out: Optional[datetime] = check_out

    @property
    def id(self) -> str:
        return self.__id

    @property
    def member_id(self) -> str:
        return self.__member_id

    @property
    def trainer_id(self) -> Optional[str]:
        return self.__trainer_id

    @trainer_id.setter
    def trainer_id(self, value: Optional[str]) -> None:
        self.__trainer_id = value

    @property
    def check_in(self) -> datetime:
        return self.__check_in

    @property
    def check_out(self) -> Optional[datetime]:
        return self.__check_out

    @check_out.setter
    def check_out(self, value: datetime) -> None:
        self.__check_out = value

    def duration_minutes(self) -> int:
        if self.__check_out and self.__check_in:
            return int((self.__check_out - self.__check_in).total_seconds() // 60)
        return 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.__id,
            "member_id": self.__member_id,
            "trainer_id": self.__trainer_id,
            "check_in": self.__check_in.isoformat(),
            "check_out": self.__check_out.isoformat() if self.__check_out else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attendance":
        raw_check_in = data.get("check_in")
        raw_check_out = data.get("check_out")

        parsed_check_in = datetime.fromisoformat(raw_check_in) if raw_check_in else None
        parsed_check_out = datetime.fromisoformat(raw_check_out) if raw_check_out else None

        return cls(
            id=data["id"],
            member_id=data["member_id"],
            trainer_id=data.get("trainer_id"),
            check_in=parsed_check_in,
            check_out=parsed_check_out,
        )