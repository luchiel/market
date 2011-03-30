import random
import string
import re
from django.utils import simplejson as json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import RequestContext
from market.models import User, Category
from market.forms import LoginForm, RegistrationForm, AdminRegistrationForm
from market.forms import AccountForm, AdminAccountForm
from market.forms import CategoryForm
from market.shortcuts import direct_to_template


def index(request):
    return direct_to_template(request, 'index.html', {'root': Category.objects.get(id='1')})


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('index')


def login(request):
    if request.user:
        return redirect('index')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        request.session['user_id'] = form.user.id
        return redirect('index')
    return direct_to_template(
        request, 'login.html', {'form': form, 'root': Category.objects.get(id='1')}
    )


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
        request, 'edit_user.html',
        {
            'form': form, 'message': msg, 'current': edited_user,
            'root': Category.objects.get(id='1')
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
        return redirect('users')
    return direct_to_template(
        request, 'registration.html', {'form': form, 'root': Category.objects.get(id='1')}
    )


def basket(request, user_id):
    return HttpResponse('No goods in the basket')


def users(request):
    if not request.user:
        return redirect('index')
    else:
        return direct_to_template(
            request, 'users.html',
            {
                'users': User.objects.all(), 'current': request.user,
                'root': Category.objects.get(id='1')
            }
        )


def delete_user(request, user_id):
    if request.method == 'POST':
        if not request.user or not request.user.is_admin:
            return redirect('index')
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
    if not request.user or not request.user.is_admin:
        return redirect('category', category_id=parent_id)
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        category = Category(
            name=form.cleaned_data['name'],
            depth=0,
            parent=Category.objects.get(id=parent_id),
        )
        category.save()
        category.make_path_and_depth(parent_id)
        category.save()
        return redirect('category', category_id=parent_id)
    if Category.objects.filter(id=parent_id).exists():
        parent_name = Category.objects.get(id=parent_id).name
    else:
        parent_name = 'root'
    return direct_to_template(
        request, 'add_category.html',
        {
            'form': form, 'parent_id': parent_id, 'parent_name': parent_name,
            'root': Category.objects.get(id='1')
        }
    )

def category(request, category_id):
    if not Category.objects.filter(id=category_id).exists() and category_id != '0':
        return redirect('index')
    cat = Category.objects.get(id=category_id)
    form = CategoryForm(request.POST or {'name': cat.name})
    if request.method == 'POST' and form.is_valid() and cat.id != 1:
        cat.name = form.cleaned_data.get('name')
        cat.save()
    return direct_to_template(
        request, 'category.html',
        {
            'form': form,
            'category': cat,
            'current': request.user,
            'root': Category.objects.get(id='1')
        }
    )


def delete_category(request, category_id):
    def move_upstairs_recursive(cat, new_parent_id):
        cat.make_path_and_depth(new_parent_id)
        for c in cat.get_direct_child_categories():
            c.move_upstairs_recursive(c, cat.id)
            
    if category_id == '1':
        return redirect('category', category_id=category_id)
    category = Category.objects.get(id=category_id)
    parent_id = category.get_parent_category().id
    if request.method == 'POST' and request.user and request.user.is_admin:
        #children?
        for cat in category.get_direct_child_categories():
            move_upstairs_recursive(cat, category.parent.id)
        category.delete()
    #goods?
    return redirect('category', category_id='1')


def category_tree(request, location):
    x = re.match(r'.*categories/(\d+)', location)
    category_path = []
    if x:
        current_cat = Category.objects.get(id=int(x.group(1)))
        category_path = current_cat.get_category_sequence()
        category_path.append(current_cat)

    cats = []
    
    def add(node):
        parent_id = node.parent.id #if node.id != node.parent.id else None
        children = node.get_direct_child_categories()
        cats.append({
            'id': node.id,
            'cell': [
                node.id,
                node.name,
                node.id,
                node.depth - 1,
                parent_id,
                len(children) == 0,
                node in category_path,
            ],
        })
        map(add, children)

    # skip root
    map(add, Category.objects.filter(depth='1'))
    #add(Category.objects.get(depth='0'))

    result = {
        'records': len(cats),
        'page': 1,
        'total': 1,
        'rows': cats,
    }
    return HttpResponse(json.dumps(result), mimetype='application/json')
