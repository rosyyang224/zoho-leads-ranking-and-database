from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# --- Lookup Tables ---

# Locations a company is based in or operates in
# id: int (PK), region: str (e.g., US, Europe, Asia)
class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String)
    country = db.Column(db.String)
    state = db.Column(db.String)
    city = db.Column(db.String)


# Company size category
# id: int (PK), fte_range: str (e.g., "<100", "100-500")
class Size(db.Model):
    __tablename__ = 'sizes'
    id = db.Column(db.Integer, primary_key=True)
    fte_range = db.Column(db.String)


# Company funding stage
# id: int (PK), stage: str (e.g., Seed, Series A), funders: str (comma-separated list or JSON)
class FundingStage(db.Model):
    __tablename__ = 'funding_stages'
    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.String)
    funders = db.Column(db.String)


# Standardized maturity stages for a modality
# id: int (PK), stage: str (e.g., Preclinical, Phase 1, Phase 2)
class ModalityMaturity(db.Model):
    __tablename__ = 'modality_maturities'
    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.String)


# Therapeutic modalities (e.g., RNA, Cell Therapy) and their subtypes (e.g., mRNA, TIL)
# id: int (PK), type: str, subtype: str
class TherapeuticModality(db.Model):
    __tablename__ = 'therapeutic_modalities'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    subtype = db.Column(db.String)


# --- Core Tables ---

# A company (organization) under evaluation
# id: int (PK), name: str, website, FKs to location/size/funding, timestamps
class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    size_id = db.Column(db.Integer, db.ForeignKey('sizes.id'))
    funding_stage_id = db.Column(db.Integer, db.ForeignKey('funding_stages.id'))

    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    leads = db.relationship('Lead', backref='company')
    modalities = db.relationship('CompanyModality', back_populates='company')


# Maps a company to a modality they are working on, with its maturity stage
# id: int (PK), FKs to company, modality, and maturity
class CompanyModality(db.Model):
    __tablename__ = 'company_modalities'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    modality_id = db.Column(db.Integer, db.ForeignKey('therapeutic_modalities.id'))
    maturity_id = db.Column(db.Integer, db.ForeignKey('modality_maturities.id'))

    company = db.relationship('Company', back_populates='modalities')
    modality = db.relationship('TherapeuticModality')
    maturity = db.relationship('ModalityMaturity')


# Maps a lead to a modality they are targeting in outreach, with expected maturity
# Composite PK: lead_id + modality_id
# FKs to lead, modality, and maturity
class LeadModality(db.Model):
    __tablename__ = 'lead_modalities'
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), primary_key=True)
    modality_id = db.Column(db.Integer, db.ForeignKey('therapeutic_modalities.id'), primary_key=True)
    maturity_id = db.Column(db.Integer, db.ForeignKey('modality_maturities.id'))

    lead = db.relationship('Lead', back_populates='modalities')
    modality = db.relationship('TherapeuticModality')
    maturity = db.relationship('ModalityMaturity')


# A specific outreach attempt linked to a company
# id: int (PK), company_id (FK), lead_status: str, lead_type: str, score: int
class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    zoho_id = db.Column(db.String, unique=True)

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    lead_status = db.Column(db.String)   # e.g., Attempting, In Discussion
    lead_type = db.Column(db.String)     # e.g., CDMO, Biotherapeutics
    score = db.Column(db.Integer)

    modalities = db.relationship('LeadModality', back_populates='lead')
    contacts = db.relationship('Contact', backref='lead')


# Contact person associated with a lead
# id: int (PK), lead_id (FK), name/title/email/phone/linkedin/buying_power
class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))

    full_name = db.Column(db.String)
    title = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    linkedin = db.Column(db.String)
    buying_power = db.Column(db.String)  # e.g., Low, Medium, High
