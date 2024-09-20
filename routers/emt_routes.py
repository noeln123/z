from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db,socketio
from models import EmergencyRequest
from forms import UpdateStatusForm
from flask_socketio import emit, join_room, leave_room
from . import emt_bp

def emt_required(f):
    from functools import wraps
    from flask import abort
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'emt':
            flash('Bạn không có quyền truy cập trang này.', 'danger')
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
    
    # Kiểm tra xem EMT có quyền xem EM này không (tùy thuộc vào logic ứng dụng của bạn)
    # Ví dụ: EMT chỉ có thể xem EM đã được dispatch tới họ
    # Nếu cần thiết, hãy thêm các kiểm tra bổ sung ở đây

    # Truy xuất thông tin hồ sơ của người dùng đã tạo EM
    user_profile = emergency_request.user.profile  # Giả sử có relationship 'user' và 'profile'

    if not user_profile:
        flash('Người dùng chưa cập nhật hồ sơ.', 'warning')
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
            # Nếu trạng thái mới là 'Arrived', cập nhật trạng thái xe cứu thương thành 'Available'
            if new_status == 'Arrived':
                if emergency_request.ambulance:
                    ambulance = emergency_request.ambulance
                    ambulance.status = 'Available'
            db.session.commit()

            # Emit sự kiện 'status_update' tới phòng tương ứng
            room = f'emergency_{emergency_request.id}'
            socketio.emit('status_update', {'status': new_status}, room=room)
            flash('Status has been updated.', 'success')
        else:
            flash('Trạng thái không hợp lệ.', 'danger')
    else:
        flash('Dữ liệu không hợp lệ.', 'danger')
    return redirect(url_for('emt.emt_dashboard'))





@socketio.on('update_location')
@login_required
@emt_required
def handle_update_location(data):
    """
    EMT gửi dữ liệu vị trí thực tế của mình qua SocketIO.
    """
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    emergency_id = data.get('emergency_id')  # ID của EM đang xử lý

    if not all([latitude, longitude, emergency_id]):
        emit('error', {'message': 'Invalid data.'})
        return

    # Truy xuất EM dựa trên ID
    emergency_request = EmergencyRequest.query.get(emergency_id)
    if emergency_request:
        # Bạn có thể thêm các trường latitude và longitude vào EmergencyRequest nếu muốn lưu trữ vị trí
        # emergency_request.latitude = latitude
        # emergency_request.longitude = longitude
        # db.session.commit()

        # Gửi dữ liệu vị trí tới các client đang theo dõi EM này
        print(f"[SERVER] Nhan vi tri cua EMT {current_user.id}: {latitude}, {longitude}")
        room = f'emergency_{emergency_id}'  # Tạo phòng cho từng EM
        emit('location_update', {'latitude': latitude, 'longitude': longitude}, room=room)
    else:
        emit('error', {'message': 'Unauthorized or EM not found.'})


# Handler cho sự kiện "join_room"
@socketio.on('join_room')
@login_required
def handle_join_room(data):
    """
    Người dùng gửi yêu cầu tham gia phòng để nhận các sự kiện cập nhật vị trí liên quan.
    """
    room = data.get('room')
    if not room:
        emit('error', {'message': 'Phòng không được cung cấp.'})
        return

    # Bạn có thể thêm logic xác thực phòng nếu cần, ví dụ:
    # emergency_id = extract_emergency_id_from_room(room)
    # emergency_request = EmergencyRequest.query.get(emergency_id)
    # if emergency_request và current_user được phép tham gia phòng này...

    join_room(room)
    emit('joined_room', {'message': f'Bạn đã tham gia phòng {room}.'}, room=request.sid)


@emt_bp.route('/join_EM/<int:request_id>', methods=['POST'])
@login_required
@emt_required
def join_em(request_id):
    emergency_request = EmergencyRequest.query.get_or_404(request_id)
    emergency_request.emt_id = current_user.id

    db.session.commit()

    # Emit sự kiện 'status_update' tới phòng tương ứng
    flash('Join Emergency Request successfully! Good Luck!.', 'success')
    return redirect(url_for('emt.emt_dashboard'))