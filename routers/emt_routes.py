from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import EmergencyRequest
from forms import UpdateStatusForm
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
    emergency_requests = EmergencyRequest.query.filter_by(status='Dispatched').all()
    return render_template('emt_dashboard.html', emergency_requests=emergency_requests)

@emt_bp.route('/patient_info/<int:request_id>')
@login_required
@emt_required
def patient_info(request_id):
    emergency_request = EmergencyRequest.query.get_or_404(request_id)
    return render_template('patient_info.html', emergency_request=emergency_request)

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
            db.session.commit()
            flash('Trạng thái đã được cập nhật.', 'success')
        else:
            flash('Trạng thái không hợp lệ.', 'danger')
    else:
        flash('Dữ liệu không hợp lệ.', 'danger')
    return redirect(url_for('emt.emt_dashboard'))
