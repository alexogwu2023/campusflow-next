
import unittest

from campusflow.tickets import (
    check_title,
    check_category,
    check_urgency,
    check_affected_users,
    calculate_priority,
    next_id,
    create_ticket,
    find_ticket,
)


class TestCheckTitle(unittest.TestCase):

    def test_valid_title(self):
        self.assertEqual(check_title("Network is down"), "Network is down")

    def test_removes_extra_spaces(self):
        self.assertEqual(check_title("  Network is down  "), "Network is down")

    def test_rejects_non_text(self):
        with self.assertRaisesRegex(ValueError, "Title must be text"):
            check_title(123)

    def test_rejects_blank_title(self):
        with self.assertRaisesRegex(ValueError, "Title cannot be blank"):
            check_title("   ")


class TestCheckCategory(unittest.TestCase):

    def test_valid_categories(self):
        for category in ["Network", "Hardware", "Software", "Other"]:
            with self.subTest(category=category):
                self.assertEqual(check_category(category), category)

    def test_normalizes_category(self):
        self.assertEqual(check_category("  network "), "Network")
        self.assertEqual(check_category("SOFTWARE"), "Software")

    
    def test_rejects_non_text(self):
        with self.assertRaisesRegex(ValueError, "Category must be text"):
            check_category(None)


    def test_rejects_invalid_category(self):
        with self.assertRaisesRegex(ValueError, "Category must be one of"):
            check_category("Security")


class TestCheckUrgency(unittest.TestCase):

    def test_valid_urgencies(self):
        for urgency in ["low", "medium", "high"]:
            with self.subTest(urgency=urgency):
                self.assertEqual(check_urgency(urgency), urgency)

    def test_normalizes_urgency(self):
        self.assertEqual(check_urgency(" HIGH "), "high")
        self.assertEqual(check_urgency("Medium"), "medium")

    def test_rejects_non_text(self):
        with self.assertRaisesRegex(ValueError, "Urgency must be text"):
            check_urgency(123)

    def test_rejects_invalid_urgency(self):
        with self.assertRaisesRegex(
            ValueError, "Urgency must be low, medium or high"
        ):
            check_urgency("urgent")


class TestCheckAffectedUsers(unittest.TestCase):

    def test_accepts_integer(self):
        self.assertEqual(check_affected_users(5), 5)

    def test_converts_numeric_text(self):
        self.assertEqual(check_affected_users("12"), 12)

    def test_removes_spaces_from_text(self):
        self.assertEqual(check_affected_users(" 5 "), 5)

    def test_rejects_boolean(self):
        for value in [True, False]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    check_affected_users(value)

    def test_rejects_invalid_text(self):
        for value in ["abc", "5.5", ""]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    check_affected_users(value)

    def test_rejects_non_integer_values(self):
        for value in [5.5, None, [], {}]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    check_affected_users(value)

    def test_rejects_zero_and_negative_numbers(self):
        for value in [0, -1, "-5"]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ValueError,
                    "Affected users must be a positive whole number"
                ):
                    check_affected_users(value)


class TestCalculatePriority(unittest.TestCase):

    def test_critical_priority(self):
        self.assertEqual(calculate_priority("high", 10), "critical")
        self.assertEqual(calculate_priority("high", 15), "critical")

    def test_high_priority(self):
        self.assertEqual(calculate_priority("high", 3), "high")
        self.assertEqual(calculate_priority("low", 10), "high")

    def test_medium_priority(self):
        self.assertEqual(calculate_priority("medium", 1), "medium")
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_low_priority(self):
        self.assertEqual(calculate_priority("low", 1), "low")
        self.assertEqual(calculate_priority("low", 2), "low")


class TestNextId(unittest.TestCase):

    def test_empty_ticket_list(self):
        self.assertEqual(next_id([]), "T001")

    def test_generates_next_id(self):
        tickets = [
            {"id": "T001"},
            {"id": "T002"},
            {"id": "T003"},
        ]
        self.assertEqual(next_id(tickets), "T004")

    def test_uses_highest_id(self):
        tickets = [
            {"id": "T002"},
            {"id": "T010"},
            {"id": "T005"},
        ]
        self.assertEqual(next_id(tickets), "T011")


