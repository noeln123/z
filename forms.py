from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EmergencyRequestForm(FlaskForm):
    hospital_name = StringField('Hospital Name', validators=[DataRequired()])
    hospital_address = StringField('Hospital Address', validators=[DataRequired()])
    user_phone = StringField('Mobile Phone', validators=[DataRequired(), Length(min=10, max=15)])
    pickup_address = StringField('Pickup Address', validators=[DataRequired()])
    request_type = SelectField('Request Type', choices=[('Emergency', 'Emergency'), ('Non-Emergency', 'Non-Emergency')], validators=[DataRequired()])
    submit = SubmitField('Submit Request')
    

class FeedbackForm(FlaskForm):
    message = TextAreaField('Feedback', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Send')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Send')

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Address', validators=[DataRequired()])
    medical_history = TextAreaField('Medical History')
    allergies = TextAreaField('Allergies')
    emergency_contact = StringField('Emergency Contact Number', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Update')

class UpdateAmbulanceForm(FlaskForm):
    ambulance_type = SelectField('Ambulance Type', choices=[
        ('Type A', 'Type A'),
        ('Type B', 'Type B'),
        ('Type C', 'Type C'),
        # Add more types if needed
    ], validators=[DataRequired()])
    
    size = SelectField('Size', choices=[
        ('Small', 'Small'),
        ('Medium', 'Medium'),
        ('Large', 'Large'),
    ], validators=[DataRequired()])
    
    equipment = SelectField('Equipment', choices=[
        ('Basic', 'Basic'),
        ('Advanced', 'Advanced'),
        ('Full', 'Full'),
    ], validators=[DataRequired()])
    
    driver_id = SelectField('Driver', coerce=int, validators=[DataRequired()])
    
    submit = SubmitField('Add Ambulance')

class DriverForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    contact_info = StringField('Contact Info', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save')

class UpdateStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('On the way', 'On the way'),
        ('Arrived', 'Arrived'),
        ('Transporting', 'Transporting')
    ], validators=[DataRequired()])
    submit = SubmitField('Update')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    subject = StringField('Title', validators=[DataRequired(), Length(max=150)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Send')


class CancelEmergencyForm(FlaskForm):
    submit = SubmitField('Cancel Emergency Request')