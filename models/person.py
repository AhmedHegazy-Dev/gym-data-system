from abc import ABC, abstractmethod
from typing import Dict, Any


class Person(ABC):

    def __init__(self, id: str, name: str, phone: str, email: str) -> None:
        self.__id: str = id
        self.__name: str = name
        self.__phone: str = phone
        self.__email: str = email

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    @property
    def phone(self) -> str:
        return self.__phone

    @phone.setter
    def phone(self, value: str) -> None:
        self.__phone = value

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, value: str) -> None:
        self.__email = value

    @abstractmethod
    def get_role(self) -> str:
        pass

    def display_info(self) -> str:
        return f"ID: {self.__id} | Name: {self.__name} | Phone: {self.__phone} | Email: {self.__email}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.__id,
            "name": self.__name,
            "phone": self.__phone,
            "email": self.__email,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        return cls(data["id"], data["name"], data["phone"], data["email"])
