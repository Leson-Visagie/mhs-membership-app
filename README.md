# 🎓 Middies Klub Membership System - COMPLETE WORKING SYSTEM

**Everything you need to run the membership system from start to finish.**

## 📁 What's Included

```
middies-klub-system/
├── static/
│   └── index.html          ← Frontend (complete, working)
├── server.py               ← Backend (complete, working)
├── add_admin.py            ← Admin setup script
├── requirements.txt        ← Dependencies
└── README.md              ← This file
```

## 🚀 Complete Setup (Step-by-Step)

### Step 1: Extract Files

1. Download the `middies-klub-system` folder
2. Put it somewhere easy to find (e.g., Desktop or Documents)
3. Open PowerShell or Command Prompt
4. Navigate to the folder:
   ```
   cd "C:\Users\YourName\Documents\middies-klub-system"
   ```

### Step 2: Install Requirements

```bash
pip install -r requirements.txt
```

You should see:
```
Successfully installed Flask-3.0.0 flask-cors-4.0.0 ...
```

### Step 3: Start Server (Creates Database)

```bash
python server.py
```

You should see:
```
✅ Database initialized successfully!
============================================================
🎓 School Membership System Server
============================================================
✅ Server starting on http://localhost:5000
...
✅ Ready to accept connections
```

**IMPORTANT:** Keep this window open! The server must stay running.

### Step 4: Add First Admin (New PowerShell Window)

