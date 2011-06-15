# coding: utf-8
from reportlab.pdfgen import canvas
import datetime
import string
from django.utils import simplejson as json
from django.http import HttpResponse
from django.db.models import Max
from market.models import Category, Purchased
from market.shortcuts import direct_to_template
from market.forms import ReportForm
from market.report_utils import *


def some_view(request):
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + somefilename + '.pdf'
    
    p = canvas.Canvas(response)
    p.drawString(100, 100, "Hello world.")
    p.showPage()
    p.save()
    return response


def reports(request):
    return direct_to_template(request, 'reports.html', { 'form': ReportForm() })


def extend_params(request, is_column):
    param_id = request.GET['row'] if is_column == '0' else request.GET['column']
    param_id = int(param_id)
    if param_id in range(2):
        response = { 'extendable': 'false' }
    else:
        if param_id == 2:
            parameters = { 'options': REPORT_PRICE_SLICES, 'comment': 'Group by' }
        elif param_id == 3:
            level = Category.objects.aggregate(Max('depth'))['depth__max']
            parameters = { 'options': range(level + 1), 'comment': 'Group by level'}
        elif param_id == 4:
            parameters = { 'options': REPORT_TIME_PERIODS, 'comment': 'Group by' }
        response = { 'extendable': 'true', 'parameters': parameters }
    return HttpResponse(json.dumps(response), mimetype='application/json')


SQL_PIECES = [
    #(select, join, group, order)
    ('p.name AS product_name', '', 'p.id', ''), #products
    (
        'a.city', [
            ('market_Basket b', 'b.id = ph.basket_id'),
            (
                'market_Address a', (
                'a.user_id = b.user_id OR ' +
                'a.session_id = b.session_id'
            )),
        ], 'a.city', ''
    ), #cities
    ('p.price', '', '', 'p.price'), #prices
    ('c.name AS category_name, c.depth', '', '', 'c.name'), #categories
    ('ph.date', '', 'ph.date', 'ph.date'), #time
]


def get_query(template, row, col):
    row_sql = SQL_PIECES[row]
    col_sql = SQL_PIECES[col]

    def compose_line(index):
        line = ''
        if row_sql[index]:
            line += ', {0}'.format(row_sql[index]) 
        if col_sql[index]:
            line += ', {0}'.format(col_sql[index])
        return line
    
    select = compose_line(0)
    
    def compose_joins(join_list):
        joins = ''
        if join_list:
            for join in join_list:
                joins += 'INNER JOIN {0} ON {1} '.format(join[0], join[1])
        return joins
        
    joins = compose_joins(row_sql[1]) + compose_joins(col_sql[1])
    group_by = compose_line(2).replace(',', 'GROUP BY', 1)
    order_by = compose_line(3).replace(',', 'ORDER BY', 1)
    return template.format(select=select, join=joins, group=group_by, order=order_by)


def output_report(request):
    TODAY = datetime.datetime.today().strftime('%d.%m.%Y')

    def set_not_empty_value(param, default):
        return param or default

    start_date = set_not_empty_value(request.POST['start_date'], TODAY)
    end_date = set_not_empty_value(request.POST['end_date'], TODAY)
    root_cat_id = set_not_empty_value(request.POST['parent_id'], '1')
    root_cat_path = Category.objects.get(id=root_cat_id).path
    row = int(request.POST['row'])
    col = int(request.POST['column'])
    
    row_param = int(request.POST.get('detail0', '0'))
    col_param = int(request.POST.get('detail1', '0'))

    query = get_query(QUERY_TEMPLATE, row, col)
    dataset = Purchased.objects.raw(query, [start_date, end_date, root_cat_path + '%'])
    current_col = 0
    current_row = 0
    grid = [[0]]
    row_header = []
    col_header = []
    #row_field
    #col_field
    while item in dataset:
        row_header.append(item[row_field])
        for CHECK_FOR_CHANGE[row](cur, prev, row_param) in [True]:
            col_header.append(item[col_field])
            for CHECK_FOR_CHANGE[col](cur, prev, col_param) in [True]:
                grid[current_row][current_col] += item['quantity_sum']
                next(dataset.iterator())
                #dataset.iterator().next()
            #if item in dataset:
            current_col = CHANGE[col](grid[current_row], 0, col_header, cur, prev, col_param)
        #if item in dataset:
        current_row = CHANGE[row](grid, [0], row_header, cur, prev, row_param)

    return HttpResponse(json.dumps(''), mimetype='application/json')


'''
To add data to events, like the timedelta until the next event, or other parameters, subclass Event (don't forget to register your subclass with 
admin.site:

from scheduler.models import Event

class RepeatingEvent(Event):
    repeat_delta = models.PositiveIntegerField(help_text="In minutes")

def update_correlations(sender, instance, **kwargs):
    # Do correlation here!
    instance.delete()
    if issubclass(sender, RepeatingEvent):
        repeat(sender, instance, **kwargs)

def repeat(sender, instance, **kwargs):
    next_event = datetime.now() + timedelta(minutes=instance.repeat_delta)
    sender.objects.create(signal=instance.signal, timestamp=next_event)

connect('correlate', update_correlations, dispatch_uid='scheduler.update_correlations')

...or if you don't want to change your handler:

def repeat(handler):
    def new_handler(sender, instance, **kwargs):
        handler(sender=sender, instance=instance, **kwargs)
        if isinstance(instance, RepeatingEvent):
            next_event = datetime.now() + timedelta(minutes=instance.repeat_delta)
            sender.objects.create(signal=instance.signal, timestamp=next_event)
    return new_handler

connect('correlate', repeat(update_correlations), dispatch_uid='scheduler.update_correlations')

Starting a thread in your signal handler:

from threading import Thread

def threaded_update_correlations(sender, instance, **kwargs):
    Thread(target=update_correlations, args=(sender, instance)).start()

connect('correlate', threaded_update_correlations, dispatch_uid='scheduler.update_correlations')'''
