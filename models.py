from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager
from flask import current_app
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(400), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user', 'admin', 'emt'
    profile = db.relationship('Profile', backref='user', uselist=False)
    emergency_requests = db.relationship('EmergencyRequest', 
                                         foreign_keys='EmergencyRequest.user_id', 
                                         backref='user', lazy=True)
    # Mối quan hệ giữa EMT và yêu cầu khẩn cấp được gán cho EMT đó
    emt_requests = db.relationship('EmergencyRequest', 
                                   foreign_keys='EmergencyRequest.emt_id', 
                                   backref='emt', lazy=True)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Ambulance(db.Model):
    __tablename__ = 'ambulances'
    id = db.Column(db.Integer, primary_key=True)
    ambulance_type = db.Column(db.String(50))
    size = db.Column(db.String(50))
    equipment = db.Column(db.Text)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))
    status = db.Column(db.String(20), default='Available')
    emergency_requests = db.relationship('EmergencyRequest', backref='ambulance', lazy=True)

class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact_info = db.Column(db.String(100))
    location = db.Column(db.String(100))
    ambulance = db.relationship('Ambulance', backref='driver', uselist=False)

class EmergencyRequest(db.Model):
    __tablename__ = 'emergency_requests'
    id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(100))
    hospital_address = db.Column(db.String(200))
    user_phone = db.Column(db.String(20))
    pickup_address = db.Column(db.String(200))
    request_type = db.Column(db.String(20))  # 'Emergency' or 'Non-Emergency'
    status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Dispatched', 'On the way', 'Transporting',  'Arrived', 'Canceled'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ambulance_id = db.Column(db.Integer, db.ForeignKey('ambulances.id'))
    emt_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    def to_dict(self):
        return {
            'id': self.id,
            'hospital_name': self.hospital_name,
            'hospital_address': self.hospital_address,
            'user_phone': self.user_phone,
            'pickup_address': self.pickup_address,
            'request_type': self.request_type,
            'status': self.status,
            'ambulance_id': self.ambulance_id,
            'user_id': self.user_id
        }


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Setting {self.key}: {self.value}>"