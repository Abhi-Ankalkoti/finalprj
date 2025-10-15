# Database Setup Guide

## Overview
This AI Resume Interview System uses MySQL as its database backend. The system has been configured to connect to your online MySQL database hosted on `2s6vhs.h.filess.io`.

## Database Configuration

### Connection Details
- **Host**: `2s6vhs.h.filess.io`
- **Port**: `61032`
- **Username**: `Major_audiencedo`
- **Password**: `b2ff8916bde72e33589ca325f0b8b32e5acbb7ce`
- **Database**: `Major_audiencedo`

### Database Schema

The system uses three main tables:

#### 1. `users` Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. `user_profiles` Table
```sql
CREATE TABLE user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    preferred_job_role VARCHAR(100),
    experience_level ENUM('Entry', 'Mid', 'Senior', 'Lead') DEFAULT 'Entry',
    skills TEXT,
    resume_text LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### 3. `session_data` Table
```sql
CREATE TABLE session_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resume_filename VARCHAR(255),
    resume_text LONGTEXT,
    job_role VARCHAR(100),
    interview_score INT DEFAULT 0,
    ats_score INT,
    ats_feedback TEXT,
    skill_gaps TEXT,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Setup Instructions

### 1. Automatic Setup (Recommended)
Run the database initialization script:
```bash
python init_database.py
```

### 2. Manual Setup
If you prefer to set up the database manually:

1. **Connect to your MySQL database** using the provided credentials
2. **Create the database** (if it doesn't exist):
   ```sql
   CREATE DATABASE IF NOT EXISTS Major_audiencedo;
   ```
3. **Run the application** - it will automatically create tables on first run

### 3. Test Database Connection
```bash
python -c "from database import db; print('Connected:', db.connection.is_connected())"
```

## Default Users

The system automatically creates these test users:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | admin |
| validuser | validpassword | user |
| valid_user | valid_password | user |
| admin_user | admin_password | admin |
| testuser | testpass | user |
| testuser_atss | testpass123 | user |

## Database Features

### Automatic Migrations
The system includes automatic database migrations that:
- Add missing columns to existing tables
- Create necessary indexes for performance
- Update table structures as needed

### Health Monitoring
The system includes database health monitoring:
- Connection status verification
- Table structure validation
- Performance statistics tracking

### API Endpoints
- `GET /api/database/status` - Database status (admin only)

## Troubleshooting

### Connection Issues
1. **Check network connectivity** to `2s6vhs.h.filess.io:61032`
2. **Verify credentials** are correct
3. **Check firewall settings** if applicable

### Database Errors
1. **Check table permissions** for the database user
2. **Verify foreign key constraints** are properly set
3. **Check for duplicate entries** in unique columns

### Performance Issues
1. **Monitor query performance** using database logs
2. **Check index usage** in slow queries
3. **Consider connection pooling** for high traffic

## Security Notes

- Database credentials are hardcoded for this setup
- Consider using environment variables for production
- Ensure SSL connections are enabled if supported
- Regular database backups are recommended

## Maintenance

### Regular Tasks
1. **Monitor database size** and growth
2. **Check for orphaned records** in related tables
3. **Update indexes** based on query patterns
4. **Backup data** regularly

### Performance Optimization
1. **Add indexes** for frequently queried columns
2. **Optimize queries** based on usage patterns
3. **Monitor connection pool** usage
4. **Archive old session data** if needed

## Support

For database-related issues:
1. Check the application logs for error messages
2. Verify database connectivity
3. Run the health check script
4. Contact the database administrator if needed
