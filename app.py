from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, FloatField, SelectField, TextAreaField, SelectMultipleField, RadioField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from collections import defaultdict
import json
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import secrets
import string

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['DATABASE'] = os.environ.get('DATABASE', 'splitwise.db')

# Set minimum cache TTL for all responses
@app.after_request
def add_cache_headers(response):
    """Add minimal cache control headers to all responses"""
    
    # Static resources (CSS, JS, images) - very short cache
    if request.endpoint == 'static' or request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=60, must-revalidate'  # 1 minute
        response.headers['Expires'] = '0'
    
    # Service worker - no cache
    elif request.path.endswith('sw.js'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # API endpoints and dynamic content - no cache
    elif request.path.startswith('/api/') or request.method == 'POST':
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # HTML pages - minimal cache
    else:
        response.headers['Cache-Control'] = 'no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # Add ETag for better cache validation
    if not response.headers.get('ETag'):
        response.add_etag()
    
    return response
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 7 * 1024 * 1024  # 7MB max file size

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

# Configure Gemini AI
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize Flask-Mail
mail = Mail(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Multi-checkbox widget for WTForms
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

# User model
class User(UserMixin):
    def __init__(self, id, username, email, password_hash, created_at):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user:
            return User(user['id'], user['username'], user['email'], user['password_hash'], user['created_at'])
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user:
            return User(user['id'], user['username'], user['email'], user['password_hash'], user['created_at'])
        return None

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user:
            return User(user['id'], user['username'], user['email'], user['password_hash'], user['created_at'])
        return None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_user(username, email, password):
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
                (username, email, password_hash, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class PasswordResetRequestForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Email')

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Create Group')

class ExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(min=1, max=200)])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    paid_by = SelectField('Paid by', coerce=int, validators=[DataRequired()])
    split_type = RadioField('Split Type', choices=[('equal', 'Equal Split'), ('custom', 'Custom Split')], default='equal')
    split_among = MultiCheckboxField('Split among', coerce=int, validators=[DataRequired()])
    custom_amounts = HiddenField('Custom Amounts')
    submit = SubmitField('Add Expense')

class SettlementForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Settle Up')

# Database functions
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            full_name TEXT,
            iban TEXT,
            bic TEXT
        )
    ''')
    
    # Groups table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_by INTEGER NOT NULL,
            invite_code TEXT UNIQUE,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Group memberships table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            joined_at TIMESTAMP NOT NULL,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(group_id, user_id)
        )
    ''')
    
    # Expenses table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            paid_by INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
            FOREIGN KEY (paid_by) REFERENCES users (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Expense shares table (who owes what for each expense)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expense_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (expense_id) REFERENCES expenses (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(expense_id, user_id)
        )
    ''')
    
    # Settlements table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settlements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            payer_id INTEGER NOT NULL,
            payee_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP NOT NULL,
            description TEXT,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
            FOREIGN KEY (payer_id) REFERENCES users (id),
            FOREIGN KEY (payee_id) REFERENCES users (id)
        )
    ''')
    
    # Password reset tokens table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Migrate existing groups to have invite codes
    migrate_existing_groups()
    
    # Migrate users table to add bank details columns
    migrate_users_table()
    
    # Migrate settlements table to add description column
    migrate_settlements_table()
    
    # Clean up any existing invalid user data
    cleanup_invalid_expense_shares()
    cleanup_invalid_settlements()

