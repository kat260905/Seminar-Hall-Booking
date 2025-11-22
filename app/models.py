from datetime import datetime, timedelta, time
from flask_login import UserMixin
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

LOCK_IN_HOURS = 12

def get_priority(event_type: str) -> int:
    """Higher number = higher priority"""
    mapping = {
        "Academic/placement events": 3,  # High
        "Official admin meetings": 2,    # Medium
        "Student club activities": 1     # Low
    }
    return mapping.get(event_type, 1)

def overlaps(start1, end1, start2, end2):
    # assumes times are datetime.time or datetime objects on same date
    return (start1 < end2) and (start2 < end1)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = {"schema": "seminar_booking"}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student", server_default="student")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SeminarHall(db.Model):
    __tablename__ = "seminar_hall"
    __table_args__ = {"schema": "seminar_booking"}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200), nullable=True)

class Booking(db.Model):
    __tablename__ = "booking"
    __table_args__ = {"schema": "seminar_booking"}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('seminar_booking.users.id'), nullable=False)
    hall_id = db.Column(db.Integer, db.ForeignKey('seminar_booking.seminar_hall.id'), nullable=False)

    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    status = db.Column(db.String(20), nullable=False, default="pending", server_default="pending")
    event_type = db.Column(db.String(100), nullable=False,default="General")
    priority = db.Column(db.Integer, nullable=False, default=1)
    #locked_reason = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='bookings')
    hall = db.relationship('SeminarHall', backref='bookings')


from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
