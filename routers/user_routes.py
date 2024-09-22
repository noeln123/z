from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, socketio
from models import User, Profile, EmergencyRequest, Feedback, ContactMessage, Driver, Ambulance, Setting
from forms import RegistrationForm, LoginForm, EmergencyRequestForm, FeedbackForm, ProfileForm, ContactForm, CancelEmergencyForm
from . import user_bp 
import time

@user_bp.route('/')
def home():
    if current_user.is_authenticated:
        existing_em = EmergencyRequest.query.filter_by(user_id=current_user.id).filter(EmergencyRequest.status != 'Arrived', EmergencyRequest.status != 'Canceled').first()
    else:
        existing_em = None
    return render_template('home.html', existing_em=existing_em)

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, role='user')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can log in now.', 'success')
        return redirect(url_for('user.login'))
    return render_template('register.html', form=form)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('user.home'))
        else:
            flash('Incorrect email or password.', 'danger')
    return render_template('login.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out.', 'info')
    return redirect(url_for('user.home'))

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if request.method == 'GET':
        if current_user.profile:
            form.full_name.data = current_user.profile.full_name
            form.phone_number.data = current_user.profile.phone_number
            form.address.data = current_user.profile.address
            form.medical_history.data = current_user.profile.medical_history
            form.allergies.data = current_user.profile.allergies
            form.emergency_contact.data = current_user.profile.emergency_contact
    if form.validate_on_submit():
        if current_user.profile:
            profile = current_user.profile
            profile.full_name = form.full_name.data
            profile.phone_number = form.phone_number.data
            profile.address = form.address.data
            profile.medical_history = form.medical_history.data
            profile.allergies = form.allergies.data
            profile.emergency_contact = form.emergency_contact.data
        else:
            profile = Profile(
                full_name=form.full_name.data,
                phone_number=form.phone_number.data,
                address=form.address.data,
                medical_history=form.medical_history.data,
                allergies=form.allergies.data,
                emergency_contact=form.emergency_contact.data,
                user=current_user
            )
            db.session.add(profile)
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('user.profile'))
    return render_template('profile.html', form=form)

@user_bp.route('/emergency_request', methods=['GET', 'POST'])
@login_required
def emergency_request():
    form = EmergencyRequestForm()

    existing_em = EmergencyRequest.query.filter_by(user_id=current_user.id).filter(EmergencyRequest.status != 'Arrived', EmergencyRequest.status != 'Canceled').first()
    if existing_em:
        flash('You have having an Emergency Request.', 'warning')
        return redirect(url_for('user.track_emergency', emergency_id=existing_em.id))

    if current_user.profile:
        form.user_phone.data = current_user.profile.phone_number
        form.pickup_address.data = current_user.profile.address

    if form.validate_on_submit():
        if form.request_type.data == 'Emergency':
            form.hospital_name.data = "Auto Find"
            form.hospital_address.data = "Auto Find"
            form.pickup_address.data = "Auto Find"

        request = EmergencyRequest(
            hospital_name=form.hospital_name.data,
            hospital_address=form.hospital_address.data,
            user_phone=form.user_phone.data,
            pickup_address=form.pickup_address.data,
            request_type=form.request_type.data,
            user_id=current_user.id
        )
        db.session.add(request)
        db.session.commit()

        auto_dispatch_setting = Setting.query.filter_by(key='auto_dispatch').first()
        if auto_dispatch_setting and auto_dispatch_setting.value == 'True':
            print("TU DONG DIEU PHIOIIIIII")
            dispatch_emergency_request(request)


        flash('Emergency request submitted.', 'success')
        return redirect(url_for('user.home'))
    return render_template("emergency_request.html", form=form)
    # return render_template('emergency_request.html', form=form)


@user_bp.route('/cancel_emergency/<int:emergency_id>', methods=['POST'])
@login_required
def cancel_emergency(emergency_id):
    form = CancelEmergencyForm()
    if form.validate_on_submit():
        emergency = EmergencyRequest.query.get_or_404(emergency_id)
        
        if emergency.user_id != current_user.id:
            flash('You do not have the right to cancel this Emergency Request.', 'danger')
            return redirect(url_for('user.track_emergency'))
        
        if emergency.status == 'Pending':
            emergency.status = 'Canceled'
            db.session.commit()
            flash('Emergency Request has been successfully canceled.', 'success')
        else:
            flash('Emergency Requests can only be canceled in state "Pending".', 'warning')
        
        return redirect(url_for('user.track_emergency'))
    else:
        flash('Invalid data.', 'danger')
        return redirect(url_for('user.track_emergency'))



@user_bp.route('/track_emergency')
@login_required
def track_emergency():
    current_em = EmergencyRequest.query.filter_by(user_id=current_user.id)\
        .filter(EmergencyRequest.status.notin_(['Arrived', 'Canceled']))\
        .first()
    
    form = CancelEmergencyForm() if current_em and current_em.status == 'Pending' else None
    
    return render_template('track_emergency.html', request=current_em, ambulance=current_em.ambulance if current_em else None, form=form)

@user_bp.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(
            user_id=current_user.id,
            message=form.message.data
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('user.home'))
    return render_template('feedback.html', form=form)

@user_bp.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    form = ContactForm()
    if form.validate_on_submit():
        contact_message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(contact_message)
        db.session.commit()
        flash('Your message has been sent. Thank you!', 'success')
        return redirect(url_for('user.contact_us'))
    return render_template('contact_us.html', form=form)

@user_bp.route('/about_us')
def about_us():
    return render_template('about_us.html')

@user_bp.route('/gallery')
def gallery():
    return render_template('gallery.html')

@user_bp.route('/ambulance_list')
def ambulance_types():
    ambulances = Ambulance.query.all()
    return render_template('ambulance_list.html', ambulances=ambulances)

@user_bp.route('/costs')
def costs():
    return render_template('costs.html')

@user_bp.route('/driver_list')
def driver_list():
    drivers = Driver.query.all()
    return render_template('driver_list.html', drivers=drivers)





def dispatch_emergency_request(emergency_request):
    available_ambulance = Ambulance.query.filter_by(status='Available').first()
    if available_ambulance:
        emergency_request.ambulance_id = available_ambulance.id
        emergency_request.status = 'Dispatched'
        available_ambulance.status = 'Unavailable'
        db.session.commit()

        room = f'emergency_{emergency_request.id}'
        print(f"admin update {room}")
        socketio.emit('status_update', {'status': emergency_request.status}, room=room)
        time.sleep(0.2)
        socketio.emit('status_update', {'status': emergency_request.status}, room=room)


        #Phân phối tới các EMTs phù hợp
        # room = f"emt_{emt.id}"
        room = "emt_2_getdispatch"
        dispatch_data = {
            'id': emergency_request.id,
            'hospital_name': emergency_request.hospital_name,
            'hospital_address': emergency_request.hospital_address,
            'user_phone': emergency_request.user_phone,
            'pickup_address': emergency_request.pickup_address,
            'request_type': emergency_request.request_type,
            'status': emergency_request.status,
        }
        socketio.emit('dispatch', dispatch_data, room=room)
