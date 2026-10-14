from campusflow.tickets import find_ticket, id_number

VALID_STATUSES = {"open", "in_progress", "resolved"}

ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"open"},
}

PRIORITY_RANK = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign an open or in-progress ticket to a staff member."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be blank.")

    ticket = find_ticket(tickets, ticket_id)

    if ticket.get("status") == "resolved":
        raise ValueError(
            "A resolved ticket must be reopened before reassignment."
        )

    ticket["assigned_to"] = staff_name.strip()
    return ticket


def update_status(tickets, ticket_id, new_status):
    """Update status using the allowed transitions."""
    if not isinstance(new_status, str):
        raise ValueError("Status must be text.")

    new_status = new_status.strip().lower()

    if new_status not in VALID_STATUSES:
        raise ValueError(
            "Status must be open, in_progress or resolved."
        )

    ticket = find_ticket(tickets, ticket_id)
    current_status = ticket.get("status")

    if current_status not in VALID_STATUSES:
        raise ValueError("Ticket has an invalid current status.")

    if new_status == current_status:
        raise ValueError(f"Ticket is already {current_status}.")

    if new_status not in ALLOWED_TRANSITIONS[current_status]:
        raise ValueError(
            f"Cannot move from {current_status} to {new_status}."
        )

    # An unassigned ticket cannot move into progress.
    if new_status == "in_progress":
        assigned_to = ticket.get("assigned_to")

        if not isinstance(assigned_to, str) or not assigned_to.strip():
            raise ValueError(
                "An unassigned ticket cannot move to in_progress."
            )

    ticket["status"] = new_status
    return ticket


def get_work_queue(tickets):
    """Return only open tickets, sorted by priority and ticket ID."""
    open_tickets = [
        ticket
        for ticket in tickets
        if ticket.get("status") == "open"
    ]

    def sort_key(ticket):
        priority = ticket["priority"].lower()
        priority_rank = PRIORITY_RANK[priority]
        ticket_number = id_number(ticket["id"])

        return priority_rank, ticket_number

    return sorted(open_tickets, key=sort_key)
