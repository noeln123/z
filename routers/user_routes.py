from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Profile, EmergencyRequest, Feedback
from forms import RegistrationForm, LoginForm, EmergencyRequestForm, FeedbackForm, ProfileForm, ContactForm
from . import user_bp  # Sử dụng relative import

@user_bp.route('/')
def home():
    return render_template('home.html')

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
        flash('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
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
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('user.home'))
        else:
            flash('Email hoặc mật khẩu không đúng.', 'danger')
    return render_template('login.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
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
        flash('Hồ sơ đã được cập nhật.', 'success')
        return redirect(url_for('user.profile'))
    return render_template('profile.html', form=form)

@user_bp.route('/emergency_request', methods=['GET', 'POST'])
@login_required
def emergency_request():
    form = EmergencyRequestForm()
    if form.validate_on_submit():
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
        flash('Yêu cầu khẩn cấp đã được gửi.', 'success')
        return redirect(url_for('user.home'))
    return render_template('emergency_request.html', form=form)

@user_bp.route('/track_emergency/<int:request_id>')
@login_required
def track_emergency(request_id):
    request_obj = EmergencyRequest.query.get_or_404(request_id)
    ambulance = request_obj.ambulance
    # Giả sử bạn có một hàm để lấy vị trí hiện tại của xe cứu thương
    # current_location = get_current_location(ambulance.id)
    return render_template('track_emergency.html', request=request_obj, ambulance=ambulance)

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
        flash('Cảm ơn phản hồi của bạn!', 'success')
        return redirect(url_for('user.home'))
    return render_template('feedback.html', form=form)

@user_bp.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    form = ContactForm()
    if form.validate_on_submit():
        # Xử lý lưu hoặc gửi email
        flash('Tin nhắn của bạn đã được gửi. Cảm ơn!', 'success')
        return redirect(url_for('user.home'))
    return render_template('contact_us.html', form=form)

@user_bp.route('/about_us')
def about_us():
    return render_template('about_us.html')

@user_bp.route('/gallery')
def gallery():
    return render_template('gallery.html')

@user_bp.route('/ambulance_types')
def ambulance_types():
    ambulances = Ambulance.query.all()
    return render_template('ambulance_types.html', ambulances=ambulances)

@user_bp.route('/costs')
def costs():
    # Giả sử bạn có bảng hoặc cấu hình để lưu thông tin chi phí
    return render_template('costs.html')

@user_bp.route('/driver_list')
def driver_list():
    drivers = Driver.query.all()
    return render_template('driver_list.html', drivers=drivers)
