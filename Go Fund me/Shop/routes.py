from flask import render_template, request, redirect, url_for, flash, request
from Shop import app, db, cloudinary, bcrypt
from Shop.forms import RegistrationForm, LoginForm
from Shop.models import User, Data, UserRequest, Fund, Donator
from flask_login import login_user, current_user, logout_user, login_required
import random
from flask_mail import Message
from Shop import mail



# Creating random One-Time-Password
OTP = random.randint(1000, 9999)


# Creating the Homepage route
@app.route('/Index')
@app.route('/')
def Index():    
    return render_template("Index.html")



# Creating the register-user route
@app.route('/register', methods=['GET', 'POST'])
def register():
# Preventing the user from logging in again if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('Index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        send_otp(form.email.data)
        flash(f'Please verify your email', 'success')
        return redirect(url_for('verify_otp', email=form.email.data))
    return render_template('register.html', title='Register', form=form)


# Creating the OTP email
def send_otp(email):
    msg = Message('Verification Token', sender='Anonymous@gmail.com', recipients=[email])
    msg.body = f'Your verification token is: {OTP}'
    mail.send(msg)
    print(f'{OTP}')



# Creating the login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('Index'))
    form = LoginForm()
    
    
    
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('User with provided email not found.', 'danger')
            print('User not found')
            return render_template('login.html', title='Login', form=form)
        
        if not user.is_verified:
            flash('You are yet to be verified', 'danger')
            send_otp(form.email.data)
            return redirect(url_for('verify_otp', email=form.email.data))
        
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'You have been logged in!', 'success')
            if user.is_admin:
                return redirect('admin_view')    
            return redirect(next_page) if next_page else redirect(url_for('show_requests'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            print('Login Failed')

    return render_template('login.html', title='Login', form=form)


# Creating the logout route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('Index'))


# Creating the user-items route
@app.route('/items',  methods=['GET', 'POST'])
@login_required
def items():
    fund_request = Fund.query.first()
    percentage = 0
    if fund_request:
        if fund_request.amount_donated and fund_request.amount_needed:
            percentage = (fund_request.amount_donated / fund_request.amount_needed) * 100

    return render_template('view_request.html', percentage=percentage, fund_request=fund_request)


# Creating the admin route 
@app.route('/admin_users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('You are not authorized to view this page!', 'danger')
        return redirect(url_for('Index'))
    else:
        users = User.query.all()
    return render_template('admin_users.html', users=users)


# Creating the admin route for viewing users
@app.route('/admin_view', methods=['GET', 'POST'])
def admin_view():
    if not current_user.is_admin:
        flash('You are not authorized to perform this action!', 'danger')
        return redirect(url_for('Index'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)


# Creating the admin route for deleting users
@app.route('/admin/delete_user/<int:user_id>/', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin:
        flash('You are not authorized to perform this action!', 'danger')
        return redirect(url_for('admin_users'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin_users'))



# Creating the admin route for viewing user-items
@app.route('/admin/view_user_items/<int:user_id>/', methods=['GET'])
@login_required
def view_user_items(user_id):
    if not current_user.is_admin:
        flash('You are not authorized to view this page!', 'danger')
        return redirect(url_for('admin_users'))

    # user = Donator.query.filter_by(user_id=user_id).all()
    # if not user:
    #     flash('User not found!', 'danger')
    #     return redirect(url_for('admin_users'))
    news = {}
    funds = Fund.query.filter_by(user_id=user_id).all()
    for fund in funds:
        donations = Donator.query.filter_by(donating_for=fund.id).all()
        news[fund] = donations
    print("doantions", donations)
    return render_template('user_items.html', donations=news)




# Creating the verify OTP for registering users
@app.route('/verify_otp/<string:email>/', methods=['GET', 'POST'])
def verify_otp(email):
    if request.method == 'POST':
        otp = request.form.get('otp')
        user = User.query.filter_by(email=email).first()
        if int(otp) != OTP:
            flash('Invalid OTP', 'danger')
            return redirect(url_for('verify_otp', email=email))
        user.is_verified = True
        db.session.commit()
        flash('Email verified successfully', 'success')
        return redirect(url_for('login'))
    return render_template('otp.html')



@app.route('/thanks')
def thanks():
    return render_template('thanks.html')



@app.route('/view_request')
@login_required
def view_request():
    
    all_percentage = {}
    fund_request = Fund.query.filter_by(user_id=current_user.id).all()
    for funds in fund_request:
        
        percentage = 0
        if funds:
            if funds.amount_donated and funds.amount_needed:
                percentage = round((funds.amount_donated / funds.amount_needed) * 100, 2)
                all_percentage[percentage] = funds

    return render_template('view_request.html', percentages=all_percentage)
    # return render_template('view_request.html')


# @app.route('/donate', methods=['GET'])
# def donate():
#     return render_template('donate.html')


@app.route('/show_requests', methods=['GET'])
def show_requests():
    return render_template('show_requests.html')



@app.route('/help', methods=['GET', 'POST'])
@login_required
def help():
    if request.method == 'POST':
        reason = request.form.get('reason')
        amount_needed = float(request.form.get('amount_needed'))
        new_request = Fund(reason=reason, amount_needed=amount_needed, user_id=current_user.id)
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('help'))

    fund_request = Fund.query.first()
    percentage = 0
    if fund_request:
        if fund_request.amount_donated and fund_request.amount_needed:
            percentage = (fund_request.amount_donated / fund_request.amount_needed) * 100

    return render_template('help.html', percentage=percentage, fund_request=fund_request)

@app.route('/donate/<fund_id>', methods=['GET','POST'])
def donate(fund_id):
    fund_request = Fund.query.get(fund_id)
    # Percentage Calculation
    # fund_request = Fund.query.first()
    percentage = 0
    if fund_request:
        if fund_request.amount_donated and fund_request.amount_needed:
            percentage = (fund_request.amount_donated / fund_request.amount_needed) * 100
    
    if not fund_request:
        flash('Fund request not found.', 'danger')
        return redirect(url_for('Index'))
    

    # Check if the amount needed has already been met
    # if fund_request.amount_donated >= fund_request.amount_needed:
    #     # flash('Thank you for your willingness to donate! However, the required amount has already been met.', 'info')
    #     return redirect(url_for('view_request'))

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        
        # Check if this donation would exceed the required amount
        if (fund_request.amount_donated + amount) > fund_request.amount_needed:
            flash('Your donation would exceed the required amount. Please adjust the amount.', 'warning')
            return redirect(url_for('donate', fund_id=fund_id, host_url=request.url_root))
        
        name = request.form.get('name')
        donator = Donator(name=name, donation_amount=amount, donating_for=fund_id)
        db.session.add(donator)
        fund_request.amount_donated += amount
        db.session.commit()
        flash(f'You have donated ${amount} successfully', 'success')
        return redirect(url_for('donate', fund_id=fund_id, user_id=fund_id, host_url=request.url_root))
    
    return render_template('donate.html', percentage=percentage, user_id=fund_id, host_url=request.url_root, fund_request=fund_request)


@app.route('/show_help', methods=['GET'])
def show_help():
    funds = Fund.query.all()
    return render_template('show_help.html', funds=funds)

@app.route('/leave')
def leave():
    return render_template('leave.html')