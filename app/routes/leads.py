from flask import Blueprint, request, jsonify
from app.models import db, Lead
from utils.csv_parser import parse_csv

bp = Blueprint("leads", __name__)

@bp.route("/upload", methods=["POST"])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    df = parse_csv(file)

    leads = []
    for _, row in df.iterrows():
        lead = Lead(
            zoho_id=row.get("Record Id"),
            account_name=row.get("Account Name"),
            first_name=row.get("First Name"),
            last_name=row.get("Last Name"),
            email=row.get("Email"),
            title=row.get("Title"),
            description=row.get("Description"),
            mailing_country=row.get("Mailing Country"),
            mailing_state=row.get("Mailing State"),
            mailing_city=row.get("Mailing City"),
            remarks=row.get("Remarks"),
            lead_quality=row.get("Lead Quality"),
            lead_type=row.get("Lead Type"),
            major_segment=row.get("Major Segment (Product subtype)")
        )
        leads.append(lead)

    db.session.bulk_save_objects(leads)
    db.session.commit()

    return jsonify({"message": f"Uploaded {len(leads)} leads successfully"})