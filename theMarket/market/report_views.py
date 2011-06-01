from reportlab.pdfgen import canvas
from django.utils import simplejson as json
from django.http import HttpResponse
from django.db.models import Max
from market.models import Category
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
    pass
