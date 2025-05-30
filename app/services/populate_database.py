import pandas as pd
from datetime import datetime
from app.models import db, Company, Location, Lead, Contact
import pycountry
import pycountry_convert as pc

def normalize_missing(val):
    """Convert empty strings and pandas NA to Python None."""
    if pd.isna(val) or str(val).strip().lower() in ["", "nan", "na", "<na>"]:
        return None
    return str(val).strip()


def preprocess_df(path):
    df = pd.read_csv(path)
    df.dropna(axis=1, how='all', inplace=True)
    df.columns = df.columns.str.strip()
    df.drop_duplicates(inplace=True)
    for col in df.select_dtypes(include=['object']):
        df[col] = df[col].map(normalize_missing)
    df = df.where(pd.notna(df), None)
    return df


def infer_region(country_name):
    try:
        country = pycountry.countries.get(name=country_name)
        if not country:
            country = pycountry.countries.search_fuzzy(country_name)[0]

        country_code = country.alpha_2
        continent_code = pc.country_alpha2_to_continent_code(country_code)

        region_map = {
            "AF": "Africa",
            "NA": "North America",
            "SA": "South America",
            "AS": "Asia",
            "OC": "Oceania",
            "EU": "Europe",
            "AN": "Antarctica"
        }

        return region_map.get(continent_code, None)

    except Exception:
        return None

def get_or_create_location(country, state, city):
    region = infer_region(country)
    location = Location.query.filter_by(
        region=region, country=country, state=state, city=city
    ).first()
    if not location:
        location = Location(
            region=region, 
            country=country, 
            state=state, 
            city=city)
        db.session.add(location)
        db.session.commit()
    return location

def get_or_create_company(name, location_id):
    if not name or pd.isna(name):
        return None
    name = name.strip()
    company = Company.query.filter_by(name=name).first()
    if not company:
        company = Company(
            name=name,
            location_id=location_id,
            size_id=None,
            funding_stage_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(company)
        db.session.commit()
    return company

def create_lead(zoho_id, lead_status, lead_type, company_id):
    lead = Lead(
        zoho_id=zoho_id,
        lead_status=lead_status,
        lead_type=lead_type,
        score=None,
        company_id=company_id
    )
    db.session.add(lead)
    db.session.commit()
    return lead

def create_contact(lead_id, full_name, title, email):
    contact = Contact(
        lead_id=lead_id,
        full_name=full_name,
        title=title,
        email=email,
        phone=None,
        linkedin=None,
        buying_power=None
    )
    db.session.add(contact)

def populate_all_from_csv(path):
    df = preprocess_df(path)
    created, skipped = 0, 0

    for _, row in df.iterrows():
        zoho_id = row.get("Record Id")
        if not zoho_id or pd.isna(zoho_id):
            skipped += 1
            continue
        if Lead.query.filter_by(zoho_id=zoho_id).first():
            skipped += 1
            continue

        # Extract fields
        account_name = row.get("Account Name")
        lead_status = row.get("Lead Quality") or None
        lead_type = row.get("Lead Type") or None
        country = row.get("Mailing Country")
        state = row.get("Mailing State")
        city = row.get("Mailing City")
        first_name = row.get("First Name") or None
        last_name = row.get("Last Name") or None
        title = row.get("Title") or None
        email = row.get("Email") or None
        full_name = f"{first_name} {last_name}".strip() or None

        location = get_or_create_location(country, state, city)
        company = get_or_create_company(account_name, location.id if location else None)
        lead = create_lead(zoho_id, lead_status, lead_type, company.id if company else None)
        create_contact(lead.id, full_name, title, email)

        created += 1

    db.session.commit()
    print(f"Created {created} leads, contacts, and companies")
    print(f"Skipped {skipped} rows (missing or duplicate Zoho ID)")
