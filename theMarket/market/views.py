import random
import string
from django.shortcuts import redirect
from market.models import User, Address
from market.forms import LoginForm, RegistrationForm, AdminRegistrationForm
from market.forms import AccountForm, AdminAccountForm, AddressForm
from market.shortcuts import direct_to_template

def index(request):
    return direct_to_template(request, 'index.html')


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('index')


def login(request):
    if request.user:
        return direct_to_template(request, 'lorem.html')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        request.session['user_id'] = form.user.id
        return redirect('index')
    return direct_to_template(request, 'login.html', {'form': form})


def edit_user(request, user_id):
    def select_form():
        form_class = AdminAccountForm if request.user.is_admin else AccountForm
        return form_class(
            data=(
                request.POST or
                {'login': edited_user.login, 'email': edited_user.email, 'is_admin': edited_user.is_admin}
            ), user=edited_user
        )
    if not request.user or (user_id != str(request.user.id) and not request.user.is_admin):
        return redirect('index')
    msg = ''
    edited_user = User.objects.get(id=user_id)
    form = select_form()
    if request.method == 'POST' and form.is_valid():
        if form.cleaned_data.get('password'):
            edited_user.password = edited_user.get_password_hash(form.cleaned_data['password'])
        edited_user.login = form.cleaned_data.get('login')
        edited_user.email = form.cleaned_data.get('email')
        if 'is_admin' in form.cleaned_data:
            edited_user.is_admin = form.cleaned_data.get('is_admin')
        edited_user.save()
        msg = 'Data saved'
    request.user = User.objects.get(id=request.user.id)
    form = select_form()
    return direct_to_template(
        request, 'edit_user.html', {'form': form, 'message': msg, 'current': edited_user}
    )


def edit_user_address(request, user_id):
    if not request.user or (user_id != str(request.user.id) and not request.user.is_admin):
        return redirect('index')

    edited_user = User.objects.get(id=user_id)
    if Address.objects.filter(user=edited_user).exists():
        address = Address.objects.get(user=edited_user)
    else:
        address = Address(user=edited_user)
    form = AddressForm(data=(request.POST or None), instance=address)

    msg = ''
    if form.is_valid():
        msg = 'Data saved'
        form.save()
            
    return direct_to_template(
        request, 'edit_user_address.html', {'form': form, 'message': msg, 'current': edited_user}
    )


def register(request):
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
        return redirect('index')
    return direct_to_template(request, 'registration.html', {'form': form})


def users(request):
    if not request.user or not request.user.is_admin:
        return redirect('index')
    return direct_to_template(
        request, 'users.html', { 'users': User.objects.all() }
    )


def delete_user(request, user_id):
    if not request.user or not request.user.is_admin:
        return redirect('index')
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        #admin must live!
        if user.is_admin and User.objects.filter(is_admin=True).count() == 1:
            return redirect('users')
        #end
        if user.id == request.user.id:
            del request.session['user_id']
        user.delete()
    return redirect('users')
