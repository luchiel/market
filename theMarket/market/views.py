import random
import string
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from market.models import User, Category
from market.forms import LoginForm, RegistrationForm, AdminRegistrationForm
from market.forms import AccountForm, AdminAccountForm
from market.forms import AddCategoryForm
from market.shortcuts import direct_to_template


def index(request):
    return direct_to_template(request, 'index.html', {'root': Category.objects.filter(depth=1)})


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
    return direct_to_template(
        request, 'login.html', {'form': form, 'root': Category.objects.filter(depth=1)}
    )


def edit_user(request, user_id):
    if not request.user or (user_id != str(request.user.id) and not request.user.is_admin):
        return HttpResponseRedirect('/theMarket/')
    msg = ''
    edited_user = User.objects.get(id=user_id)
    form_class = AdminAccountForm if request.user.is_admin else AccountForm
    form = form_class(
        data=(
            request.POST or
            {'login': edited_user.login, 'email': edited_user.email, 'is_admin': edited_user.is_admin}
        ), user=edited_user
    )
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
    return direct_to_template(
        request, 'edit_user.html',
        {
            'form': form, 'message': msg, 'current': edited_user,
            'root': Category.objects.filter(depth=1)
        }
    )


def product(request, product_id):
    return HttpResponse("ID: %s" % product_id)


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
        return HttpResponseRedirect('/theMarket/')
    return direct_to_template(
        request, 'registration.html', {'form': form, 'root': Category.objects.filter(depth=1)}
    )


def basket(request, user_id):
    return HttpResponse('No goods in the basket')


def users(request):
    if not request.user:
        return HttpResponseRedirect('/theMarket/')
    else:
        return direct_to_template(
            request, 'users.html',
            {
                'users': User.objects.all(), 'current': request.user,
                'root': Category.objects.filter(depth=1)
            }
        )


def delete_user(request, user_id):
    if request.method == 'POST':
        if not request.user or not request.user.is_admin:
            return HttpResponseRedirect('/theMarket/')
        user = User.objects.get(id=user_id)
        #admin must live!
        if user.is_admin and User.objects.filter(is_admin=True).count() == 1:
            return HttpResponseRedirect('/theMarket/users/')
        #end
        if user.id == request.user.id:
            del request.session['user_id']
        user.delete()
    return HttpResponseRedirect('/theMarket/users/')


def add_category(request, parent_id):
    form = AddCategoryForm(request.POST or None)
    if form.is_valid():
        category = Category(
            name=form.cleaned_data['name'],
            depth=0,
        )
        category.save()
        category.make_path_and_depth(parent_id)
        category.save()
        return HttpResponseRedirect('/theMarket/')
    if Category.objects.filter(id=parent_id).exists():
        parent_name = Category.objects.get(id=parent_id).name
    else:
        parent_name = 'root'
    return direct_to_template(
        request, 'add_category.html',
        {
            'form': form, 'parent_id': parent_id, 'parent_name': parent_name,
            'root': Category.objects.filter(depth=1)
        }
    )

def category(request, category_id):
    if not Category.objects.filter(id=category_id).exists():
        return HttpResponseRedirect('/theMarket/')
    return direct_to_template(
        request, 'category.html',
        {
            'category': Category.objects.get(id=category_id),
            'root': Category.objects.filter(depth=1)
        }
    )
