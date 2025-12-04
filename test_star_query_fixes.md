# Manual Test Plan - Star Unstar & Query Persistence

## ✅ Backend Tests - ALL PASSED
```
✓ Authentication works for both accounts
✓ Predictions save to database  
✓ User isolation enforced (no cross-account access)
✓ Unauthorized requests rejected
✓ Invalid tokens rejected
✓ Feedback system works
```

## Frontend Fixes Implemented

### Fix 1: Query Persistence
**Issue:** Query gets cleared when navigating away from predictions page
**Solution:** Added localStorage persistence
- On page load: Restore `twin_last_query` from localStorage
- On input change: Save query to localStorage (debounced 500ms)
- Query now persists across navigation

### Fix 2: Star Unstar Toggle
**Issue:** Can't click starred button to remove prediction
**Solution:** Added saved state check on button creation
- On star button render: Check `getSavedPredictions()` for matching ID
- If found: Set button to disabled/filled star state
- Click handler already supports unstar (was working but button state was wrong)

## Manual Testing Steps

### Test 1: Query Persistence
1. Login to account
2. Type query "Tesla in 5 days" in input field
3. Submit query and view results
4. Navigate to predictions page (menu → PREDICTIONS)
5. Navigate back to index.html
6. **Expected:** Query "Tesla in 5 days" still in input field
7. **Previous behavior:** Input field empty

### Test 2: Star/Unstar Toggle
1. Login to account
2. Type query "Apple in 3 days" and submit
3. Click star button (should fill and disable)
4. **NEW:** Click the filled star again
5. **Expected:** Star becomes empty, prediction removed
6. Check predictions page - should not show Apple
7. Go back, submit same query again
8. **Expected:** Star is empty (can star again)

### Test 3: Multi-Account Isolation
1. Login Account 1 (dazrini@gmail.com)
2. Query "Tesla" and star it
3. Go to predictions - should see Tesla
4. Logout
5. Login Account 2 (test2@gmail.com)
6. Go to predictions
7. **Expected:** Empty (Account 2 doesn't see Account 1's predictions)
8. Query "Microsoft" and star it
9. Go to predictions - should see ONLY Microsoft

## Files Modified
- `script.js` lines 1319-1339: Added query persistence (restore & save)
- `script.js` lines 1716-1732: Added saved state check for star buttons
