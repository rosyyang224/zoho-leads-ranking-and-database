from app.models import db, Company, Lead, Contact, Location
from sqlalchemy import func

def print_database_summary():
    print("\nDATABASE SUMMARY\n" + "-" * 40)

    # Companies summary
    company_counts = (
        db.session.query(Company.name, func.count(Lead.id))
        .join(Lead, isouter=True)
        .group_by(Company.id)
        .order_by(func.count(Lead.id).desc())
        .all()
    )
    print(f"\nCompanies ({len(company_counts)} total):")
    for name, count in company_counts[:10]:  # top 10 companies
        print(f"  - {name}: {count} lead(s)")
    if len(company_counts) > 10:
        print(f"  ...and {len(company_counts) - 10} more.")

    # Leads summary
    total_leads = db.session.query(Lead).count()
    print(f"\nLeads: {total_leads} total")

    lead_status_counts = (
        db.session.query(Lead.lead_status, func.count(Lead.id))
        .group_by(Lead.lead_status)
        .all()
    )
    print("  Breakdown by status:")
    for status, count in lead_status_counts:
        print(f"    - {status or 'Unknown'}: {count}")

    lead_type_counts = (
        db.session.query(Lead.lead_type, func.count(Lead.id))
        .group_by(Lead.lead_type)
        .all()
    )
    print("  Breakdown by type:")
    for lead_type, count in lead_type_counts:
        print(f"    - {lead_type or 'Unknown'}: {count}")

    # Contacts summary
    total_contacts = db.session.query(Contact).count()
    print(f"\nContacts: {total_contacts} total")

    contacts_with_email = db.session.query(Contact).filter(Contact.email != None).count()
    contacts_with_title = (
        db.session.query(Contact.title, func.count(Contact.id))
        .group_by(Contact.title)
        .order_by(func.count(Contact.id).desc())
        .limit(5)
        .all()
    )
    print(f"  - With email: {contacts_with_email}")
    print(f"  - Top titles:")
    for title, count in contacts_with_title:
        print(f"    - {title or 'Unknown'}: {count}")

    # Locations summary
    location_counts = (
        db.session.query(Location.region, func.count(Location.id))
        .group_by(Location.region)
        .all()
    )
    print(f"\n🌍 Locations by region:")
    for region, count in location_counts:
        print(f"  - {region or 'Unknown'}: {count}")

    print("\nSummary complete.\n")
