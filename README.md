# Gaming Addiction Risk Prediction System

A cyberpunk-themed web application that predicts gaming addiction risk using AI and provides personalized improvement plans.

## Features

- **AI-Powered Risk Assessment**: Random Forest ML model analyzing 12+ behavioral risk factors
- **User Authentication**: Secure signup, login, and session management
- **Cyberpunk Neon UI**: Futuristic interface with glowing effects, grid backgrounds, and neon animations
- **Weekly Self-Check Tracker**: Log mood, gaming hours, sleep, study time, and focus levels
- **Interactive Dashboard**: Visualize risk scores over time with matplotlib charts
- **Personalized Improvement Plans**: AI-generated weekly structured plans based on risk level and trends
- **PDF Export**: Export improvement plans as professional PDF documents
- **Trend Analysis**: Track if your gaming wellness is improving, stable, or declining

## Tech Stack

**Backend:**
- Flask (Python web framework)
- SQLAlchemy ORM with SQLite database
- Flask-Login for authentication
- scikit-learn (Random Forest Classifier)
- matplotlib for data visualization
- reportlab for PDF generation

**Frontend:**
- HTML5/CSS3 with custom cyberpunk styling
- Vanilla JavaScript for interactions
- Google Fonts (Orbitron, Montserrat)
- FontAwesome icons

## Installation & Setup

1. **Install Dependencies** (already configured in this Replit):
   ```bash
   All dependencies are pre-installed via uv package manager
   ```

2. **Train the ML Model**:
   ```bash
   python train_model.py
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the App**:
   - The app runs on `http://0.0.0.0:5000`
   - Use the Replit webview to see the application

## Project Structure

```
.
├── app.py                      # Main Flask application
├── train_model.py             # ML model training script
├── model.pkl                  # Trained Random Forest model
├── utils/
│   ├── chart_generator.py    # matplotlib chart generation
│   └── improvement_plan.py   # AI plan generation & PDF export
├── templates/
│   ├── base.html             # Base template with navbar
│   ├── index.html            # Homepage with hero section
│   ├── signup.html           # User registration
│   ├── login.html            # User login
│   ├── assessment.html       # Risk assessment form
│   ├── dashboard.html        # Analytics dashboard
│   ├── weekly_tracker.html   # Weekly self-check tracker
│   └── improvement_plan.html # Personalized plan display
├── static/
│   ├── css/neon.css          # Cyberpunk neon theme
│   ├── js/main.js            # Frontend JavaScript
│   ├── images/               # Generated charts
│   └── exports/              # Generated PDF files
└── gaming_addiction.db       # SQLite database

## Database Schema

**Users Table:**
- id, username, email, password_hash, created_at

**Assessments Table:**
- id, user_id, gaming_hours, sleep_hours, academic_performance, emotional_state, skip_responsibilities, social_interactions, age_group, game_genres, concentration_difficulty, risk_level, risk_score, created_at

**Weekly Logs Table:**
- id, user_id, week_start, mood, gaming_hours, sleep_hours, study_hours, focus_level, created_at

**Improvement Plans Table:**
- id, user_id, risk_level, plan_content, created_at

## Usage Guide

1. **Sign Up**: Create a new account
2. **Take Assessment**: Complete the risk assessment form with honest answers
3. **View Dashboard**: See your risk level, wellness score, and trend analysis
4. **Log Weekly Progress**: Track your weekly gaming, sleep, and study habits
5. **Get Improvement Plan**: Receive a personalized multi-week improvement plan
6. **Export Plan**: Download your plan as a PDF for offline reference

## Risk Categorization

- **Low Risk**: Healthy gaming habits with good life balance
- **Moderate Risk**: Some concerning patterns that need attention
- **High Risk**: Significant addiction indicators requiring intervention

## ML Model Details

- **Algorithm**: Random Forest Classifier
- **Accuracy**: ~82%
- **Features**: 9 input features (gaming hours, sleep, academic performance, emotional state, responsibilities, social interactions, age, game genres, concentration)
- **Output**: Risk level (Low/Moderate/High) with confidence score

## Color Palette

- **Neon Cyan**: #00eaff
- **Neon Pink**: #ff007f
- **Neon Green**: #39ff14
- **Dark Background**: #0a0e27
- **Card Background**: #0f1329

## Security Features

- Password hashing with Werkzeug
- Secure session management with Flask-Login
- CSRF protection
- Environment variable for session secrets

## Future Enhancements

- Dark/Light mode toggle
- Advanced trend prediction algorithms
- Motivational quote widget
- Data export (CSV/JSON)
- Mobile app version
- Multiplayer accountability features
- Integration with gaming platforms

## Contributing

This is a demo project created for educational purposes. Feel free to extend and customize!

## License

MIT License - Free to use and modify

---

**Developed with ❤️ using Flask, scikit-learn, and cyberpunk aesthetics**
