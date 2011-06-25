# -*- coding: utf-8 -*-
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import ttfonts, pdfmetrics
from datetime import datetime
import os
import string
import threading
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.utils import simplejson as json
from django.shortcuts import redirect
from django.http import HttpResponse
from django.db.models import Max
import matplotlib.mlab as mlab
import matplotlib.pyplot as plot
from matplotlib import font_manager
from market.models import Category, Purchased, Report
from market.shortcuts import direct_to_template
from market.forms import ReportForm
from market.report_utils import *
from market.shortcuts import direct_to_template


class TaskThread(threading.Thread):
    def __init__(self, request, run_function):
        threading.Thread.__init__(self)
        self.request = request
        self.task = Report()
        self.task.save()
        self.name = str(self.task.id)
        self.function = run_function

    def run(self):
        self.function(self.request, self.canvas)
        self.task.is_completed = True
        self.task.save()

class ReportThread(TaskThread):
    def __init__(self, request, run_function):
        TaskThread.__init__(self, request, run_function)
        self.canvas = canvas.Canvas(get_report_name(self.name))


class HistoThread(TaskThread):
    def __init__(self, request, run_function):
        TaskThread.__init__(self, request, run_function)
        self.canvas = self.name


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
        else:
            parameters = {}
        response = { 'extendable': 'true', 'parameters': parameters }
    return HttpResponse(json.dumps(response), mimetype='application/json')


def output_report(request):
    if not request.POST or request.POST['row'] == request.POST['column']:
        return redirect('reports')

    t = ReportThread(request, create_report)
    result = { 'report': t.task.id }
    t.start()

    return HttpResponse(json.dumps(result), mimetype='application/json')


def report(request, report_index):
    if not Report.objects.filter(id=report_index).exists():
        return HttpResponse('No file')
    if not Report.objects.get(id=report_index).is_completed:
        return HttpResponse('Update page')
    filename = get_report_name(report_index)
    wrapper = FileWrapper(open(filename, 'rb'))
    response = HttpResponse(wrapper, content_type='application/pdf')
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response


def create_report(request, p):
    #extract data from request.POST
    root_cat_id = set_not_empty_value(request.POST['parent_id'], '1')
    root_cat = Category.objects.get(id=root_cat_id)
    row = int(request.POST['row'])
    col = int(request.POST['column'])
    row_param = int(request.POST.get('detail0', '0'))
    col_param = int(request.POST.get('detail1', '0'))
    start_date, end_date = get_dates_from_request(request)

    #data
    dataset = Purchased.objects.raw(get_query(QUERY_TEMPLATE, row, col), [start_date, end_date, root_cat.path + '%'])
    row_header = MAKE_HEADER[row](row_param, start_date, end_date, root_cat.path)
    col_header = MAKE_HEADER[col](col_param, start_date, end_date, root_cat.path)

    #fill grid
    grid = [[0]]
    dataset = list(dataset)
    i = 0
    if dataset:
        item = dataset[i]
    current_row = 0

    while i < len(dataset):
        while current_row < len(row_header) and not CHECK_FOR_CHANGE[row](item, row_header[current_row], row_param):
            current_row += 1
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
            while(
                CHECK_FOR_CHANGE[col](item, col_header[current_col], col_param) and
                CHECK_FOR_CHANGE[row](item, row_header[current_row], row_param)
            ):
                grid[current_row][current_col] += item.quantity
                i += 1
                if i == len(dataset):
                    break
                item = dataset[i]
            if i == len(dataset):
                break
    #output data
    font_name = 'Arial'
    font = ttfonts.TTFont(font_name, os.path.join(os.environ['WINDIR'], 'fonts', 'arial.ttf'))
    pdfmetrics.registerFont(font)
    
    #titles
    output_row_header = [OUTPUT_HEADER[row](row_param, header) for header in row_header]
    sizes = [p.stringWidth(header, font_name, 8) for header in output_row_header]
    row_header_width = max(sizes) if sizes else 0
    output_col_header = [OUTPUT_HEADER[col](col_param, header) for header in col_header]
    sizes = [p.stringWidth(header, font_name, 8) for header in output_col_header]
    col_header_height = max(sizes) if sizes else 0

    INDENT = 0.2 * cm
    line_height = 1 * cm
    #grid
    t_width, t_height = A4
    t_width -= 4 * cm
    t_height -= 6.5 * cm + line_height
    xlines = [0, row_header_width + INDENT * 2]
    while xlines[-1] < t_width:
        xlines.append(xlines[-1] + line_height)
    ylines = [t_height, t_height - col_header_height - INDENT * 2]
    while ylines[-1] > 0:
        ylines.append(ylines[-1] - line_height)
    row_count = len(ylines) - 2
    col_count = len(xlines) - 2

    def new_page(ll_row, ll_col):
        width, height = A4
        p.translate(2 * cm, 3 * cm)
        width -= 4 * cm
        height -= 6 * cm
        line_count = 0

        def draw_line(line, count):
            p.drawString(0, height - line_height * count, line)

        #header
        p.setFont(font_name, 20)
        draw_line('Report from ' + datetime.strftime(datetime.today(), '%d.%m.%Y'), line_count)
        line_count += 1
        p.setFont(font_name, 14)
        draw_line(
            'Sales from {0} to {1}, products from category {2}.'.format(
                datetime.strftime(start_date, '%d.%m.%Y'),
                datetime.strftime(end_date, '%d.%m.%Y'),
                root_cat.name
            ),
            line_count
        )
        height -= line_height * line_count
        p.setFont(font_name, 8)
        #grid
        p.translate(0, -0.5 * cm)
        height -= 0.5 * cm
        p.grid(xlines, ylines)
        #titles
        line_count = 0
        while line_count < row_count and line_count + ll_row < len(output_row_header):
        #for header in output_row_header:
            p.drawRightString(
                xlines[1] - INDENT,
                ylines[1] + INDENT - line_height * (line_count + 1),
                output_row_header[line_count + ll_row]
            )
            line_count += 1
        p.rotate(-90)
        line_count = 0
        while line_count < col_count and line_count + ll_col < len(output_col_header):
        #for header in output_col_header:
            p.drawRightString(
                -(ylines[1] + INDENT),
                xlines[1] + INDENT + line_height * line_count,
                output_col_header[line_count + ll_col]
            )
            line_count += 1
        p.rotate(90)

    #grid data
    last_list_row = 0
    last_list_col = 0
    def output_page(ll_row, ll_col):
        new_page(ll_row, ll_col)
        c_row = 0
        while c_row < row_count and c_row + ll_row < len(grid):
            c_col = 0
            while c_col < col_count and c_col + ll_col < len(grid[c_row + ll_row]):
                if grid[c_row + ll_row][c_col + ll_col] != 0:
                    p.drawRightString(
                        xlines[c_col + 2] - INDENT,
                        ylines[c_row + 2] + INDENT,
                        str(grid[c_row + ll_row][c_col + ll_col])
                    )
                c_col += 1
            c_row += 1
        p.showPage()

    while last_list_row < len(row_header):
        last_list_col = 0
        while last_list_col < len(col_header):
            output_page(last_list_row, last_list_col)
            last_list_col += col_count
        last_list_row += row_count
    p.save()


