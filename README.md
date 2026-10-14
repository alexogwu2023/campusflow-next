# CampusFlow Next teamALEX AND AMINA

A Python CLI helpdesk system for creating, prioritizing, assigning, and tracking technical support tickets.

## Running Tests

Run the complete test suite:

```bash
python3 -m unittest discover -s test -v
```

Run search tests only:

```bash
python3 -m unittest discover -s test -p 'test_search.py' -v
```

Run report tests only:

```bash
python3 -m unittest discover -s test -p 'test_reports.py' -v
```