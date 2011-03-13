from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from market.models import User
from hashlib import sha1
from market.forms import LoginForm, RegistrationForm, AccountForm
import random
import string

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))
    
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return HttpResponseRedirect('/theMarket/')

def login(request):
    if request.user:
        return HttpResponseRedirect('/theMarket/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            request.session['user_id'] = form.user.id
            return HttpResponseRedirect('/theMarket/')
    else:
        form = LoginForm()
    return render_to_response(
        'login.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )

def account(request):
    if not request.user:
        return HttpResponseRedirect('/theMarket/')
    msg = ''
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('new_password') != '':
                request.user.password = request.user.get_password_hash(form.cleaned_data['new_password'])
            request.user.email = form.cleaned_data.get('email')
            request.user.save()
            msg = 'Data saved'
    else:
        form = AccountForm({'email': request.user.email})
    return render_to_response(
        'account.html',
        {
            'form': form,
            'message': msg,
        },
        context_instance=RequestContext(request)
    )

def product(request, product_id):
    return HttpResponse("ID: %s" % product_id)

def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User(
                login=form.cleaned_data['login'],
                email=form.cleaned_data['email'],
                salt=''.join(random.choice(string.letters) for i in range(10)),
            )
            user.password = user.get_password_hash(form.cleaned_data['password'])
            user.save()
            return HttpResponseRedirect('/theMarket/')
    else:
        form = RegistrationForm()
    return render_to_response(
        'registration.html',
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )

def basket(request):
    return HttpResponse("No goods in the basket")
    
def users(request):
    return render_to_response(
        'users.html',
        {
            'users': User.objects.all().order_by('login'),
        },
        context_instance=RequestContext(request)
    )