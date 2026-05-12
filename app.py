from flask import Flask, request, jsonify
from models import db, Vehicle, Fine
from flask_migrate import Migrate
import africastalking
import os
from dotenv import load_dotenv
from datetime import datetime
import random

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)

# Initialize Africa's Talking sms gateway
africastalking.initialize(os.getenv('AT_USERNAME'), os.getenv('AT_API_KEY'))
sms = africastalking.SMS

def generate_gepg_control_number():
    date_str = datetime.now().strftime("%Y%m%d%H%M")
    random_part = random.randint(100000, 999999)
    return f"GEPG-{date_str}-{random_part}"

@app.route('/api/detect-plate', methods=['POST'])
def detect_plate():
    data = request.get_json()
    plate = data.get('plate_number', '').strip().upper()
    if not plate:
        return jsonify({"error": "No plate provided"}), 400

    vehicle = Vehicle.query.filter_by(plate_number=plate).first()

    if not vehicle:
        return jsonify({"status": "unknown", "message": "Plate not registered"}), 200

    if vehicle.vehicle_type == 'brt_bus':
        return jsonify({"status": "exempt", "message": "BRT Bus - No fine"}), 200

    # get control number for the normal car
    control_number = generate_gepg_control_number()

    # Log fine to the database
    fine = Fine(plate_number=plate, control_number=control_number)
    db.session.add(fine)
    db.session.commit()

    # Send SMS
    #message = f"Dear {vehicle.owner_name}, you have been fined 100,000 TSh for BRT violation. " \
    #         f"Pay via GePG Control Number: {control_number}. Thank you."

    message = f"Dear {vehicle.owner_name},please check your account regarding a pending charge.Thank you."

    try:
        response = sms.send(message, [vehicle.phone_number])
        print("SMS sent:", response)
    except Exception as e:
        print("SMS failed:", e)
      

    return jsonify({
        "status": "fined",
        "plate": plate,
        "control_number": control_number,
        "owner": vehicle.owner_name,
        "amount": 100000
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)