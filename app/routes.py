from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime, date, time, timedelta
from .models import Booking, SeminarHall, db, User, get_priority, overlaps, LOCK_IN_HOURS

from flask_login import current_user, login_required

import pytz
IST = pytz.timezone("Asia/Kolkata")

main_bp = Blueprint("main", __name__)

def is_within_lockin(booking_date: date, start_time: time) -> bool:
    # event_start = datetime.combine(booking_date, start_time)
    # return datetime.utcnow() >= (event_start - timedelta(hours=LOCK_IN_HOURS))

        # event datetime in IST
    event_start = IST.localize(datetime.combine(booking_date, start_time))

    # current time in IST
    now = datetime.now(IST)

    # lock-in window
    lock_time = event_start - timedelta(hours=LOCK_IN_HOURS)

    return now >= lock_time


def check_conflicts(hall_id, booking_date, start_time, end_time):
    """
    Returns: dict with keys:
      - overlapping (list of Booking)
      - approved_conflict (Booking or None)
      - pending_conflicts (list)
    """
    conflicts = Booking.query.filter_by(hall_id=hall_id, date=booking_date).filter(
        Booking.status.in_(["pending", "Approved"])
    ).all()

    overlapping = []
    approved_conflict = None
    pending_conflicts = []
    for b in conflicts:
        # build datetime ranges and check overlap
        if overlaps(
            datetime.combine(b.date, b.start_time), datetime.combine(b.date, b.end_time),
            datetime.combine(booking_date, start_time), datetime.combine(booking_date, end_time)
        ):
            overlapping.append(b)
            if b.status == "Approved":
                approved_conflict = b
            elif b.status == "pending":
                pending_conflicts.append(b)

    return {
        "overlapping": overlapping,
        "approved_conflict": approved_conflict,
        "pending_conflicts": pending_conflicts
    }

def find_alternate_slots(hall_id, booking_date, duration_minutes=60, window_days=3):
    """Return simple alternate suggestions (same hall different time / other halls)."""
    suggestions = []
    # Try same date different times (simple: try start at every hour)
    for hour in range(8, 20):  # working hours
        sug_start = time(hour, 0)
        sug_end = (datetime.combine(booking_date, sug_start) + timedelta(minutes=duration_minutes)).time()
        conflicts = check_conflicts(hall_id, booking_date, sug_start, sug_end)
        if not conflicts["overlapping"]:
            suggestions.append({
                "hall_id": hall_id,
                "date": str(booking_date),
                "start": sug_start.strftime("%H:%M"),
                "end": sug_end.strftime("%H:%M")
            })
            if len(suggestions) >= 3:
                break

    # Try other halls (first available)
    if len(suggestions) < 3:
        halls = SeminarHall.query.all()
        for h in halls:
            if h.id == hall_id:
                continue
            conflicts = check_conflicts(h.id, booking_date, time(9,0), time(10,0))
            if not conflicts["overlapping"]:
                suggestions.append({"hall_id": h.id, "date": str(booking_date), "start": "09:00", "end": "10:00"})
            if len(suggestions) >= 3:
                break

    return suggestions


def send_notification(user: User, subject: str, message: str):
    """
    Stub for notifications — replace with real email/push logic.
    """
    if not user:
        print(f"NOTIFY <unknown user>: {subject} - {message}")
        return
    print(f"NOTIFY {user.email}: {subject} - {message}")


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/halls")
def halls():
    halls = SeminarHall.query.all()
    return render_template("halls.html", halls=halls, user=current_user)


