import sqlite3

DATABASE_NAME = "tickets.db"

def create_tickets_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            summary TEXT,
            issue_type TEXT,
            urgency TEXT,
            affected_item TEXT,
            suggested_action TEXT,
            needs_ticket INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def insert_ticket_data(data, source="email"):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tickets (source, summary, issue_type, urgency, affected_item, suggested_action, needs_ticket)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        source,
        data.get("summary", "N/A"),
        data.get("issue_type", "Other"),
        data.get("urgency", "Medium"),
        data.get("affected_item", "N/A"),
        data.get("suggested_action", "No suggested action."),
        int(data.get("needs_ticket", False))
    ))

    conn.commit()
    conn.close()
    print(f"Data inserted into local database: {data.get('summary', 'N/A')}")
create_tickets_table()