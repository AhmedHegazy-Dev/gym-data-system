import unittest
import shutil
import os
from datetime import date, timedelta

from models.member import Member
from models.trainer import Trainer
from models.enums import MembershipType, PaymentMethod
from models.exception import ValidationError, BusinessRuleError
from services.gym import Gym


class TestGymManagementSystem(unittest.TestCase):
    def setUp(self):
        self.test_data_dir = "test_data_tmp"
        os.makedirs(self.test_data_dir, exist_ok=True)
        self.gym = Gym(name="Test Gym", data_dir=self.test_data_dir)

    def tearDown(self):
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir, ignore_errors=True)

    # 1. Successful Scenarios
    def test_01_create_member_and_membership(self):
        member = Member("M001", "Ahmed", "01000000000", "ahmed@test.com")
        self.gym.add_member(member)
        membership = self.gym.create_membership("M001", MembershipType.MONTHLY, price=50.0)
        self.assertTrue(member.has_active_membership())
        self.assertEqual(membership.price, 50.0)

    def test_02_record_valid_attendance(self):
        member = Member("M001", "Ahmed", "01000000000", "ahmed@test.com")
        self.gym.add_member(member)
        self.gym.create_membership("M001", MembershipType.MONTHLY)
        att = self.gym.record_attendance("M001")
        self.assertIsNotNone(att.check_in)
        self.assertEqual(len(member.attendances), 1)

    def test_03_record_payment_balance(self):
        member = Member("M001", "Ahmed", "01000000000", "ahmed@test.com")
        self.gym.add_member(member)
        membership = self.gym.create_membership("M001", MembershipType.MONTHLY, price=100.0)
        payment = self.gym.record_payment(membership.id, amount=40.0, method=PaymentMethod.CASH)
        self.assertEqual(payment.amount, 40.0)
        self.assertEqual(membership.get_total_paid(), 40.0)
        self.assertEqual(membership.get_remaining_balance(), 60.0)

    # 2. Invalid Input Scenarios
    def test_04_payment_zero_or_negative(self):
        member = Member("M001", "Ahmed", "01000000000", "ahmed@test.com")
        self.gym.add_member(member)
        membership = self.gym.create_membership("M001", MembershipType.MONTHLY)
        with self.assertRaises(ValidationError):
            self.gym.record_payment(membership.id, amount=0.0)
        with self.assertRaises(ValidationError):
            self.gym.record_payment(membership.id, amount=-20.0)

    def test_05_create_member_empty_fields(self):
        with self.assertRaises(ValidationError):
            self.gym.add_member(Member("", "Valid Name", "010", "a@a.com"))
        with self.assertRaises(ValidationError):
            self.gym.add_member(Member("M002", "   ", "010", "a@a.com"))

    def test_06_attendance_nonexistent_member(self):
        with self.assertRaises(ValidationError):
            self.gym.record_attendance("DOES_NOT_EXIST_999")

    # 3. Business-Rule Violations
    def test_07_attendance_expired_membership(self):
        member = Member("M002", "Sara", "01111111111", "sara@test.com")
        self.gym.add_member(member)
        # Sara has no active membership -> cannot attend
        with self.assertRaises(BusinessRuleError):
            self.gym.record_attendance("M002")

    def test_08_concurrent_active_memberships(self):
        member = Member("M001", "Ahmed", "01000000000", "ahmed@test.com")
        self.gym.add_member(member)
        self.gym.create_membership("M001", MembershipType.MONTHLY)
        # Attempting second active membership
        with self.assertRaises(BusinessRuleError):
            self.gym.create_membership("M001", MembershipType.YEARLY)

    # 4. Edge Cases
    def test_09_renewal_of_expired_membership(self):
        member = Member("M001", "Ahmed", "01000000000", "ahmed@test.com")
        self.gym.add_member(member)
        membership = self.gym.create_membership("M001", MembershipType.MONTHLY)
        # Artificially expire the membership
        membership._Membership__end_date = date.today() - timedelta(days=10)
        self.assertTrue(membership.is_expired())
        self.gym.renew_membership(membership.id, months=1)
        self.assertTrue(membership.is_active())
        self.assertGreaterEqual(membership.end_date, date.today())

    def test_10_attendance_duration_without_checkout(self):
        member = Member("M001", "Ahmed", "01000000000", "ahmed@test.com")
        self.gym.add_member(member)
        self.gym.create_membership("M001", MembershipType.MONTHLY)
        att = self.gym.record_attendance("M001")
        self.assertEqual(att.duration_minutes(), 0)


if __name__ == "__main__":
    unittest.main()
