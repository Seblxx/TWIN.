"""
TWIN Authentication with Supabase - Quick Setup
This is the EASIEST authentication solution!

Supabase includes:
- Authentication (email, Google, GitHub, etc.)
- Database (PostgreSQL) for storing predictions
- Real-time updates
- Free tier: 50,000 monthly active users
"""

# Step 1: Install Supabase
# pip install supabase

# Step 2: Sign up at https://supabase.com/
# Create a new project and get your credentials

# Step 3: Add to app.py
from supabase import create_client, Client

SUPABASE_URL = "your-project-url"
SUPABASE_KEY = "your-anon-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Step 4: Create predictions table in Supabase
"""
SQL to run in Supabase SQL Editor:

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

-- Enable Row Level Security
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own predictions
CREATE POLICY "Users can view own predictions" ON predictions
  FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own predictions
CREATE POLICY "Users can insert own predictions" ON predictions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own predictions
CREATE POLICY "Users can update own predictions" ON predictions
  FOR UPDATE USING (auth.uid() = user_id);
"""

# Step 5: Add authentication endpoints to app.py
@app.post("/auth/signup")
def signup():
    """Sign up a new user"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return jsonify({"success": True, "user": response.user})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.post("/auth/login")
def login():
    """Log in a user"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return jsonify({
            "success": True,
            "user": response.user,
            "session": response.session
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.post("/api/predictions")
def save_prediction_db():
    """Save prediction to database"""
    # Get token from Authorization header
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return jsonify({"error": "No token provided"}), 401
    
    try:
        # Verify token and get user
        user = supabase.auth.get_user(token)
        user_id = user.user.id
        
        # Get prediction data
        pred = request.get_json()
        
        # Save to database
        result = supabase.table('predictions').insert({
            'user_id': user_id,
            'stock': pred['stock'],
            'duration': pred['duration'],
            'last_close': pred['lastClose'],
            'predicted_price': pred['predictedPrice'],
            'method': pred['method'],
            'delta': pred['delta'],
            'pct': pred['pct'],
            'timestamp': pred['timestamp']
        }).execute()
        
        return jsonify({"success": True, "data": result.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/api/predictions")
def get_predictions_db():
    """Get user's predictions from database"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return jsonify({"error": "No token provided"}), 401
    
    try:
        user = supabase.auth.get_user(token)
        user_id = user.user.id
        
        # Get predictions from database
        result = supabase.table('predictions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
        
        return jsonify({"predictions": result.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Frontend JavaScript for intro.html
"""
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script>
  const SUPABASE_URL = 'your-project-url';
  const SUPABASE_ANON_KEY = 'your-anon-key';
  
  const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  
  // Sign up
  async function signUp(email, password) {
    const { data, error } = await supabase.auth.signUp({
      email: email,
      password: password
    });
    
    if (error) {
      alert(error.message);
    } else {
      alert('Check your email for verification link!');
    }
  }
  
  // Login
  async function login(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email,
      password: password
    });
    
    if (error) {
      alert(error.message);
    } else {
      localStorage.setItem('twin_user_logged_in', 'true');
      localStorage.setItem('twin_user_email', email);
      localStorage.setItem('twin_supabase_token', data.session.access_token);
      window.location.href = 'index.html';
    }
  }
  
  // Check if already logged in
  supabase.auth.getSession().then(({ data: { session } }) => {
    if (session) {
      localStorage.setItem('twin_user_logged_in', 'true');
      localStorage.setItem('twin_user_email', session.user.email);
      localStorage.setItem('twin_supabase_token', session.access_token);
      window.location.href = 'index.html';
    }
  });
  
  // Logout
  async function logout() {
    await supabase.auth.signOut();
    localStorage.clear();
    window.location.href = 'intro.html';
  }
</script>
"""

print("""
=== SUPABASE SETUP COMPLETE ===

Next steps:
1. Install: pip install supabase
2. Sign up at https://supabase.com/
3. Replace 'your-project-url' and 'your-anon-key' in the code
4. Run the SQL to create the predictions table
5. Test signup and login!

Benefits:
✅ Real authentication (not localStorage)
✅ User data persists across devices
✅ Predictions saved to real database
✅ Email verification included
✅ Password reset built-in
✅ Free tier is generous
""")
