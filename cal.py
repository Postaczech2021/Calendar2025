from datetime import datetime, timedelta
from flask import render_template_string, url_for
from models import Event, Category
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
        end_date = datetime(self.year, self.month + 1, 1) if self.month < 12 else datetime(self.year + 1, 1, 1)

        events = Event.query.filter(Event.start_date < end_date, Event.end_date >= start_date).all()
        events_per_day = {}
        for event in events:
            event_start = max(event.start_date, start_date)
            event_end = min(event.end_date, end_date - timedelta(days=1))
            current_day = event_start.day
            while current_day <= event_end.day:
                if current_day not in events_per_day:
                    events_per_day[current_day] = []
                events_per_day[current_day].append(event)
                current_day += 1
        return events_per_day

    def get_event_bg_color(self, event):
        category = Category.query.get(event.category_id)
        if category and category.name == 'Work':
            first_letter = event.name[0]
            if first_letter == 'O':
                return 'bg-purple'
            elif first_letter == 'R':
                return 'border border-danger'
        return ''

    def formatday(self, day, weekday):
        if day == 0:
            return '<td></td>'  # Neplatný den
        else:
            today_color = 'bg-success' if (self.year == self.today.year and self.month == self.today.month and day == self.today.day) else ''
            events = self.events_per_day.get(day, [])
            events_info_top_right = ''
            events_info_bottom_left = ''
            work_bg_color = ''
            work_border = ''
            other_count = 0

            for event in events:
                category = Category.query.get(event.category_id)
                if category:
                    if category.name == 'Směny':
                        first_letter = event.name[0]
                        color = 'bg-primary' if first_letter == 'S' else ''
                        color = 'border border-danger' if first_letter == 'R' else color
                        color = 'bg-purple' if first_letter == 'O' else color
                        if color:
                            events_info_bottom_left += f'<span class="badge position-absolute bottom-0 start-0 {color}">{first_letter}</span>'
                    elif category.name == 'Work':
                        if event.name == 'O':
                            work_border = f'<div class="position-absolute bottom-0 start-0 w-100 bg-purple" style="height: 8px; z-index: 10; border:0 !important;margin:0;"></div>'
                        elif event.name == 'R':
                            work_border = f'<div class="position-absolute bottom-0 start-0 w-100 bg-danger" style="height: 8px; z-index: 10; border:0 !important;margin:0;"></div>'
                    else:
                        other_count += 1

            if not work_bg_color and not work_border:
                work_border = f'<div class="position-absolute bottom-0 start-0 w-100 border border-success" style="height: 8px; z-index: 10; border:0 !important;margin:0;"></div>'

            if other_count > 0:
                events_info_top_right += f'<span class=" bg-warning position-absolute top-0 end-0" style="padding:2px;">{other_count}</span>'

            return f'<td class="{today_color} position-relative text-center"><a href="/day/{day}/{self.month}/{self.year}" class="text-decoration-none {today_color}">{day}</a>{events_info_top_right}{events_info_bottom_left}{work_border}</td>'

    def formatmonth(self, withyear=True):
        events = f'<table class="table table-bordered table-dark table-hover calendar-table">\n'
        events += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            events += '<tr>'
            for day, weekday in week:
                events += self.formatday(day, weekday)
            events += '</tr>\n'
        events += '</table>'
        return events

    def formatmonthname(self, theyear, themonth, withyear=True):
        month_links = ''.join(f'<a href="/calendar/{theyear}/{i+1}" class="btn btn-dark btn-sm mx-1 month-link">{MONTHS[i][:3]}</a>' for i in range(12))
        return f'{month_links}'

    def formatweekheader(self):
        headers = ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne']
        return '<tr>' + ''.join(f'<th class="text-center">{header}</th>' for header in headers) + '</tr>'

def generate_calendar(year, month):
    calendar = CustomHTMLCalendar(year, month)
    return calendar.formatmonth(withyear=True)

def get_upcoming_events():
    work_category_id = Category.query.filter_by(name='Work').first().id
    upcoming_events = (Event.query.filter(Event.category_id != work_category_id)
                       .order_by(Event.start_date.desc())
                       .limit(10)
                       .all())

    events_html = '<ul class="list-group">'
    for event in upcoming_events:
        events_html += f'<li class="list-group-item"><a href="/day/{event.start_date.day}/{event.start_date.month}/{event.start_date.year}">{event.name}</a> ({event.start_date.strftime("%d/%m/%Y %H:%M")})</li>'
    events_html += '</ul>'

    return events_html

def generate_month_links(year):
    month_links = ''.join(f'<a href="/calendar/{year}/{i+1}" class="btn btn-dark btn-sm mx-1 month-link">{MONTHS[i][:3]}</a>' for i in range(12))
    return month_links

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
        <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.8.1/font/bootstrap-icons.min.css" rel="stylesheet">
        <title>Kalendář</title>
        <style>
            .calendar-container {{ margin-top: 3px; }}
            .calendar-table th, .calendar-table td {{ text-align: center; vertical-align: middle; }}
            .calendar-table a {{ text-decoration: none; }}
            .month-links a {{ font-size: 0.8rem; padding: 0.25rem 0.5rem; }}
            .badge {{ border-radius: 0; }}
            .bg-purple {{ background-color: purple; }}
            .border-danger {{ border-color: red !important; }}
            .border-success {{ border-color: green !important; }}
            .bg-success a {{ color: black !important; }}
        </style>
    </head>
    <body class="bg-dark text-light">
        <div class="mt-3 container calendar-container">
            <div class="d-flex justify-content-between mb-3">
                <a href="{url_for('calendar_view', year=prev_month.year, month=prev_month.month)}" class="btn btn-primary"><i class="bi bi-arrow-left"></i></a>
                <h2 class="text-center w-100">{MONTHS[month - 1]} {year}</h2>
                <a href="{url_for('calendar_view', year=next_month.year, month=next_month.month)}" class="btn btn-primary"><i class="bi bi-arrow-right"></i></a>
            </div>
           <div class="mt-3"> {calendar_html}</div>

            <div class="text-center">
                
                <div class="month-links">
                    {generate_month_links(year)}
                </div>
            </div>
            <h3 class="mt-5">Události</h3>
            <hr>
            {events_html}
        </div>
        <script src="https://cdn.jsdelivr.net[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://github.com/EmanoelPequeno/PHP/tree/988720fa95a4ad228b92648429876fa9df309cc4/API%2FQuestao09%2FCadastro.php?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "1")[43dcd9a7-70db-4a1f-b0ae-981daa162054](https://github.com/krishnadheerajp/krishnadheerajp.github.io/tree/0e41803e74609647f6b1c76c9c162c40777b523e/GRIP%20%20Internship%2Ftransfer.php?citationMarker=43dcd9a7-70db-4a1f-b0ae-981daa162054 "2")

        </body>
            </html>
            '''
    return render_template_string(html)
