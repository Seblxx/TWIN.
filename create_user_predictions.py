"""
Create user_predictions table in Supabase using Python
"""
from supabase import create_client, Client

# Supabase credentials
url = 'https://tocuqnqdewhqhbhkbplm.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3VxbnFkZXdocWhiaGticGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMDE2MzgsImV4cCI6MjA3OTU3NzYzOH0.vWfItFkQpHA7Is-KX4eQalI-wxUAJcejPAvy7NDQHvc'

supabase: Client = create_client(url, key)

print("✓ Connected to Supabase\n")

# SQL to create the table
create_table_sql = """
CREATE TABLE IF NOT EXISTS user_predictions (
  id BIGSERIAL PRIMARY KEY,
  user_email TEXT NOT NULL,
  prediction_id TEXT NOT NULL,
  stock TEXT NOT NULL,
  duration TEXT,
  last_close DECIMAL(10, 2),
  predicted_price DECIMAL(10, 2),
  method TEXT,
  delta DECIMAL(10, 2),
  pct DECIMAL(10, 2),
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  feedback TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_predictions_email ON user_predictions(user_email);
CREATE INDEX IF NOT EXISTS idx_user_predictions_timestamp ON user_predictions(timestamp DESC);

ALTER TABLE user_predictions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for now" ON user_predictions
  FOR ALL
  USING (true)
  WITH CHECK (true);
"""

print("Attempting to create user_predictions table...")
print("NOTE: You need to run the SQL in create_predictions_table.sql in your Supabase SQL Editor")
print("The Python Supabase client can't execute DDL statements directly.")
print("\nSteps:")
print("1. Go to your Supabase dashboard: https://tocuqnqdewhqhbhkbplm.supabase.co")
print("2. Navigate to SQL Editor")
print("3. Paste the contents of 'create_predictions_table.sql'")
print("4. Click 'Run' to execute")
print("\nOR use the PostgreSQL connection string if you have psql installed.")
