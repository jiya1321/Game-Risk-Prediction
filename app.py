from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import pickle
import numpy as np
import markdown
from utils.chart_generator import generate_risk_chart, generate_gaming_sleep_chart
from utils.improvement_plan import generate_improvement_plan, export_plan_to_pdf

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gaming_addiction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

@app.template_filter('markdown_to_html')
def markdown_to_html(text):
    return markdown.markdown(text, extensions=['nl2br', 'fenced_code'])

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assessments = db.relationship('Assessment', backref='user', lazy=True)
    weekly_logs = db.relationship('WeeklyLog', backref='user', lazy=True)
    improvement_plans = db.relationship('ImprovementPlan', backref='user', lazy=True)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gaming_hours = db.Column(db.Float, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)
    academic_performance = db.Column(db.String(20), nullable=False)
    emotional_state = db.Column(db.String(50), nullable=False)
    skip_responsibilities = db.Column(db.String(20), nullable=False)
    social_interactions = db.Column(db.Integer, nullable=False)
    age_group = db.Column(db.String(20), nullable=False)
    game_genres = db.Column(db.String(200), nullable=False)
    concentration_difficulty = db.Column(db.Boolean, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WeeklyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    mood = db.Column(db.String(20), nullable=False)
    gaming_hours = db.Column(db.Float, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)
    study_hours = db.Column(db.Float, nullable=False)
    focus_level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ImprovementPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    plan_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    if request.method == 'POST':
        gaming_hours = float(request.form.get('gaming_hours'))
        sleep_hours = float(request.form.get('sleep_hours'))
        academic_performance = request.form.get('academic_performance')
        emotional_state = request.form.get('emotional_state')
        skip_responsibilities = request.form.get('skip_responsibilities')
        social_interactions = int(request.form.get('social_interactions'))
        age_group = request.form.get('age_group')
        game_genres = ','.join(request.form.getlist('game_genres'))
        concentration_difficulty = request.form.get('concentration_difficulty') == 'yes'
        
        academic_map = {'improving': 1, 'stable': 2, 'declining': 3}
        emotional_map = {'happy': 1, 'neutral': 2, 'anxious': 3, 'irritable': 4}
        skip_map = {'never': 1, 'rarely': 2, 'sometimes': 3, 'often': 4}
        age_map = {'13-17': 1, '18-24': 2, '25-34': 3, '35+': 4}
        genre_map = {
            'moba': 1, 'fps': 2, 'mmorpg': 3, 'rpg': 4,
            'battle_royale': 5, 'strategy': 6, 'sports': 7
        }
        
        genre_list = request.form.getlist('game_genres')
        genre_value = genre_map.get(genre_list[0], 4) if genre_list else 4
        
        features = [
            gaming_hours,
            sleep_hours,
            academic_map.get(academic_performance, 2),
            emotional_map.get(emotional_state, 2),
            skip_map.get(skip_responsibilities, 2),
            social_interactions,
            age_map.get(age_group, 2),
            genre_value,
            1 if concentration_difficulty else 0
        ]
        
        prediction = model.predict([features])[0]
        risk_proba = model.predict_proba([features])[0]
        risk_score = float(max(risk_proba) * 100)
        
        risk_levels = ['Low Risk', 'Moderate Risk', 'High Risk']
        risk_level = risk_levels[prediction]
        
        new_assessment = Assessment(
            user_id=current_user.id,
            gaming_hours=gaming_hours,
            sleep_hours=sleep_hours,
            academic_performance=academic_performance,
            emotional_state=emotional_state,
            skip_responsibilities=skip_responsibilities,
            social_interactions=social_interactions,
            age_group=age_group,
            game_genres=game_genres,
            concentration_difficulty=concentration_difficulty,
            risk_level=risk_level,
            risk_score=risk_score
        )
        db.session.add(new_assessment)
        db.session.commit()
        
        flash(f'Assessment complete! Your risk level: {risk_level}', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('assessment.html')

@app.route('/dashboard')
@login_required
def dashboard():
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).all()
    weekly_logs = WeeklyLog.query.filter_by(user_id=current_user.id).order_by(WeeklyLog.week_start.desc()).limit(12).all()
    
    latest_assessment = assessments[0] if assessments else None
    
    wellness_score = 50
    if latest_assessment:
        wellness_score = 100 - latest_assessment.risk_score
    
    trend = "stable"
    if len(assessments) >= 2:
        recent_score = assessments[0].risk_score
        previous_score = assessments[1].risk_score
        if recent_score < previous_score - 10:
            trend = "improving"
        elif recent_score > previous_score + 10:
            trend = "declining"
    
    risk_chart_path = None
    gaming_sleep_chart_path = None
    
    if assessments:
        risk_chart_path = generate_risk_chart(assessments)
        gaming_sleep_chart_path = generate_gaming_sleep_chart(weekly_logs if weekly_logs else assessments)
    
    return render_template('dashboard.html', 
                         assessments=assessments,
                         weekly_logs=weekly_logs,
                         latest_assessment=latest_assessment,
                         wellness_score=wellness_score,
                         trend=trend,
                         risk_chart=risk_chart_path,
                         gaming_sleep_chart=gaming_sleep_chart_path)

@app.route('/weekly-tracker', methods=['GET', 'POST'])
@login_required
def weekly_tracker():
    if request.method == 'POST':
        mood = request.form.get('mood')
        gaming_hours = float(request.form.get('gaming_hours'))
        sleep_hours = float(request.form.get('sleep_hours'))
        study_hours = float(request.form.get('study_hours'))
        focus_level = int(request.form.get('focus_level'))
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        existing_log = WeeklyLog.query.filter_by(
            user_id=current_user.id,
            week_start=week_start
        ).first()
        
        if existing_log:
            existing_log.mood = mood
            existing_log.gaming_hours = gaming_hours
            existing_log.sleep_hours = sleep_hours
            existing_log.study_hours = study_hours
            existing_log.focus_level = focus_level
        else:
            new_log = WeeklyLog(
                user_id=current_user.id,
                week_start=week_start,
                mood=mood,
                gaming_hours=gaming_hours,
                sleep_hours=sleep_hours,
                study_hours=study_hours,
                focus_level=focus_level
            )
            db.session.add(new_log)
        
        db.session.commit()
        flash('Weekly log saved successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('weekly_tracker.html')

@app.route('/improvement-plan')
@login_required
def improvement_plan():
    latest_assessment = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).first()
    weekly_logs = WeeklyLog.query.filter_by(user_id=current_user.id).order_by(WeeklyLog.week_start.desc()).limit(4).all()
    
    if not latest_assessment:
        flash('Please complete an assessment first!', 'error')
        return redirect(url_for('assessment'))
    
    trend = "stable"
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).limit(2).all()
    if len(assessments) >= 2:
        if assessments[0].risk_score < assessments[1].risk_score - 10:
            trend = "improving"
        elif assessments[0].risk_score > assessments[1].risk_score + 10:
            trend = "declining"
    
    plan_content = generate_improvement_plan(latest_assessment, weekly_logs, trend)
    
    existing_plan = ImprovementPlan.query.filter_by(user_id=current_user.id).order_by(ImprovementPlan.created_at.desc()).first()
    if existing_plan and (datetime.utcnow() - existing_plan.created_at).days < 7:
        plan = existing_plan
    else:
        plan = ImprovementPlan(
            user_id=current_user.id,
            risk_level=latest_assessment.risk_level,
            plan_content=plan_content
        )
        db.session.add(plan)
        db.session.commit()
    
    return render_template('improvement_plan.html', plan=plan, plan_content=plan_content)

@app.route('/export-plan/<int:plan_id>')
@login_required
def export_plan(plan_id):
    plan = ImprovementPlan.query.get_or_404(plan_id)
    
    if plan.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    pdf_path = export_plan_to_pdf(plan, current_user.username)
    
    return send_file(pdf_path, as_attachment=True, download_name=f'improvement_plan_{current_user.username}.pdf')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