def get_dates_from_request(request):
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
    return (start_date, end_date)


def output_histo(request):
    if not request.POST:
        return redirect('reports')

    t = HistoThread(request, create_histo)
    result = { 'histogram': t.task.id }
    t.start()

    return HttpResponse(json.dumps(result), mimetype='application/json')


def create_histo(request, p):
    root_cat_id = set_not_empty_value(request.POST['parent_id'], '1')
    root_cat = Category.objects.get(id=root_cat_id)
    row = int(request.POST['row'])
    param = int(request.POST.get('detail0', '0'))
    start_date, end_date = get_dates_from_request(request)
    #dataset
    dataset = Purchased.objects.raw(get_query(QUERY_TEMPLATE, row, 5), [start_date, end_date, root_cat.path + '%'])
    header = MAKE_HEADER[row](param, start_date, end_date, root_cat.path)
    dataset = list(dataset)
    y = [0]
    current_row = 0
    for item in dataset:
        while current_row < len(header) - 1 and not CHECK_FOR_CHANGE[row](item, header[current_row], param):
            y.append(0)
            current_row += 1
        y[current_row] += item.quantity
    while current_row < len(header) - 1:
        y.append(0)
        current_row += 1
    #output
    plot.clf()
    plot.cla()
    plot.rcParams['font.sans-serif'] = 'Verdana'
    #plot.xticks(range(len(header)), [OUTPUT_HEADER[row](param, item) for item in header], rotation=45)
    #plot.bar(range(len(header)), y, align='center')
    #plot.xlabel(REPORT_CHOICES[row][1])
    #plot.ylabel('Quantity')

    plot.yticks(range(len(header)), [OUTPUT_HEADER[row](param, item) for item in header], rotation=45)
    plot.barh(range(len(header)), y, height=0.5, align='center')
    #plot.legend([OUTPUT_HEADER[row](param, item) for item in header], loc='left')
    plot.ylabel(REPORT_CHOICES[row][1])
    plot.xlabel('Quantity')

    plot.title('{0}. Category: {1}, {2}-{3}'.format(
        REPORT_CHOICES[row][1],
        root_cat.name,
        start_date.strftime('%d.%m.%Y'),
        end_date.strftime('%d.%m.%Y')
    ))
    plot.grid(True)
    plot.savefig(get_histogram_name(p))


def histogram(request, histogram_index):
    if not Report.objects.filter(id=histogram_index).exists():
        return HttpResponse('No file')
    if not Report.objects.get(id=histogram_index).is_completed:
        return HttpResponse('Update page')
    filename = get_histogram_name(histogram_index)
    print 'ku'
    if not os.path.exists(filename):
        return HttpResponse('No file. Strange')
    print 'kuku'
    wrapper = FileWrapper(open(filename, 'rb'))
    response = HttpResponse(wrapper, content_type='application/png')
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=histogram.png'
    return response
