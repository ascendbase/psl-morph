# Setting up DATABASE_URL for Railway PostgreSQL

## Steps to get the DATABASE_URL:

1. **Go to your Railway dashboard**: https://railway.com/project/074473a1-9123-4cb6-bc3d-1d570209bbb2

2. **Click on the PostgreSQL service** (not the main psl-morph service)

3. **Go to the Variables tab** in the PostgreSQL service

4. **Look for one of these variables:**
   - `DATABASE_URL`
   - `POSTGRES_URL` 
   - `DATABASE_PRIVATE_URL`

5. **Copy the full URL** - it should look something like:
   ```
   postgresql://postgres:password@ballast.proxy.rlwy.net:12345/railway
   ```

6. **Add it to your main service** using this command:
   ```bash
   railway variables --set DATABASE_URL="postgresql://postgres:password@ballast.proxy.rlwy.net:12345/railway"
   ```

## Alternative: Manual Construction

If you can't find the DATABASE_URL, you can construct it manually using:
- Host: `ballast.proxy.rlwy.net`
- Port: (usually 5432 or a custom port)
- Database: `railway`
- Username: `postgres`
- Password: (you'll need to get this from Railway)

The format is:
```
postgresql://username:password@host:port/database
```

## After setting the DATABASE_URL:

1. Run the database initialization:
   ```bash
   railway run python init_database.py
   ```

2. Redeploy the app:
   ```bash
   railway up --detach
