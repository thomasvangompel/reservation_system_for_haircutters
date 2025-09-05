from flask import render_template, redirect, url_for, request, session, flash
from app.models import db, User, Customer, CalendarEvent, Skill, Reservation
from flask import Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText

main = Blueprint('main', __name__)

@main.route('/reservation', methods=['GET', 'POST'])
def reservation():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    import datetime
    skills = Skill.query.filter_by(user_id=user_id).all()
    events = CalendarEvent.query.filter_by(user_id=user_id).all()
    # Generate available blocks for each skill
    for skill in skills:
        interval = skill.duration if skill.duration else 15  # default to 15 min if not set
        available_blocks = []
        for event in events:
            if event.start_time and event.end_time:
                def time_to_minutes(t):
                    h, m = map(int, t.split(':'))
                    return h * 60 + m
                def minutes_to_time(m):
                    h = m // 60
                    m = m % 60
                    return f"{h:02d}:{m:02d}"
                start = time_to_minutes(event.start_time)
                end = time_to_minutes(event.end_time)
                # Build a list of all possible block starts
                block_starts = list(range(start, end, interval))
                for block_start in block_starts:
                    block_end = block_start + skill.duration
                    if block_end > end:
                        continue  # Not enough time left in this event
                    # Check if all sub-blocks are free
                    is_free = True
                    for check_start in range(block_start, block_end, interval):
                        check_end = check_start + interval
                        block_str = f"{event.date} {minutes_to_time(check_start)} - {minutes_to_time(check_end)}"
                        reserved = Reservation.query.filter_by(user_id=user_id, block=block_str).first()
                        if reserved:
                            is_free = False
                            break
                    if is_free:
                        block_str = f"{event.date} {minutes_to_time(block_start)} - {minutes_to_time(block_end)}"
                        available_blocks.append(block_str)
        skill.available_times = available_blocks
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        skill_id = request.form.get('skill_id')
        block = request.form.get('block')
        # Save reservation
        new_res = Reservation(customer_name=customer_name, customer_email=customer_email, skill_id=skill_id, block=block, user_id=user_id)
        db.session.add(new_res)
        # Remove reserved block from CalendarEvent
        block_date, times = block.split(' ', 1)
        start_time, end_time = times.split(' - ')
        # Find and delete the reserved event
        reserved_event = CalendarEvent.query.filter_by(user_id=user_id, date=block_date, start_time=start_time, end_time=end_time).first()
        if reserved_event:
            db.session.delete(reserved_event)
        # Remove overlapping blocks if skill duration is longer than the block
        skill = Skill.query.get(skill_id)
        if skill and skill.duration:
            # Convert times to minutes
            def time_to_minutes(t):
                h, m = map(int, t.split(':'))
                return h * 60 + m
            block_start = time_to_minutes(start_time)
            block_end = block_start + skill.duration
            overlapping_events = CalendarEvent.query.filter_by(user_id=user_id, date=block_date).all()
            for event in overlapping_events:
                ev_start = time_to_minutes(event.start_time)
                ev_end = time_to_minutes(event.end_time)
                # If event overlaps with reserved block
                if (ev_start < block_end and ev_end > block_start):
                    db.session.delete(event)
        db.session.commit()
        # Send email to customer
        send_reservation_email(customer_email, block)
        flash(f'Reservation for {customer_name} at {block} has been saved and an email has been sent to {customer_email}!')
        return redirect(url_for('main.thankyou'))
    return render_template('reservation.html', skills=skills)

def send_reservation_email(to_email, block):
    # Gmail SMTP configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'yourgmail@gmail.com'  # Replace with your Gmail address
    smtp_pass = 'your_app_password'    # Use an App Password, not your main Gmail password
    msg = MIMEText(f'Your reservation is confirmed for {block}.')
    msg['Subject'] = 'Reservation Confirmation'
    msg['From'] = smtp_user
    msg['To'] = to_email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
    except Exception as e:
        print('Email error:', e)

@main.route('/agenda')
def agenda():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
    return render_template('agenda.html', reservations=reservations)

