from datetime import datetime, timedelta
from flask import render_template_string, url_for
from models import Event
from calendar import HTMLCalendar, MONDAY

# České názvy měsíců
MONTHS = ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen", "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"]

class CustomHTMLCalendar(HTMLCalendar):
    def __init__(self, year, month):
        super().__init__(firstweekday=MONDAY)
        self.year = year
        self.month = month
        self.today = datetime.today()
        self.events_per_day = self.get_events_per_day()

    def get_events_per_day(self):
        start_date = datetime(self.year, self.month, 1)
        if self.month == 12:
            end_date = datetime(self.year + 1, 1, 1)
        else:
            end_date = datetime(self.year, self.month + 1, 1)

        events = Event.query.filter(Event.start_date < end_date, Event.end_date >= start_date).all()
        events_per_day = {}
        for event in events:
            event_start = max(event.start_date, start_date)
            event_end = min(event.end_date, end_date - timedelta(days=1))
            current_day = event_start.day
            while current_day <= event_end.day:
                if current_day in events_per_day:
                    events_per_day[current_day] += 1
                else:
                    events_per_day[current_day] = 1
                current_day += 1
        return events_per_day

    def formatday(self, day, weekday):
        if day == 0:
            return '<td></td>'  # Neplatný den
        else:
            bg_color = 'bg-success' if (self.year == self.today.year and self.month == self.today.month and day == self.today.day) else ''
            events_count = self.events_per_day.get(day, 0)
            events_info = f'<span class="badge bg-danger">{events_count}</span>' if events_count > 0 else ''
            return f'<td class="{bg_color}"><a href="/day/{day}/{self.month}/{self.year}">{day} {events_info}</a></td>'

    def formatmonth(self, withyear=True):
        events = f'<table class="table table-bordered">\n'
        events += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        events += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            events += '<tr>'
            for day, weekday in week:
                events += self.formatday(day, weekday)
            events += '</tr>\n'
        events += '</table>'
        return events

    def formatmonthname(self, theyear, themonth, withyear=True):
        month_name = MONTHS[themonth - 1]
        return f'<tr><th colspan="7" class="text-center">{month_name} {theyear if withyear else ""}</th></tr>'

    def formatweekheader(self):
        headers = ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne']
        return '<tr>' + ''.join(f'<th>{header}</th>' for header in headers) + '</tr>'

def generate_calendar(year, month):
    calendar = CustomHTMLCalendar(year, month)
    return calendar.formatmonth(withyear=True)

def get_upcoming_events():
    upcoming_events = (Event.query.order_by(Event.start_date.desc())
                       .limit(10)
                       .all())

    events_html = '<ul class="list-group">'
    for event in upcoming_events:
        events_html += f'<li class="list-group-item"><a href="/day/{event.start_date.day}/{event.start_date.month}/{event.start_date.year}">{event.name}</a> ({event.start_date.strftime("%d/%m/%Y %H:%M")})</li>'
    events_html += '</ul>'

    return events_html

def render_calendar(year, month):
    calendar_html = generate_calendar(year, month)
    events_html = get_upcoming_events()

    prev_month = datetime(year, month, 1) - timedelta(days=1)
    next_month = datetime(year, month, 28) + timedelta(days=4)
    next_month = next_month.replace(day=1)  # Nastav první den v následujícím měsíci

    html = f'''
    <!doctype html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>Kalendář</title>
    </head>
    <body>
        <div class="container">
            <div class="d-flex justify-content-between mb-3">
                <a href="{url_for('calendar_view', year=prev_month.year, month=prev_month.month)}" class="btn btn-primary">Předchozí měsíc</a>
                <h2>{MONTHS[month - 1]} {year}</h2>
                <a href="{url_for('calendar_view', year=next_month.year, month=next_month.month)}" class="btn btn-primary">Následující měsíc</a>
            </div>
            {calendar_html}
            <h3>10 nejčerstvějších událostí</h3>
            {events_html}
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    return render_template_string(html)
