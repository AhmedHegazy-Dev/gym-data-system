from enum import Enum

class MembershipType(str, Enum):
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"