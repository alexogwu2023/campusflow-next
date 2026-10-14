
import unittest
from campusflow.reports import generate_report


class TestGenerateReport(unittest.TestCase):

    def test_report_counts_total_tickets(self):
        tickets = [
            {"status": "open", "priority": "high"},
            {"status": "resolved", "priority": "low"},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["total_tickets"], 2)

    def test_report_counts_tickets_by_category(self):
        tickets = [
            {"status": "open", "priority": "high", "category": "Network"},
            {"status": "resolved", "priority": "low", "category": "Hardware"},
            {"status": "open", "priority": "medium", "category": "Network"},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["by_category"]["Network"], 2)
        self.assertEqual(report["by_category"]["Hardware"], 1)

    def test_report_counts_unresolved_tickets(self):
        tickets = [
            {"status": "open", "priority": "high"},
            {"status": "in_progress", "priority": "medium"},
            {"status": "resolved", "priority": "low"},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["unresolved_tickets"], 2)

    def test_report_counts_resolved_tickets(self):
        tickets = [
            {"status": "open", "priority": "high"},
            {"status": "resolved", "priority": "low"},
            {"status": "resolved", "priority": "medium"},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["resolved_tickets"], 2)

    def test_report_calculates_resolution_percentage(self):
        tickets = [
            {"status": "resolved", "priority": "low"},
            {"status": "resolved", "priority": "high"},
            {"status": "open", "priority": "medium"},
            {"status": "in_progress", "priority": "low"},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["resolution_percentage"], 50.0)


if __name__ == "__main__":
    unittest.main()
