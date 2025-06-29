# Kids Quiz App - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Database Setup
You'll need a PostgreSQL database. The easiest way is using [Supabase](https://supabase.com):

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Go to Settings → Database
4. Copy the connection string (it looks like this):
   ```
   postgresql://postgres.xxx:YOUR_PASSWORD@xxx.supabase.co:6543/postgres
   ```

### 2. Configure Environment
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and replace `YOUR_PASSWORD` with your actual database password:
   ```env
   DATABASE_URL=postgresql://postgres.your_id:YOUR_ACTUAL_PASSWORD@your-host.supabase.co:6543/postgres
   ```

### 3. Install and Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run setup (creates database tables and admin user)
python setup.py

# Start the app
streamlit run app.py
```

### 4. First Login
- Visit: http://localhost:8501
- Login with: `admin` / `admin123`
- Or create a new student account

## 🎯 Default Credentials
- **Admin**: username: `admin`, password: `admin123`
- **Students**: Create your own accounts

## 📊 Sample Data
The setup script can load sample Mathematics quizzes to get you started quickly.

## 🔧 Troubleshooting

### Database Connection Issues
- Verify your DATABASE_URL in `.env`
- Check if your Supabase project is active
- Ensure the password is correct (no special characters encoding issues)

### Module Import Errors
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

## 📱 Features Overview

### For Students:
- Browse subjects → topics → classes → levels → quizzes
- Take timed quizzes with multiple choice questions
- View detailed results with explanations
- Track performance across multiple attempts

### For Admins:
- Upload quiz data via JSON files
- Manage quiz visibility (show/hide)
- View all user attempts and statistics
- Monitor system usage

## 🎓 Adding Your Own Content

1. Login as admin
2. Go to Admin Dashboard → Upload Quiz Data
3. Upload a JSON file with your quiz content (see `sample_quiz_data.json` for format)

That's it! You now have a fully functional quiz app running. 🎉
