from django.utils import simplejson as json
from django.http import HttpResponse
from django.shortcuts import redirect
from market.shortcuts import direct_to_template
from market.models import Address
from market.forms import AddressForm

def offices(request):
    if not request.user or not request.user.is_admin:
        return redirect('index')
    return direct_to_template(
        request, 'offices.html', { 'offices': Address.objects.filter(user=None, session_id=None) }
    )


def add_office(request):
    return redirect('edit_office', 0)


def edit_office(request, office_id):
    if not request.user or not request.user.is_admin:
        return redirect('index')
    address = Address() if office_id == '0' else Address.objects.get(id=office_id)
    form = AddressForm(data=(request.POST or None), instance=address)
    msg = ''
    if form.is_valid():
        msg = 'Data saved'
        form.save()
    return direct_to_template(request, 'edit_office.html', { 'office_id': office_id, 'form': form, 'message': msg })


def delete_office(request, office_id):
    if not request.user or not request.user.is_admin:
        return redirect('index')
    if request.method == 'POST':
        office = Address.objects.get(id=office_id)
        office.delete()
    return redirect('offices')


def office_map(request):
    return direct_to_template(request, 'office_map.html')


def map_data(request):
    def make_address_str(a):
        return u'г. {0}, ул. {1}, дом {2}'.format(a.city, a.street, a.house)

    result = []
    address = '';
    if request.user:
        if Address.objects.filter(user=request.user).exists():
            user_address = Address.objects.get(user=request.user)
            address = make_address_str(user_address)
    else:
        if Address.objects.filter(session_id=request.session.session_key).exists():
            user_address = Address.objects.get(session_id=request.session.session_key)
            address = make_address_str(user_address)
    
    result.append(address)
    for a in Address.objects.filter(user=None, session_id=None):
        result.append(make_address_str(a))
    return HttpResponse(json.dumps(result), mimetype='application/json')