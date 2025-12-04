# Backend Testing & Supabase Table Fix

## Issue Found
The `predictions` table in Supabase was created with a different schema that uses Supabase Auth (`user_id UUID`), but your current app uses simple email-based authentication. This mismatch is causing the backend API to fail.

## Solution
You need to add two columns to the existing `predictions` table to support email-based user identification.

### Steps to Fix:

1. **Open Supabase Dashboard**
   - Go to: https://tocuqnqdewhqhbhkbplm.supabase.co
   - Log in to your Supabase account

2. **Open SQL Editor**
   - In the left sidebar, click on "SQL Editor"
   - Click "New Query"

3. **Run Migration SQL**
   - Copy the entire contents of `migrate_predictions_table.sql`
   - Paste into the SQL editor
   - Click "Run" button

4. **Verify Success**
   - You should see: "Migration completed! Columns added: user_email, prediction_id"
   - If you get any errors, send me the error message

### What the Migration Does:
- Adds `user_email TEXT` column to store user emails
- Adds `prediction_id TEXT` column to store prediction IDs
- Creates indexes for faster queries
- Updates security policies to allow access (since we're not using Supabase Auth)

## Alternative: Manual Column Addition

If the migration fails, you can add columns manually:

1. Go to "Table Editor" in Supabase
2. Select `predictions` table
3. Click "Add Column" twice to add:
   - Column name: `user_email`, Type: `text`, Allow nullable: ✓
   - Column name: `prediction_id`, Type: `text`, Allow nullable: ✓
4. Go to "SQL Editor" and run:
   ```sql
   DROP POLICY IF EXISTS "Users can view own predictions" ON predictions;
   DROP POLICY IF EXISTS "Users can insert own predictions" ON predictions;
   DROP POLICY IF EXISTS "Users can update own predictions" ON predictions;
   
   CREATE POLICY "Allow all access" ON predictions FOR ALL USING (true) WITH CHECK (true);
   ```

## After Migration

Once the migration is complete, the backend API will work correctly. Then:

1. Test with curl/PowerShell (I'll do this)
2. Clear Edge cache:
   - Open Edge
   - Press `Ctrl+Shift+Delete`
   - Select "Cached images and files" and "Cookies and other site data"
   - Click "Clear now"
3. Hard refresh: `Ctrl+F5`

## Why Chrome Works But Edge Doesn't

Chrome has the latest JavaScript code cached, while Edge has old code. Both are using localStorage currently (no database yet). Once we fix the database and clear Edge's cache, both browsers will work identically and save to the database.

## Current Status

✅ Backend code updated to use `predictions` table  
⚠️ Database migration needed (manual step required)  
⚠️ Edge cache needs clearing (after migration)  

Let me know once you've run the migration SQL!
