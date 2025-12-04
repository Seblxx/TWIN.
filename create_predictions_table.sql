-- Create user_predictions table in Supabase
-- Run this SQL in your Supabase SQL Editor

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

-- Create index for faster lookups by user email
CREATE INDEX IF NOT EXISTS idx_user_predictions_email ON user_predictions(user_email);

-- Create index for timestamp sorting
CREATE INDEX IF NOT EXISTS idx_user_predictions_timestamp ON user_predictions(timestamp DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE user_predictions ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to see only their own predictions
-- Note: This requires authentication. For now, we'll allow all operations
-- You should implement proper authentication and update these policies
CREATE POLICY "Allow all operations for now" ON user_predictions
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Optional: Add a trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_predictions_updated_at BEFORE UPDATE
    ON user_predictions FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Verify table creation
SELECT 'Table user_predictions created successfully!' as status;
