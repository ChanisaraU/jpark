from flask import Flask, render_template, url_for
from flask_restful import Api,Resource, abort ,reqparse
from flask_sqlalchemy import SQLAlchemy , Model
from sqlalchemy import create_engine
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']="mysql://root:@localhost/car_trmp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

class Parking_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    license_plate = db.Column(db.String(10), unique=True, nullable=False)
    province = db.Column(db.String(50), unique=True, nullable=False)
    img_face_in = db.Column(db.String(120), unique=True, nullable=False)
    img_license_plate_in = db.Column(db.String(80), unique=True, nullable=False)
    car_type = db.Column(db.String(20), unique=True, nullable=False)
    time_in = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_in = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    insert_by_in = db.Column(db.String(50), unique=True, nullable=False)
    insert_date_in = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cancel = db.Column(db.String(80), unique=True, nullable=False)
    img_face_out = db.Column(db.String(120), unique=True, nullable=False)
    img_license_plate_out = db.Column(db.String(80), unique=True, nullable=False)
    time_out = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_out = db.Column(db.DateTime, default=datetime.utcnow, nullable=False )
    time_total = db.Column(db.String(10), unique=True, nullable=False)
    discount_name = db.Column(db.String(50), unique=True, nullable=False)
    pay_fine = db.Column(db.Float, unique=True, nullable=False)
    amount = db.Column(db.Float, unique=True, nullable=False)
    discount = db.Column(db.Float, unique=True, nullable=False)
    earn = db.Column(db.Float, unique=True, nullable=False)
    changes = db.Column(db.Float, unique=True, nullable=False)
    insert_by_out = db.Column(db.String(120), unique=True, nullable=False)
    insert_date_out = db.Column(db.String(120), unique=True, nullable=False)
    reason = db.Column(db.String(120), unique=True, nullable=False)
    total_amount = db.Column(db.Float, unique=True, nullable=False)
    vat = db.Column(db.Float, unique=True, nullable=False)
    fines = db.Column(db.Float, unique=True, nullable=False)
    licenplate_out = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return '<Parking_log %r>' % self.Parking_log

    db.create_all()   

if __name__ == "__main__":
    app.run(debug=True)