# Helper functions
def get_user_groups(user_id):
    conn = get_db_connection()
    groups = conn.execute('''
        SELECT g.*, u.username as creator_name
        FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        JOIN users u ON g.created_by = u.id
        WHERE gm.user_id = ?
        ORDER BY g.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return groups

def get_group_members(group_id):
    conn = get_db_connection()
    members = conn.execute('''
        SELECT u.id, u.username, u.email, gm.joined_at
        FROM users u
        JOIN group_members gm ON u.id = gm.user_id
        WHERE gm.group_id = ?
        ORDER BY gm.joined_at
    ''', (group_id,)).fetchall()
    conn.close()
    return members

def calculate_balances(group_id):
    conn = get_db_connection()
    
    # Get valid group member IDs
    valid_member_ids = set(member['id'] for member in get_group_members(group_id))
    
    # Get all expenses and their shares, but only for valid group members
    expenses = conn.execute('''
        SELECT e.id, e.amount, e.paid_by, es.user_id, es.amount as share_amount
        FROM expenses e
        JOIN expense_shares es ON e.id = es.expense_id
        WHERE e.group_id = ? AND es.user_id IN ({})
    '''.format(','.join('?' * len(valid_member_ids))), (group_id,) + tuple(valid_member_ids)).fetchall()
    
    # Get all settlements, but only for valid group members
    settlements = conn.execute('''
        SELECT payer_id, payee_id, amount
        FROM settlements
        WHERE group_id = ? AND payer_id IN ({}) AND payee_id IN ({})
    '''.format(','.join('?' * len(valid_member_ids)), ','.join('?' * len(valid_member_ids))), 
        (group_id,) + tuple(valid_member_ids) + tuple(valid_member_ids)).fetchall()
    
    conn.close()
    
    # Calculate net balances
    balances = defaultdict(float)
    processed_expenses = set()
    
    # Process expenses
    for expense in expenses:
        # Credit the payer with the full amount (only once per expense)
        if expense['id'] not in processed_expenses:
            balances[expense['paid_by']] += expense['amount']
            processed_expenses.add(expense['id'])
        
        # Debit each person for their share (including the payer)
        balances[expense['user_id']] -= expense['share_amount']
    
    # Process settlements
    for settlement in settlements:
        # When you settle up, your debt decreases (balance becomes more positive)
        balances[settlement['payer_id']] += settlement['amount']
        # When you receive payment, people owe you less (balance becomes less positive)  
        balances[settlement['payee_id']] -= settlement['amount']
    
    return dict(balances)

def simplify_debts(balances):
    """Simplify debts to minimize number of transactions"""
    creditors = [(user_id, amount) for user_id, amount in balances.items() if amount > 0]
    debtors = [(user_id, -amount) for user_id, amount in balances.items() if amount < 0]
    
    transactions = []
    
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1], reverse=True)
    
    i, j = 0, 0
    while i < len(creditors) and j < len(debtors):
        creditor_id, credit_amount = creditors[i]
        debtor_id, debt_amount = debtors[j]
        
        settle_amount = min(credit_amount, debt_amount)
        
        if settle_amount > 0.01:  # Avoid tiny amounts
            transactions.append({
                'from': debtor_id,
                'to': creditor_id,
                'amount': round(settle_amount, 2)
            })
        
        creditors[i] = (creditor_id, credit_amount - settle_amount)
        debtors[j] = (debtor_id, debt_amount - settle_amount)
        
        if creditors[i][1] <= 0.01:
            i += 1
        if debtors[j][1] <= 0.01:
            j += 1
    
    return transactions

def get_group_by_invite_code(invite_code):
    """Get group by invite code"""
    conn = get_db_connection()
    group = conn.execute('SELECT * FROM groups WHERE invite_code = ?', (invite_code,)).fetchone()
    conn.close()
    return group

def generate_invite_code():
    """Generate a unique invite code for a group"""
    return str(uuid.uuid4())[:8].upper()

def is_user_in_group(user_id, group_id):
    """Check if user is already a member of the group"""
    conn = get_db_connection()
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, user_id)).fetchone()
    conn.close()
    return membership is not None

def add_user_to_group(user_id, group_id):
    """Add user to group"""
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO group_members (group_id, user_id, joined_at)
            VALUES (?, ?, ?)
        ''', (group_id, user_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def migrate_existing_groups():
    """Add invite codes to existing groups that don't have them"""
    conn = get_db_connection()
    
    try:
        # Check if invite_code column exists
        cursor = conn.execute("PRAGMA table_info(groups)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'invite_code' not in columns:
            # Add the invite_code column if it doesn't exist (without UNIQUE constraint)
            conn.execute('ALTER TABLE groups ADD COLUMN invite_code TEXT')
            conn.commit()
        
        # Find groups without invite codes
        groups_without_codes = conn.execute('''
            SELECT id FROM groups WHERE invite_code IS NULL OR invite_code = ''
        ''').fetchall()
        
        for group in groups_without_codes:
            # Generate unique invite code
            while True:
                invite_code = generate_invite_code()
                # Check if code already exists
                existing = conn.execute('''
                    SELECT id FROM groups WHERE invite_code = ?
                ''', (invite_code,)).fetchone()
                
                if not existing:
                    break
            
            # Update group with invite code
            conn.execute('''
                UPDATE groups SET invite_code = ? WHERE id = ?
            ''', (invite_code, group['id']))
        
        conn.commit()
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

def migrate_users_table():
    """Add bank details columns to existing users table"""
    conn = get_db_connection()
    
    try:
        # Check if bank details columns exist
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'full_name' not in columns:
            conn.execute('ALTER TABLE users ADD COLUMN full_name TEXT')
            
        if 'iban' not in columns:
            conn.execute('ALTER TABLE users ADD COLUMN iban TEXT')
            
        if 'bic' not in columns:
            conn.execute('ALTER TABLE users ADD COLUMN bic TEXT')
            
        conn.commit()
        
    except Exception as e:
        print(f"User table migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

def migrate_settlements_table():
    """Add description column to settlements table if it doesn't exist"""
    conn = get_db_connection()
    
    try:
        # Check if description column exists
        cursor = conn.execute("PRAGMA table_info(settlements)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'description' not in columns:
            conn.execute('ALTER TABLE settlements ADD COLUMN description TEXT')
            conn.commit()
            print("Added description column to settlements table")
            
    except Exception as e:
        print(f"Settlements table migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

def cleanup_invalid_expense_shares():
    """Remove expense shares for users that are not valid group members"""
    conn = get_db_connection()
    try:
        # Get all groups
        groups = conn.execute('SELECT id FROM groups').fetchall()
        
        for group in groups:
            group_id = group['id']
            # Get valid member IDs for this group
            valid_member_ids = [member['id'] for member in get_group_members(group_id)]
            
            if valid_member_ids:
                # Delete expense shares for invalid user IDs
                placeholders = ','.join('?' * len(valid_member_ids))
                deleted = conn.execute('''
                    DELETE FROM expense_shares 
                    WHERE expense_id IN (
                        SELECT id FROM expenses WHERE group_id = ?
                    ) AND user_id NOT IN ({})
                '''.format(placeholders), (group_id,) + tuple(valid_member_ids))
                
                if deleted.rowcount > 0:
                    print(f"Cleaned up {deleted.rowcount} invalid expense shares for group {group_id}")
        
        conn.commit()
        print("Completed cleanup of invalid expense shares")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        conn.rollback()
    finally:
        conn.close()

def cleanup_invalid_settlements():
    """Remove settlements for users that are not valid group members"""
    conn = get_db_connection()
    try:
        # Get all groups
        groups = conn.execute('SELECT id FROM groups').fetchall()
        
        for group in groups:
            group_id = group['id']
            # Get valid member IDs for this group
            valid_member_ids = [member['id'] for member in get_group_members(group_id)]
            
            if valid_member_ids:
                # Delete settlements for invalid user IDs
                placeholders = ','.join('?' * len(valid_member_ids))
                deleted = conn.execute('''
                    DELETE FROM settlements 
                    WHERE group_id = ? AND (payer_id NOT IN ({}) OR payee_id NOT IN ({}))
                '''.format(placeholders, placeholders), 
                    (group_id,) + tuple(valid_member_ids) + tuple(valid_member_ids))
                
                if deleted.rowcount > 0:
                    print(f"Cleaned up {deleted.rowcount} invalid settlements for group {group_id}")
        
        conn.commit()
        print("Completed cleanup of invalid settlements")
    except Exception as e:
        print(f"Error during cleanup: {e}")
        conn.rollback()
    finally:
        conn.close()

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Ensure upload folder exists"""
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def generate_epc_qr_code(amount, recipient_name, recipient_iban, recipient_bic=None, reference=None):
    """Generate EPC QR code for SEPA payments"""
    try:
        # EPC QR code format according to European Payments Council guidelines
        epc_data = [
            "BCD",  # Service Tag
            "002",  # Version
            "1",    # Character set (UTF-8)
            "SCT",  # Identification (SEPA Credit Transfer)
            recipient_bic or "",  # BIC of the Beneficiary Bank
            recipient_name,  # Name of the Beneficiary
            recipient_iban,  # Account number (IBAN)
            f"EUR{amount:.2f}",  # Amount in EUR
            "",     # Purpose (empty)
            reference or "",  # Structured Reference
            ""      # Unstructured Remittance Information
        ]
        
        # Join with newlines as per EPC specification
        epc_string = '\n'.join(epc_data)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=4,
        )
        qr.add_data(epc_string)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for embedding in HTML
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error generating EPC QR code: {e}")
        return None

def analyze_receipt_with_gemini(file_path):
    """Analyze receipt using Gemini AI and extract individual items"""
    if not GEMINI_API_KEY:
        return None
    
    try:
        # Upload file to Gemini
        file = genai.upload_file(file_path)
        
        # Create the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Analyze the receipt
        prompt = """
        Analyze this receipt image and extract ALL individual items as separate entries.
        If an item has quantity > 1, create separate entries for each individual item.
        
        Return a JSON object with this structure:
        {
            "store_name": "Name of the store/restaurant",
            "total_amount": 0.00,
            "currency": "EUR",
            "items": [
                {
                    "name": "Item name",
                    "price": 0.00
                }
            ]
        }
        
        CRITICAL RULES:
        - If receipt shows "5 Tiramisu €42.50", create 5 separate entries:
          * Each entry: {"name": "Tiramisu", "price": 8.50}
          * Calculate unit price: 42.50 ÷ 5 = 8.50 per item
        - If receipt shows "2 Coke €6.00", create 2 separate entries:
          * Each entry: {"name": "Coke", "price": 3.00}
        - Each person should be able to select individual items
        - "price" field should always be the unit price (per single item)
        - Expand all quantities into individual item entries
        - Include ALL items from the receipt as separate entries
        - Return valid JSON only, no other text
        """
        
        response = model.generate_content([file, prompt])
        
        # Parse JSON response
        response_text = response.text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        parsed_result = json.loads(response_text)
        
        # Validate and fix the parsed result
        if 'items' in parsed_result:
            for item in parsed_result['items']:
                # Ensure required fields exist and are valid
                if 'name' not in item or not item['name']:
                    item['name'] = 'Unknown Item'
                if 'price' not in item:
                    item['price'] = 0.0
                
                # Ensure price is a valid number
                try:
                    item['price'] = float(item['price'])
                except (ValueError, TypeError):
                    item['price'] = 0.0
                
                # Ensure price is positive
                if item['price'] < 0:
                    item['price'] = 0.0
        
        return parsed_result
        
    except Exception as e:
        print(f"Error analyzing receipt: {e}")
        return None

# Password reset helper functions
def generate_reset_token():
    """Generate a secure random token for password reset"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def create_password_reset_token(user_id):
    """Create a password reset token for a user"""
    token = generate_reset_token()
    expires_at = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
    
    conn = get_db_connection()
    try:
        # Delete any existing unused tokens for this user
        conn.execute('''
            DELETE FROM password_reset_tokens 
            WHERE user_id = ? AND used = FALSE
        ''', (user_id,))
        
        # Insert new token
        conn.execute('''
            INSERT INTO password_reset_tokens (user_id, token, expires_at, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, token, expires_at.isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        return token
    except Exception as e:
        print(f"Error creating password reset token: {e}")
        return None
    finally:
        conn.close()

def validate_reset_token(token):
    """Validate a password reset token and return user_id if valid"""
    conn = get_db_connection()
    try:
        result = conn.execute('''
            SELECT user_id, expires_at, used
            FROM password_reset_tokens
            WHERE token = ?
        ''', (token,)).fetchone()
        
        if not result:
            return None
        
        # Check if token is already used
        if result['used']:
            return None
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(result['expires_at'])
        if datetime.now() > expires_at:
            return None
        
        return result['user_id']
    finally:
        conn.close()

def mark_token_as_used(token):
    """Mark a reset token as used"""
    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE password_reset_tokens
            SET used = TRUE
            WHERE token = ?
        ''', (token,))
        conn.commit()
    finally:
        conn.close()

def send_password_reset_email(user_email, reset_token):
    """Send password reset email with reset code"""
    try:
        # Get sender from config or use a default
        sender = app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME')
        if not sender:
            print("Error: No email sender configured. Please set MAIL_DEFAULT_SENDER or MAIL_USERNAME.")
            return False
        
        # Debug logging
        print(f"Sending password reset email to: {user_email}")
        print(f"Using sender: {sender}")
        print(f"SMTP server: {app.config.get('MAIL_SERVER')}:{app.config.get('MAIL_PORT')}")
        
        msg = Message(
            subject='Smart Split - Password Reset',
            sender=sender,
            recipients=[user_email],
            html=render_template('auth/password_reset_email.html', 
                               reset_token=reset_token,
                               app_name='Smart Split')
        )
        mail.send(msg)
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        print(f"Email config - Server: {app.config.get('MAIL_SERVER')}, Port: {app.config.get('MAIL_PORT')}")
        print(f"Email config - Username: {app.config.get('MAIL_USERNAME')}, TLS: {app.config.get('MAIL_USE_TLS')}")
        return False

def cleanup_expired_tokens():
    """Clean up expired password reset tokens"""
    conn = get_db_connection()
    try:
        conn.execute('''
            DELETE FROM password_reset_tokens
            WHERE expires_at < ? OR used = TRUE
        ''', (datetime.now().isoformat(),))
        conn.commit()
    finally:
        conn.close()

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            
            # Check if user was trying to join a group via invite code
            invite_code = session.pop('join_invite_code', None)
            if invite_code:
                flash('Login successful! Redirecting to join group...', 'success')
                return redirect(url_for('join_group', invite_code=invite_code))
            
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.get_by_username(form.username.data):
            flash('Username already exists', 'error')
        elif User.get_by_email(form.email.data):
            flash('Email already registered', 'error')
        else:
            if User.create_user(form.username.data, form.email.data, form.password.data):
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please try again.', 'error')
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user:
            # Clean up expired tokens first
            cleanup_expired_tokens()
            
            # Generate reset token
            reset_token = create_password_reset_token(user.id)
            if reset_token:
                # Send email with reset code
                if send_password_reset_email(user.email, reset_token):
                    flash('If an account with that email exists, you will receive a password reset email shortly.', 'info')
                else:
                    flash('Failed to send reset email. Please try again later.', 'error')
            else:
                flash('Failed to generate reset token. Please try again.', 'error')
        else:
            # Don't reveal if email exists or not for security
            flash('If an account with that email exists, you will receive a password reset email shortly.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('auth/forgot_password.html', form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Validate token
    user_id = validate_reset_token(token)
    if not user_id:
        flash('Invalid or expired reset token. Please request a new password reset.', 'error')
        return redirect(url_for('forgot_password'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Update user password
        user = User.get(user_id)
        if user:
            new_password_hash = generate_password_hash(form.password.data)
            
            conn = get_db_connection()
            try:
                conn.execute('''
                    UPDATE users 
                    SET password_hash = ?
                    WHERE id = ?
                ''', (new_password_hash, user_id))
                conn.commit()
                
                # Mark token as used
                mark_token_as_used(token)
                
                flash('Your password has been reset successfully. You can now log in with your new password.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash('Error updating password. Please try again.', 'error')
                print(f"Error updating password: {e}")
            finally:
                conn.close()
        else:
            flash('User not found. Please try again.', 'error')
    
    return render_template('auth/reset_password.html', form=form, token=token)

@app.route('/dashboard')
@login_required
def dashboard():
    groups = get_user_groups(current_user.id)
    
    # Calculate total balances across all groups
    total_you_owe = 0
    total_owed_to_you = 0
    
    for group in groups:
        balances = calculate_balances(group['id'])
        user_balance = balances.get(current_user.id, 0)
        if user_balance < 0:
            total_you_owe += abs(user_balance)
        else:
            total_owed_to_you += user_balance
    
    return render_template('dashboard.html', 
                         groups=groups, 
                         total_you_owe=total_you_owe,
                         total_owed_to_you=total_owed_to_you)

@app.route('/groups')
@login_required
def groups():
    user_groups = get_user_groups(current_user.id)
    return render_template('groups.html', groups=user_groups)

@app.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create_group():
    form = GroupForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate unique invite code
        invite_code = generate_invite_code()
        
        # Create group
        cursor.execute('''
            INSERT INTO groups (name, description, created_by, invite_code, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (form.name.data, form.description.data, current_user.id, invite_code, datetime.now().isoformat()))
        
        group_id = cursor.lastrowid
        
        # Add creator as member
        cursor.execute('''
            INSERT INTO group_members (group_id, user_id, joined_at)
            VALUES (?, ?, ?)
        ''', (group_id, current_user.id, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        flash(f'Group "{form.name.data}" created successfully!', 'success')
        return redirect(url_for('group_detail', group_id=group_id))
    
    return render_template('groups/create.html', form=form)

@app.route('/groups/<int:group_id>')
@login_required
def group_detail(group_id):
    conn = get_db_connection()
    
    # Check if user is member of group
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('groups'))
    
    # Get group info
    group = conn.execute('SELECT * FROM groups WHERE id = ?', (group_id,)).fetchone()
    
    # Get members
    members = get_group_members(group_id)
    
    # Get recent expenses
    expenses = conn.execute('''
        SELECT e.*, u.username as paid_by_name, uc.username as created_by_name
        FROM expenses e
        JOIN users u ON e.paid_by = u.id
        JOIN users uc ON e.created_by = uc.id
        WHERE e.group_id = ?
        ORDER BY e.created_at DESC
        LIMIT 10
    ''', (group_id,)).fetchall()
    
    conn.close()
    
    # Calculate balances
    balances = calculate_balances(group_id)
    
    # Get simplified debts
    simplified_debts = simplify_debts(balances)
    
    # Get member names for debts
    member_names = {m['id']: m['username'] for m in members}
    
    return render_template('groups/detail.html', 
                         group=group, 
                         members=members, 
                         expenses=expenses,
                         balances=balances,
                         simplified_debts=simplified_debts,
                         member_names=member_names)

@app.route('/groups/<int:group_id>/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense(group_id):
    conn = get_db_connection()
    
    # Check if user is member of group
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('groups'))
    
    # Get group and members
    group = conn.execute('SELECT * FROM groups WHERE id = ?', (group_id,)).fetchone()
    members = get_group_members(group_id)
    
    form = ExpenseForm()
    form.paid_by.choices = [(m['id'], m['username']) for m in members]
    form.split_among.choices = [(m['id'], m['username']) for m in members]
    
    if form.validate_on_submit():
        cursor = conn.cursor()
        
        # Validate custom amounts if custom split is selected
        if form.split_type.data == 'custom':
            try:
                custom_amounts = json.loads(form.custom_amounts.data) if form.custom_amounts.data else {}
                total_custom = sum(float(amount) for amount in custom_amounts.values())
                
                # Check if custom amounts add up to total expense amount (within 0.01 tolerance)
                if abs(total_custom - form.amount.data) > 0.01:
                    flash(f'Custom amounts (€{total_custom:.2f}) must equal the total expense amount (€{form.amount.data:.2f})', 'error')
                    conn.close()
                    return render_template('groups/add_expense.html', form=form, group=group, members=members)
                    
                # Check if all selected members have custom amounts
                for member_id in form.split_among.data:
                    if str(member_id) not in custom_amounts:
                        flash('Please enter custom amounts for all selected members', 'error')
                        conn.close()
                        return render_template('groups/add_expense.html', form=form, group=group, members=members)
                        
            except (json.JSONDecodeError, ValueError, TypeError):
                flash('Invalid custom amounts data', 'error')
                conn.close()
                return render_template('groups/add_expense.html', form=form, group=group, members=members)
        
        # Create expense
        cursor.execute('''
            INSERT INTO expenses (group_id, description, amount, paid_by, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (group_id, form.description.data, form.amount.data, 
              form.paid_by.data, current_user.id, datetime.now().isoformat()))
        
        expense_id = cursor.lastrowid
        
        # Create expense shares based on split type
        if form.split_type.data == 'equal':
            # Calculate equal split among selected members
            split_members = form.split_among.data
            share_amount = form.amount.data / len(split_members)
            
            for member_id in split_members:
                cursor.execute('''
                    INSERT INTO expense_shares (expense_id, user_id, amount)
                    VALUES (?, ?, ?)
                ''', (expense_id, member_id, share_amount))
        else:
            # Use custom amounts
            custom_amounts = json.loads(form.custom_amounts.data)
            for member_id in form.split_among.data:
                amount = float(custom_amounts[str(member_id)])
                cursor.execute('''
                    INSERT INTO expense_shares (expense_id, user_id, amount)
                    VALUES (?, ?, ?)
                ''', (expense_id, member_id, amount))
        
        conn.commit()
        conn.close()
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('group_detail', group_id=group_id))
    
    conn.close()
    return render_template('groups/add_expense.html', form=form, group=group, members=members)

@app.route('/groups/<int:group_id>/scan_receipt', methods=['GET', 'POST'])
@login_required
def scan_receipt(group_id):
    conn = get_db_connection()
    
    # Check if user is member of group
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('groups'))
    
    # Get group info
    group = conn.execute('SELECT * FROM groups WHERE id = ?', (group_id,)).fetchone()
    conn.close()
    
    if request.method == 'POST':
        ensure_upload_folder()
        
        # Check if file was uploaded
        if 'receipt_file' not in request.files:
            flash('No file selected', 'error')
            return render_template('groups/scan_receipt.html', group=group)
        
        file = request.files['receipt_file']
        
        # Check if file was actually selected
        if file.filename == '':
            flash('No file selected', 'error')
            return render_template('groups/scan_receipt.html', group=group)
        
        # Validate file type and save
        if file and allowed_file(file.filename):
            # Create secure filename with timestamp and user ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            original_filename = secure_filename(file.filename)
            filename = f"receipt_{current_user.id}_{group_id}_{timestamp}_{original_filename}"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Analyze receipt with Gemini AI
            receipt_analysis = analyze_receipt_with_gemini(file_path)
            
            if receipt_analysis:
                # Store analysis in session for item selection
                session['receipt_analysis'] = receipt_analysis
                session['receipt_filename'] = filename
                return redirect(url_for('select_receipt_items', group_id=group_id))
            else:
                if not GEMINI_API_KEY:
                    flash('Gemini AI not configured. Please set GEMINI_API_KEY environment variable.', 'warning')
                else:
                    flash('Could not analyze receipt. Please add items manually.', 'warning')
                return redirect(url_for('add_expense', group_id=group_id))
        else:
            flash('Invalid file type. Please upload an image file (PNG, JPG, JPEG, GIF, BMP, WebP)', 'error')
    
    return render_template('groups/scan_receipt.html', group=group)

@app.route('/groups/<int:group_id>/select_items', methods=['GET', 'POST'])
@login_required
def select_receipt_items(group_id):
    conn = get_db_connection()
    
    # Check if user is member of group
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('groups'))
    
    # Get group info and members
    group = conn.execute('SELECT * FROM groups WHERE id = ?', (group_id,)).fetchone()
    members_rows = conn.execute('''
        SELECT u.* FROM users u 
        JOIN group_members gm ON u.id = gm.user_id 
        WHERE gm.group_id = ?
    ''', (group_id,)).fetchall()
    
    # Convert SQLite Row objects to dictionaries for JSON serialization
    members = [dict(member) for member in members_rows]
    
    # Check if we have receipt analysis in session
    receipt_analysis = session.get('receipt_analysis')
    if not receipt_analysis:
        flash('No receipt analysis found. Please upload a receipt again.', 'error')
        return redirect(url_for('scan_receipt', group_id=group_id))
    
    if request.method == 'POST':
        # Get who paid the bill
        bill_payer_id = request.form.get('bill_payer')
        if not bill_payer_id:
            flash('Please select who paid the bill.', 'error')
            conn.close()
            return render_template('groups/select_receipt_items.html', 
                                 group=group, members=members, 
                                 receipt_analysis=receipt_analysis)
        
        try:
            bill_payer_id = int(bill_payer_id)
        except (ValueError, TypeError):
            flash('Invalid bill payer selection.', 'error')
            conn.close()
            return render_template('groups/select_receipt_items.html', 
                                 group=group, members=members, 
                                 receipt_analysis=receipt_analysis)
        
        # Get confirmed payments
        confirmed_payments_data = request.form.get('confirmed_payments', '[]')
        try:
            confirmed_payments = json.loads(confirmed_payments_data) if confirmed_payments_data else []
        except json.JSONDecodeError:
            confirmed_payments = []
        
        # Get guest users data (but don't include them in group expense calculations)
        guest_users_data = request.form.get('guest_users', '[]')
        try:
            guest_users = json.loads(guest_users_data) if guest_users_data else []
            guest_user_ids = set(guest['id'] for guest in guest_users)
        except json.JSONDecodeError:
            guest_user_ids = set()
        
        # Get valid group member IDs only
        valid_member_ids = set(member['id'] for member in members)
        
        # Process item selections
        selected_items = []
        total_amount = 0
        
        for i, item in enumerate(receipt_analysis['items']):
            # Check if this item is in split mode
            is_split_mode = f'item_{i}_split' in request.form
            
            selected_by = []
            
            if is_split_mode:
                # Split mode - use checkboxes
                checkbox_users = request.form.getlist(f'item_{i}_users')
                if checkbox_users:
                    selected_by = [int(user_id) for user_id in checkbox_users]
            else:
                # Single user mode - use dropdown
                dropdown_user = request.form.get(f'item_{i}_user')
                if dropdown_user:
                    selected_by = [int(dropdown_user)]
            
            if selected_by:
                # Filter out guest users - only include actual group members in expense calculations
                group_members_only = [user_id for user_id in selected_by if user_id in valid_member_ids]
                
                if group_members_only:  # Only create expense if group members are involved
                    # Calculate individual share for this single item
                    try:
                        price = float(item.get('price', 0))
                        
                        # Calculate individual share based on group members only (ignore guests for debt tracking)
                        individual_share = round(price / len(group_members_only), 2)
                        
                        selected_items.append({
                            'name': item['name'],
                            'price': price,
                            'selected_by': group_members_only,  # Only group members for expense tracking
                            'individual_share': individual_share,
                            'is_split': is_split_mode
                        })
                        total_amount += price
                    except (ValueError, TypeError, ZeroDivisionError) as e:
                        flash(f'Error processing item {item.get("name", "Unknown")}: {str(e)}', 'error')
                        conn.close()
                        return render_template('groups/select_receipt_items.html', 
                                             group=group, members=members, 
                                             receipt_analysis=receipt_analysis)
        
        if not selected_items:
            flash('Please select at least one item and assign it to users.', 'error')
            conn.close()
            return render_template('groups/select_receipt_items.html', 
                                 group=group, members=members, 
                                 receipt_analysis=receipt_analysis)
        
        # Parse confirmed payments to get user names and amounts
        confirmed_user_payments = {}
        for payment_key in confirmed_payments:
            if '_' in payment_key:
                parts = payment_key.rsplit('_', 1)  # Split from the right to handle names with underscores
                if len(parts) == 2:
                    user_name, amount_str = parts
                    try:
                        amount = float(amount_str)
                        confirmed_user_payments[user_name] = amount
                    except ValueError:
                        continue
        
        # Get user IDs for confirmed payments
        confirmed_user_ids = set()
        for member in members:
            if member['username'] in confirmed_user_payments:
                confirmed_user_ids.add(member['id'])
        
        # Filter out confirmed payments from selected items
        filtered_selected_items = []
        actual_total_amount = 0
        
        for item in selected_items:
            # Remove confirmed users from this item
            remaining_users = [user_id for user_id in item['selected_by'] if user_id not in confirmed_user_ids]
            
            if remaining_users:
                # Recalculate individual share for remaining users
                individual_share = item['price'] / len(remaining_users)
                filtered_selected_items.append({
                    'name': item['name'],
                    'price': item['price'],
                    'selected_by': remaining_users,
                    'individual_share': individual_share,
                    'is_split': item['is_split']
                })
                actual_total_amount += item['price']
        
        # Only create expense if there are remaining unpaid items
        if not filtered_selected_items:
            # All payments were confirmed, no expense to create
            # Clear session data
            session.pop('receipt_analysis', None)
            session.pop('receipt_filename', None)
            
            confirmed_count = len(confirmed_user_payments)
            flash(f'All {confirmed_count} payment(s) have been confirmed! No expense added to the group.', 'success')
            return redirect(url_for('group_detail', group_id=group_id))

        # Create single expense for the remaining unpaid amount
        try:
            cursor = conn.cursor()
            
            # Create the main expense
            store_name = receipt_analysis.get('store_name', 'Receipt')
            cursor.execute('''
                INSERT INTO expenses (group_id, description, amount, paid_by, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (group_id, f"Receipt from {store_name}", actual_total_amount, bill_payer_id, current_user.id, datetime.now().isoformat()))
            
            expense_id = cursor.lastrowid
            
            # Aggregate expense shares per user (to avoid duplicate user_id entries)
            user_shares = {}
            for item in filtered_selected_items:
                for user_id in item['selected_by']:
                    if user_id not in user_shares:
                        user_shares[user_id] = 0
                    user_shares[user_id] += item['individual_share']
            
            # Create expense shares for each user
            for user_id, total_share in user_shares.items():
                cursor.execute('''
                    INSERT INTO expense_shares (expense_id, user_id, amount)
                    VALUES (?, ?, ?)
                ''', (expense_id, user_id, total_share))
            
            conn.commit()
            conn.close()
            
            # Clear session data
            session.pop('receipt_analysis', None)
            session.pop('receipt_filename', None)
            
            # Get payer name for flash message
            payer_name = next((m['username'] for m in members if m['id'] == bill_payer_id), 'Someone')
            
            # Create success message based on confirmed payments
            if confirmed_user_payments:
                confirmed_total = sum(confirmed_user_payments.values())
                flash(f'Receipt processed! {len(confirmed_user_payments)} payment(s) confirmed (€{confirmed_total:.2f}). Expense added for remaining €{actual_total_amount:.2f} paid by {payer_name}.', 'success')
            else:
                flash(f'Successfully added receipt expenses! {payer_name} paid €{actual_total_amount:.2f} total.', 'success')
            
            return redirect(url_for('group_detail', group_id=group_id))
            
        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f'Error adding expenses: {str(e)}', 'error')
            return render_template('groups/select_receipt_items.html', 
                                 group=group, members=members, 
                                 receipt_analysis=receipt_analysis)
    
    # Get bill payer info from session if available
    bill_payer_info = None
    if 'bill_payer_id' in session:
        bill_payer_info = next((m for m in members if m['id'] == session['bill_payer_id']), None)
    
    conn.close()
    return render_template('groups/select_receipt_items.html', 
                         group=group, members=members, 
                         receipt_analysis=receipt_analysis,
                         bill_payer_info=bill_payer_info)

@app.route('/groups/<int:group_id>/expenses/<int:expense_id>')
@login_required
def expense_detail(group_id, expense_id):
    """View detailed information about a specific expense"""
    conn = get_db_connection()
    
    # Check if user is member of group
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        conn.close()
        return redirect(url_for('groups'))
    
    # Get expense details
    expense = conn.execute('''
        SELECT e.*, 
               up.username as paid_by_name, 
               uc.username as created_by_name,
               g.name as group_name
        FROM expenses e
        JOIN users up ON e.paid_by = up.id
        JOIN users uc ON e.created_by = uc.id
        JOIN groups g ON e.group_id = g.id
        WHERE e.id = ? AND e.group_id = ?
    ''', (expense_id, group_id)).fetchone()
    
    if not expense:
        flash('Expense not found.', 'error')
        conn.close()
        return redirect(url_for('group_detail', group_id=group_id))
    
    # Get expense shares (who owes what)
    # Get valid group member IDs for this group
    members = get_group_members(group_id)
    valid_member_ids = [member['id'] for member in members]
    
    expense_shares = conn.execute('''
        SELECT es.*, u.username, u.id as user_id
        FROM expense_shares es
        JOIN users u ON es.user_id = u.id
        WHERE es.expense_id = ? AND es.user_id IN ({})
        ORDER BY u.username
    '''.format(','.join('?' * len(valid_member_ids))), (expense_id,) + tuple(valid_member_ids)).fetchall()
    
    # Get group info for navigation
    group = conn.execute('SELECT * FROM groups WHERE id = ?', (group_id,)).fetchone()
    
    conn.close()
    
    # Convert to dictionaries for template
    expense_dict = dict(expense)
    shares_list = [dict(share) for share in expense_shares]
    group_dict = dict(group)
    
    return render_template('groups/expense_detail.html', 
                         expense=expense_dict, 
                         expense_shares=shares_list,
                         group=group_dict)

@app.route('/groups/<int:group_id>/balance-details')
@login_required
def balance_details(group_id):
    """Show detailed balance calculation breakdown"""
    conn = get_db_connection()
    
    # Check if user is member of group
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        conn.close()
        return redirect(url_for('groups'))
    
    # Get group info
    group = conn.execute('SELECT * FROM groups WHERE id = ?', (group_id,)).fetchone()
    
    # Get all group members
    members = get_group_members(group_id)
    
    # Get all expenses with detailed information
    expenses = conn.execute('''
        SELECT e.*, 
               up.username as paid_by_name, 
               uc.username as created_by_name
        FROM expenses e
        JOIN users up ON e.paid_by = up.id
        JOIN users uc ON e.created_by = uc.id
        WHERE e.group_id = ?
        ORDER BY e.created_at DESC
    ''', (group_id,)).fetchall()
    
    # Get valid group member IDs
    valid_member_ids = [member['id'] for member in members]
    
    # Get all expense shares, but only for valid group members
    expense_shares = conn.execute('''
        SELECT es.*, e.description as expense_description, e.created_at, u.username
        FROM expense_shares es
        JOIN expenses e ON es.expense_id = e.id
        JOIN users u ON es.user_id = u.id
        WHERE e.group_id = ? AND es.user_id IN ({})
        ORDER BY e.created_at DESC, u.username
    '''.format(','.join('?' * len(valid_member_ids))), (group_id,) + tuple(valid_member_ids)).fetchall()
    
    # Get all settlements, but only for valid group members
    settlements = conn.execute('''
        SELECT s.*, 
               up.username as payer_name, 
               ue.username as payee_name
        FROM settlements s
        JOIN users up ON s.payer_id = up.id
        JOIN users ue ON s.payee_id = ue.id
        WHERE s.group_id = ? AND s.payer_id IN ({}) AND s.payee_id IN ({})
        ORDER BY s.created_at DESC
    '''.format(','.join('?' * len(valid_member_ids)), ','.join('?' * len(valid_member_ids))), 
        (group_id,) + tuple(valid_member_ids) + tuple(valid_member_ids)).fetchall()
    
    conn.close()
    
    # Calculate balances for display
    balances = calculate_balances(group_id)
    
    # Organize data by member for detailed view
    member_details = {}
    for member in members:
        member_id = member['id']
        member_details[member_id] = {
            'member': dict(member),
            'balance': balances.get(member_id, 0),
            'expenses_paid': [],
            'expense_shares': [],
            'settlements_made': [],
            'settlements_received': []
        }
    
    # Add expense details
    for expense in expenses:
        paid_by_id = expense['paid_by']
        if paid_by_id in member_details:
            member_details[paid_by_id]['expenses_paid'].append(dict(expense))
    
    # Add expense share details
    for share in expense_shares:
        user_id = share['user_id']
        if user_id in member_details:
            member_details[user_id]['expense_shares'].append(dict(share))
    
    # Add settlement details
    for settlement in settlements:
        payer_id = settlement['payer_id']
        payee_id = settlement['payee_id']
        
        if payer_id in member_details:
            member_details[payer_id]['settlements_made'].append(dict(settlement))
        
        if payee_id in member_details:
            member_details[payee_id]['settlements_received'].append(dict(settlement))
    
    # Calculate summary statistics
    total_expenses = len(expenses)
    total_settlements = len(settlements)
    
    return render_template('groups/balance_details.html', 
                         group=dict(group), 
                         members=members,
                         member_details=member_details,
                         balances=balances,
                         total_expenses=total_expenses,
                         total_settlements=total_settlements)

@app.route('/groups/<int:group_id>/admin', methods=['GET', 'POST'])
@login_required
def group_admin(group_id):
    """Admin dashboard for group creators to manage balances"""
    conn = get_db_connection()
    
    # Check if user is member of group
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('groups'))
    
    # Get group info and check if user is creator
    group = conn.execute('SELECT * FROM groups WHERE id = ?', (group_id,)).fetchone()
    
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('groups'))
    
    if group['created_by'] != current_user.id:
        flash('Only the group creator can access the admin dashboard.', 'error')
        return redirect(url_for('group_detail', group_id=group_id))
    
    # Get members
    members = get_group_members(group_id)
    
    if request.method == 'POST':
        # Handle manual balance adjustment
        try:
            payer_id = int(request.form.get('payer_id'))
            payee_id = int(request.form.get('payee_id'))
            amount = float(request.form.get('amount'))
            description = request.form.get('description', '').strip()
            
            if amount <= 0:
                flash('Amount must be positive.', 'error')
            elif payer_id == payee_id:
                flash('Payer and payee cannot be the same person.', 'error')
            else:
                # Validate that both users are group members
                payer_member = any(m['id'] == payer_id for m in members)
                payee_member = any(m['id'] == payee_id for m in members)
                
                if not payer_member or not payee_member:
                    flash('Invalid payer or payee selection.', 'error')
                else:
                    # Create settlement entry
                    cursor = conn.cursor()
                    settlement_desc = description or 'Manual adjustment by admin'
                    
                    cursor.execute('''
                        INSERT INTO settlements (group_id, payer_id, payee_id, amount, created_at, description)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (group_id, payer_id, payee_id, amount, datetime.now().isoformat(), settlement_desc))
                    
                    conn.commit()
                    
                    payer_name = next((m['username'] for m in members if m['id'] == payer_id), 'Unknown')
                    payee_name = next((m['username'] for m in members if m['id'] == payee_id), 'Unknown')
                    
                    flash(f'Balance adjusted: {payer_name} paid €{amount:.2f} to {payee_name}', 'success')
                    
        except (ValueError, TypeError) as e:
            flash('Invalid input. Please check your entries.', 'error')
    
    # Calculate current balances
    balances = calculate_balances(group_id)
    
    # Get recent settlements for this group
    recent_settlements = conn.execute('''
        SELECT s.*, 
               up.username as payer_name, 
               ue.username as payee_name
        FROM settlements s
        JOIN users up ON s.payer_id = up.id
        JOIN users ue ON s.payee_id = ue.id
        WHERE s.group_id = ?
        ORDER BY s.created_at DESC
        LIMIT 20
    ''', (group_id,)).fetchall()
    
    conn.close()
    
    return render_template('groups/admin.html', 
                         group=group, 
                         members=members, 
                         balances=balances,
                         recent_settlements=recent_settlements)

@app.route('/api/quick-settle', methods=['POST'])
@login_required
def quick_settle():
    """Quick settlement API - mark a debt as paid with one click"""
    try:
        data = request.get_json()
        group_id = data.get('group_id')
        payee_id = data.get('payee_id')
        amount = data.get('amount')
        
        if not all([group_id, payee_id, amount]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        conn = get_db_connection()
        
        # Check if user is member of group
        membership = conn.execute('''
            SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
        ''', (group_id, current_user.id)).fetchone()
        
        if not membership:
            conn.close()
            return jsonify({'error': 'Not authorized'}), 403
        
        # Check if payee is also a member
        payee_membership = conn.execute('''
            SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
        ''', (group_id, payee_id)).fetchone()
        
        if not payee_membership:
            conn.close()
            return jsonify({'error': 'Payee is not a member of this group'}), 400
        
        # Get payee name for response
        payee = conn.execute('''
            SELECT username FROM users WHERE id = ?
        ''', (payee_id,)).fetchone()
        
        if not payee:
            conn.close()
            return jsonify({'error': 'Payee not found'}), 404
        
        # Record the settlement
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO settlements (group_id, payer_id, payee_id, amount, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (group_id, current_user.id, payee_id, amount, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Payment of €{amount:.2f} to {payee["username"]} recorded successfully',
            'amount': amount,
            'payee': payee['username']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_payment_qr')
@login_required
def generate_payment_qr():
    """Generate EPC QR code for payment"""
    try:
        amount = float(request.args.get('amount', 0))
        payer_id = int(request.args.get('payer_id'))
        reference = request.args.get('reference', f'Payment from {current_user.username}')
        
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Get payer's bank details
        conn = get_db_connection()
        payer = conn.execute('''
            SELECT full_name, iban, bic FROM users WHERE id = ?
        ''', (payer_id,)).fetchone()
        conn.close()
        
        if not payer:
            return jsonify({'error': 'Payer not found'}), 404
        
        if not payer['iban']:
            return jsonify({'error': 'Payer has no bank details configured'}), 400
        
        # Generate QR code
        qr_data = generate_epc_qr_code(
            amount=amount,
            recipient_name=payer['full_name'] or 'Unknown',
            recipient_iban=payer['iban'],
            recipient_bic=payer['bic'],
            reference=reference
        )
        
        if not qr_data:
            return jsonify({'error': 'Failed to generate QR code'}), 500
        
        return jsonify({
            'qr_code': qr_data,
            'amount': amount,
            'recipient': payer['full_name'] or 'Unknown',
            'iban': payer['iban']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/groups/<int:group_id>/settle/<int:payee_id>', methods=['GET', 'POST'])
@login_required
def settle_debt(group_id, payee_id):
    conn = get_db_connection()
    
    # Check if user is member of group
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('groups'))
    
    # Get group and payee info
    group = conn.execute('SELECT * FROM groups WHERE id = ?', (group_id,)).fetchone()
    payee = conn.execute('SELECT * FROM users WHERE id = ?', (payee_id,)).fetchone()
    
    # Calculate current balance
    balances = calculate_balances(group_id)
    current_balance = balances.get(current_user.id, 0)
    
    form = SettlementForm()
    
    if form.validate_on_submit():
        cursor = conn.cursor()
        
        # Record settlement
        cursor.execute('''
            INSERT INTO settlements (group_id, payer_id, payee_id, amount, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (group_id, current_user.id, payee_id, form.amount.data, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        flash(f'Settlement of €{form.amount.data:.2f} recorded!', 'success')
        return redirect(url_for('group_detail', group_id=group_id))
    
    conn.close()
    return render_template('groups/settle.html', 
                         form=form, 
                         group=group, 
                         payee=payee,
                         current_balance=current_balance)

# Group Invitation Routes
@app.route('/groups/<int:group_id>/invite')
@login_required
def group_invite(group_id):
    """Show group invite details for sharing"""
    conn = get_db_connection()
    
    # Check if user is member of group
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('groups'))
    
    # Get group info
    group = conn.execute('SELECT * FROM groups WHERE id = ?', (group_id,)).fetchone()
    conn.close()
    
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('groups'))
    
    invite_link = url_for('join_group', invite_code=group['invite_code'], _external=True)
    
    return render_template('groups/invite.html', group=group, invite_link=invite_link)

@app.route('/groups/<int:group_id>/regenerate_invite', methods=['POST'])
@login_required
def regenerate_invite_code(group_id):
    """Regenerate invite code for a group"""
    conn = get_db_connection()
    
    # Check if user is member of group
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    
    if not membership:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('groups'))
    
    # Generate new invite code
    new_invite_code = generate_invite_code()
    
    conn.execute('''
        UPDATE groups SET invite_code = ? WHERE id = ?
    ''', (new_invite_code, group_id))
    conn.commit()
    conn.close()
    
    flash('New invite code generated!', 'success')
    return redirect(url_for('group_invite', group_id=group_id))

@app.route('/join', methods=['GET', 'POST'])
@login_required
def join_group_form():
    """Form to join a group by entering invite code"""
    if request.method == 'POST':
        invite_code = request.form.get('invite_code', '').strip().upper()
        
        if not invite_code:
            flash('Please enter an invite code.', 'error')
            return render_template('groups/join.html')
        
        return redirect(url_for('join_group', invite_code=invite_code))
    
    return render_template('groups/join.html')

@app.route('/join/<invite_code>')
def join_group(invite_code):
    """Join a group using invite code"""
    if not current_user.is_authenticated:
        session['join_invite_code'] = invite_code
        flash('Please log in to join the group.', 'info')
        return redirect(url_for('login'))
    
    # Get group by invite code
    group = get_group_by_invite_code(invite_code)
    
    if not group:
        flash('Invalid invite code.', 'error')
        return redirect(url_for('groups'))
    
    # Check if user is already a member
    if is_user_in_group(current_user.id, group['id']):
        flash(f'You are already a member of "{group["name"]}".', 'info')
        return redirect(url_for('group_detail', group_id=group['id']))
    
    # Add user to group
    if add_user_to_group(current_user.id, group['id']):
        flash(f'Successfully joined "{group["name"]}"!', 'success')
        return redirect(url_for('group_detail', group_id=group['id']))
    else:
        flash('Failed to join group. Please try again.', 'error')
        return redirect(url_for('groups'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Handle bank details update
        full_name = request.form.get('full_name', '').strip()
        iban = request.form.get('iban', '').strip()
        bic = request.form.get('bic', '').strip()
        
        # Update user bank details
        conn = get_db_connection()
        try:
            conn.execute('''
                UPDATE users 
                SET full_name = ?, iban = ?, bic = ?
                WHERE id = ?
            ''', (full_name, iban, bic, current_user.id))
            conn.commit()
            flash('Bank details updated successfully!', 'success')
        except Exception as e:
            flash('Error updating bank details. Please try again.', 'error')
            print(f"Error updating bank details: {e}")
        finally:
            conn.close()
        
        return redirect(url_for('settings'))
    
    # GET request - load current bank details
    conn = get_db_connection()
    user_data = conn.execute('''
        SELECT full_name, iban, bic 
        FROM users 
        WHERE id = ?
    ''', (current_user.id,)).fetchone()
    conn.close()
    
    bank_details = {
        'full_name': user_data['full_name'] if user_data and user_data['full_name'] else '',
        'iban': user_data['iban'] if user_data and user_data['iban'] else '',
        'bic': user_data['bic'] if user_data and user_data['bic'] else ''
    }
    
    return render_template('settings.html', bank_details=bank_details)

# PWA Routes
@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/sw.js')
def service_worker():
    response = app.send_static_file('sw.js')
    # Force no cache for service worker - critical for updates
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = ''
    response.headers['ETag'] = ''
    return response

@app.route('/offline')
def offline():
    return render_template('offline.html')

# API Routes
@app.route('/api/groups/<int:group_id>/balances')
@login_required
def api_group_balances(group_id):
    conn = get_db_connection()
    membership = conn.execute('''
        SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?
    ''', (group_id, current_user.id)).fetchone()
    conn.close()
    
    if not membership:
        return jsonify({'error': 'Not authorized'}), 403
    
    balances = calculate_balances(group_id)
    simplified_debts = simplify_debts(balances)
    
    return jsonify({
        'balances': balances,
        'simplified_debts': simplified_debts
    })

@app.route('/api/user/stats')
@login_required
def api_user_stats():
    """Get user statistics for profile page"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'member_since': current_user.created_at.isoformat() if hasattr(current_user.created_at, 'isoformat') else str(current_user.created_at)
    })

@app.route('/api/dashboard/summary')
@login_required
def api_dashboard_summary():
    groups = get_user_groups(current_user.id)
    
    total_you_owe = 0
    total_owed_to_you = 0
    group_balances = []
    
    for group in groups:
        balances = calculate_balances(group['id'])
        user_balance = balances.get(current_user.id, 0)
        
        group_balances.append({
            'group_id': group['id'],
            'group_name': group['name'],
            'balance': user_balance
        })
        
        if user_balance < 0:
            total_you_owe += abs(user_balance)
        else:
            total_owed_to_you += user_balance
    
    return jsonify({
        'total_you_owe': round(total_you_owe, 2),
        'total_owed_to_you': round(total_owed_to_you, 2),
        'group_balances': group_balances,
        'net_balance': round(total_owed_to_you - total_you_owe, 2)
    })

@app.route('/privacy-policy')
def privacy_policy():
    """Privacy policy page"""
    return render_template('privacy_policy.html')

@app.route('/debug/email-config')
def debug_email_config():
    """Debug route to check email configuration (development only)"""
    if not app.debug and os.environ.get('FLASK_ENV') != 'development':
        return "Debug routes only available in development mode", 403
    
    config_info = {
        'MAIL_SERVER': app.config.get('MAIL_SERVER'),
        'MAIL_PORT': app.config.get('MAIL_PORT'),
        'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
        'MAIL_USE_SSL': app.config.get('MAIL_USE_SSL'),
        'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
        'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER'),
        'MAIL_PASSWORD_SET': bool(app.config.get('MAIL_PASSWORD')),
    }
    
    return jsonify({
        'email_config': config_info,
        'sender_available': bool(app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME')),
        'ready_to_send': all([
            config_info['MAIL_SERVER'],
            config_info['MAIL_USERNAME'],
            config_info['MAIL_PASSWORD_SET']
        ])
    })

if __name__ == '__main__':
    init_db()
    ensure_upload_folder()
    app.run(debug=True, host='0.0.0.0', port=3000)
