import json
from campusflow.tickets import calculate_priority
from pathlib import Path

DEFAULT_PATH = "data/tickets.json"


class StorageError(Exception):
    pass

VALID_CATEGORIES = {"Network", "Hardware", "Software", "Other"}
VALID_URGENCIES = {"low", "medium", "high"}
VALID_STATUSES = {"open", "in_progress", "resolved"}
VALID_PRIORITIES = {"critical", "high", "medium", "low"}

def validate_note(note, seen_note_ids):
    if not isinstance(note, dict):
        raise StorageError("A note has the wrong format")

    required_fields = {"note_id", "author", "message"}
    if not required_fields.issubset(note):
        raise StorageError("A note is missing a required field")

    note_id = note["note_id"]
    author = note["author"]
    message = note["message"]

    if not isinstance(note_id, str):
        raise StorageError("Invalid note ID")

    if (
        len(note_id) < 4
        or not note_id.startswith("N")
        or not note_id[1:].isdigit()
    ):
        raise StorageError("Invalid note ID")

    if note_id in seen_note_ids:
        raise StorageError("Duplicate note ID")

    if not isinstance(author, str) or not author.strip():
        raise StorageError("Invalid note author")

    if not isinstance(message, str):
        raise StorageError("Invalid note message")

    if not 5 <= len(message.strip()) <= 300:
        raise StorageError("Invalid note message length")

    seen_note_ids.add(note_id)


def validate_ticket(ticket, seen_ticket_ids):
    required_fields = {
        "id", "title", "category", "urgency", "affected_users",
        "priority", "status", "assigned_to"
    }

    if not isinstance(ticket, dict):
        raise StorageError("Ticket file has the wrong format")

    
    missing_fields = required_fields - ticket.keys()

    if missing_fields:
        field = sorted(missing_fields)[0]
        raise StorageError(f"A ticket is missing field: {field}")



    ticket_id = ticket["id"]

    if not isinstance(ticket_id, str):
        raise StorageError("Invalid ticket ID")

    if (
        len(ticket_id) < 4
        or not ticket_id.startswith("T")
        or not ticket_id[1:].isdigit()
    ):
        raise StorageError("Invalid ticket ID")

    if ticket_id in seen_ticket_ids:
        raise StorageError("Duplicate ticket ID")

    if not isinstance(ticket["title"], str) or not ticket["title"].strip():
        raise StorageError("Invalid ticket title")

    if ticket["category"] not in VALID_CATEGORIES:
        raise StorageError("Invalid ticket category")

    if ticket["urgency"] not in VALID_URGENCIES:
        raise StorageError("Invalid ticket urgency")

    affected_users = ticket["affected_users"]
    if (
        isinstance(affected_users, bool)
        or not isinstance(affected_users, int)
        or affected_users < 1
    ):
        raise StorageError("Invalid affected users value")

    if ticket["status"] not in VALID_STATUSES:
        raise StorageError("Invalid ticket status")

    assigned_to = ticket["assigned_to"]
    if assigned_to is not None and (
        not isinstance(assigned_to, str) or not assigned_to.strip()
    ):
        raise StorageError("Invalid ticket assignment")

    expected_priority = calculate_priority(
        ticket["urgency"],
        affected_users
    )

    if (
        ticket["priority"] not in VALID_PRIORITIES
        or ticket["priority"] != expected_priority
    ):
        raise StorageError("Ticket priority is inconsistent")

    # Support older tickets that were created before notes existed.
    ticket.setdefault("notes", [])

    if not isinstance(ticket["notes"], list):
        raise StorageError("Ticket notes must be a list")

    seen_note_ids = set()
    for note in ticket["notes"]:
        validate_note(note, seen_note_ids)

    seen_ticket_ids.add(ticket_id)


def load_tickets(path=DEFAULT_PATH):
    file_path = Path(path)

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    except OSError as error:
        raise StorageError(
            f"Could not read the file: {error}"
        ) from error

    try:
        tickets = json.loads(text)
    except json.JSONDecodeError as error:
        raise StorageError(
            f"Ticket file is corrupted: {error}"
        ) from error

    if not isinstance(tickets, list):
        raise StorageError("Ticket file has the wrong format")

    seen_ticket_ids = set()

    for ticket in tickets:
        validate_ticket(ticket, seen_ticket_ids)

    return tickets


def save_tickets(tickets, path=DEFAULT_PATH):
    file_path = Path(path)
    temp_path = file_path.with_name(file_path.name + ".tmp")

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        text = json.dumps(tickets, indent=4)

        with open(temp_path, "w", encoding="utf-8") as file:
            file.write(text)

        temp_path.replace(file_path)

    except (OSError, TypeError, ValueError) as error:
        raise StorageError(f"Could not save tickets: {error}") from error
