# 🚀 TWIN - Supabase Authentication Setup

## ✅ Installation Complete!

Supabase has been integrated into your TWIN app. Follow these simple steps to activate it:

---

## 📋 Step-by-Step Setup (15 minutes)

### Step 1: Create Supabase Account
1. Go to https://supabase.com/
2. Click "Start your project"
3. Sign up with GitHub (easiest) or email
4. Create a new project:
   - Name: `TWIN`
   - Database Password: (create a strong password - save it!)
   - Region: Choose closest to you
   - Click "Create new project"
   - Wait 2-3 minutes for setup

### Step 2: Get Your Credentials
1. In your Supabase project dashboard, click "⚙️ Settings" (bottom left)
2. Click "API" in the left sidebar
3. Copy two values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon/public key** (long string starting with `eyJ...`)

### Step 3: Add Credentials to TWIN

Open `app.py` and find these lines (around line 11-12):
```python
SUPABASE_URL = os.getenv('SUPABASE_URL', 'YOUR_SUPABASE_URL_HERE')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'YOUR_SUPABASE_ANON_KEY_HERE')
```

Replace with:
```python
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your-long-anon-key-here')
```

### Step 4: Create Database Table
1. In Supabase dashboard, click "📊 Table Editor" (left sidebar)
2. Click "SQL Editor" tab at the top
3. Click "+ New query"
4. Paste this SQL:

```sql
-- Create predictions table
CREATE TABLE predictions (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users NOT NULL,
  stock TEXT NOT NULL,
  duration TEXT NOT NULL,
  last_close DECIMAL NOT NULL,
  predicted_price DECIMAL NOT NULL,
  method TEXT NOT NULL,
  delta DECIMAL NOT NULL,
  pct DECIMAL NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  feedback TEXT,
  feedback_timestamp TIMESTAMPTZ,
  inaccuracy_type TEXT,
  inaccuracy_value DECIMAL,
  inaccuracy_notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own predictions
CREATE POLICY "Users view own predictions" ON predictions
  FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own predictions
CREATE POLICY "Users insert own predictions" ON predictions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own predictions
CREATE POLICY "Users update own predictions" ON predictions
  FOR UPDATE USING (auth.uid() = user_id);
```

5. Click "Run" (or press Ctrl+Enter)
6. You should see "Success. No rows returned"

### Step 5: Restart Your Server
```bash
# Stop the current server (Ctrl+C)
python app.py
```

---

## 🎉 You're Done!

Now you have **REAL authentication**:

### ✅ What Works Now:
- **Real signup**: Users create accounts with email verification
- **Real login**: Secure password authentication
- **Password reset**: Users can reset forgotten passwords
- **Session management**: Users stay logged in
- **Secure**: Passwords are hashed, not stored in plain text

### 🧪 Test It:
1. Go to `http://127.0.0.1:5000/intro.html`
2. Click "Sign In" → "Sign up"
3. Enter email and password (min 6 characters)
4. Check your email for verification link
5. Click verification link
6. Login with your credentials
7. You're now using real authentication!

---

## 🔒 Security Features:
- ✅ Passwords encrypted (bcrypt)
- ✅ Email verification required
- ✅ Session tokens expire
- ✅ Row Level Security (users only see their own data)
- ✅ HTTPS ready
- ✅ GDPR compliant

---

## 🆘 Troubleshooting:

**"Supabase not configured" in console:**
- Make sure you replaced the credentials in `app.py`
- Restart the Flask server

**"Invalid login credentials":**
- Check email is verified (check spam folder)
- Password must be at least 6 characters
- Email must be valid

**"Failed to fetch config":**
- Make sure Flask server is running
- Check http://127.0.0.1:5000/api/config returns your Supabase URL

---

## 📚 Next Steps:

### Want to save predictions to database?
The table is ready! Just need to update the save prediction function to use Supabase instead of localStorage.

### Want social login (Google, GitHub)?
Supabase supports it! Go to Authentication → Providers in your dashboard.

### Want to customize email templates?
Go to Authentication → Email Templates in your dashboard.

---

## 💡 Demo Mode:
If you don't set up Supabase credentials, TWIN will run in demo mode with localStorage (current behavior). This is fine for testing but not secure for production.

---

Need help? The Supabase docs are excellent: https://supabase.com/docs
