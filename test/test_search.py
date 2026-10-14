
import unittest
from campusflow.search import search_tickets


class TestSearchTickets(unittest.TestCase):
    def test_search_title_ignores_case(self):
        tickets = [
            {
                "id": "T001",
                "title": "WIFI connection failed",
                "category": "Network",
                "status": "open",
                "priority": "high",
            },
            {
                "id": "T002",
                "title": "Laptop screen issue",
                "category": "Hardware",
                "status": "open",
                "priority": "low",
            },
        ]

        results = search_tickets(tickets, "wifi")

        self.assertEqual([ticket["id"] for ticket in results], ["T001"])

    def test_search_filters_by_category(self):
        tickets = [
            {
                "id": "T001",
                "title": "WIFI connection failed",
                "category": "Network",
                "status": "open",
                "priority": "high",
            },
            {
                "id": "T002",
                "title": "WIFI laptop issue",
                "category": "Hardware",
                "status": "open",
                "priority": "low",
            },
        ]

        results = search_tickets(tickets, "wifi", category="Network")

        self.assertEqual([ticket["id"] for ticket in results], ["T001"])

    def test_search_filters_by_status(self):
        tickets = [
            {
                "id": "T001",
                "title": "WIFI connection failed",
                "category": "Network",
                "status": "open",
                "priority": "high",
            },
            {
                "id": "T002",
                "title": "WIFI disconnects",
                "category": "Network",
                "status": "resolved",
                "priority": "high",
            },
        ]

        results = search_tickets(tickets, "wifi", status="open")

        self.assertEqual([ticket["id"] for ticket in results], ["T001"])

    def test_search_filters_by_priority(self):
        tickets = [
            {
                "id": "T001",
                "title": "WIFI connection failed",
                "category": "Network",
                "status": "open",
                "priority": "high",
            },
            {
                "id": "T002",
                "title": "WIFI disconnects",
                "category": "Network",
                "status": "open",
                "priority": "low",
            },
        ]

        results = search_tickets(tickets, "wifi", priority="high")

        self.assertEqual([ticket["id"] for ticket in results], ["T001"])

    def test_search_combines_filters(self):
        tickets = [
            {
                "id": "T001",
                "title": "WIFI connection failed",
                "category": "Network",
                "status": "open",
                "priority": "high",
            },
            {
                "id": "T002",
                "title": "WIFI laptop issue",
                "category": "Network",
                "status": "open",
                "priority": "low",
            },
            {
                "id": "T003",
                "title": "WIFI disconnects",
                "category": "Network",
                "status": "resolved",
                "priority": "high",
            },
        ]

        results = search_tickets(
            tickets,
            "wifi",
            category="Network",
            status="open",
            priority="high",
        )

        self.assertEqual([ticket["id"] for ticket in results], ["T001"])

    def test_search_returns_empty_list_when_no_match(self):
        tickets = [
            {
                "id": "T001",
                "title": "WIFI connection failed",
                "category": "Network",
                "status": "open",
                "priority": "high",
            }
        ]

        results = search_tickets(tickets, "printer")

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
