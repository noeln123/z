from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db, socketio
from models import Ambulance, Driver, EmergencyRequest, Setting
from forms import UpdateAmbulanceForm
from . import admin_bp
import time

def admin_required(f):
    from functools import wraps
    from flask import abort
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('user.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin_dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_ambulances = Ambulance.query.count()
    total_drivers = Driver.query.count()
    total_emergency_requests = EmergencyRequest.query.count()
    
    pending_requests = EmergencyRequest.query.filter_by(status='Pending').count()
    dispatched_requests = EmergencyRequest.query.filter_by(status='Dispatched').count()
    on_the_way_requests = EmergencyRequest.query.filter_by(status='On the way').count()
    arrived_requests = EmergencyRequest.query.filter_by(status='Arrived').count()
    transporting_requests = EmergencyRequest.query.filter_by(status='Transporting').count()
    
    recent_requests = EmergencyRequest.query.order_by(EmergencyRequest.id.desc()).limit(10).all()
    
    statuses = ['On the way', 'Transporting']
    active_ambulances = Ambulance.query.join(EmergencyRequest).filter(EmergencyRequest.status.in_(statuses)).all()
    
    # Lấy cài đặt auto_dispatch
    auto_dispatch_setting = Setting.query.filter_by(key='auto_dispatch').first()
    auto_dispatch = auto_dispatch_setting.value if auto_dispatch_setting else 'False'

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
                           active_ambulances=active_ambulances,
                           auto_dispatch=auto_dispatch)

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

    drivers = Driver.query.all()
    form.driver_id.choices = [(driver.id, driver.name) for driver in Driver.query.all()]
    driver_choices = []
    for driver in drivers:
        assigned = Ambulance.query.filter_by(driver_id=driver.id).first()
        is_available = not assigned  # If not assigned, the driver is available
        driver_choices.append((driver.id, driver.name, is_available))

    # form.driver_id.choices = driver_choices

    if form.validate_on_submit():
        ambulance = Ambulance(
            ambulance_type=form.ambulance_type.data,
            size=form.size.data,
            equipment=form.equipment.data,
            driver_id=form.driver_id.data
        )
        db.session.add(ambulance)
        db.session.commit()
        flash('Ambulance has been added.', 'success')
        return redirect(url_for('admin.manage_ambulances'))

    return render_template('add_ambulance.html', form=form, driver_choices=driver_choices)

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
        flash('Ambulance information has been updated.', 'success')
        return redirect(url_for('admin.manage_ambulances'))
    return render_template('edit_ambulance.html', form=form, ambulance=ambulance)

@admin_bp.route('/delete_ambulance/<int:ambulance_id>', methods=['POST'])
@login_required
@admin_required
def delete_ambulance(ambulance_id):
    ambulance = Ambulance.query.get_or_404(ambulance_id)
    db.session.delete(ambulance)
    db.session.commit()
    flash('Ambulance has been deleted.', 'success')
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
    from forms import DriverForm 
    form = DriverForm()
    if form.validate_on_submit():
        driver = Driver(
            name=form.name.data,
            contact_info=form.contact_info.data,
            location=form.location.data
        )
        db.session.add(driver)
        db.session.commit()
        flash('Driver has been added.', 'success')
        return redirect(url_for('admin.manage_drivers'))
    return render_template('add_driver.html', form=form)

@admin_bp.route('/edit_driver/<int:driver_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    from forms import DriverForm
    form = DriverForm(obj=driver)
    if form.validate_on_submit():
        driver.name = form.name.data
        driver.contact_info = form.contact_info.data
        driver.location = form.location.data
        db.session.commit()
        flash('Driver information has been updated.', 'success')
        return redirect(url_for('admin.manage_drivers'))
    return render_template('edit_driver.html', form=form, driver=driver)

@admin_bp.route('/delete_driver/<int:driver_id>', methods=['POST'])
@login_required
@admin_required
def delete_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    db.session.delete(driver)
    db.session.commit()
    flash('Driver has been deleted.', 'success')
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
            ambulance.status = 'Unavailable'
            db.session.commit()

            room = f'emergency_{emergency_request.id}'
            print(f"admin update {room}")
            socketio.emit('status_update', {'status': emergency_request.status}, room=room)
            time.sleep(0.1)
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


            flash('Ambulance has been assigned.', 'success')

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
    flash('Message has been sent.', 'success')
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/toggle_auto_dispatch', methods=['POST'])
@login_required
@admin_required 
def toggle_auto_dispatch():
    print("admin tat autoooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
    setting = Setting.query.filter_by(key='auto_dispatch').first()
    if setting.value == 'True':
        setting.value = 'False'
        flash('Auto Dispatch has been turned OFF.', 'warning')
    else:
        setting.value = 'True'
        flash('Auto Dispatch has been turned ON.', 'success')
    
    db.session.commit()
    
    
    return redirect(url_for('admin.admin_dashboard'))