Open a **NEW** PowerShell window (don't close the server!):

```bash
cd "C:\Users\YourName\Documents\middies-klub-system"
python add_admin.py
```

Enter your details:
```
Email address: lesonvisagie@gmail.com
First name: Leson
Surname: Visagie
Member number (e.g., M0001): M9999
```

You should see:
```
✅ Admin created successfully!
============================================================
Login Credentials:
============================================================
Email:    lesonvisagie@gmail.com
Password: lesonvisagie@gmail.com
```

### Step 5: Access the System

Open your browser and go to:
```
http://localhost:5000
```

### Step 6: Login

- Email: lesonvisagie@gmail.com
- Password: lesonvisagie@gmail.com

You should now see the member dashboard!

### Step 7: Import Your Excel

1. Click **"Admin"** button (top right)
2. Scroll down to "Import Member Data"
3. Drag your `MiddiesKlub__Responses_.xlsx` file or click to upload
4. Wait for "✅ Imported X members successfully!"

## ✅ Testing Everything Works

### Test 1: Check Admin Dashboard
- After login, click "Admin"
- You should see statistics
- You should see members table (empty until you import)

### Test 2: Import Excel
- Upload your Excel file
- Should show success message
- Members table should now have data

### Test 3: Test Member Login
- Logout (button in top right)
- Login with a member's email from Excel
- Password is their email
- Should see their membership card with QR code

### Test 4: Test Scanner (Admin Only)
- Login as admin
- Click "Scanner"
- Click "Start Scanner"
- Allow camera access
- Point at QR code
- Should show access granted/denied

## 🌐 Access from Phones/Tablets

### Same WiFi Network

1. **Find your computer's IP address:**

   Windows PowerShell:
   ```
   ipconfig
   ```
   Look for: `IPv4 Address. . . . . . . . . . . : 192.168.X.X`

2. **On phone/tablet:**
   - Connect to same WiFi as computer
   - Open browser
   - Go to: `http://192.168.X.X:5000`
   - Example: `http://192.168.1.100:5000`

3. **Login:**
   - Use your email from Excel
   - Password is your email

4. **Save to Home Screen:**
   - iPhone: Safari → Share → Add to Home Screen
   - Android: Chrome → Menu → Add to Home Screen

## 📊 Your Excel Format (Auto-Configured)

The system reads these columns from your Google Form export:

| Column Name | Used For |
|-------------|----------|
| Name & Surname | Split into First + Last name |
| Email Adress | Login email |
| Contact Number | Phone |
| Membership Type | Solo or Family Package |
| If family Package - Details of spouse | Creates spouse card (M1001-S1) |
| Upload profile picture | Member photo |

**Auto-generated:**
- Member Number: M1001, M1002, M1003...
- Expiry Date: 1 year from import
- Status: active

## 🔑 Default Passwords

Everyone's password = their email address

Examples:
- reinettevandyk@gmail.com → Password: reinettevandyk@gmail.com
- demilspires@gmail.com → Password: demilspires@gmail.com

## 👥 Member vs Admin Features

### Regular Members See:
✅ Their membership card with QR code  
✅ Points balance (10 per scan)  
✅ Attendance history  
✅ Family member cards (if Family Package)  

### Admins See Everything Above PLUS:
✅ "Admin" button → Dashboard  
✅ "Scanner" button → QR scanner  
✅ Import Excel data  
✅ View all members  
✅ View all attendance  
✅ Statistics  

## 🏠 Family Package Example

From your Excel:
```
Demi Spires (demilspires@gmail.com)
Spouse: Dwainne Venter
```

System creates:
- **M1001** - Demi Spires (main card + QR)
- **M1001-S1** - Dwainne Venter (spouse card + QR)

Both QR codes work at events. Points go to M1001.

## 🔧 Troubleshooting

### "Cannot connect" or "404 Not Found"

**Problem:** Server not finding files

**Solution:**
1. Make sure you're in the right folder
2. Check folder structure:
   ```
   middies-klub-system/
   ├── static/
   │   └── index.html  ← Must be here!
   └── server.py
   ```
3. Restart server (Ctrl+C, then `python server.py`)

### "No such table: members"

**Problem:** Database not created yet

**Solution:**
1. Run `python server.py` first (creates database)
2. THEN run `python add_admin.py`

### "Invalid email or password"

**Problem:** Wrong credentials

**Solution:**
- Password is your email address (exactly as in Excel)
- Check email for typos
- Make sure account was imported

### Camera not working

**Problem:** Scanner can't access camera

**Solution:**
- Use Chrome or Edge browser (best support)
- Allow camera permissions when prompted
- Check camera isn't used by another app
- Try on phone (better camera access)

### Import fails

**Problem:** Excel file not reading correctly

**Solution:**
1. Make sure it's .xlsx format (not .csv)
2. Download fresh from Google Forms
3. Don't edit column names
4. Check for duplicate emails

## 💾 Backup Your Data

**CRITICAL:** Backup the database file regularly!

```bash
# Copy database file
copy membership.db membership_backup.db

# Or with date
copy membership.db membership_2026-01-27.db
```

The database file contains:
- All member accounts
- All points
- All attendance records
- All login sessions

**Without backup = lose everything if file corrupted!**

## 📱 Mobile Usage

### For Members:
1. Open site on phone
2. Login with email
3. Add to home screen
4. Show QR at events
5. Check points anytime

### For Admins (Scanning):
1. Use tablet or phone
2. Login as admin
3. Click "Scanner"
4. Good lighting essential
5. Point camera at member's QR
6. Instant feedback: ✅ or ❌

## 🔄 Updating Members

### Add New Members:
1. They fill out Google Form
2. Download updated Excel
3. Upload to system
4. New members added automatically

### Update Existing:
1. Update Excel file
2. Re-upload
3. Existing members updated
4. Passwords unchanged

### Add More Admins:
1. Option A: Add "Is Admin" column to Excel (Yes/No)
2. Option B: Run `python add_admin.py` again

## ⚠️ Important Notes

### Keep Server Running:
- Server must stay running for system to work
- Don't close PowerShell window
- If computer restarts, run `python server.py` again

### Network Access:
- Local only (same WiFi) by default
- For public access, need proper hosting
- See SETUP_GUIDE.md for deployment options

### Security:
- Default passwords are emails (not secure!)
- Users should change passwords (feature can be added)
- Admin access controlled by Excel import only

## 📞 Need Help?

### Common Questions:

**Q: Can I use this on multiple computers?**
A: Server must run on ONE computer. Others access via browser.

**Q: What happens if server stops?**
A: Nothing lost! Database saved. Just restart: `python server.py`

**Q: How do I reset everything?**
A: Delete `membership.db` file and start over.

**Q: Can members change passwords?**
A: Not in current version. Must be reset by admin or re-import Excel.

**Q: How many members supported?**
A: Hundreds easily. Thousands with proper hosting.

### Still Having Issues?

1. Check this README carefully
2. Verify folder structure is correct
3. Ensure server is running
4. Check browser console (F12) for errors
5. Try different browser

## ✅ Quick Reference

### Start Server:
```bash
python server.py
```

### Add Admin:
```bash
python add_admin.py
```

### Access System:
```
http://localhost:5000
```

### From Other Devices:
```
http://YOUR_IP:5000
```

### Backup Database:
```bash
copy membership.db backup.db
```

### Stop Server:
```
Ctrl+C (in server window)
```

## 🎉 You're Ready!

Your system is fully configured and ready to use. Just follow the steps above and you'll have a working membership system in 5 minutes!

---

**Version:** 2.0 - Complete Working System  
**Configured For:** MiddiesKlub Google Form  
**Last Updated:** January 27, 2026  

**Support:** lesonvisagie@gmail.com