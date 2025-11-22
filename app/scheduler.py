from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from flask import current_app
from .models import Booking, User, db
from .utils import send_notification, LOCK_IN_HOURS

scheduler = BackgroundScheduler()

def lockin_job():
    """
    Runs every 10 minutes to lock events within the lock-in period.
    """
    app = current_app._get_current_object()

    with app.app_context():
        now = datetime.utcnow()

        bookings = Booking.query.filter(
            Booking.status.in_(["Approved", "pending"])
        ).all()

        for b in bookings:
            event_start = datetime.combine(b.date, b.start_time)

            # If inside lock-in window:
            if now >= (event_start - timedelta(hours=LOCK_IN_HOURS)):

                # Approved → becomes locked
                if b.status == "Approved":
                    b.status = "locked"

                # Optional reason (if field exists)
                # b.locked_reason = "Lock-in activated"

                db.session.add(b)

                send_notification(
                    User.query.get(b.user_id),
                    "Lock-in Activated",
                    "Your event has entered lock-in period."
                )

        db.session.commit()


def start_scheduler(app):
    """
    Prevents APScheduler from running twice in debug mode.
    """
    if not scheduler.running:
        scheduler.add_job(lockin_job, 'interval', minutes=10)
        scheduler.start()
        print("APScheduler Started")
