import sys
import os
print(f"Current Path: {os.getcwd()}")
try:
    import database
    print(f"Database file: {database.__file__}")
    print(f"get_all_patients in database: {'get_all_patients' in dir(database)}")
    print(f"delete_patient in database: {'delete_patient' in dir(database)}")
    
    from database import add_patient, get_all_patients, delete_patient
    print("Import from database in PR style: SUCCESS")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
