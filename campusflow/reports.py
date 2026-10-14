
VALID_STATUSES = ["open", "in_progress", "resolved"]
VALID_PRIORITIES = ["critical", "high", "medium", "low"]


def generate_report(tickets):
    """Summarize ticket counts by status, priority, and category."""
    if tickets is None:
        tickets = []

    total_tickets = len(tickets)

    status_counts = {status: 0 for status in VALID_STATUSES}
    priority_counts = {priority: 0 for priority in VALID_PRIORITIES}
    category_counts = {}

    extra_statuses = {}
    extra_priorities = {}

    for ticket in tickets:
        status = str(ticket.get("status", "open")).lower()

        if status in status_counts:
            status_counts[status] += 1
        else:
            extra_statuses[status] = extra_statuses.get(status, 0) + 1

        priority = str(ticket.get("priority", "low")).lower()

        if priority in priority_counts:
            priority_counts[priority] += 1
        else:
            extra_priorities[priority] = extra_priorities.get(priority, 0) + 1

        category = str(ticket.get("category", "other")).title()
        category_counts[category] = category_counts.get(category, 0) + 1

    status_counts.update(extra_statuses)
    priority_counts.update(extra_priorities)

    # Unresolved tickets are open or in progress.
    unresolved_tickets = (
        status_counts.get("open", 0)
        + status_counts.get("in_progress", 0)
    )

    # Count resolved tickets.
    resolved_tickets = status_counts.get("resolved", 0)

    # Calculate resolution percentage safely.
    resolution_percentage = (
        resolved_tickets / total_tickets * 100
        if total_tickets > 0
        else 0.0
    )

    return {
        "total_tickets": total_tickets,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "by_category": category_counts,
        "unresolved_tickets": unresolved_tickets,
        "resolved_tickets": resolved_tickets,
        "resolution_percentage": resolution_percentage,
    }


def format_report_text(report_data):
    """Format summary output into printable text."""
    lines = [
        "=== CAMPUSFLOW TICKET REPORT ===",
        f"Total Tickets: {report_data['total_tickets']}",
        "",
        "Status Breakdown:",
    ]

    for status, count in report_data["by_status"].items():
        lines.append(f"  - {status.replace('_', ' ').title()}: {count}")

    lines.extend(["", "Priority Breakdown:"])

    for priority, count in report_data["by_priority"].items():
        lines.append(f"  - {priority.capitalize()}: {count}")

    if "by_category" in report_data:
        lines.extend(["", "Category Breakdown:"])

        for category, count in report_data["by_category"].items():
            lines.append(f"  - {category}: {count}")

    lines.extend([
        "",
        f"Unresolved Tickets: {report_data['unresolved_tickets']}",
        f"Resolved Tickets: {report_data['resolved_tickets']}",
        f"Resolution Percentage: {report_data['resolution_percentage']:.1f}%",
    ])

    return "\n".join(lines)