@main_bp.route("/book", methods=["GET", "POST"])
@login_required
def book():
    # if current_user.role != "club_head":
    #     flash("Only club heads can request bookings.", "danger")
    #     return redirect(url_for("main.halls"))

    if request.method == "POST":
        # Validate and parse fields
        hall_id_raw = request.form.get("hall_id")
        date = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        event_type = request.form.get("event_type")

        if not (hall_id_raw and event_type and date and start_time and end_time):
            flash("Please fill all required fields", "danger")
            return redirect(url_for("main.book"))

        try:
            hall_id = int(hall_id_raw)
        except (ValueError, TypeError):
            flash("Invalid hall selected.", "danger")
            return redirect(url_for("main.book"))

        # Convert string to Python datetime/time objects
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            start_time_obj = datetime.strptime(start_time, "%H:%M").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
            flash("Invalid date/time format. Use YYYY-MM-DD and HH:MM.", "danger")
            return redirect(url_for("main.book"))
        
        now = datetime.now()

        requested_start = datetime.combine(date_obj, start_time_obj)

        if requested_start < now:
            flash("Cannot book for past date or past time.", "danger")
            return redirect(url_for("main.book"))

        # basic time validation
        if datetime.combine(date_obj, end_time_obj) <= datetime.combine(date_obj, start_time_obj):
            flash("End time must be after start time.", "danger")
            return redirect(url_for("main.book"))

        # # Lock-in check (no new booking inside lock-in)
        # if is_within_lockin(date_obj, start_time_obj):
        #     flash("This slot is locked because an approved event is starting soon.", "danger")
        #     return redirect(url_for("main.book"))

        # Check conflicts (PASS time objects)
        conflicts = check_conflicts(hall_id, date_obj, start_time_obj, end_time_obj)
        new_priority = get_priority(event_type)

        # If an approved booking exists
        if conflicts["approved_conflict"]:
            approved = conflicts["approved_conflict"]

            # If existing approved is within lock-in -> no override allowed
            if is_within_lockin(approved.date, approved.start_time):
                flash("Cannot override an approved booking within lock-in window. Choose another slot.", "danger")
                return redirect(url_for("main.book"))

            # If new has higher priority -> allow pending + mark approved for potential auto-cancel_pending
            if new_priority > approved.priority:
                approved.status = "auto_cancel_pending"
                db.session.add(approved)

                new_booking = Booking(
                    hall_id=hall_id,
                    user_id=current_user.id,
                    date=date_obj,
                    start_time=start_time_obj,
                    end_time=end_time_obj,
                    event_type=event_type,
                    priority=new_priority,
                    status="pending"
                )

                db.session.add(new_booking)
                db.session.commit()

                # notify admin and both users
                send_notification(current_user, "Booking created", "Your high-priority booking is pending approval.")
                send_notification(User.query.get(approved.user_id), "Your booking is at risk", "A higher priority booking requested the same slot.")
                flash("Booking created as pending. Existing booking marked for admin review.", "success")
                return redirect(url_for("main.my_bookings"))
            else:
                # new has lower or equal priority → not allowed to book (do not save at_risk)
                flash("This time slot is already approved for a higher or equal priority event. Please choose another time slot.", "danger")
                return redirect(url_for("main.book"))

        # If there are pending conflicts, compare priorities and mark lower pending ones as at_risk
        if conflicts["pending_conflicts"]:
            lower_found = False
            for p in conflicts["pending_conflicts"]:
                if new_priority > p.priority:
                    p.status = "at_risk"
                    db.session.add(p)
                    lower_found = True
                else:
                    # we leave the pending booking as-is; the new one will be at_risk
                    pass

            new_booking_status = "pending" if lower_found else "at_risk"
            new_booking = Booking(
                hall_id=hall_id,
                user_id=current_user.id,
                date=date_obj,
                start_time=start_time_obj,
                end_time=end_time_obj,
                event_type=event_type,
                priority=new_priority,
                status=new_booking_status
            )
            db.session.add(new_booking)
            db.session.commit()
            flash("Booking requested. Status: " + new_booking_status, "info")
            return redirect(url_for("main.my_bookings"))

        # No conflicts -> create pending booking
        new_booking = Booking(
            hall_id=hall_id,
            user_id=current_user.id,
            date=date_obj,
            start_time=start_time_obj,
            end_time=end_time_obj,
            event_type=event_type,
            priority=new_priority,
            status="pending"
        )
        db.session.add(new_booking)
        db.session.commit()
        send_notification(current_user, "Booking submitted", "Your booking is pending approval.")
        flash("Booking request submitted! Awaiting approval.", "success")
        return redirect(url_for("main.my_bookings"))

    halls = SeminarHall.query.all()
    return render_template("book.html", halls=halls, user=current_user)


@main_bp.route("/my_bookings")
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id, ).all()
    return render_template("my_bookings.html", bookings=bookings, user=current_user)


@main_bp.route("/booked")
@login_required
def booked():
    # use .all() and use status string exactly as you're storing ("Approved")
    bookings = Booking.query.filter_by(status="Approved").all()
    return render_template("booked.html", bookings=bookings, user=current_user)


@main_bp.route("/approvals")
@login_required
def approvals():
    if current_user.role not in ["admin", "hod"]:
        return "Access denied"

    bookings = Booking.query.filter(Booking.status.in_(["pending", "at_risk", "auto_cancel_pending"])).all()
    return render_template("approve.html", bookings=bookings, user=current_user)


@main_bp.route("/approve/<int:id>", methods=["GET", "POST"])
@login_required
def approve(id):
    if current_user.role not in ["admin", "hod"]:
        return "Access denied"

    booking = Booking.query.get_or_404(id)

    #Optionally prevent approving within lock-in (uncomment if desired)
    if is_within_lockin(booking.date, booking.start_time):
        flash("Cannot approve this booking within lock-in window.", "danger")
        return redirect(url_for("main.approvals"))

    booking.status = "Approved"
    db.session.add(booking)

    # Reject conflicting pending bookings in same hall/date/time with lower priority
    conflicts = Booking.query.filter(
        Booking.hall_id == booking.hall_id,
        Booking.date == booking.date,
        Booking.id != booking.id,
        Booking.status.in_(["pending", "at_risk", "auto_cancel_pending"])
    ).all()

    for c in conflicts:
        # if c overlaps with booking
        if overlaps(
            datetime.combine(c.date, c.start_time), datetime.combine(c.date, c.end_time),
            datetime.combine(booking.date, booking.start_time), datetime.combine(booking.date, booking.end_time)
        ):
            c.status = "Rejected"
            db.session.add(c)
            send_notification(User.query.get(c.user_id), "Booking rejected", "Your booking was rejected due to a higher priority approval.")

    db.session.commit()
    send_notification(User.query.get(booking.user_id), "Booking approved", f"Your booking (id {booking.id}) is approved.")
    return redirect(url_for("main.approvals"))


@main_bp.route("/reject/<int:id>", methods=["GET","POST"])
@login_required
def reject(id):
    if current_user.role not in ["admin", "hod"]:
        return "Access denied"

    booking = Booking.query.get_or_404(id)
    reason = request.form.get("reason", "Rejected by admin")
    booking.status = "Rejected"
    db.session.add(booking)
    db.session.commit()
    send_notification(User.query.get(booking.user_id), "Booking rejected", reason)
    return redirect(url_for("main.approvals"))

            



