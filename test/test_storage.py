
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from campusflow.storage import load_tickets, save_tickets, StorageError


def sample_ticket():
    return {
        "id": "T001",
        "title": "Network is down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 12,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
        "notes": []
    }



class TestLoadTickets(unittest.TestCase):

    def test_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "missing.json"

            result = load_tickets(path)

            self.assertEqual(result, [])

    def test_loads_valid_tickets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            tickets = [sample_ticket()]

            path.write_text(json.dumps(tickets), encoding="utf-8")

            result = load_tickets(path)

            self.assertEqual(result, tickets)

    def test_loads_empty_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            path.write_text("[]", encoding="utf-8")

            self.assertEqual(load_tickets(path), [])

    def test_corrupted_json_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            corrupted_text = '{"id": "T001", invalid JSON'
            path.write_text(corrupted_text, encoding="utf-8")

            with self.assertRaisesRegex(
                StorageError, "Ticket file is corrupted"
            ):
                load_tickets(path)

            # The corrupted file must remain unchanged.
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                corrupted_text
            )

    def test_non_list_json_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            path.write_text('{"id": "T001"}', encoding="utf-8")

            with self.assertRaisesRegex(
                StorageError, "Ticket file has the wrong format"
            ):
                load_tickets(path)

    def test_non_dictionary_ticket_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            path.write_text(
                json.dumps(["not a ticket"]),
                encoding="utf-8"
            )

            with self.assertRaisesRegex(
                StorageError, "Ticket file has the wrong format"
            ):
                load_tickets(path)

    def test_missing_required_field_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            ticket = sample_ticket()
            del ticket["title"]

            path.write_text(json.dumps([ticket]), encoding="utf-8")

            with self.assertRaisesRegex(
                StorageError, "A ticket is missing field: "
            ):
                load_tickets(path)

    def test_read_failure_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            path.write_text("[]", encoding="utf-8")

            with patch(
                "builtins.open",
                side_effect=PermissionError("Permission denied")
            ):
                with self.assertRaisesRegex(
                    StorageError, "Could not read the file"
                ):
                    load_tickets(path)


class TestStorageValidation(unittest.TestCase):

    def test_duplicate_ticket_ids_raise_storage_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"

            first_ticket = sample_ticket()
            second_ticket = sample_ticket()

            tickets = [first_ticket, second_ticket]

            path.write_text(
                json.dumps(tickets),
                encoding="utf-8"
            )

            with self.assertRaisesRegex(
                StorageError, "Duplicate ticket ID"
            ):
                load_tickets(path)

    def test_invalid_ticket_status_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            ticket = sample_ticket()
            ticket["status"] = "flying"

            path.write_text(
                json.dumps([ticket]),
                encoding="utf-8"
            )

            with self.assertRaisesRegex(
                StorageError, "Invalid ticket status"
            ):
                load_tickets(path)

    def test_valid_ticket_statuses_are_accepted(self):
        valid_statuses = ["open", "in_progress", "resolved"]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"

            for status in valid_statuses:
                ticket = sample_ticket()
                ticket["status"] = status

                path.write_text(
                    json.dumps([ticket]),
                    encoding="utf-8"
                )

                result = load_tickets(path)

                self.assertEqual(result[0]["status"], status)



class TestSaveTickets(unittest.TestCase):

    def test_saves_tickets_successfully(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            tickets = [sample_ticket()]

            save_tickets(tickets, path)

            saved_tickets = json.loads(
                path.read_text(encoding="utf-8")
            )

            self.assertEqual(saved_tickets, tickets)

    def test_creates_missing_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "data" / "tickets.json"

            save_tickets([sample_ticket()], path)

            self.assertTrue(path.exists())
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                [sample_ticket()]
            )

    def test_saved_json_is_indented(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"

            save_tickets([sample_ticket()], path)

            text = path.read_text(encoding="utf-8")

            self.assertIn("\n", text)
            self.assertIn('    "id": "T001"', text)

    def test_replaces_existing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            path.write_text("[]", encoding="utf-8")

            tickets = [sample_ticket()]
            save_tickets(tickets, path)

            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                tickets
            )

    def test_save_failure_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"

            # A set cannot be converted to JSON.
            invalid_tickets = [{"invalid": {1, 2, 3}}]

            with self.assertRaisesRegex(
                StorageError, "Could not save tickets"
            ):
                save_tickets(invalid_tickets, path)

    def test_temporary_file_is_removed_after_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            temp_path = path.with_name(path.name + ".tmp")

            save_tickets([sample_ticket()], path)

            self.assertTrue(path.exists())
            self.assertFalse(temp_path.exists())

    
    def test_saves_and_loads_ticket_notes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            ticket = sample_ticket()
            ticket["notes"] = [
                {
                    "note_id": "N001",
                    "author": "Alex",
                    "message": "Router needs restarting"
                }
            ]

            save_tickets([ticket], path)
            loaded_tickets = load_tickets(path)

            self.assertEqual(loaded_tickets[0]["notes"], ticket["notes"])

    def test_preserves_multiple_notes_and_their_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            ticket = sample_ticket()
            ticket["notes"] = [
                {
                    "note_id": "N001",
                    "author": "Alex",
                    "message": "Router needs restarting"
                },
                {
                    "note_id": "N002",
                    "author": "Grace",
                    "message": "The router has been checked"
                }
            ]

            save_tickets([ticket], path)
            loaded_tickets = load_tickets(path)

            self.assertEqual(
                loaded_tickets[0]["notes"],
                ticket["notes"]
            )

    def test_next_note_id_continues_after_loading(self):
        from campusflow.tickets import add_note

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tickets.json"
            ticket = sample_ticket()
            ticket["notes"] = [
                {
                    "note_id": "N001",
                    "author": "Alex",
                    "message": "Router needs restarting"
                },
                {
                    "note_id": "N002",
                    "author": "Grace",
                    "message": "The router has been checked"
                }
            ]

            save_tickets([ticket], path)
            loaded_tickets = load_tickets(path)

            add_note(
                loaded_tickets,
                "T001",
                "John",
                "The connection works"
            )

            self.assertEqual(
                loaded_tickets[0]["notes"][-1]["note_id"],
                "N003"
            )



if __name__ == "__main__":
    unittest.main()
