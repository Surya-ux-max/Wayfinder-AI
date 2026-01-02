# Wayfinder Backend Deployment

## Quick Deploy Options

### 1. Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Select the `backend` folder
4. Add environment variables:
   - `GEMINI_API_KEY`
   - `MONGODB_URI` 
   - `JWT_SECRET`
5. Deploy automatically

### 2. Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repo
4. Root Directory: `backend`
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python app.py`
7. Add environment variables

### 3. Heroku
```bash
heroku create wayfinder-backend
heroku config:set GEMINI_API_KEY=your_key
heroku config:set MONGODB_URI=your_mongodb_uri
heroku config:set JWT_SECRET=your_secret
git subtree push --prefix backend heroku main
```

## Environment Variables Needed
- `GEMINI_API_KEY`: Your Google Gemini API key
- `MONGODB_URI`: MongoDB connection string (use MongoDB Atlas)
- `JWT_SECRET`: Random secret for JWT tokens

## MongoDB Setup
1. Create free cluster at [MongoDB Atlas](https://cloud.mongodb.com)
2. Get connection string
3. Replace `<password>` with your password
4. Use this as `MONGODB_URI`

## Update Frontend
After deployment, update `BASE_URL` in frontend `script.js`:
```javascript
const BASE_URL = "https://your-backend-url.com";
```