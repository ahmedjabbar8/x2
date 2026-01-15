import database
import sqlite3
from datetime import datetime

def test():
    try:
        conn = sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        
        # Ensure at least one patient exists
        cursor.execute("INSERT OR IGNORE INTO patients (id, name, en_name) VALUES (999, 'Test Patient', 'Test Patient')")
        
        # Add an unpaid invoice
        cursor.execute("""
            INSERT INTO invoices (patient_id, amount, status, description, created_at)
            VALUES (999, 125000, 'Unpaid', 'Lab: Blood Test & Consultation', CURRENT_TIMESTAMP)
        """)
        conn.commit()
        conn.close()
        
        print("Testing get_unpaid_invoices...")
        unpaid = database.get_unpaid_invoices()
        print(f"Count: {len(unpaid)}")
        
        print("Testing get_financial_report...")
        today = datetime.now().strftime('%Y-%m-%d')
        report = database.get_financial_report(today, today)
        print(f"Report: {report}")
        
        print("All database tests passed.")
    except Exception as e:
        print(f"TEST FAILED: {e}")

if __name__ == "__main__":
    test()
