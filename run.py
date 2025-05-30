from app import create_app
from app.models import db
from app.services.populate_database import populate_all_from_csv
from app.utils.debug_utils import print_database_summary

app = create_app()

with app.app_context():
    print("Dropping and recreating all tables...")
    db.drop_all()
    db.create_all()
    print("Database reset complete.")
    print("Populating tables from our Zoho leads csv...")
    populate_all_from_csv("/Users/a43152/Desktop/UBrigene/zoho_leads_platform/Leads_2025_05_28.csv")
    print_database_summary()

if __name__ == "__main__":
    app.run(debug=True)
