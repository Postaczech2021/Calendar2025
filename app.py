from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from models import db, Category, Event
from datetime import datetime
from cal import render_calendar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chhx7383827ciri38f8cicicjcifidiru'  # Nastavení tajného klíče pro session
db.init_app(app)

@app.route('/calendar/<int:year>/<int:month>')
def calendar_view(year, month):
    return render_calendar(year, month)
    
@app.route('/add/work', methods=['GET', 'POST'])
def add_work():
    if request.method == 'POST':
        try:
            event_name = request.form['eventName']
            date_range = request.form['dateRange']
            print(f'Data z formuláře: Název: {event_name}, Rozsah dat: {date_range}')  # Ladící výpis

            dates = date_range.split(',')
            print(f'Hodnoty z formuláře: {dates}')  # Ladící výpis

            work_category = Category.query.filter_by(name='Work').first()
            if not work_category:
                work_category = Category(name='Work')
                db.session.add(work_category)
                db.session.commit()
                print(f'Vytvořena nová kategorie Work: {work_category.id}')  # Ladící výpis

            for date in dates:
                date = date.strip()  # Odstranění nadbytečných mezer kolem hodnoty
                description = ''
                if event_name == 'O':
                    description = '14:00-22:15'
                elif event_name == 'R':
                    description = '05:45-14:00'
                
                new_event = Event(
                    name=event_name,
                    start_date=date, 
                    end_date=date, 
                    category_id=work_category.id, 
                    description=description
                )
                db.session.add(new_event)
                print(f'Přidána událost: {new_event}')  # Ladící výpis

            db.session.commit()
            print('Všechny události byly úspěšně uloženy.')  # Ladící výpis

            # Flash messages for user
            flash('Událost úspěšně přidána!', 'success')
            return redirect(url_for('add_work'))
        except Exception as e:
            print(f'Chyba: {str(e)}')  # Ladící výpis
            flash(f'Chyba při přidávání události: {str(e)}', 'danger')
            return redirect(url_for('add_work'))
    return render_template('add_work.html')
            
@app.route('/events')
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

@app.route('/day/<int:day>/<int:month>/<int:year>')
def day_view(day, month, year):
    date = datetime(year, month, day)
    events = Event.query.filter(Event.start_date <= date, Event.end_date >= date).all()

    return render_template('day_events.html', day=day, month=month, year=year, events=events)

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
