def search_tickets(tickets, title_query, category=None, status=None, priority=None):
    title_query = title_query.casefold()
    results = []

    for ticket in tickets:
        ticket_title = ticket["title"].casefold()

        if category is not None and ticket["category"].casefold() != category.casefold():
            continue

        if status is not None and ticket["status"].casefold() != status.casefold():
            continue

        if priority is not None and ticket["priority"].casefold() != priority.casefold():
            continue



        if title_query in ticket_title:
            results.append(ticket)

    return results
