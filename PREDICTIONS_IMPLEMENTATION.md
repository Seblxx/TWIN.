# User-Specific Predictions Implementation

## Overview
Implemented a backend database system for user-specific predictions while keeping chat history in localStorage for session persistence.

## Architecture

### 1. **Chat History (User Queries)**
- **Storage**: Browser localStorage (session-based)
- **Key**: `twin_messages_basic`, `twin_messages_plus`
- **Persistence**: Stays in browser until manually cleared
- **Purpose**: When you navigate back to index.html, you see all your previous queries/conversation history

### 2. **Saved Predictions (Star Button)**
- **Storage**: Supabase database (account-based)
- **Table**: `user_predictions`
- **Key**: `user_email` (identifies which account owns the prediction)
- **Persistence**: Stored permanently in database, accessible from any device when logged in
- **Fallback**: Guest users still use localStorage

## Setup Instructions

### 1. Create Supabase Table
Run the SQL script in your Supabase SQL Editor:
```bash
# File: create_predictions_table.sql
```

Navigate to: https://supabase.com/dashboard/project/tocuqnqdewhqhbhkbplm/editor

Paste and execute the contents of `create_predictions_table.sql`

### 2. Backend API Endpoints Created

#### Save Prediction
```
POST /api/predictions/save
Body: {
  "userEmail": "user@example.com",
  "id": "pred_123",
  "stock": "AAPL",
  "duration": "1 week",
  "lastClose": 150.25,
  "predictedPrice": 155.50,
  "method": "random_forest",
  "delta": 5.25,
  "pct": 3.49,
  "timestamp": "2025-12-01T..."
}
```

#### Get User Predictions
```
GET /api/predictions/user/{user_email}
Response: {
  "success": true,
  "predictions": [...]
}
```

### 3. Frontend Updates

#### script.js
- `savePrediction()` - Now saves to backend for logged-in users, localStorage for guests
- `getSavedPredictions()` - Returns Promise, fetches from backend or localStorage
- `showLeaderboard()` - Now async, handles Promise-based predictions

#### predictions.js
- `getPredictions()` - Now async, fetches from backend
- `loadPredictions()` - Now async, awaits predictions

## User Flow

### Guest User (Not Logged In)
1. Enter query → Saved to localStorage
2. Click star → Prediction saved to localStorage
3. Visit predictions.html → Loads from localStorage
4. Navigate back to index.html → Chat history still there

### Logged-In User
1. Enter query → Saved to localStorage (chat history)
2. Click star → Prediction saved to **Supabase database** with user_email
3. Visit predictions.html → Loads from **database** (user's predictions only)
4. Navigate back to index.html → Chat history still there
5. **Different device/browser** → Predictions sync via database (chat history is device-specific)

## Testing

### Test 1: Guest User Flow
```bash
# Open incognito window
# Navigate to http://127.0.0.1:5000/index.html
# Don't log in
# Enter: "AAPL in 1 week"
# Click star button
# Navigate to predictions.html
# Should see prediction (from localStorage)
```

### Test 2: Logged-In User Flow
```bash
# Open normal browser
# Log in with email (e.g., user@example.com)
# localStorage.setItem('twin_user_email', 'user@example.com')
# Enter: "TSLA in 2 weeks"
# Click star button
# Check network tab → should see POST to /api/predictions/save
# Navigate to predictions.html
# Check network tab → should see GET from /api/predictions/user/user@example.com
# Should see prediction
```

### Test 3: Different Accounts
```bash
# User A logs in
# Saves predictions for AAPL, TSLA
# User A logs out
# User B logs in
# Should see NO predictions (User B's account is empty)
# User B saves predictions for MSFT
# User A logs back in
# Should see AAPL, TSLA (not MSFT)
```

## Database Schema

```sql
user_predictions (
  id BIGSERIAL PRIMARY KEY,
  user_email TEXT NOT NULL,           -- Which account owns this
  prediction_id TEXT NOT NULL,        -- Unique ID for this prediction
  stock TEXT NOT NULL,                -- Stock symbol (AAPL, TSLA, etc.)
  duration TEXT,                      -- "1 week", "2 months", etc.
  last_close DECIMAL(10, 2),         -- Price when predicted
  predicted_price DECIMAL(10, 2),    -- What we predicted
  method TEXT,                        -- ML method used
  delta DECIMAL(10, 2),              -- $ change
  pct DECIMAL(10, 2),                -- % change
  timestamp TIMESTAMPTZ,              -- When prediction was made
  feedback TEXT,                      -- "yes"/"no" user feedback
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)
```

## Current Status
✅ Backend API endpoints created
✅ Frontend updated to use backend for logged-in users
✅ Fallback to localStorage for guest users
✅ Chat history remains in localStorage (session-based)
⏳ Supabase table needs to be created (run SQL script)
⏳ User authentication needs to be implemented (currently using localStorage for user_email)

## Next Steps
1. Run `create_predictions_table.sql` in Supabase
2. Implement proper user authentication (login/signup flow)
3. Set `twin_user_email` in localStorage when user logs in
4. Test with multiple accounts
