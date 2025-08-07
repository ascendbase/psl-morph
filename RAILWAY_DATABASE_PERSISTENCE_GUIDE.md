# Railway Database Persistence Guide

## Problem
Railway rebuilds the database on each deployment, causing all user data to be lost. This happens because Railway treats the SQLite database file as part of the application code rather than persistent data.

## Solution: Use Railway PostgreSQL Database

### Step 1: Add PostgreSQL Database to Railway Project

1. **Go to your Railway dashboard**
2. **Click on your project**
3. **Click "New Service" → "Database" → "Add PostgreSQL"**
4. **Railway will automatically create a PostgreSQL database**

### Step 2: Update Environment Variables

Railway will automatically create these environment variables for your PostgreSQL database:
- `DATABASE_URL` (this will be the PostgreSQL connection string)
- `PGHOST`
- `PGPORT` 
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

### Step 3: Update Your App Configuration

Update your `config.py` to use PostgreSQL instead of SQLite:

```python
import os

# Database Configuration
if os.environ.get('RAILWAY_ENVIRONMENT'):
    # Production on Railway - use PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Fix for newer SQLAlchemy versions
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    # Local development - use SQLite
    DATABASE_URL = 'sqlite:///instance/app.db'
```

### Step 4: Install PostgreSQL Dependencies

Add to your `requirements.txt`:
```
psycopg2-binary==2.9.7
```

### Step 5: Update Railway Deployment

Your Railway deployment will now:
1. **Keep the database persistent** across deployments
2. **Automatically backup** your data
3. **Scale better** with more users
4. **Support concurrent connections**

### Step 6: Migration Script

Create a one-time migration script to move existing data:

```python
# migrate_to_postgres.py
import os
import sqlite3
from sqlalchemy import create_engine
from models import User, Generation, Transaction

def migrate_sqlite_to_postgres():
    # Connect to old SQLite database
    sqlite_conn = sqlite3.connect('instance/app.db')
    
    # Connect to new PostgreSQL database
    postgres_url = os.environ.get('DATABASE_URL')
    postgres_engine = create_engine(postgres_url)
    
    # Migration logic here...
```

## Benefits of PostgreSQL on Railway

✅ **Persistent Data**: Database survives deployments
✅ **Automatic Backups**: Railway handles backups
✅ **Better Performance**: Optimized for web applications  
✅ **Concurrent Users**: Supports multiple simultaneous users
✅ **Scalability**: Can handle growth in users and data
✅ **ACID Compliance**: Better data integrity
✅ **Advanced Features**: Full-text search, JSON support, etc.

## Alternative: Railway Volume Mounting (Not Recommended)

Railway also supports volume mounting for SQLite, but PostgreSQL is the better solution for production web applications.

## Testing the Fix

1. **Deploy with PostgreSQL**
2. **Create test users and data**
3. **Deploy a code change**
4. **Verify data persists**

## Rollback Plan

If issues occur:
1. **Keep the SQLite version** in a separate branch
2. **Railway allows easy rollbacks** to previous deployments
3. **Database backups** are available in Railway dashboard

---

**Next Steps:**
1. Add PostgreSQL service to Railway project
2. Update config.py for PostgreSQL
3. Add psycopg2-binary to requirements.txt
4. Deploy and test persistence
