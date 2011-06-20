# coding: utf-8
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import ttfonts, pdfmetrics
from datetime import datetime
import os
import string
import threading
from django.utils import simplejson as json
from django.shortcuts import redirect
from django.http import HttpResponse
from django.db.models import Max
from market.models import Category, Purchased
from market.shortcuts import direct_to_template
from market.forms import ReportForm
from market.report_utils import *
from market.shortcuts import direct_to_template


class report_thread(threading.Thread):
    def run(self):
        pass
'''
class threading.Thread(group=None, target=None, name=None, args=(), kwargs={}) 
This constructor should always be called with keyword arguments. Arguments are:

group should be None; reserved for future extension when a ThreadGroup class is implemented.

target is the callable object to be invoked by the run() method. Defaults to None, meaning nothing is called.

name is the thread name. By default, a unique name is constructed of the form �Thread-N� where N is a small decimal number.

args is the argument tuple for the target invocation. Defaults to ().

kwargs is a dictionary of keyword arguments for the target invocation. Defaults to {}.

'''

'''
Thread.run() 
Method representing the thread�s activity.

You may override this method in a subclass. The standard run() method invokes the callable object passed to the object�s constructor as the target 
argument, if any, with sequential and keyword arguments taken from the args and kwargs arguments, respectively.
'''


def reports(request):
    if not request.user or not request.user.is_admin:
        return redirect('index')
    return direct_to_template(request, 'reports.html', { 'form': ReportForm() })


def extend_params(request, is_column):
    param_id = request.GET['row'] if is_column == '0' else request.GET['column']
    param_id = int(param_id)
    if param_id < 2:
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
    if not request.POST:
        return redirect('reports')

    def set_not_empty_value(param, default):
        return param or default

    #extract data from request.POST
    root_cat_id = set_not_empty_value(request.POST['parent_id'], '1')
    root_cat = Category.objects.get(id=root_cat_id)
    row = int(request.POST['row'])
    col = int(request.POST['column'])
    if row == col:
        return redirect('reports')
    row_param = int(request.POST.get('detail0', '0'))
    col_param = int(request.POST.get('detail1', '0'))
    #partical validation
    start_date = datetime.today()
    end_date = datetime.today()
    form = ReportForm(request.POST)
    if not form.errors.get('start_date'):
        start_date = datetime.strptime(form.data['start_date'], '%d.%m.%Y')
    if not form.errors.get('end_date'):
        end_date = datetime.strptime(form.data['end_date'], '%d.%m.%Y')
    #change request params if needed
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    #dataset
    dataset = Purchased.objects.raw(get_query(QUERY_TEMPLATE, row, col), [start_date, end_date, root_cat.path + '%'])

    #make headers
    row_header = MAKE_HEADER[row](row_param, start_date, end_date, root_cat.path)
    col_header = MAKE_HEADER[col](col_param, start_date, end_date, root_cat.path)

    grid = [[0]]

    #fill grid
    if not list(dataset):
        return redirect('reports')
    i = 0
    item = dataset[i]
    current_row = 0
    dataset = list(dataset)

    while i < len(dataset):
        while current_row < len(row_header) and not CHECK_FOR_CHANGE[row](item, row_header[current_row], row_param):
            current_row = current_row + 1
            grid.append([0])
        if current_row == len(row_header):
            break
        current_col = 0
        while CHECK_FOR_CHANGE[row](item, row_header[current_row], row_param):
            while current_col < len(col_header) and not CHECK_FOR_CHANGE[col](item, col_header[current_col], col_param):
                current_col += 1
                grid[current_row].append(0)
            if current_col == len(col_header):
                break
            while CHECK_FOR_CHANGE[col](item, col_header[current_col], col_param):
                grid[current_row][current_col] += item.quantity
                i += 1
                if i == len(dataset):
                    break
                item = dataset[i]
            if i == len(dataset):
                break
    #test_output
    #print grid
    #print row_header
    #print col_header
    #output data
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + 'report' + '.pdf'

    #doc = SimpleDocTemplate('report.pdf', pagesize=A4)
    #elements = []
    p = canvas.Canvas(response)
    font_name = 'Arial'
    font = ttfonts.TTFont(font_name, os.path.join(os.environ['WINDIR'], 'fonts', 'arial.ttf'))
    pdfmetrics.registerFont(font)
    width, height = A4
    p.translate(2 * cm, 3 * cm)
    width -= 4 * cm
    height -= 6 * cm
    line_height = 1 * cm
    line_count = 0

    def drawLine(line, count):
        p.drawString(0, height - line_height * count, line)

    #header
    p.setFont(font_name, 20)
    drawLine('Report from ' + datetime.strftime(datetime.today(), '%d.%m.%Y'), line_count)
    line_count += 1
    p.setFont(font_name, 14)
    drawLine(
        'Sales from {0} to {1}, products from category {2}.'.format(
            datetime.strftime(start_date, '%d.%m.%Y'),
            datetime.strftime(end_date, '%d.%m.%Y'),
            root_cat.name
        ),
        line_count
    )
    height -= line_height * line_count
    p.setFont(font_name, 8)
    #titles
    output_row_header = [OUTPUT_HEADER[row](row_param, header) for header in row_header]
    row_header_width = max([p.stringWidth(header, font_name, 8) for header in output_row_header])
    output_col_header = [OUTPUT_HEADER[col](col_param, header) for header in col_header]
    col_header_height = max([p.stringWidth(header, font_name, 8) for header in output_col_header])
    #grid
    INDENT = 0.2 * cm
    p.translate(0, -0.5 * cm)
    height -= 0.5 * cm
    xlines = [0, row_header_width + INDENT * 2]
    while xlines[-1] < width:
        xlines.append(xlines[-1] + line_height)
    ylines = [height, height - col_header_height - INDENT * 2]
    while ylines[-1] > 0:
        ylines.append(ylines[-1] - line_height)
    p.grid(xlines, ylines)
    #output titles
    line_count = 1
    for header in output_row_header:
        p.drawRightString(
            xlines[1] - INDENT,
            ylines[1] + INDENT - line_height * line_count,
            header
        )
        line_count += 1
    p.rotate(-90)
    line_count = 0
    for header in output_col_header:
        p.drawRightString(
            -(ylines[1] + INDENT),
            xlines[1] + INDENT + line_height * line_count,
            header
        )
        line_count += 1
    p.rotate(90)
    #grid data
    c_row = 1
    for row in grid:
        c_col = 1
        for val in row:
            p.drawString(
                0, 0,
                str(val)
            )
            c_col += 1
        c_row += 1
    p.showPage()
    p.save()
    return response


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
