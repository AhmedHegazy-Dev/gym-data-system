from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid

from models.member import Member
from models.trainer import Trainer
from models.membership import Membership
from models.payment import Payment
from models.attendance import Attendance
from models.enums import MembershipType, MembershipStatus, PaymentMethod
from models.exception import ValidationError, BusinessRuleError
from file_manager.file_manager import FileManager


class Gym:

    def __init__(self, name: str = "Instant Fitness Gym", data_dir: str = "data") -> None:
        self.__name: str = name
        self.__file_manager: FileManager = FileManager(data_dir=data_dir)

        self.__members: List[Member] = []
        self.__trainers: List[Trainer] = []
        self.__memberships: List[Membership] = []
        self.__payments: List[Payment] = []
        self.__attendances: List[Attendance] = []

        self.load_data()
        if len(self.__members) == 0:
            self.seed_sample_data()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def members(self) -> List[Member]:
        return self.__members

    @property
    def trainers(self) -> List[Trainer]:
        return self.__trainers

    @property
    def memberships(self) -> List[Membership]:
        return self.__memberships

    @property
    def payments(self) -> List[Payment]:
        return self.__payments

    @property
    def attendances(self) -> List[Attendance]:
        return self.__attendances

    def add_member(self, member: Member) -> None:
        if not member.id or not member.name.strip():
            raise ValidationError("Member ID and Name cannot be empty.", 400)
        if any(m.id == member.id for m in self.__members):
            raise ValidationError(f"Member with ID '{member.id}' already exists.", 409)
        self.__members.append(member)
        self.save_data()

    def update_member(self, updated_member: Member) -> None:
        existing = self.find_member(updated_member.id)
        if not existing:
            raise ValidationError(f"Cannot update: Member '{updated_member.id}' not found.", 404)
        existing.name = updated_member.name
        existing.phone = updated_member.phone
        existing.email = updated_member.email
        self.save_data()

    def delete_member(self, member_id: str) -> None:
        member = self.find_member(member_id)
        if not member:
            raise ValidationError(f"Cannot delete: Member '{member_id}' not found.", 404)
        self.__members = [m for m in self.__members if m.id != member_id]
        for t in self.__trainers:
            t.unassign_member(member_id)
        self.save_data()

    def find_member(self, member_id: str) -> Optional[Member]:
        for m in self.__members:
            if m.id == member_id:
                return m
        return None

    def search_members(self, query: str) -> List[Member]:
        q = query.strip().lower()
        if not q:
            return list(self.__members)
        return [
            m for m in self.__members
            if q in m.name.lower() or q in m.id.lower() or q in m.phone.lower()
        ]

    def filter_members(self, status: str) -> List[Member]:
        s = status.strip().lower()
        if s == "active":
            return [m for m in self.__members if m.has_active_membership()]
        elif s in ("expired", "inactive"):
            return [m for m in self.__members if not m.has_active_membership()]
        return list(self.__members)

    def add_trainer(self, trainer: Trainer) -> None:
        if not trainer.id or not trainer.name.strip():
            raise ValidationError("Trainer ID and Name cannot be empty.", 400)
        if any(t.id == trainer.id for t in self.__trainers):
            raise ValidationError(f"Trainer with ID '{trainer.id}' already exists.", 409)
        self.__trainers.append(trainer)
        self.save_data()

    def find_trainer(self, trainer_id: str) -> Optional[Trainer]:
        for t in self.__trainers:
            if t.id == trainer_id:
                return t
        return None

    def assign_trainer(self, member_id: str, trainer_id: str) -> None:
        member = self.find_member(member_id)
        if not member:
            raise ValidationError(f"Member '{member_id}' not found.", 404)
        trainer = self.find_trainer(trainer_id)
        if not trainer:
            raise ValidationError(f"Trainer '{trainer_id}' not found.", 404)
        trainer.assign_member(member.id)
        self.save_data()

    def create_membership(
        self,
        member_id: str,
        membership_type: MembershipType,
        price: Optional[float] = None
    ) -> Membership:
        member = self.find_member(member_id)
        if not member:
            raise ValidationError(f"Member with ID '{member_id}' does not exist.", 404)

        if member.has_active_membership():
            raise BusinessRuleError("A member cannot have two active memberships simultaneously.", 4001)

        today = date.today()
        if membership_type == MembershipType.MONTHLY:
            end_date = today + timedelta(days=30)
            default_price = 50.0
        elif membership_type == MembershipType.QUARTERLY:
            end_date = today + timedelta(days=90)
            default_price = 130.0
        elif membership_type == MembershipType.YEARLY:
            end_date = today + timedelta(days=365)
            default_price = 450.0
        else:
            end_date = today + timedelta(days=30)
            default_price = 50.0

        actual_price = price if price is not None else default_price
        if actual_price < 0:
            raise ValidationError("Membership price cannot be negative.", 400)

        membership_id = f"MS-{uuid.uuid4().hex[:6].upper()}"
        new_membership = Membership(
            id=membership_id,
            member_id=member_id,
            type=membership_type,
            start_date=today,
            end_date=end_date,
            price=actual_price,
            status=MembershipStatus.ACTIVE
        )

        member.add_membership(new_membership)
        self.__memberships.append(new_membership)
        self.save_data()
        return new_membership

    def renew_membership(self, membership_id: str, months: int = 1) -> None:
        if months <= 0:
            raise ValidationError("Renewal duration must be at least 1 month.", 400)

        target: Optional[Membership] = None
        for m in self.__memberships:
            if m.id == membership_id:
                target = m
                break

        if not target:
            raise ValidationError(f"Membership '{membership_id}' not found.", 404)

        target.renew(months)
        self.save_data()

    def record_payment(
        self,
        membership_id: str,
        amount: float,
        method: PaymentMethod = PaymentMethod.CASH
    ) -> Payment:
        if amount <= 0:
            raise ValidationError("Payment amount must be greater than zero.", 4002)

        target: Optional[Membership] = None
        for m in self.__memberships:
            if m.id == membership_id:
                target = m
                break

        if not target:
            raise ValidationError(f"Membership '{membership_id}' not found.", 404)

        payment_id = f"PAY-{uuid.uuid4().hex[:6].upper()}"
        new_payment = Payment(
            id=payment_id,
            membership_id=membership_id,
            amount=amount,
            payment_date=date.today(),
            method=method
        )

        target.add_payment(new_payment)
        self.__payments.append(new_payment)
        self.save_data()
        return new_payment

    def record_attendance(
        self,
        member_id: str,
        trainer_id: Optional[str] = None
    ) -> Attendance:
        member = self.find_member(member_id)
        if not member:
            raise ValidationError(f"A member must exist before attendance can be recorded. ID: '{member_id}'", 4004)

        if not member.has_active_membership():
            raise BusinessRuleError("A member cannot attend if their membership is expired or inactive.", 4003)

        if trainer_id:
            trainer = self.find_trainer(trainer_id)
            if not trainer:
                raise ValidationError(f"Trainer '{trainer_id}' does not exist.", 404)

        attendance_id = f"ATT-{uuid.uuid4().hex[:6].upper()}"
        new_attendance = Attendance(
            id=attendance_id,
            member_id=member_id,
            trainer_id=trainer_id,
            check_in=datetime.now(),
            check_out=None
        )

        member.record_attendance(new_attendance)
        self.__attendances.append(new_attendance)
        self.save_data()
        return new_attendance

    def get_dashboard_stats(self) -> Dict[str, Any]:
        total_members = len(self.__members)
        active_memberships = sum(1 for m in self.__members if m.has_active_membership())
        expired_memberships = total_members - active_memberships
        total_revenue = sum(p.amount for p in self.__payments)

        today_date = date.today()
        today_attendances = sum(
            1 for a in self.__attendances if a.check_in.date() == today_date
        )

        return {
            "total_members": total_members,
            "active_memberships": active_memberships,
            "expired_memberships": expired_memberships,
            "total_trainers": len(self.__trainers),
            "today_attendances": today_attendances,
            "total_revenue": round(total_revenue, 2),
        }

    def load_data(self) -> None:
        trainers_raw = self.__file_manager.load("trainers")
        self.__trainers = [Trainer.from_dict(t) for t in trainers_raw]

        members_raw = self.__file_manager.load("members")
        self.__members = [Member.from_dict(m) for m in members_raw]

        self.__memberships = []
        self.__attendances = []
        self.__payments = []

        for m in self.__members:
            for ms in m.memberships:
                self.__memberships.append(ms)
                for p in ms.payments:
                    self.__payments.append(p)
            for att in m.attendances:
                self.__attendances.append(att)

    def seed_sample_data(self) -> None:
        if self.__file_manager.file_exists("members") or self.__file_manager.file_exists("trainers"):
            return

        t1 = Trainer("T101", "Captain Mohamed", "01011112233", "mohamed@gym.com", "CrossFit & Strength", 2500.0, True)
        t2 = Trainer("T102", "Coach Sarah", "01099887766", "sarah@gym.com", "Cardio & Fitness", 2200.0, True)
        self.__trainers = [t1, t2]

        today = date.today()
        m1 = Member("M101", "Ahmed Hegazy", "01012345678", "ahmed@example.com", join_date=today - timedelta(days=20))
        ms1 = Membership("MS-101", "M101", MembershipType.MONTHLY, start_date=today - timedelta(days=10), end_date=today + timedelta(days=20), price=50.0, status=MembershipStatus.ACTIVE)
        p1 = Payment("PAY-101", ms1.id, 50.0, today - timedelta(days=10), PaymentMethod.CASH)
        ms1.add_payment(p1)
        m1.add_membership(ms1)

        m2 = Member("M102", "Omar Khaled", "01122334455", "omar@example.com", join_date=today - timedelta(days=45))
        ms2 = Membership("MS-102", "M102", MembershipType.QUARTERLY, start_date=today - timedelta(days=30), end_date=today + timedelta(days=60), price=130.0, status=MembershipStatus.ACTIVE)
        p2 = Payment("PAY-102", ms2.id, 130.0, today - timedelta(days=30), PaymentMethod.CARD)
        ms2.add_payment(p2)
        m2.add_membership(ms2)

        m3 = Member("M103", "Kareem Tarek", "01233445566", "kareem@example.com", join_date=today - timedelta(days=70))
        ms3 = Membership("MS-103", "M103", MembershipType.MONTHLY, start_date=today - timedelta(days=60), end_date=today - timedelta(days=30), price=50.0, status=MembershipStatus.EXPIRED)
        p3 = Payment("PAY-103", ms3.id, 50.0, today - timedelta(days=60), PaymentMethod.ONLINE)
        ms3.add_payment(p3)
        m3.add_membership(ms3)

        self.__members = [m1, m2, m3]
        t1.assign_member("M101")
        t2.assign_member("M102")

        att1 = Attendance("ATT-001", "M101", trainer_id="T101", check_in=datetime.now() - timedelta(minutes=45), check_out=datetime.now())
        m1.record_attendance(att1)

        self.save_data()
        self.load_data()

    def save_data(self) -> None:
        self.__file_manager.save("members", [m.to_dict() for m in self.__members])
        self.__file_manager.save("trainers", [t.to_dict() for t in self.__trainers])
