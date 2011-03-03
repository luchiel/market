from hashlib import sha1
import random
import string
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from market.models import User
from market.forms import LoginForm, RegistrationForm, AccountForm, AdminRegistrationForm, AdminAccountForm
from market.shortcuts import direct_to_template


def index(request):
    return direct_to_template(request, 'index.html')


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return HttpResponseRedirect('/theMarket/')


def login(request):
    if request.user:
        return HttpResponseRedirect('/theMarket/')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        request.session['user_id'] = form.user.id
        return HttpResponseRedirect('/theMarket/')
    return direct_to_template(request, 'login.html', {'form': form})


def account(request, user_login):
    if not request.user or (user_login != request.user.login and not request.user.is_admin):
        return HttpResponseRedirect('/theMarket/')
    msg = ''
    edited_user = User.objects.get(login=user_login)
    form_class = AdminAccountForm if request.user.is_admin else AccountForm
    form = form_class(
        data=(
            request.POST or
            {'login': edited_user.login, 'email': edited_user.email, 'is_admin': edited_user.is_admin}
        ), user=edited_user
    )
    if request.method == 'POST' and form.is_valid():
        if form.cleaned_data.get('password') != '':
            edited_user.password = edited_user.get_password_hash(form.cleaned_data['password'])
        edited_user.login = form.cleaned_data.get('login')
        edited_user.email = form.cleaned_data.get('email')
        if 'is_admin' in form.cleaned_data:
            edited_user.is_admin = form.cleaned_data.get('is_admin')
        edited_user.save()
        msg = 'Data saved'
    request.user = User.objects.get(id=request.user.id)
    return direct_to_template(request, 'account.html', {'form': form, 'message': msg, 'current': edited_user})


def add(request):
    if not request.user or not request.user.is_admin:
        return HttpResponseRedirect('/theMarket/users/')
    return direct_to_template(request, 'registration.html', {'form': AdminRegistrationForm()})


def product(request, product_id):
    return HttpResponse("ID: %s" % product_id)


def registration(request):
    form_class = AdminRegistrationForm if request.user and request.user.is_admin else RegistrationForm
    form = form_class(request.POST or None)
    if form.is_valid():
        user = User(
            login=form.cleaned_data['login'],
            email=form.cleaned_data['email'],
            salt=''.join(random.choice(string.letters) for i in range(10)),
        )
        user.password = user.get_password_hash(form.cleaned_data['password'])
        if 'is_admin' in form.cleaned_data:
            user.is_admin = form.cleaned_data.get('is_admin')
        user.save()
        return HttpResponseRedirect('/theMarket/')
    return direct_to_template(request, 'registration.html', {'form': form})


def basket(request):
    return HttpResponse("No goods in the basket")


def users(request):
    return direct_to_template(request, 'users.html', {'users': User.objects.all(), 'current': request.user})

def delete(request, user_login):
    if request.method == 'POST':
        if not request.user or not request.user.is_admin:
            return HttpResponseRedirect('/theMarket/')
        user = User.objects.get(login=user_login)
        #admin must live!
        if user.is_admin and User.objects.filter(is_admin=True).count() == 1:
            return HttpResponseRedirect('/theMarket/users/')
        #end
        if user.id == request.user.id:
            del request.session['user_id']
        user.delete()
    return HttpResponseRedirect('/theMarket/users/')