class TestCreateTicket(unittest.TestCase):

    def setUp(self):
        self.tickets = []

    def test_new_ticket_starts_with_empty_notes(self):
        ticket = create_ticket(
            self.tickets,
            "WiFi is down",
            "Network",
            "high",
            5,
        )

        self.assertEqual(ticket["notes"], [])

    def test_creates_ticket_successfully(self):
        ticket = create_ticket(
            self.tickets,
            " Network is down ",
            "network",
            "HIGH",
            "12",
        )

        self.assertEqual(ticket, {
            "id": "T001",
            "title": "Network is down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 12,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
            "notes": [],
        })

        self.assertEqual(len(self.tickets), 1)
        self.assertIs(self.tickets[0], ticket)

    def test_creates_sequential_ticket_ids(self):
        first = create_ticket(
            self.tickets, "First issue", "Network", "low", 1
        )
        second = create_ticket(
            self.tickets, "Second issue", "Hardware", "medium", 3
        )

        self.assertEqual(first["id"], "T001")
        self.assertEqual(second["id"], "T002")

    def test_invalid_title_does_not_change_tickets(self):
        original = self.tickets.copy()

        with self.assertRaises(ValueError):
            create_ticket(
                self.tickets, " ", "Network", "low", 1
            )

        self.assertEqual(self.tickets, original)

    def test_invalid_category_does_not_change_tickets(self):
        with self.assertRaises(ValueError):
            create_ticket(
                self.tickets, "Printer issue", "Invalid", "low", 1
            )

        self.assertEqual(self.tickets, [])

    def test_invalid_urgency_does_not_change_tickets(self):
        with self.assertRaises(ValueError):
            create_ticket(
                self.tickets, "Printer issue", "Hardware", "urgent", 1
            )

        self.assertEqual(self.tickets, [])

    def test_invalid_affected_users_does_not_change_tickets(self):
        with self.assertRaises(ValueError):
            create_ticket(
                self.tickets, "Printer issue", "Hardware", "low", True
            )

        self.assertEqual(self.tickets, [])


class TestFindTicket(unittest.TestCase):

    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Network issue",
            },
            {
                "id": "T002",
                "title": "Printer issue",
            },
        ]

    def test_finds_existing_ticket(self):
        ticket = find_ticket(self.tickets, "T001")
        self.assertEqual(ticket["title"], "Network issue")

    def test_finds_ticket_with_lowercase_id(self):
        ticket = find_ticket(self.tickets, "t001")
        self.assertEqual(ticket["id"], "T001")

    def test_finds_ticket_with_surrounding_spaces(self):
        ticket = find_ticket(self.tickets, " t002 ")
        self.assertEqual(ticket["id"], "T002")

    def test_rejects_missing_ticket(self):
        with self.assertRaisesRegex(ValueError, "Ticket not found"):
            find_ticket(self.tickets, "T999")



class TestAddNote(unittest.TestCase):

    def setUp(self):
        self.tickets = []
        self.ticket = create_ticket(
            self.tickets,
            "WiFi is down",
            "Network",
            "high",
            5
        )

    def test_add_note_successfully(self):
        from campusflow.tickets import add_note

        note = add_note(
            self.tickets,
            self.ticket["id"],
            "Alex",
            "Router needs restarting"
        )

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Alex")
        self.assertEqual(note["message"], "Router needs restarting")
        self.assertEqual(len(self.ticket["notes"]), 1)

    def test_note_author_cannot_be_blank(self):
        from campusflow.tickets import add_note

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                self.ticket["id"],
                "   ",
                "Router needs restarting"
            )

        self.assertEqual(self.ticket["notes"], [])

    def test_note_message_must_have_at_least_five_characters(self):
        from campusflow.tickets import add_note

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                self.ticket["id"],
                "Alex",
                "Hey"
            )

        self.assertEqual(self.ticket["notes"], [])

    def test_resolved_ticket_rejects_notes(self):
        from campusflow.tickets import add_note

        self.ticket["status"] = "resolved"

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                self.ticket["id"],
                "Alex",
                "Router needs restarting"
            )

        self.assertEqual(self.ticket["notes"], [])

    def test_note_ids_increase_sequentially(self):
        from campusflow.tickets import add_note

        first = add_note(
            self.tickets,
            self.ticket["id"],
            "Alex",
            "Router needs restarting"
        )

        second = add_note(
            self.tickets,
            self.ticket["id"],
            "Grace",
            "The router has been checked"
        )

        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N002")



if __name__ == "__main__":
    unittest.main()
