# TWIN Authentication Setup Guide

## Current Status
- ✅ Basic localStorage-based login (insecure, demo only)
- ❌ No actual authentication
- ❌ No user data persistence
- ❌ No password hashing

## Recommended Solution: Auth0

Auth0 is the easiest and most secure option for authentication. Here's why:
- Free tier: Up to 7,000 active users
- Built-in social login (Google, GitHub, etc.)
- Secure password hashing and storage
- Easy to implement
- Handles signup, login, password reset automatically

## Implementation Steps

### 1. Sign up for Auth0
1. Go to https://auth0.com/
2. Create a free account
3. Create a new application (Single Page Application)
4. Note your Domain and Client ID

### 2. Install Auth0 SDK
```bash
# No npm needed - we'll use CDN
```

### 3. Update HTML Files

Add to `intro.html` (replace existing login):
```html
<script src="https://cdn.auth0.com/js/auth0-spa-js/2.0/auth0-spa-js.production.js"></script>
<script>
  let auth0Client;

  async function initAuth0() {
    auth0Client = await auth0.createAuth0Client({
      domain: 'YOUR_AUTH0_DOMAIN',
      clientId: 'YOUR_CLIENT_ID',
      authorizationParams: {
        redirect_uri: window.location.origin + '/index.html'
      }
    });

    // Check if user is authenticated
    const isAuthenticated = await auth0Client.isAuthenticated();
    if (isAuthenticated) {
      const user = await auth0Client.getUser();
      localStorage.setItem('twin_user_logged_in', 'true');
      localStorage.setItem('twin_user_email', user.email);
      window.location.href = 'index.html';
    }
  }

  async function login() {
    await auth0Client.loginWithRedirect();
  }

  async function signup() {
    await auth0Client.loginWithRedirect({
      authorizationParams: {
        screen_hint: 'signup'
      }
    });
  }

  window.addEventListener('DOMContentLoaded', initAuth0);
</script>
```

### 4. Update Backend (app.py)

Add user data storage:
```python
from functools import wraps
import jwt
from jwt import PyJWKClient

# Auth0 configuration
AUTH0_DOMAIN = 'YOUR_AUTH0_DOMAIN'
AUTH0_API_AUDIENCE = 'YOUR_API_IDENTIFIER'

# User predictions storage (use database in production)
user_data = {}

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            jwks_client = PyJWKClient(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=['RS256'],
                audience=AUTH0_API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            
            request.user_id = payload['sub']
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
    
    return decorated

@app.post('/api/save_prediction')
@requires_auth
def save_user_prediction():
    user_id = request.user_id
    prediction = request.get_json()
    
    if user_id not in user_data:
        user_data[user_id] = {'predictions': []}
    
    user_data[user_id]['predictions'].append(prediction)
    
    # In production, save to database
    # db.predictions.insert_one({'user_id': user_id, 'prediction': prediction})
    
    return jsonify({'success': True})

@app.get('/api/get_predictions')
@requires_auth
def get_user_predictions():
    user_id = request.user_id
    predictions = user_data.get(user_id, {}).get('predictions', [])
    return jsonify({'predictions': predictions})
```

### 5. Install Required Python Packages
```bash
pip install PyJWT cryptography
```

### 6. Frontend Updates

Update fetch calls to include auth token:
```javascript
// Get token from Auth0
const token = await auth0Client.getTokenSilently();

// Include in API calls
fetch('http://localhost:5000/api/save_prediction', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(prediction)
});
```

## Alternative: Supabase (Even Easier!)

Supabase is another great option that includes:
- Authentication (email, social, etc.)
- Database (PostgreSQL)
- Real-time subscriptions
- Storage

Setup is similar but includes built-in database for storing predictions.

## Migration Plan

1. **Phase 1: Setup Auth0/Supabase** (1-2 hours)
   - Create account
   - Configure application
   - Get credentials

2. **Phase 2: Update Frontend** (2-3 hours)
   - Replace localStorage login with Auth0
   - Update intro.html with real login
   - Add token management

3. **Phase 3: Update Backend** (2-3 hours)
   - Add JWT verification
   - Create user-specific endpoints
   - Store predictions per user

4. **Phase 4: Testing** (1-2 hours)
   - Test signup flow
   - Test login flow
   - Test prediction saving per user
   - Test logout

## Total Time Estimate: 6-10 hours

## Next Steps

Would you like me to:
1. Implement Auth0 integration now? (Need your Auth0 credentials)
2. Implement Supabase instead? (Even easier, includes database)
3. Create a simple backend-only authentication? (Less secure but faster)

Let me know which option you prefer!
