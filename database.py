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
    decoder_operations = db.Column(db.Integer, default=0)
    comparer_operations = db.Column(db.Integer, default=0)
    sequencer_operations = db.Column(db.Integer, default=0)
    extender_events = db.Column(db.Integer, default=0)
    target_additions = db.Column(db.Integer, default=0)
    logger_requests = db.Column(db.Integer, default=0)
    session_minutes = db.Column(db.Integer, default=0)
    sessions_count = db.Column(db.Integer, default=0)

class StreakInfo(db.Model):
    __tablename__ = 'streak_info'
    
    id = db.Column(db.Integer, primary_key=True)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_active_date = db.Column(db.String(10))

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String(100), default='')
    bio = db.Column(db.String(500), default='')
    github = db.Column(db.String(200), default='')

def init_db():
    """Initialize database tables"""
    db.create_all()
    
    # Create initial streak entry if none exists
    if not StreakInfo.query.first():
        streak = StreakInfo(current_streak=0, longest_streak=0)
        db.session.add(streak)
    
    # Create initial profile entry if none exists
    if not UserProfile.query.first():
        profile = UserProfile(handle='', bio='', github='')
        db.session.add(profile)
        
    db.session.commit()
