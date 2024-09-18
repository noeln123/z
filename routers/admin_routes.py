from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Ambulance, Driver, EmergencyRequest
from forms import UpdateAmbulanceForm
from . import admin_bp

def admin_required(f):
    from functools import wraps
    from flask import abort
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('user.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin_dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Truy vấn dữ liệu tổng quan
    total_ambulances = Ambulance.query.count()
    total_drivers = Driver.query.count()
    total_emergency_requests = EmergencyRequest.query.count()
    
    # Các yêu cầu khẩn cấp theo trạng thái
    pending_requests = EmergencyRequest.query.filter_by(status='Pending').count()
    dispatched_requests = EmergencyRequest.query.filter_by(status='Dispatched').count()
    on_the_way_requests = EmergencyRequest.query.filter_by(status='On the way').count()
    arrived_requests = EmergencyRequest.query.filter_by(status='Arrived').count()
    transporting_requests = EmergencyRequest.query.filter_by(status='Transporting').count()
    
    # Truy vấn danh sách yêu cầu khẩn cấp gần đây
    recent_requests = EmergencyRequest.query.order_by(EmergencyRequest.id.desc()).limit(10).all()
    
    # Truy vấn danh sách xe cứu thương đang hoạt động (join với EM có status 'Transporting', 'On the way', )
    statuses = ['On the way', 'Transporting']
    active_ambulances = Ambulance.query.join(EmergencyRequest).filter(EmergencyRequest.status.in_(statuses)).all()
    
    return render_template('admin_dashboard.html',
                           total_ambulances=total_ambulances,
                           total_drivers=total_drivers,
                           total_emergency_requests=total_emergency_requests,
                           pending_requests=pending_requests,
                           dispatched_requests=dispatched_requests,
                           on_the_way_requests=on_the_way_requests,
                           arrived_requests=arrived_requests,
                           transporting_requests=transporting_requests,
                           recent_requests=recent_requests,
                           active_ambulances=active_ambulances)



@admin_bp.route('/manage_ambulances', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_ambulances():
    ambulances = Ambulance.query.all()
    return render_template('manage_ambulances.html', ambulances=ambulances)

@admin_bp.route('/add_ambulance', methods=['GET', 'POST'])
@login_required
@admin_required
def add_ambulance():
    form = UpdateAmbulanceForm()
    form.driver_id.choices = [(driver.id, driver.name) for driver in Driver.query.all()]
    if form.validate_on_submit():
        ambulance = Ambulance(
            ambulance_type=form.ambulance_type.data,
            size=form.size.data,
            equipment=form.equipment.data,
            driver_id=form.driver_id.data
        )
        db.session.add(ambulance)
        db.session.commit()
        flash('Xe cứu thương đã được thêm.', 'success')
        return redirect(url_for('admin.manage_ambulances'))
    return render_template('add_ambulance.html', form=form)

@admin_bp.route('/edit_ambulance/<int:ambulance_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_ambulance(ambulance_id):
    ambulance = Ambulance.query.get_or_404(ambulance_id)
    form = UpdateAmbulanceForm(obj=ambulance)
    form.driver_id.choices = [(driver.id, driver.name) for driver in Driver.query.all()]
    if form.validate_on_submit():
        ambulance.ambulance_type = form.ambulance_type.data
        ambulance.size = form.size.data
        ambulance.equipment = form.equipment.data
        ambulance.driver_id = form.driver_id.data
        db.session.commit()
        flash('Thông tin xe cứu thương đã được cập nhật.', 'success')
        return redirect(url_for('admin.manage_ambulances'))
    return render_template('edit_ambulance.html', form=form, ambulance=ambulance)

@admin_bp.route('/delete_ambulance/<int:ambulance_id>', methods=['POST'])
@login_required
@admin_required
def delete_ambulance(ambulance_id):
    ambulance = Ambulance.query.get_or_404(ambulance_id)
    db.session.delete(ambulance)
    db.session.commit()
    flash('Xe cứu thương đã được xóa.', 'success')
    return redirect(url_for('admin.manage_ambulances'))

@admin_bp.route('/manage_drivers', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_drivers():
    drivers = Driver.query.all()
    return render_template('manage_drivers.html', drivers=drivers)

@admin_bp.route('/add_driver', methods=['GET', 'POST'])
@login_required
@admin_required
def add_driver():
    from forms import DriverForm  # Tạo một form mới cho Driver
    form = DriverForm()
    if form.validate_on_submit():
        driver = Driver(
            name=form.name.data,
            contact_info=form.contact_info.data,
            location=form.location.data
        )
        db.session.add(driver)
        db.session.commit()
        flash('Tài xế đã được thêm.', 'success')
        return redirect(url_for('admin.manage_drivers'))
    return render_template('add_driver.html', form=form)

@admin_bp.route('/edit_driver/<int:driver_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    from forms import DriverForm  # Tạo một form mới cho Driver
    form = DriverForm(obj=driver)
    if form.validate_on_submit():
        driver.name = form.name.data
        driver.contact_info = form.contact_info.data
        driver.location = form.location.data
        db.session.commit()
        flash('Thông tin tài xế đã được cập nhật.', 'success')
        return redirect(url_for('admin.manage_drivers'))
    return render_template('edit_driver.html', form=form, driver=driver)

@admin_bp.route('/delete_driver/<int:driver_id>', methods=['POST'])
@login_required
@admin_required
def delete_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    db.session.delete(driver)
    db.session.commit()
    flash('Tài xế đã được xóa.', 'success')
    return redirect(url_for('admin.manage_drivers'))

@admin_bp.route('/dispatch_control/<int:request_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def dispatch_control(request_id):
    emergency_request = EmergencyRequest.query.get_or_404(request_id)
    ambulances = Ambulance.query.filter_by(status='Available').all()
    if request.method == 'POST':
        ambulance_id = request.form.get('ambulance_id')
        ambulance = Ambulance.query.get(ambulance_id)
        if ambulance:
            emergency_request.ambulance_id = ambulance.id
            emergency_request.status = 'Dispatched'
            # Cập nhật trạng thái xe cứu thương nếu cần
            db.session.commit()
            flash('Xe cứu thương đã được chỉ định.', 'success')
            return redirect(url_for('admin.admin_dashboard'))
    return render_template('dispatch_control.html', emergency_request=emergency_request, ambulances=ambulances)

@admin_bp.route('/real_time_monitor')
@login_required
@admin_required
def real_time_monitor():
    emergency_requests = EmergencyRequest.query.filter_by(status='Dispatched').all()
    return render_template('real_time_monitor.html', emergency_requests=emergency_requests)

@admin_bp.route('/send_message', methods=['POST'])
@login_required
@admin_required
def send_message():
    # Xử lý gửi tin nhắn đến EMT hoặc người dùng
    # Bạn có thể sử dụng các công cụ như Flask-Mail hoặc tích hợp API gửi tin nhắn
    flash('Tin nhắn đã được gửi.', 'success')
    return redirect(url_for('admin.admin_dashboard'))
