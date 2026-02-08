from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DailyStat(db.Model):
    __tablename__ = 'daily_stats'
    
    date = db.Column(db.String(10), primary_key=True)
    intercepted_requests = db.Column(db.Integer, default=0)
    repeater_requests = db.Column(db.Integer, default=0)
    intruder_requests = db.Column(db.Integer, default=0)
    scanner_requests = db.Column(db.Integer, default=0)
    spider_requests = db.Column(db.Integer, default=0)
    session_minutes = db.Column(db.Integer, default=0)
    sessions_count = db.Column(db.Integer, default=0)

class StreakInfo(db.Model):
    __tablename__ = 'streak_info'
    
    id = db.Column(db.Integer, primary_key=True)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_active_date = db.Column(db.String(10))

def init_db():
    """Initialize database tables"""
    db.create_all()
    
    # Create initial streak entry if none exists
    if not StreakInfo.query.first():
        streak = StreakInfo(current_streak=0, longest_streak=0)
        db.session.add(streak)
        db.session.commit()
