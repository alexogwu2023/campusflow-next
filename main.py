from copy import deepcopy

from campusflow.tickets import (
    create_ticket,
    find_ticket,
    add_note,
    get_notes,
)
from campusflow.workflow import (
    assign_ticket,
    update_status,
    get_work_queue,
)
from campusflow.search import search_tickets
from campusflow.storage import load_tickets, save_tickets, StorageError


def show_ticket(ticket):
    print(f"ID: {ticket['id']}")
    print(f"Title: {ticket['title']}")
    print(f"Category: {ticket['category']}")
    print(f"Urgency: {ticket['urgency']}")
    print(f"Affected users: {ticket['affected_users']}")
    print(f"Priority: {ticket['priority']}")
    print(f"Status: {ticket['status']}")

    assignee = ticket.get("assigned_to")

    if not assignee:
        print("Assigned to: Unassigned")
    else:
        print(f"Assigned to: {assignee}")

    print(f"Notes: {len(ticket.get('notes', []))}")


def show_ticket_list(tickets):
    if not tickets:
        print("No tickets found.")
        return

    for ticket in tickets:
        assignee = ticket.get("assigned_to") or "Unassigned"

        print(
            f"{ticket['id']} | {ticket['title']} | "
            f"{ticket['priority']} | {ticket['status']} | "
            f"{assignee}"
        )


def save_changes(tickets, previous_tickets):
    """Save changes or restore the previous in-memory collection."""
    try:
        save_tickets(tickets)
        return True
    except StorageError as error:
        tickets[:] = previous_tickets
        print(f"Could not save changes: {error}")
        print("The previous in-memory state has been restored.")
        return False


def handle_create(tickets):
    title = input("Title: ")
    category = input(
        "Category (Network/Hardware/Software/Other): "
    )
    urgency = input("Urgency (low/medium/high): ")
    affected_users = input("Number of affected users: ")

    previous_tickets = deepcopy(tickets)

    try:
        ticket = create_ticket(
            tickets,
            title,
            category,
            urgency,
            affected_users,
        )
    except ValueError as error:
        print(f"Error: {error}")
        return

    if not save_changes(tickets, previous_tickets):
        return

    print(
        f"Created ticket {ticket['id']} "
        f"with priority {ticket['priority']}."
    )


def handle_view_ticket(tickets):
    ticket_id = input("Enter ticket ID: ").strip()

    try:
        ticket = find_ticket(tickets, ticket_id)
    except ValueError as error:
        print(f"Error: {error}")
        return

    show_ticket(ticket)


def handle_assign(tickets):
    ticket_id = input("Enter ticket ID: ").strip()
    staff_name = input("Enter staff name: ").strip()

    previous_tickets = deepcopy(tickets)

    try:
        ticket = assign_ticket(tickets, ticket_id, staff_name)
    except ValueError as error:
        print(f"Error: {error}")
        return

    if not save_changes(tickets, previous_tickets):
        return

    print(
        f"Ticket {ticket['id']} assigned to "
        f"{ticket['assigned_to']} successfully."
    )


def handle_update_status(tickets):
    ticket_id = input("Enter ticket ID: ").strip()

    print("Available statuses: open, in_progress, resolved")
    new_status = input("Enter new status: ").strip().lower()

    previous_tickets = deepcopy(tickets)

    try:
        ticket = update_status(tickets, ticket_id, new_status)
    except ValueError as error:
        print(f"Error: {error}")
        return

    if not save_changes(tickets, previous_tickets):
        return

    print(
        f"Ticket {ticket['id']} status updated to "
        f"{ticket['status']}."
    )


def handle_work_queue(tickets):
    queue = get_work_queue(tickets)

    if not queue:
        print("No open tickets in the work queue.")
        return

    print("\n=== WORK QUEUE ===")
    show_ticket_list(queue)


def handle_search(tickets):
    title_query = input("Search title: ").strip()

    category = input("Category filter (Enter to skip): ").strip()
    status = input("Status filter (Enter to skip): ").strip()
    priority = input("Priority filter (Enter to skip): ").strip()

    try:
        results = search_tickets(
            tickets,
            title_query,
            category=category or None,
            status=status or None,
            priority=priority or None,
        )
    except (ValueError, AttributeError) as error:
        print(f"Search error: {error}")
        return

    print("\n=== SEARCH RESULTS ===")
    show_ticket_list(results)


def handle_add_note(tickets):
    ticket_id = input("Enter ticket ID: ").strip()
    author = input("Your name: ").strip()
    message = input("Note (5–300 characters): ")

    previous_tickets = deepcopy(tickets)

    try:
        note = add_note(tickets, ticket_id, author, message)
    except ValueError as error:
        print(f"Error: {error}")
        return

    if not save_changes(tickets, previous_tickets):
        return

    print(f"Note {note['note_id']} added to ticket {ticket_id}.")


def handle_view_notes(tickets):
    ticket_id = input("Enter ticket ID: ").strip()

    try:
        notes = get_notes(tickets, ticket_id)
    except ValueError as error:
        print(f"Error: {error}")
        return

    if not notes:
        print("This ticket has no notes.")
        return

    print(f"\n=== NOTES FOR {ticket_id.upper()} ===")

    for note in notes:
        print(f"\nNote ID: {note['note_id']}")
        print(f"Author: {note['author']}")
        print(f"Message: {note['message']}")


def handle_report(tickets):
    try:
        from campusflow.reports import (
            generate_report,
            format_report_text,
        )

        report_data = generate_report(tickets)
        print(format_report_text(report_data))

    except (ImportError, AttributeError) as error:
        print(f"Reporting is not available: {error}")


def display_menu():
    print("\n=== CAMPUSFLOW TICKET SYSTEM ===")
    print("1. Create ticket")
    print("2. View all tickets")
    print("3. View a ticket")
    print("4. Assign ticket")
    print("5. Update ticket status")
    print("6. View work queue")
    print("7. Generate report")
    print("8. Search tickets")
    print("9. Add a note")
    print("10. View ticket notes")
    print("0. Exit")


def main():
    try:
        tickets = load_tickets()
    except StorageError as error:
        print(f"Could not load tickets: {error}")
        return

    print(f"Loaded {len(tickets)} ticket(s).")

    while True:
        display_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            handle_create(tickets)

        elif choice == "2":
            show_ticket_list(tickets)

        elif choice == "3":
            handle_view_ticket(tickets)

        elif choice == "4":
            handle_assign(tickets)

        elif choice == "5":
            handle_update_status(tickets)

        elif choice == "6":
            handle_work_queue(tickets)

        elif choice == "7":
            handle_report(tickets)

        elif choice == "8":
            handle_search(tickets)

        elif choice == "9":
            handle_add_note(tickets)

        elif choice == "10":
            handle_view_notes(tickets)

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please select an option from the menu.")


if __name__ == "__main__":
    main()
