
import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, update_status, get_work_queue


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(
            self.tickets, "WiFi is down", "Network", "high", 12
        )
        create_ticket(
            self.tickets, "Keyboard broken", "Hardware", "low", 1
        )

    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        original = self.tickets[0].copy()

        with self.assertRaises(ValueError):
            update_status(self.tickets, "T001", "in_progress")

        self.assertEqual(self.tickets[0], original)

    def test_resolved_ticket_cannot_be_reassigned(self):
        assign_ticket(self.tickets, "T001", "Ada")
        update_status(self.tickets, "T001", "in_progress")
        update_status(self.tickets, "T001", "resolved")
        original = self.tickets[0].copy()

        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Grace")

        self.assertEqual(self.tickets[0], original)

    def test_work_queue_contains_only_open_tickets(self):
        assign_ticket(self.tickets, "T001", "Ada")
        update_status(self.tickets, "T001", "in_progress")

        queue = get_work_queue(self.tickets)

        self.assertEqual([ticket["id"] for ticket in queue], ["T002"])

    def test_work_queue_sorts_by_priority_then_ticket_id(self):
        create_ticket(
            self.tickets, "Another network issue", "Network", "high", 10
        )

        queue = get_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T001", "T003", "T002"],
        )


if __name__ == "__main__":
    unittest.main()
