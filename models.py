from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    events = db.relationship('Event', backref='category', lazy=True)

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __init__(self, name, description, start_date, end_date, category_id):
        self.name = name
        self.description = description
        self.start_date = datetime.strptime(start_date, '%d.%m.%Y')
        self.end_date = datetime.strptime(end_date, '%d.%m.%Y')
        self.category_id = category_id

    def get_dates_formatted(self):
        return {
            'start_date': self.start_date.strftime('%d.%m.%Y'),
            'end_date': self.end_date.strftime('%d.%m.%Y')
        }