@main.route('/bulk_delete_availability', methods=['POST'])
def bulk_delete_availability():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    ids = request.form.getlist('delete_ids')
    if ids:
        for event_id in ids:
            event = CalendarEvent.query.get(event_id)
            if event and event.user_id == session['user_id']:
                db.session.delete(event)
        db.session.commit()
        flash('Selected availabilities deleted!')
    else:
        flash('No availabilities selected!')
    return redirect(url_for('main.calendar'))

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('User already exists!')
            return redirect(url_for('main.register'))
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials!')
    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return render_template('dashboard.html', username=session['username'])

@main.route('/customers', methods=['GET', 'POST'])
def customers():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        new_customer = Customer(name=name, phone=phone, user_id=user_id)
        db.session.add(new_customer)
        db.session.commit()
        flash('Customer added!')
    customer_list = Customer.query.filter_by(user_id=user_id).all()
    return render_template('customers.html', customers=customer_list)

@main.route('/calendar', methods=['GET', 'POST'])
def calendar():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = 5
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        selected_days = request.form.get('selected_days')
        if selected_days:
            import datetime
            days = selected_days.split(',')
            base_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            weekday_map = {
                'Monday': 0,
                'Tuesday': 1,
                'Wednesday': 2,
                'Thursday': 3,
                'Friday': 4,
                'Saturday': 5,
                'Sunday': 6
            }
            for day in days:
                # Find next date for each selected weekday
                day_num = weekday_map[day]
                delta_days = (day_num - base_date.weekday()) % 7
                target_date = base_date + datetime.timedelta(days=delta_days)
                new_event = CalendarEvent(title=title, date=target_date.strftime("%Y-%m-%d"), start_time=start_time, end_time=end_time, user_id=user_id)
                db.session.add(new_event)
            db.session.commit()
            flash('Availability added for selected days!')
        else:
            new_event = CalendarEvent(title=title, date=date, start_time=start_time, end_time=end_time, user_id=user_id)
            db.session.add(new_event)
            db.session.commit()
            flash('Availability added!')
    events = CalendarEvent.query.filter_by(user_id=user_id).order_by(CalendarEvent.date, CalendarEvent.start_time).paginate(page=page, per_page=per_page)
    return render_template('calendar.html', events=events)

@main.route('/delete_availability/<int:event_id>', methods=['POST'])
def delete_availability(event_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    event = CalendarEvent.query.get_or_404(event_id)
    if event.user_id != session['user_id']:
        flash('Unauthorized!')
        return redirect(url_for('main.calendar'))
    db.session.delete(event)
    db.session.commit()
    flash('Availability deleted!')
    return redirect(url_for('main.calendar'))

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('main.login'))


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.street = request.form.get('street')
        user.postal_code = request.form.get('postal_code')
        user.city = request.form.get('city')
        user.country = request.form.get('country')
        db.session.commit()
        flash('Profile updated!')
    return render_template('profile.html', user=user)

@main.route('/skills', methods=['GET', 'POST'])
def skills():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user_id = session['user_id']
    if request.method == 'POST':
        gender = request.form.get('gender', 'x')
        skill_type = request.form.get('type')
        price = request.form.get('price', type=float)
        duration = request.form.get('duration', type=int)
        image_url = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                image_path = f'static/uploads/{image.filename}'
                image.save(f'app/{image_path}')
                image_url = '/' + image_path
        if gender and skill_type and image_url and price and duration:
            new_skill = Skill(name=skill_type, gender=gender, type=skill_type, image_url=image_url, price=price, duration=duration, user_id=user_id)
            db.session.add(new_skill)
            db.session.commit()
            flash('Skill added!')
    page = request.args.get('page', 1, type=int)
    per_page = 3
    skills = Skill.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)
    return render_template('skills.html', skills=skills)

@main.route('/delete_skill/<int:skill_id>', methods=['POST'])
def delete_skill(skill_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != session['user_id']:
        flash('Unauthorized!')
        return redirect(url_for('main.skills'))
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted!')
    return redirect(url_for('main.skills'))

@main.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')