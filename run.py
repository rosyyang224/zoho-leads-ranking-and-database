from app import create_app
# from apscheduler.schedulers.background import BackgroundScheduler
from app.services.sync_leads import sync_and_process_zoho_leads

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=sync_and_process_zoho_leads, trigger="interval", hours=6)
# scheduler.start()

app = create_app()

if __name__ == "__main__":
    # sync_and_process_zoho_leads()
    app.run(debug=True)
