from reportlab.pdfgen import canvas
from django.http import HttpResponse

def some_view(request):
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + somefilename + '.pdf'

    p = canvas.Canvas(response)

    p.drawString(100, 100, "Hello world.")

    p.showPage()
    p.save()
    return response