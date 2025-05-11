
# This will irrevocably delete ALL users and vault entries from your database.

import os
from dotenv import load_dotenv
from backend import create_app, db
from backend.model import User, PasswordEntry

def main():
    # Load environment variables (e.g. DATABASE_URL)
    load_dotenv()

    # Create the Flask app and push context
    app = create_app()
    with app.app_context():
        # Delete all vault entries first (FK constraint)
        entries_deleted = db.session.query(PasswordEntry).delete()
        # Delete all users
        users_deleted = db.session.query(User).delete()
        db.session.commit()

        print(f"Deleted {entries_deleted} vault entries.")
        print(f"Deleted {users_deleted} users.")

if __name__ == "__main__":
    main()
