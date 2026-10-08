from enum import Enum


class PaymentMethod(str, Enum):
    CASH = "Cash"
    CARD = "Card"
    ONLINE = "Online"
