def check_title(title):
    if not isinstance(title, str):
        raise ValueError("Title must be text")

    title = title.strip()
    if len(title) == 0:
        raise ValueError("Title cannot be blank")

    return title


def check_category(category):
    if not isinstance(category, str):
        raise ValueError("Category must be text")

    cleaned = category.strip().lower()
    allowed_name = ["Network", "Hardware", "Software", "Other"]

    for official_name in allowed_name:
        if official_name.lower() == cleaned:
            return official_name

    raise ValueError(
        "Category must be one of: Network, Hardware, Software, Other"
    )


def check_urgency(urgency):
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be text")

    cleaned = urgency.strip().lower()
    if cleaned != "low" and cleaned != "medium" and cleaned != "high":
        raise ValueError("Urgency must be low, medium or high")

    return cleaned


def check_affected_users(value):
    if isinstance(value, bool):
        raise ValueError("Affected users must be a positive whole number")

    if isinstance(value, int):
        number = value

    elif isinstance(value, str):
        value = value.strip()

        try:
            number = int(value)
        except ValueError:
            raise ValueError(
                "Affected users must be a positive whole number"
            )

    else:
        raise ValueError("Affected users must be a positive whole number")

    if number < 1:
        raise ValueError("Affected users must be a positive whole number")

    return number


def calculate_priority(urgency, affected_users):
    if urgency == "high" and affected_users >= 10:
        return "critical"

    if urgency == "high" or affected_users >= 10:
        return "high"

    if urgency == "medium" or affected_users >= 3:
        return "medium"

    return "low"


def next_id(existing_tickets):
    highest = 0

    for ticket in existing_tickets:
        ticket_id = ticket["id"]
        number = int(ticket_id[1:])

        if number > highest:
            highest = number

    new_number = highest + 1

    return f"T{new_number:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    clean_title = check_title(title)
    clean_category = check_category(category)
    clean_urgency = check_urgency(urgency)
    clean_users = check_affected_users(affected_users)

    priority = calculate_priority(clean_urgency, clean_users)
    new_id = next_id(tickets)

    ticket = {
        "id": new_id,
        "title": clean_title,
        "category": clean_category,
        "urgency": clean_urgency,
        "affected_users": clean_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }

    tickets.append(ticket)

    return ticket


def find_ticket(tickets, ticket_id):
    if not isinstance(ticket_id, str):
        raise ValueError("Ticket ID must be text")

    ticket_id = ticket_id.strip().upper()

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise ValueError("Ticket not found")


def id_number(identifier):
    return int(identifier[1:])


def check_note_author(author):
    if not isinstance(author, str):
        raise ValueError("Author must be text")

    author = author.strip()

    if not author:
        raise ValueError("Author cannot be blank")

    return author


def check_note_message(message):
    if not isinstance(message, str):
        raise ValueError("Message must be text")

    message = message.strip()

    if len(message) < 5 or len(message) > 300:
        raise ValueError("Message must contain 5 to 300 characters")

    return message


def check_note_id(note_id):
    if not isinstance(note_id, str):
        raise ValueError("Note ID must be text")

    note_id = note_id.strip().upper()

    if len(note_id) < 2 or note_id[0] != "N":
        raise ValueError("Note ID must start with N")

    if not note_id[1:].isdigit():
        raise ValueError("Note ID must contain a number after N")

    return note_id


def check_notes(notes):
    if not isinstance(notes, list):
        raise ValueError("Notes must be a list")

    seen_ids = set()

    for note in notes:
        if not isinstance(note, dict):
            raise ValueError("Each note must be a dictionary")

        if "note_id" not in note:
            raise ValueError("Note ID is required")

        note_id = check_note_id(note["note_id"])

        if note_id in seen_ids:
            raise ValueError("Duplicate note ID")

        seen_ids.add(note_id)

        if "author" not in note:
            raise ValueError("Author is required")

        if "message" not in note:
            raise ValueError("Message is required")

        check_note_author(note["author"])
        check_note_message(note["message"])

    return notes


def next_note_id(notes):
    highest = 0

    for note in notes:
        number = id_number(note["note_id"])

        if number > highest:
            highest = number

    return f"N{highest + 1:03d}"


def get_notes(tickets, ticket_id):
    ticket = find_ticket(tickets, ticket_id)

    notes = ticket.get("notes", [])
    check_notes(notes)

    return sorted(notes, key=lambda note: id_number(note["note_id"]))

def add_note(tickets, ticket_id, author, message):
    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] == "resolved":
        raise ValueError("Ticket is resolved. Reopen it first.")

    if ticket["status"] not in ("open", "in_progress"):
        raise ValueError("Notes can only be added to active tickets")

    author = check_note_author(author)
    message = check_note_message(message)

    notes = ticket.get("notes", [])
    check_notes(notes)

    note_id = next_note_id(notes)

    note = {
        "note_id": note_id,
        "author": author,
        "message": message,
    }

    # Create the notes field only when adding a note.
    if "notes" not in ticket:
        ticket["notes"] = []

    ticket["notes"].append(note)

    return note