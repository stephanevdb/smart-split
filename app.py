from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, FloatField, SelectField, TextAreaField, SelectMultipleField, RadioField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from wtforms.widgets import CheckboxInput, ListWidget
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import uuid
from datetime import datetime
from collections import defaultdict
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['DATABASE'] = 'splitwise.db'

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
                (username, email, password_hash, datetime.now())
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
            created_at TIMESTAMP NOT NULL
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
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
            FOREIGN KEY (payer_id) REFERENCES users (id),
            FOREIGN KEY (payee_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Migrate existing groups to have invite codes
    migrate_existing_groups()

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
    
    # Get all expenses and their shares
    expenses = conn.execute('''
        SELECT e.id, e.amount, e.paid_by, es.user_id, es.amount as share_amount
        FROM expenses e
        JOIN expense_shares es ON e.id = es.expense_id
        WHERE e.group_id = ?
    ''', (group_id,)).fetchall()
    
    # Get all settlements
    settlements = conn.execute('''
        SELECT payer_id, payee_id, amount
        FROM settlements
        WHERE group_id = ?
    ''', (group_id,)).fetchall()
    
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
        ''', (group_id, user_id, datetime.now()))
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

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        groups = get_user_groups(current_user.id)
        return render_template('index.html', groups=groups)
    return render_template('index.html')

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
        ''', (form.name.data, form.description.data, current_user.id, invite_code, datetime.now()))
        
        group_id = cursor.lastrowid
        
        # Add creator as member
        cursor.execute('''
            INSERT INTO group_members (group_id, user_id, joined_at)
            VALUES (?, ?, ?)
        ''', (group_id, current_user.id, datetime.now()))
        
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
              form.paid_by.data, current_user.id, datetime.now()))
        
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
        ''', (group_id, current_user.id, payee_id, form.amount.data, datetime.now()))
        
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

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

# PWA Routes
@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/sw.js')
def service_worker():
    return app.send_static_file('sw.js')

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=3000)
