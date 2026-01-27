# Health Tracker Dashboard

A personal health tracking dashboard built with FastAPI and SQLite, designed to monitor daily health habits and progress with beautiful data visualizations.

## 🎯 Project Overview

This web application provides a simple yet comprehensive dashboard for tracking personal health metrics including:

- **Daily Metrics**: Caloric intake, step count, exercises, weight
- **Progress Tracking**: Streak indicators and historical trends
- **Data Visualization**: Interactive charts and graphs
- **User Management**: Primary user (data entry) and secondary user (view-only)
- **Mobile-First Design**: Optimized for mobile use with touch-friendly interfaces and responsive design

### Key Features

- 🔐 **Authentication System**: Secure login with role-based permissions
- 📊 **Interactive Dashboard**: Real-time health metrics with Chart.js visualizations
- 📝 **Daily Data Entry**: Single form for all daily health data
- 📈 **Historical Analysis**: Detailed history pages for each metric category
- 🎯 **Streak Tracking**: Monitor consistency in health habits
- 👥 **Multi-User Support**: Primary (edit) and secondary (view-only) users
- 📱 **Mobile-First UX**: Designed primarily for mobile use with intuitive touch interactions and quick data entry

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **SQLite**: Lightweight database for personal use
- **SQLAlchemy**: ORM for database interactions
- **Jinja2**: Template engine for server-side rendering
- **Passlib**: Password hashing and authentication
- **Python-Jose**: JWT token handling

### Frontend
- **HTML5/CSS3**: Semantic markup and modern styling
- **JavaScript**: Interactive functionality
- **Chart.js**: Data visualization library
- **Bootstrap 5**: Responsive CSS framework
- **Jinja2 Templates**: Server-side rendering

### Deployment
- **Fly.io**: Cloud deployment platform
- **Custom Domain**: health.marcbm.com.au
- **SQLite**: Production database (suitable for personal use)

## 🏗️ Architecture

```
health_tracker/
├── app/                      # Main application package
│   ├── database/            # Database models and configuration
│   ├── routers/             # FastAPI route handlers
│   ├── templates/           # Jinja2 HTML templates
│   └── middleware.py        # Authentication middleware
├── static/                  # Static assets (CSS, JS, images)
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── *.py                     # Utility scripts (setup, database, users)
└── fly.toml                 # Deployment configuration
```

### Directory Structure Details

- **`app/`**: Core application code
  - **`database/`**: SQLAlchemy models (`User`, `DailyData`) and database configuration
  - **`routers/`**: FastAPI route handlers for authentication and data endpoints
  - **`templates/`**: Jinja2 templates for web pages, organized into base templates, auth pages, and dashboard sections
  - **`middleware.py`**: JWT authentication middleware for route protection

- **`static/`**: Frontend assets served directly by FastAPI
  - **`css/`**: Custom Bootstrap-based styling
  - **`js/`**: Client-side JavaScript for forms and interactions
  - **`images/`**: Static images and icons

- **Root Level**: Configuration and utility scripts
  - **`main.py`**: FastAPI application entry point and route registration
  - **`init_db.py`**: Database schema initialization
  - **`create_user.py`**: User management utility
  - **`dev_setup.sh`** / **`start_dev.sh`**: Development environment scripts
  - **`generate_dummy_data.py`**: Test data generation for development

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd health_tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

7. **Access the application**
   - Open http://localhost:8000 in your browser
   - Create your primary user account
   - Start tracking your health data!

## 📊 Data Models

### User Model
The user model handles authentication and authorization, storing user credentials and permissions. It distinguishes between primary users (who can edit data) and secondary users (view-only access).

### DailyData Model
The core data model that stores daily health metrics for each user. Each record represents one day's worth of health data including physical activity, nutrition, and wellness indicators. The model supports tracking multiple metrics per day with timestamp tracking for data integrity.

## 🔐 Authentication & Authorization

- **JWT-based authentication**: Secure token-based sessions
- **Role-based access**: Primary users can create/edit, secondary users are read-only
- **Password security**: Bcrypt hashing with salt
- **Session management**: Secure cookie-based sessions

## 📈 Data Visualization

### Dashboard Charts
- **Weight Trend**: Line chart showing weight progression over time
- **Calorie Tracking**: Bar chart of daily caloric intake
- **Step Counter**: Progress bars and trend lines
- **Exercise Streaks**: Calendar heatmap visualization
- **Weekly Summaries**: Aggregated weekly progress charts

### Interactive Features
- Hover tooltips with detailed information
- Clickable chart elements linking to detailed views
- Date range selectors for historical analysis
- Export functionality for data backup

## 🚀 Deployment

### Fly.io Deployment

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login to Fly.io**
   ```bash
   fly auth login
   ```

3. **Deploy the application**
   ```bash
   fly deploy
   ```

4. **Set up custom domain**
   ```bash
   fly certs create health.marcbm.com.au
   ```

### Environment Variables
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: SQLite database path
- `ADMIN_USERNAME`: Default admin username
- `ADMIN_PASSWORD`: Default admin password

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 Development Roadmap

- [ ] **Phase 1**: Basic authentication and data models
- [ ] **Phase 2**: Dashboard with core visualizations
- [ ] **Phase 3**: Data entry forms and validation
- [ ] **Phase 4**: Historical data views and analysis
- [ ] **Phase 5**: Advanced features (goals, notifications)
- [ ] **Phase 6**: Mobile app companion (future consideration)

## 🐛 Known Issues

- None currently identified

## 📄 License

This project is for personal use. All rights reserved.

## 📞 Support

For questions or issues, please create an issue in the GitHub repository.

---

**Note**: This application is designed for personal health tracking. Always consult with healthcare professionals for medical advice and decisions.
