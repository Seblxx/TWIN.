# Session Isolation Test Plan - Chrome Testing

## Test Accounts
- **Account 1**: dazrini@gmail.com
- **Account 2**: test2@gmail.com

## Test 1: Logout Functionality
1. Open http://127.0.0.1:5000/intro.html in Chrome
2. Click "Already a member? Sign in"
3. Login with dazrini@gmail.com
4. Open menu (three dots)
5. Verify button shows "LOGOUT" (not "HOME")
6. Click "LOGOUT"
7. Confirm the modal appears with Yes/Cancel buttons
8. Click "Yes"
9. **Expected**: Should redirect to intro.html in logged-out state
10. **Verify**: Button should now show "HOME" when you click menu

## Test 2: Get Started Fresh Session
1. On intro.html, click "Get Started" (do not login)
2. **Expected**: Should go to index.html with blank slate
3. **Verify**: No query in input field, no chat messages, no predictions
4. Open menu - verify button shows "HOME" (not "LOGOUT")
5. **Verify**: Predictions button is OFF/disabled (grayed out)

## Test 3: Modal Styling Consistency
1. From index.html (not logged in), open menu
2. Click "HOME" - should show confirmation modal
3. **Verify**: Modal has same styling as login modal:
   - Blur backdrop
   - Rounded corners (20px)
   - Gradient "Yes" button matching login "Sign In" button
   - Transparent border "Cancel" button
   - Same padding and spacing

## Test 4: Session Isolation - Account 1
1. Go to intro.html, login as **dazrini@gmail.com**
2. In index.html, type query: "What is the weather in NYC?"
3. Click send, get prediction
4. Click star button to save prediction
5. Navigate to predictions.html
6. **Verify**: Should see "What is the weather in NYC?" prediction
7. Note the prediction details for comparison
8. Go back to index.html
9. **Verify**: Query "What is the weather in NYC?" should still be in input field
10. Open menu, click "LOGOUT", confirm "Yes"

## Test 5: Session Isolation - Account 2
1. Should be on intro.html after logout
2. Click "Already a member? Sign in"
3. Login as **test2@gmail.com**
4. **Verify**: Input field should be BLANK (no "What is the weather in NYC?")
5. **Verify**: No chat messages from dazrini account
6. Navigate to predictions.html
7. **Verify**: Should NOT see "What is the weather in NYC?" prediction
8. **Verify**: Should see empty state or only test2's own predictions
9. Go back to index.html
10. Type different query: "Stock price of AAPL today?"
11. Click send, get prediction
12. Click star to save
13. Navigate to predictions.html
14. **Verify**: Should ONLY see "Stock price of AAPL today?" (not NYC weather)

## Test 6: Cross-Account Verification
1. Still logged in as test2@gmail.com
2. Open predictions.html
3. Open browser DevTools (F12), go to Console
4. Try to get Account 1's predictions:
   ```javascript
   // This should fail or return empty for test2
   fetch('http://127.0.0.1:5000/api/predictions/list', {
     headers: {'Authorization': 'Bearer ' + localStorage.getItem('twin_supabase_token')}
   }).then(r=>r.json()).then(console.log)
   ```
5. **Verify**: Should NOT return Account 1's predictions
6. Logout from test2
7. Login as dazrini@gmail.com
8. Navigate to predictions.html
9. **Verify**: Should see "What is the weather in NYC?" (Account 1's prediction)
10. **Verify**: Should NOT see "Stock price of AAPL today?" (Account 2's prediction)

## Test 7: Query Persistence vs Fresh Session
1. Login as dazrini@gmail.com
2. Type in query: "Tell me about Tesla"
3. Do NOT send it, just type it
4. Navigate to predictions.html
5. Click back button to index.html
6. **Verify**: "Tell me about Tesla" should still be in input field
7. Open menu, click "LOGOUT", confirm
8. Should be back at intro.html
9. Click "Get Started" (do not login)
10. **Verify**: Input field should be BLANK (query should NOT persist across logout)

## Success Criteria
✅ All modals use consistent styling (blur, rounded corners, gradient buttons)
✅ Logout redirects to intro.html immediately after clicking Yes
✅ Logout button shows "LOGOUT" when logged in, "HOME" when not logged in
✅ Get Started leads to blank state (no query, no messages, predictions off)
✅ Fresh sessions have empty input field
✅ Account 1 cannot see Account 2's predictions
✅ Account 2 cannot see Account 1's predictions
✅ Query persists when navigating back from predictions (same session)
✅ Query does NOT persist after logout → Get Started (new session)
✅ No cache conflicts between accounts
