import time
print("🚀 Application starting...")
time.sleep(2)  # Give time for environment to load

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import hashlib
import secrets
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/env')
def show_env():
    """Debug endpoint to show environment variables"""
    return {
        'port': os.environ.get('PORT'),
        'database_url': os.environ.get('DATABASE_URL'),
        'python_version': os.sys.version,
        'is_render': 'RENDER' in os.environ,
        'timestamp': datetime.now().isoformat()
    }
    
# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# Determine if we're in production (Render)
IS_RENDER = 'RENDER' in os.environ

def get_db():
    """Get database connection - works with SQLite (local) and PostgreSQL (Render)"""
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        # PostgreSQL (Render/Production)
        import psycopg2
        from psycopg2.extras import DictCursor
        
        # Fix URL format for newer PostgreSQL drivers
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
        try:
            conn = psycopg2.connect(db_url, cursor_factory=DictCursor)
            print("✅ Connected to PostgreSQL on Render")
            return conn
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            print("Falling back to SQLite...")
            # Continue to SQLite fallback
    
    # SQLite (Local Development)
    import sqlite3
    DATABASE = 'membership.db'
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    print("✅ Connected to SQLite (local development)")
    return conn

def init_db():
    """Initialize database with required tables - works for both SQLite and PostgreSQL"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check database type
    try:
        cursor.execute("SELECT sqlite_version()")
        db_type = "SQLite"
        print("📊 Initializing SQLite database...")
        
        # SQLite table definitions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_number TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                surname TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                password_hash TEXT NOT NULL,
                membership_type TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                photo_url TEXT,
                points INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS family_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                primary_member_id INTEGER NOT NULL,
                member_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                relationship TEXT,
                FOREIGN KEY (primary_member_id) REFERENCES members (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_number TEXT NOT NULL,
                member_name TEXT NOT NULL,
                event_name TEXT,
                scanned_by TEXT,
                timestamp TEXT NOT NULL,
                points_awarded INTEGER DEFAULT 10,
                status TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL
            )
        ''')
        
    except:
        db_type = "PostgreSQL"
        print("📊 Initializing PostgreSQL database...")
        
        # PostgreSQL table definitions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id SERIAL PRIMARY KEY,
                member_number VARCHAR(50) UNIQUE NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                surname VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20),
                password_hash TEXT NOT NULL,
                membership_type VARCHAR(50) NOT NULL,
                expiry_date DATE NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                photo_url TEXT,
                points INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS family_members (
                id SERIAL PRIMARY KEY,
                primary_member_id INTEGER NOT NULL,
                member_number VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                relationship VARCHAR(50),
                FOREIGN KEY (primary_member_id) REFERENCES members (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                member_number VARCHAR(50) NOT NULL,
                member_name VARCHAR(200) NOT NULL,
                event_name VARCHAR(100),
                scanned_by VARCHAR(255),
                timestamp TIMESTAMP NOT NULL,
                points_awarded INTEGER DEFAULT 10,
                status VARCHAR(20) NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                token TEXT UNIQUE NOT NULL,
                role VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        ''')
        
        # Create indexes for PostgreSQL
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_members_email ON members(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_member ON attendance(member_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_timestamp ON attendance(timestamp)')
    
    conn.commit()
    conn.close()
    print(f"✅ {db_type} database initialized successfully!")

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    """Generate secure random token"""
    return secrets.token_urlsafe(32)

def verify_token(token):
    """Verify if token is valid and return user info"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Use correct parameter style
    param = '%s' if IS_RENDER else '?'
    query = f'''
        SELECT s.email, s.role, m.first_name, m.surname, m.member_number, m.is_admin
        FROM sessions s
        LEFT JOIN members m ON s.email = m.email
        WHERE s.token = {param} AND s.expires_at > {param}
    '''
    
    cursor.execute(query, (token, datetime.now().isoformat()))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'email': result[0],
            'role': result[1],
            'first_name': result[2],
            'surname': result[3],
            'member_number': result[4],
            'is_admin': result[5]
        }
    return None

# Initialize database on startup (but handle errors)
try:
    init_db()
    print("✅ Database initialized successfully!")
except Exception as e:
    print(f"⚠️  Database initialization warning: {e}")
    print("Continuing... tables may already exist.")

# ============= API ROUTES =============

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('static', 'index.html')

