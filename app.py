from flask import Flask, request, jsonify, render_template, redirect, url_for
from models import db, Category, Event
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    events = Event.query.all()
    formatted_events = []
    for event in events:
        dates = event.get_dates_formatted()
        formatted_events.append({
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'start_date': dates['start_date'],
            'end_date': dates['end_date'],
            'category_id': event.category_id
        })
    return render_template('events.html', events=formatted_events)

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        category_id = int(request.form['category_id'])
        
        new_event = Event(name=name, description=description, start_date=start_date, end_date=end_date, category_id=category_id)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('index'))

    categories = Category.query.all()
    return render_template('add_event.html', categories=categories)

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.name = request.form['name']
        event.description = request.form.get('description', '')
        event.start_date = datetime.strptime(request.form['start_date'], '%d.%m.%Y')
        event.end_date = datetime.strptime(request.form['end_date'], '%d.%m.%Y')
        event.category_id = int(request.form['category_id'])
        
        db.session.commit()
        return redirect(url_for('index'))

    categories = Category.query.all()
    return render_template('edit_event.html', event=event, categories=categories)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('categories'))

    return render_template('add_category.html')

@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        category.name = request.form['name']
        db.session.commit()
        return redirect(url_for('categories'))
    
    return render_template('edit_category.html', category=category)

@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('categories'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
