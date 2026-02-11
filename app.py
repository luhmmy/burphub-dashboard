from flask import Flask, render_template, jsonify, request
from database import db, DailyStat, StreakInfo, UserProfile, init_db
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
elif not database_url:
    # Use SQLite for free tier (no PostgreSQL database)
    database_url = 'sqlite:///burphub.db'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SYNC_API_KEY'] = os.environ.get('SYNC_API_KEY')

# Initialize database
db.init_app(app)
with app.app_context():
    init_db()

@app.after_request
def add_security_headers(response):
    """Add OWASP-recommended security headers"""
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com;"
    return response

# Simple in-memory rate limiter for sync attempts
sync_attempts = {}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    try:
        # Get streak info
        streak = StreakInfo.query.first()
        if not streak:
            streak = StreakInfo(current_streak=0, longest_streak=0)
        
        # Get today's stats
        today = datetime.now().date().isoformat()
        today_stats = DailyStat.query.filter_by(date=today).first()
        
        # Get total stats
        all_stats = DailyStat.query.all()
        total_requests = sum(s.intercepted_requests + s.repeater_requests + 
                           s.intruder_requests + s.scanner_requests + 
                           s.spider_requests for s in all_stats)
        total_minutes = sum(s.session_minutes for s in all_stats)
        active_days = len(all_stats)
        
        # Get heatmap data (last 365 days)
        heatmap = {}
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=364)
        
        # Initialize all dates with 0
        current_date = start_date
        while current_date <= end_date:
            heatmap[current_date.isoformat()] = 0
            current_date += timedelta(days=1)
        
        # Fill in actual data
        for stat in all_stats:
            if stat.date in heatmap:
                total = (stat.intercepted_requests + stat.repeater_requests +
                        stat.intruder_requests + stat.scanner_requests + stat.spider_requests)
                heatmap[stat.date] = total
        
        # Tool breakdown (last 30 days)
        thirty_days_ago = (datetime.now().date() - timedelta(days=30)).isoformat()
        recent_stats = DailyStat.query.filter(DailyStat.date >= thirty_days_ago).all()
        
        tools = {
            'proxy': sum(s.intercepted_requests for s in recent_stats),
            'repeater': sum(s.repeater_requests for s in recent_stats),
            'intruder': sum(s.intruder_requests for s in recent_stats),
            'scanner': sum(s.scanner_requests for s in recent_stats),
            'spider': sum(s.spider_requests for s in recent_stats),
            'decoder': sum(s.decoder_operations for s in recent_stats),
            'comparer': sum(s.comparer_operations for s in recent_stats),
            'sequencer': sum(s.sequencer_operations for s in recent_stats),
            'extender': sum(s.extender_events for s in recent_stats),
            'target': sum(s.target_additions for s in recent_stats)
        }
        
        # Get profile info
        profile = UserProfile.query.first()
        if not profile:
            profile = UserProfile(handle='', bio='', github='')
        
        return jsonify({
            'streak': {
                'current': streak.current_streak,
                'longest': streak.longest_streak,
                'last_active': streak.last_active_date
            },
            'profile': {
                'handle': profile.handle,
                'bio': profile.bio,
                'github': profile.github
            },
            'today': {
                'requests': (today_stats.intercepted_requests + today_stats.repeater_requests +
                           today_stats.intruder_requests + today_stats.scanner_requests +
                           today_stats.spider_requests) if today_stats else 0
            },
            'totals': {
                'requests': total_requests,
                'time_hours': total_minutes // 60,
                'time_minutes': total_minutes % 60,
                'active_days': active_days
            },
            'heatmap': heatmap,
            'tools': tools
        })
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync', methods=['POST'])
def sync_data():
    """Sync endpoint for BurpHub extension"""
    client_ip = request.remote_addr
    now = datetime.now()
    
    # Simple rate limiting: 10 syncs per minute per IP
    if client_ip in sync_attempts:
        last_time, count = sync_attempts[client_ip]
        if now - last_time < timedelta(minutes=1):
            if count >= 10:
                print(f"[SECURITY] Rate limit exceeded for IP: {client_ip} at {now}")
                return jsonify({'error': 'Rate limit exceeded'}), 429
            sync_attempts[client_ip] = (last_time, count + 1)
        else:
            sync_attempts[client_ip] = (now, 1)
    else:
        sync_attempts[client_ip] = (now, 1)

    # Verify API key
    api_key = request.headers.get('X-API-Key')
    if api_key != app.config['SYNC_API_KEY']:
        print(f"[SECURITY] Failed sync attempt - Invalid API Key from IP: {client_ip} at {now}")
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        data = request.json
        
        # Update daily stats
        for date_str, stats in data.get('daily_stats', {}).items():
            daily_stat = DailyStat.query.filter_by(date=date_str).first()
            if not daily_stat:
                daily_stat = DailyStat(date=date_str)
                db.session.add(daily_stat)
            
            daily_stat.intercepted_requests = stats.get('intercepted_requests', 0)
            daily_stat.repeater_requests = stats.get('repeater_requests', 0)
            daily_stat.intruder_requests = stats.get('intruder_requests', 0)
            daily_stat.scanner_requests = stats.get('scanner_requests', 0)
            daily_stat.spider_requests = stats.get('spider_requests', 0)
            daily_stat.decoder_operations = stats.get('decoder_operations', 0)
            daily_stat.comparer_operations = stats.get('comparer_operations', 0)
            daily_stat.sequencer_operations = stats.get('sequencer_operations', 0)
            daily_stat.extender_events = stats.get('extender_events', 0)
            daily_stat.target_additions = stats.get('target_additions', 0)
            daily_stat.logger_requests = stats.get('logger_requests', 0)
            daily_stat.session_minutes = stats.get('session_minutes', 0)
            daily_stat.sessions_count = stats.get('sessions_count', 0)
        
        # Update streak info
        streak_data = data.get('streak', {})
        if streak_data:
            streak = StreakInfo.query.first()
            if not streak:
                streak = StreakInfo()
                db.session.add(streak)
            
            streak.current_streak = streak_data.get('current_streak', 0)
            streak.longest_streak = streak_data.get('longest_streak', 0)
            streak.last_active_date = streak_data.get('last_active_date')
        
        # Update profile info
        profile_data = data.get('profile', {})
        if profile_data:
            profile = UserProfile.query.first()
            if not profile:
                profile = UserProfile()
                db.session.add(profile)
            
            profile.handle = profile_data.get('handle', '')
            profile.bio = profile_data.get('bio', '')
            profile.github = profile_data.get('github', '')
        
        db.session.commit()
        return jsonify({'status': 'success', 'synced': len(data.get('daily_stats', {}))}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Sync error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
