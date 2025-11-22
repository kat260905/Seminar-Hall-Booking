LOCK_IN_HOURS = 12  # or your value

def send_notification(user, subject, message):
    if user:
        print(f"[NOTIFY] {user.email} | {subject}: {message}")
