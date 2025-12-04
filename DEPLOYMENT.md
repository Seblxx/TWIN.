# 🚀 Deploy TWIN to Render

This guide will help you deploy your TWIN Stock Assistant application to Render.

## Prerequisites

- A GitHub account with your TWIN repository
- A Render account (sign up at https://render.com)
- Your code pushed to GitHub

## Deployment Steps

### Option 1: Automatic Deployment (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Connect to Render**
   - Go to https://dashboard.render.com
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub repository

3. **Configure the Web Service**
   - **Name**: `twin-stock-assistant` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free` (or upgrade as needed)

4. **Advanced Settings** (Optional)
   - Add environment variables if needed
   - Set Python version to `3.11.0`

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Wait for the build to complete (usually 5-10 minutes)

### Option 2: Using render.yaml (Blueprint)

1. **Push your code with render.yaml**
   ```bash
   git add .
   git commit -m "Add Render blueprint"
   git push origin main
   ```

2. **Deploy via Blueprint**
   - Go to https://dashboard.render.com
   - Click "New +" > "Blueprint"
   - Connect your repository
   - Render will auto-detect the `render.yaml` file
   - Click "Apply" to deploy

## Post-Deployment

### Update Frontend API URLs

After deployment, you'll get a URL like: `https://twin-stock-assistant.onrender.com`

Update the API endpoints in your JavaScript files:

**In `script.js`, replace all instances of:**
```javascript
http://localhost:5000
```

**With your Render URL:**
```javascript
https://twin-stock-assistant.onrender.com
```

### Serve Static Files

For production, you should serve your HTML/CSS/JS files:

1. **Option A**: Host frontend separately on:
   - Netlify (recommended for static sites)
   - Vercel
   - GitHub Pages

2. **Option B**: Serve from Flask (update app.py):
   ```python
   from flask import send_from_directory
   
   @app.route('/')
   def index():
       return send_from_directory('.', 'index.html')
   
   @app.route('/<path:path>')
   def static_files(path):
       return send_from_directory('.', path)
   ```

## Environment Variables (if needed)

Add these in Render Dashboard under "Environment":

- `FLASK_ENV=production`
- `PORT=10000` (Render uses port 10000 by default)

## Troubleshooting

### Build Fails
- Check that `requirements.txt` has all dependencies
- Ensure Python version compatibility
- Review build logs in Render dashboard

### App Crashes
- Check Render logs for error messages
- Verify `gunicorn` is in requirements.txt
- Ensure Flask app is properly initialized

### CORS Issues
- Flask-CORS should handle cross-origin requests
- If issues persist, check CORS configuration in `app.py`

### Free Tier Limitations
- Free instances spin down after 15 minutes of inactivity
- First request after spindown will be slow (30-60 seconds)
- Consider upgrading for production use

## Updating Your Deployment

```bash
git add .
git commit -m "Update description"
git push origin main
```

Render will automatically redeploy when you push to GitHub!

## Alternative: Deploy to Other Platforms

### Heroku
```bash
heroku create twin-stock-assistant
git push heroku main
```

### Railway
1. Connect GitHub repository
2. Railway auto-detects Python app
3. Deploy with one click

### PythonAnywhere
1. Upload code via web interface
2. Set up WSGI configuration
3. Configure static files

## Need Help?

- Render Docs: https://render.com/docs
- Flask Deployment: https://flask.palletsprojects.com/en/latest/deploying/
- GitHub Issues: Create an issue in your repository

---

**Note**: Remember to update API endpoints in your frontend after deployment!
