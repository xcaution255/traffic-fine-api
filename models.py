from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Fine(db.Model):
    __tablename__ = 'fines'
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), db.ForeignKey('vehicles.plate_number'))
    control_number = db.Column(db.String(30), unique=True, nullable=False)
    amount = db.Column(db.Integer, default=100000)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)