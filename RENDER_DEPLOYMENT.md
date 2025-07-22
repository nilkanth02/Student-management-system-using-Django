# Deploy Student Management System to Render.com

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository

Make sure all files are committed to your Git repository:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Connect your GitHub repository

### 3. Deploy Using Blueprint (Recommended)

1. In Render Dashboard, click **"New +"**
2. Select **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Click **"Apply"**

### 4. Manual Deployment (Alternative)

If blueprint doesn't work, deploy manually:

#### Create PostgreSQL Database:
1. Click **"New +"** → **"PostgreSQL"**
2. Name: `student-management-db`
3. Database Name: `student_management`
4. User: `student_management_user`
5. Click **"Create Database"**

#### Create Web Service:
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `student-management-system`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn student_management.wsgi:application`
   - **Plan**: Free

#### Set Environment Variables:
1. In your web service settings, go to **"Environment"**
2. Add these variables:
   ```
   DATABASE_URL = [Copy from your PostgreSQL database]
   SECRET_KEY = [Generate a random secret key]
   DEBUG = False
   PYTHON_VERSION = 3.11.9
   ```

### 5. Generate Secret Key

Generate a secure secret key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Deploy

1. Click **"Create Web Service"**
2. Render will automatically build and deploy your app
3. Wait for the build to complete (5-10 minutes)

## 🔧 Troubleshooting

### Build Fails?

1. **Check build logs** in Render dashboard
2. **Common issues**:
   - Missing dependencies in `requirements.txt`
   - Build script permissions: `chmod +x build.sh`
   - Python version mismatch

### Database Connection Issues?

1. **Verify DATABASE_URL** is correctly set
2. **Check PostgreSQL database** is running
3. **Ensure migrations ran** during build

### Static Files Not Loading?

1. **Check STATIC_ROOT** setting in `settings.py`
2. **Verify WhiteNoise** is in middleware
3. **Run collectstatic** in build script

## 📱 Access Your Deployed App

Once deployed, you'll get a URL like:
`https://student-management-system.onrender.com`

### Default Access:
- **Dashboard**: `https://your-app.onrender.com/`
- **Admin**: `https://your-app.onrender.com/admin/`
- **API**: `https://your-app.onrender.com/api/api/`

### Create Superuser (After Deployment):

1. Go to your web service in Render
2. Click **"Shell"** tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```

## 🎯 Important Notes

### Free Tier Limitations:
- **Sleep after 15 minutes** of inactivity
- **750 hours/month** limit
- **Slower cold starts**

### For Production:
- Upgrade to paid plan for better performance
- Set up custom domain
- Configure proper ALLOWED_HOSTS
- Enable SSL (automatic on Render)

## 🔐 Security Checklist

- ✅ DEBUG = False
- ✅ Strong SECRET_KEY
- ✅ HTTPS enabled
- ✅ Database secured
- ✅ Static files served properly

## 📞 Support

If deployment fails:
1. Check Render build logs
2. Verify all files are committed
3. Test locally first: `python manage.py runserver`
4. Check Render documentation

---

**Your Student Management System will be live and accessible to recruiters worldwide! 🌍**