@app.route('/api/import-excel', methods=['POST'])
def import_excel():
    """Import members from Excel file (Admin only)"""
    token = request.headers.get('Authorization')
    user = verify_token(token)
    
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized - Admin access required'}), 401
    
    data = request.json.get('members', [])
    conn = get_db()
    cursor = conn.cursor()
    
    imported = 0
    errors = []
    
    for member_data in data:
        try:
            email = member_data.get('email', '').strip().lower()
            member_number = member_data.get('member_number', '').strip()
            
            if not email or not member_number:
                errors.append(f"Missing email or member number for {member_data}")
                continue
            
            default_password = email
            password_hash = hash_password(default_password)
            
            is_admin = 1 if str(member_data.get('is_admin', '')).lower() in ['yes', 'true', '1', 'admin'] else 0
            
            # Use correct SQL for database type
            if IS_RENDER:
                # PostgreSQL
                cursor.execute('''
                    INSERT INTO members 
                    (member_number, first_name, surname, email, phone, password_hash, 
                     membership_type, expiry_date, status, photo_url, points, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
                    ON CONFLICT (email) 
                    DO UPDATE SET
                        member_number = EXCLUDED.member_number,
                        first_name = EXCLUDED.first_name,
                        surname = EXCLUDED.surname,
                        phone = EXCLUDED.phone,
                        membership_type = EXCLUDED.membership_type,
                        expiry_date = EXCLUDED.expiry_date,
                        status = EXCLUDED.status,
                        photo_url = EXCLUDED.photo_url,
                        is_admin = EXCLUDED.is_admin
                ''', (
                    member_number,
                    member_data.get('first_name', '').strip(),
                    member_data.get('surname', '').strip(),
                    email,
                    member_data.get('phone', '').strip(),
                    password_hash,
                    member_data.get('membership_type', 'Solo'),
                    member_data.get('expiry_date', ''),
                    member_data.get('status', 'active'),
                    member_data.get('photo_url', 'https://ui-avatars.com/api/?name=' + member_data.get('first_name', 'U') + '+' + member_data.get('surname', 'U')),
                    is_admin
                ))
            else:
                # SQLite
                cursor.execute('''
                    INSERT OR REPLACE INTO members 
                    (member_number, first_name, surname, email, phone, password_hash, 
                     membership_type, expiry_date, status, photo_url, points, is_admin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                ''', (
                    member_number,
                    member_data.get('first_name', '').strip(),
                    member_data.get('surname', '').strip(),
                    email,
                    member_data.get('phone', '').strip(),
                    password_hash,
                    member_data.get('membership_type', 'Solo'),
                    member_data.get('expiry_date', ''),
                    member_data.get('status', 'active'),
                    member_data.get('photo_url', 'https://ui-avatars.com/api/?name=' + member_data.get('first_name', 'U') + '+' + member_data.get('surname', 'U')),
                    is_admin
                ))
            
            # Get member ID
            query = 'SELECT id FROM members WHERE email = %s' if IS_RENDER else 'SELECT id FROM members WHERE email = ?'
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            member_id = result[0] if result else None
            
            # Insert family members
            if 'family_members' in member_data and member_data['family_members'] and member_id:
                for fm in member_data['family_members']:
                    if IS_RENDER:
                        cursor.execute('''
                            INSERT INTO family_members 
                            (primary_member_id, member_number, name, relationship)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (member_number) 
                            DO UPDATE SET
                                name = EXCLUDED.name,
                                relationship = EXCLUDED.relationship
                        ''', (member_id, fm['member_number'], fm['name'], fm['relationship']))
                    else:
                        cursor.execute('''
                            INSERT OR REPLACE INTO family_members 
                            (primary_member_id, member_number, name, relationship)
                            VALUES (?, ?, ?, ?)
                        ''', (member_id, fm['member_number'], fm['name'], fm['relationship']))
            
            imported += 1
            
        except Exception as e:
            errors.append(f"{member_data.get('member_number', 'Unknown')}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'imported': imported,
        'errors': errors
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint - email-based authentication"""
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Find member by email - use correct parameter style
    query = 'SELECT * FROM members WHERE email = %s' if IS_RENDER else 'SELECT * FROM members WHERE email = ?'
    cursor.execute(query, (email,))
    member = cursor.fetchone()
    
    if member and member['password_hash'] == hash_password(password):
        role = 'admin' if member['is_admin'] == 1 else 'member'
        token = generate_token()
        expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        
        insert_query = 'INSERT INTO sessions (email, token, role, expires_at) VALUES (%s, %s, %s, %s)' if IS_RENDER else 'INSERT INTO sessions (email, token, role, expires_at) VALUES (?, ?, ?, ?)'
        cursor.execute(insert_query, (email, token, role, expires_at))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'token': token,
            'role': role,
            'member': {
                'member_number': member['member_number'],
                'first_name': member['first_name'],
                'surname': member['surname'],
                'email': member['email'],
                'membership_type': member['membership_type'],
                'status': member['status'],
                'points': member['points'],
                'is_admin': member['is_admin']
            }
        })
    
    conn.close()
    return jsonify({'error': 'Invalid email or password'}), 401

# ... (KEEP ALL OTHER ROUTE FUNCTIONS AS THEY WERE IN YOUR ORIGINAL)
# Just make sure they use the parameter style checks like above

@app.route('/api/member/profile', methods=['GET'])
def get_member_profile():
    """Get member profile and attendance"""
    token = request.headers.get('Authorization')
    user = verify_token(token)
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get member details
    query = 'SELECT * FROM members WHERE email = %s' if IS_RENDER else 'SELECT * FROM members WHERE email = ?'
    cursor.execute(query, (user['email'],))
    member = cursor.fetchone()
    
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    
    # Get family members
    query = '''
        SELECT * FROM family_members 
        WHERE primary_member_id = (SELECT id FROM members WHERE email = %s)
    ''' if IS_RENDER else '''
        SELECT * FROM family_members 
        WHERE primary_member_id = (SELECT id FROM members WHERE email = ?)
    '''
    cursor.execute(query, (user['email'],))
    family_members = [dict(row) for row in cursor.fetchall()]
    
    # Get attendance history
    query = '''
        SELECT * FROM attendance 
        WHERE member_number = %s OR member_number IN (
            SELECT member_number FROM family_members 
            WHERE primary_member_id = (SELECT id FROM members WHERE email = %s)
        )
        ORDER BY timestamp DESC
        LIMIT 50
    ''' if IS_RENDER else '''
        SELECT * FROM attendance 
        WHERE member_number = ? OR member_number IN (
            SELECT member_number FROM family_members 
            WHERE primary_member_id = (SELECT id FROM members WHERE email = ?)
        )
        ORDER BY timestamp DESC
        LIMIT 50
    '''
    cursor.execute(query, (member['member_number'], user['email']))
    attendance = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'member': dict(member),
        'family_members': family_members,
        'attendance': attendance
    })

@app.route('/api/scan', methods=['POST'])
def scan_qr():
    """Handle QR code scanning (Admin only)"""
    token = request.headers.get('Authorization')
    user = verify_token(token)
    
    if not user or user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized - Admin access required'}), 401
    
    data = request.json
    scanned_member_number = data.get('member_number')
    event_name = data.get('event_name', 'General Access')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if it's a primary member or family member
    query = '''
        SELECT m.*, CONCAT(m.first_name, ' ', m.surname) as full_name
        FROM members m
        WHERE m.member_number = %s
    ''' if IS_RENDER else '''
        SELECT m.*, m.first_name || ' ' || m.surname as full_name
        FROM members m
        WHERE m.member_number = ?
    '''
    cursor.execute(query, (scanned_member_number,))
    
    member = cursor.fetchone()
    
    # If not found, check family members
    if not member:
        query = '''
            SELECT m.*, fm.name as full_name, fm.member_number as scanned_number
            FROM family_members fm
            JOIN members m ON fm.primary_member_id = m.id
            WHERE fm.member_number = %s
        ''' if IS_RENDER else '''
            SELECT m.*, fm.name as full_name, fm.member_number as scanned_number
            FROM family_members fm
            JOIN members m ON fm.primary_member_id = m.id
            WHERE fm.member_number = ?
        '''
        cursor.execute(query, (scanned_member_number,))
        
        family_result = cursor.fetchone()
        if family_result:
            member = family_result
            member_name = family_result['full_name']
        else:
            conn.close()
            return jsonify({
                'success': False,
                'status': 'error',
                'message': 'Member not found'
            }), 404
    else:
        member_name = member['full_name']
    
    # Check if membership is active
    expiry_date = member['expiry_date']
    if isinstance(expiry_date, str):
        expiry_date = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
    
    is_active = member['status'] == 'active' and expiry_date > datetime.now()
    
    # Award points if active
    points_awarded = 10 if is_active else 0
    
    # Log attendance
    insert_query = '''
        INSERT INTO attendance 
        (member_number, member_name, event_name, scanned_by, timestamp, points_awarded, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''' if IS_RENDER else '''
        INSERT INTO attendance 
        (member_number, member_name, event_name, scanned_by, timestamp, points_awarded, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    cursor.execute(insert_query, (
        scanned_member_number,
        member_name,
        event_name,
        user['email'],
        datetime.now().isoformat(),
        points_awarded,
        'granted' if is_active else 'denied'
    ))
    
    # Update member points if active (only for primary member)
    if is_active:
        update_query = '''
            UPDATE members 
            SET points = points + %s 
            WHERE member_number = %s OR id = (
                SELECT primary_member_id FROM family_members WHERE member_number = %s
            )
        ''' if IS_RENDER else '''
            UPDATE members 
            SET points = points + ? 
            WHERE member_number = ? OR id = (
                SELECT primary_member_id FROM family_members WHERE member_number = ?
            )
        '''
        cursor.execute(update_query, (points_awarded, scanned_member_number, scanned_member_number))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'status': 'granted' if is_active else 'denied',
        'member_name': member_name,
        'points_awarded': points_awarded,
        'message': 'Access Granted' if is_active else 'Membership Expired'
    })

# ... (CONTINUE WITH ALL OTHER ROUTES, ADJUSTING PARAMETER STYLE AS NEEDED)

@app.route('/api/test')
def test():
    """Test endpoint to verify server is running"""
    return jsonify({
        'status': 'ok',
        'message': 'Server is running',
        'database': 'PostgreSQL' if IS_RENDER else 'SQLite',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # For local development only
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)