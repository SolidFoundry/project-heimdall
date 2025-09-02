# Database Schema Documentation

## Overview

This directory contains the database schema files for Project Heimdall. The schema includes all necessary tables for the AI intent advertising engine, including user management, product catalog, advertising campaigns, and recommendation systems.

## Schema Files

### `001_initial_schema.sql`

This is the complete database schema file that creates all necessary tables and inserts sample data for testing. It includes:

#### Core Tables:
- **schema_migrations** - Tracks applied database migrations
- **chat_sessions** - Stores chat session metadata
- **chat_messages** - Stores individual chat messages
- **user_profiles** - User profile information and preferences
- **user_behaviors** - Tracks user behavior events
- **user_sessions** - Web session tracking

#### Business Tables:
- **product_categories** - Product category hierarchy
- **products** - Product catalog with detailed information
- **ads** - Advertisement campaigns and creatives
- **intent_analyses** - Analysis of user intent
- **recommendations** - Generated recommendations
- **ad_recommendations** - Specific ad recommendations with tracking
- **ab_tests** - A/B test variant assignments

#### Features:
- All tables include proper indexes for performance
- Automatic timestamp management with triggers
- Foreign key constraints for data integrity
- Sample data for testing and development

## Setup Instructions

### For New Development Environment

1. **Create Database**
   ```bash
   # Create PostgreSQL database
   createdb heimdall_db
   ```

2. **Apply Schema**
   ```bash
   # Apply the complete schema
   psql -d heimdall_db -f sql/001_initial_schema.sql
   ```

3. **Verify Setup**
   ```bash
   # Check database structure
   python check_db_structure.py
   ```

### For Existing Environment

If you already have a running database and want to ensure all tables exist:

```bash
# The schema file uses IF NOT EXISTS, so it's safe to run on existing databases
psql -d heimdall_db -f sql/001_initial_schema.sql
```

## Sample Data

The schema includes sample data for testing:

- **8 Product Categories** - 电子产品, 服装, 家居, 运动户外, 美妆护肤, 食品饮料, 图书音像, 母婴用品
- **8 Products** - Including iPhone 15 Pro, MacBook Air, Nike shoes, etc.
- **2 User Profiles** - English test user (user_english_test) and Chinese test user (user_test_profile)
- **3 Ads** - Sample advertising campaigns
- **User Behaviors** - Sample user interaction data
- **Intent Analyses** - Sample intent analysis results

## Testing Users

For testing the recommendation system and user features:

1. **English Test User**: `user_english_test`
   - Profile: John Doe, 28, male, New York
   - Interests: 电子产品, 运动
   - Activity Level: 15
   - Price Range: 1000-10000

2. **Chinese Test User**: `user_test_profile`
   - Profile: 测试用户, 25, female, 北京
   - Interests: 美妆护肤, 服装
   - Activity Level: 8
   - Price Range: 100-2000

## Database Requirements

- PostgreSQL 12 or higher
- UTF-8 encoding
- Recommended connection pool settings:
  - Pool size: 20
  - Max overflow: 30
  - Pool timeout: 30 seconds
  - Pool recycle: 3600 seconds

## Environment Variables

Ensure your `.env` file has the correct database configuration:

```
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=heimdall_db
```

## Troubleshooting

If you encounter any issues:

1. Check database connection in `.env` file
2. Ensure PostgreSQL is running
3. Verify database exists
4. Check user permissions
5. Run `python check_db_structure.py` to verify setup