from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')

class EmergencyRequestForm(FlaskForm):
    hospital_name = StringField('Tên bệnh viện', validators=[DataRequired()])
    hospital_address = StringField('Địa chỉ bệnh viện', validators=[DataRequired()])
    user_phone = StringField('Số điện thoại di động', validators=[DataRequired(), Length(min=10, max=15)])
    pickup_address = StringField('Địa chỉ đón', validators=[DataRequired()])
    request_type = SelectField('Loại cấp cứu', choices=[('Emergency', 'Khẩn cấp'), ('Non-Emergency', 'Không khẩn cấp')], validators=[DataRequired()])
    submit = SubmitField('Yêu cầu')

class FeedbackForm(FlaskForm):
    message = TextAreaField('Phản hồi', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Gửi')

class ContactForm(FlaskForm):
    name = StringField('Tên', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Số điện thoại', validators=[DataRequired(), Length(min=10, max=15)])
    message = TextAreaField('Tin nhắn', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Gửi')

class ProfileForm(FlaskForm):
    full_name = StringField('Họ và Tên', validators=[DataRequired()])
    phone_number = StringField('Số điện thoại', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Địa chỉ', validators=[DataRequired()])
    medical_history = TextAreaField('Tiền sử bệnh án')
    allergies = TextAreaField('Dị ứng')
    emergency_contact = StringField('Số liên lạc khẩn cấp', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Cập nhật')

class UpdateAmbulanceForm(FlaskForm):
    ambulance_type = StringField('Loại xe cứu thương', validators=[DataRequired()])
    size = StringField('Kích cỡ', validators=[DataRequired()])
    equipment = TextAreaField('Trang thiết bị', validators=[DataRequired()])
    driver_id = SelectField('Tài xế', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Cập nhật')

class DriverForm(FlaskForm):
    name = StringField('Tên', validators=[DataRequired(), Length(max=100)])
    contact_info = StringField('Thông tin liên lạc', validators=[DataRequired(), Length(max=100)])
    location = StringField('Vị trí', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Lưu')


class UpdateStatusForm(FlaskForm):
    status = SelectField('Trạng thái', choices=[
        ('On the way', 'Đang trên đường'),
        ('Arrived', 'Đã đến'),
        ('Transporting', 'Đang vận chuyển')
    ], validators=[DataRequired()])
    submit = SubmitField('Cập nhật')