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



def output_report(request):
    TODAY = datetime.datetime.today().strftime('%d.%m.%Y')

    def set_not_empty_value(param, default):
        return param or default

    #extract data from request.POST
    root_cat_id = set_not_empty_value(request.POST['parent_id'], '1')
    root_cat_path = Category.objects.get(id=root_cat_id).path
    row = int(request.POST['row'])
    col = int(request.POST['column'])
    row_param = int(request.POST.get('detail0', '0'))
    col_param = int(request.POST.get('detail1', '0'))
    start_date = set_not_empty_value(request.POST['start_date'], TODAY)
    end_date = set_not_empty_value(request.POST['end_date'], TODAY)
    #change request params if needed
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    #dataset
    dataset = Purchased.objects.raw(get_query(QUERY_TEMPLATE, row, col), [start_date, end_date, root_cat_path + '%'])

    #make headers
    row_header = MAKE_HEADER[row](row_param, start_date, end_date, root_cat_path)
    col_header = MAKE_HEADER[col](col_param, start_date, end_date, root_cat_path)

    current_col = 0
    current_row = 0
    grid = [[0]]

    #fill grid
    while item in dataset:
        for CHECK_FOR_CHANGE[row](item, row_header[current_row], row_param) in [True]:
            for CHECK_FOR_CHANGE[col](item, col_header[current_col], col_param) in [True]:
                grid[current_row][current_col] += item['quantity_sum']
                next(dataset.iterator())
                #dataset.iterator().next()

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
