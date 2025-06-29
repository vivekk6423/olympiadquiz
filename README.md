# Kids Quiz App - Streamlit Version

A comprehensive, interactive quiz learning platform built with Streamlit and PostgreSQL. This application provides a complete educational quiz system with user authentication, hierarchical content organization, and powerful admin features.

## 🌟 Features

### Student Features
- 🔐 **User Authentication**: Secure login/registration system
- 📚 **Hierarchical Navigation**: Subjects → Topics → Classes → Levels → Quizzes
- ⏱️ **Timed Quizzes**: Interactive quiz interface with countdown timer
- 📊 **Real-time Progress**: Question navigation and progress tracking
- 🎯 **Instant Results**: Detailed scoring and performance analysis
- 📈 **Performance History**: Track your progress across multiple attempts
- 🔄 **Retake Quizzes**: Improve your scores with multiple attempts

### Admin Features
- � **Admin Dashboard**: Comprehensive system overview and statistics
- 🧩 **Quiz Management**: Create, edit, hide/show, and delete quizzes
- 📤 **Bulk Upload**: Import quiz data via JSON files
- 👥 **User Management**: Create, update, delete users and reset passwords
- 🔑 **Admin Controls**: Grant or revoke admin privileges
- 📊 **User Analytics**: Detailed statistics on user performance 
- 📈 **Activity Tracking**: Monitor most active users and performance metrics
- 🎛️ **Visibility Control**: Show/hide quizzes for students

### Technical Features
- 🗄️ **PostgreSQL Database**: Robust data storage with Supabase
- 🔒 **Secure Authentication**: Password hashing and session management
- 📱 **Responsive Design**: Works on desktop and mobile devices
- ⚡ **Fast Performance**: Optimized database queries and caching
- 🎨 **Modern UI**: Clean, intuitive interface built with Streamlit

## 🏗️ Architecture

### Database Schema
```
Subject (1:N) → Topic (1:N) → Class (1:N) → Level (1:N) → Quiz (1:N) → Question (1:N) → Answer
User (1:N) → QuizAttempt (N:1) → Quiz
```

### Project Structure
```
streamlit/
├── app.py                    # Main application entry point
├── models.py                 # SQLAlchemy database models
├── database.py               # Database connection and utilities
├── auth.py                   # Authentication functions
├── quiz_utils.py             # Quiz-related utilities
├── admin_utils.py            # Admin functionality
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create from .env.example)
├── .env.example              # Environment variables template
├── config/                   # Configuration files
├── utils/                    # Utility functions
└── assets/                   # Static assets
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL database (Supabase recommended)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd streamlit
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Configuration
Create a `.env` file from the template:
```bash
cp .env.example .env
```

Update `.env` with your database credentials:
```env
DATABASE_URL=postgresql://postgres.your_id:YOUR_PASSWORD@your-host.supabase.co:6543/postgres
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### 5. Run the Application
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 📊 Database Setup

### Supabase Setup
1. Create a [Supabase](https://supabase.com) account
2. Create a new project
3. Get your database URL from Settings → Database
4. Update the `.env` file with your credentials

### Database Schema
The application automatically creates all required tables on first run:
- `subject`, `topic`, `class`, `level` - Content hierarchy
- `quiz`, `question`, `answer` - Quiz content
- `user`, `quiz_attempt` - User data and attempts

## 🎯 Usage

### For Students
1. **Register/Login**: Create an account or login
2. **Browse Content**: Navigate through Subjects → Topics → Classes → Levels
3. **Take Quizzes**: Select a quiz and complete it within the time limit
4. **View Results**: See detailed results with explanations
5. **Track Progress**: Monitor your performance over time

### For Admins
1. **Login**: Use admin credentials (admin/admin123 by default)
2. **Access Admin Panel**: Click "Admin Dashboard" in sidebar
3. **Manage Content**: Upload quiz data, manage visibility
4. **Monitor Users**: View quiz attempts and user statistics

### Quiz Data Format
Upload quiz data in JSON format:
```json
{
  "subject": {
    "name": "Mathematics",
    "topics": [
      {
        "name": "Algebra",
        "classes": [
          {
            "name": "Class 8",
            "levels": [
              {
                "name": "Basic Algebra",
                "quizzes": [
                  {
                    "title": "Linear Equations",
                    "description": "Basic linear equations",
                    "time_limit": 30,
                    "questions": [
                      {
                        "question": "Solve: 2x + 3 = 7",
                        "options": ["x = 1", "x = 2", "x = 3", "x = 4"],
                        "answer": 1,
                        "explanation": "2x = 7 - 3 = 4, so x = 2"
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `ADMIN_USERNAME`: Default admin username
- `ADMIN_PASSWORD`: Default admin password
- `SECRET_KEY`: Application secret key

### Customization
- Modify `config/config.yaml` for app settings
- Update `assets/styles/main.css` for custom styling
- Add new features in respective utility modules

## 📈 Features Comparison

| Feature | Flask Version | Streamlit Version |
|---------|---------------|-------------------|
| User Authentication | ✅ | ✅ |
| Quiz Taking | ✅ | ✅ |
| Admin Panel | ✅ | ✅ |
| Question Reporting | ✅ | 🔄 (Can be added) |
| Bulk Upload | ✅ | ✅ |
| Mobile Responsive | ✅ | ✅ |
| Real-time Updates | ❌ | ✅ |
| Modern UI | ⚡ | ✅ |

## 🛠️ Development

### Adding New Features
1. **Database Models**: Update `models.py`
2. **Business Logic**: Add functions to appropriate utility files
3. **UI Components**: Create new pages or update existing ones
4. **Admin Features**: Extend `admin_utils.py`

### Testing
```bash
# Run with debug mode
streamlit run app.py --logger.level=debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- Check the logs for database connection issues
- Ensure all environment variables are set correctly
- Verify PostgreSQL database accessibility
- Contact support for additional help

---

**Built with ❤️ using Streamlit and PostgreSQL**
