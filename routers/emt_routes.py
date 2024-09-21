from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db, socketio
from models import EmergencyRequest
from forms import UpdateStatusForm
from flask_socketio import emit, join_room, leave_room
from . import emt_bp
import time

def emt_required(f):
    from functools import wraps
    from flask import abort
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'emt':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('user.home'))
        return f(*args, **kwargs)
    return decorated_function

@emt_bp.route('/emt_dashboard')
@login_required
@emt_required
def emt_dashboard():
    form = UpdateStatusForm()
    statuses = ['Dispatched', 'On the way', 'Transporting']
    emergency_requests = EmergencyRequest.query.filter(EmergencyRequest.status.in_(statuses)).all()
    joined = False
    for em in emergency_requests:
        if em.emt_id == current_user.id:
            joined = em.emt_id
    return render_template('emt_dashboard.html', emergency_requests=emergency_requests, form=form, joined=joined)

@emt_bp.route('/patient_info/<int:request_id>')
@login_required
@emt_required
def patient_info(request_id):
    emergency_request = EmergencyRequest.query.get_or_404(request_id)

    user_profile = emergency_request.user.profile

    if not user_profile:
        flash('The user has not updated their profile.', 'warning')
        return redirect(url_for('emt.emt_dashboard'))
    
    return render_template('patient_info.html', emergency_request=emergency_request, profile=user_profile)


@emt_bp.route('/update_status/<int:request_id>', methods=['POST'])
@login_required
@emt_required
def update_status(request_id):
    emergency_request = EmergencyRequest.query.get_or_404(request_id)
    form = UpdateStatusForm()
    if form.validate_on_submit():
        new_status = form.status.data
        if new_status in ['On the way', 'Arrived', 'Transporting']:
            emergency_request.status = new_status
            # If the new status is 'Arrived', update the ambulance's status to 'Available'
            if new_status == 'Arrived':
                if emergency_request.ambulance:
                    ambulance = emergency_request.ambulance
                    ambulance.status = 'Available'
            db.session.commit()

            # Emit the 'status_update' event to the corresponding room
            room = f'emergency_{emergency_request.id}'
            socketio.emit('status_update', {'status': new_status}, room=room)
            time.sleep(0.1)
            socketio.emit('status_update', {'status': new_status}, room=room)
            flash('Status has been updated.', 'success')
        else:
            flash('Invalid status.', 'danger')
    else:
        flash('Invalid data.', 'danger')
    return redirect(url_for('emt.emt_dashboard'))


@socketio.on('update_location')
@login_required
@emt_required
def handle_update_location(data):
    """
    EMT sends their real-time location data via SocketIO.
    """
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    emergency_id = data.get('emergency_id')  # ID of the emergency being handled

    if not all([latitude, longitude, emergency_id]):
        emit('error', {'message': 'Invalid data.'})
        return

    # Retrieve the emergency based on the ID
    emergency_request = EmergencyRequest.query.get(emergency_id)
    if emergency_request:

        print(f"[SERVER] Received location from EMT {current_user.id}: {latitude}, {longitude}")
        room = f'emergency_{emergency_id}'  # Create a room for each emergency
        emit('location_update', {'latitude': latitude, 'longitude': longitude}, room=room)
        time.sleep(0.1)
        emit('location_update', {'latitude': latitude, 'longitude': longitude}, room=room)
    else:
        emit('error', {'message': 'Unauthorized or emergency not found.'})


@socketio.on('join_room')
@login_required
def handle_join_room(data):
    """
    User sends a request to join a room to receive location update events.
    """
    room = data.get('room')
    if not room:
        emit('error', {'message': 'Room not provided.'})
        return

    join_room(room)
    emit('joined_room', {'message': f'You have joined room {room}.'}, room=request.sid)


@emt_bp.route('/join_EM/<int:request_id>', methods=['POST'])
@login_required
@emt_required
def join_em(request_id):
    emergency_request = EmergencyRequest.query.get_or_404(request_id)
    emergency_request.emt_id = current_user.id

    db.session.commit()

    # Emit the 'status_update' event to the corresponding room
    flash('Successfully joined Emergency Request! Good luck!', 'success')
    return redirect(url_for('emt.emt_dashboard'))
