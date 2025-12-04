-- Migration: Add user_email and prediction_id columns to predictions table
-- Run this in Supabase SQL Editor

-- Make user_id nullable (since we're using user_email instead)
ALTER TABLE predictions ALTER COLUMN user_id DROP NOT NULL;

-- Add user_email column
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS user_email TEXT;

-- Add prediction_id column  
ALTER TABLE predictions ADD COLUMN IF NOT EXISTS prediction_id TEXT;

-- Create indexes for the new columns
CREATE INDEX IF NOT EXISTS idx_predictions_user_email ON predictions(user_email);
CREATE INDEX IF NOT EXISTS idx_predictions_prediction_id ON predictions(prediction_id);

-- Update RLS policies to allow access by user_email (in addition to user_id)
-- Drop old restrictive policies that require auth.uid()
DROP POLICY IF EXISTS "Users can view own predictions" ON predictions;
DROP POLICY IF EXISTS "Users can insert own predictions" ON predictions;
DROP POLICY IF EXISTS "Users can update own predictions" ON predictions;

-- Create new permissive policies (since we're not using Supabase auth)
CREATE POLICY "Allow all read access" ON predictions
  FOR SELECT USING (true);

CREATE POLICY "Allow all insert access" ON predictions
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow all update access" ON predictions
  FOR UPDATE USING (true);

-- Verify the changes
SELECT 'Migration completed! user_id is now nullable, columns added: user_email, prediction_id' as status;
