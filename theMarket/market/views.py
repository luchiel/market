import random
import string
import re
from django.db import connection, transaction
from django.utils import simplejson as json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import RequestContext
from market.models import User, Category, Product, Basket, Purchased, Address
from market.forms import LoginForm, RegistrationForm, AdminRegistrationForm
from market.forms import AccountForm, AdminAccountForm, AddressForm
from market.forms import CategoryForm, MoveForm
from market.forms import ProductForm, ProductChoiceForm
from market.shortcuts import direct_to_template
from market.image_utils import save_image, remove_image
from market.process_product import process_product

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


def add_category(request, parent_id):
    if not request.user or not request.user.is_admin:
        return redirect('category', category_id=parent_id)
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        category = Category(
            name=form.cleaned_data['name'],
            depth=0,
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
        request, 'add_category.html', {'form': form, 'parent_id': parent_id, 'parent_name': parent_name}
    )

def category(request, category_id):
    if not Category.objects.filter(id=category_id).exists() and category_id != '0':
        return redirect('index')
    cat = Category.objects.get(id=category_id)
    form = CategoryForm(request.POST or {'name': cat.name})
    product_form = ProductChoiceForm()
    if request.method == 'POST' and form.is_valid() and cat.id != 1 and request.user.is_admin:
        cat.name = form.cleaned_data.get('name')
        cat.save()
    return direct_to_template(
        request, 'category.html', {'form': form, 'product_form': product_form, 'category': cat}
    )


def delete_category(request, category_id):
    if category_id == '1':
        return redirect('category', category_id=category_id)
    category = Category.objects.get(id=category_id)
    parent = category.get_parent_category()
    if request.method == 'POST' and request.user and request.user.is_admin:
        for cat in category.get_direct_child_categories():
            cat.change_parent(parent.id)
        for product in category.get_products():
            product.category = parent
            product.save()
        category.delete()
    return redirect('category', category_id=parent.id)


def product_grid(request, location, category_id):
    ps = []
    #category_id?
    def add(product):
        '''ps.append({
            'id': product.id,
            'cell': [
                product.id, product.name, product.id, product.image,
                #?
            ],
        })'''
        pass
    products = Category.objects.get(id=category_id).get_products
    map(add, products)
    result = {
        'records': len(ps),
        'page': 1,
        'total': 1,
        'rows': ps,
    }
    return HttpResponse(json.dumps(result), mimetype='application/json')


def category_tree(request, location, category_id):
    x = re.match(r'.*categories/(\d+)', location)
    y = re.match(r'.*products/(\d+)', location)
    category_path = []
    cats = []
    if x or y:
        if x:
            current_cat = Category.objects.get(id=int(x.group(1)))
        else:
            current_cat = Product.objects.get(id=int(y.group(1))).category
        category_path = current_cat.get_category_sequence()
        category_path.append(current_cat)

    def add(node):
        parent_id = node.get_parent_category().id if node.depth != 0 else None
        if node.id == int(category_id):
            return
        children = node.get_direct_child_categories().exclude(id=category_id)
        cats.append({
            'id': node.id,
            'cell': [
                node.id, node.name, node.id, node.depth,
                parent_id, len(children) == 0, node in category_path or node.depth == 0,
            ],
        })
        map(add, children)
        
    def add_list(keyword):
        categories = Category.objects.filter(name__startswith=keyword)
        for cat in categories:
            cats.append({
                'id': cat.id,
                'cell': [
                    cat.id, cat.name, cat.id, 0,
                    0, True, False,
                ],
            })

    keyword = request.GET.get('search_keyword', '')
    if 'filters' in request.GET and keyword == '':
        rules = json.loads(request.GET['filters'])['rules']
        if rules:
            keyword = rules[0]['data']
    if keyword == '':
        add(Category.objects.get(depth='0'))
    else:
        add_list(keyword)
    result = {
        'records': len(cats),
        'page': 1,
        'total': 1,
        'rows': cats,
    }
    return HttpResponse(json.dumps(result), mimetype='application/json')


def move_category(request, category_id):
    if not request.user or not request.user.is_admin:
        return redirect('category', category_id=category_id)
    category = Category.objects.get(id=category_id)
    form = MoveForm(request.POST or
        {'parent': category.get_parent_category().name, 'parent_id': category.get_parent_category().id}
    )
    if request.POST and form.is_valid():
        category.change_parent(form.cleaned_data.get('parent_id'))
        return redirect('category', category_id=category_id)
    return direct_to_template(
        request, 'move_category.html', {'category': category, 'form': form}
    )


def product(request, product_id):
    product = Product.objects.get(id=product_id)
    form = ProductForm(request.POST, request.FILES) if request.POST else ProductForm({
            'name': product.name,
            'price': product.price,
            'category': category,
            'image': product.image,
            'description': product.description,
        })
    product_form = ProductChoiceForm()
    if request.POST and (not request.user or not request.user.is_admin):
        return redirect('product', product_id=product.id)
    msg = ''
    if request.POST and form.is_valid():
        product.name = form.cleaned_data.get('name')
        product.description = form.cleaned_data.get('description')
        if 'image' in request.FILES:
            remove_image(product.image)
            product.image = save_image(request.FILES['image'])
        product.save()
        msg = 'Data saved'
        
    return direct_to_template(
        request, 'edit_product.html', {'message': msg, 'product': product, 'form': form, 'product_form': product_form}
    )


def add_product(request, category_id):
    if not request.user or not request.user.is_admin:
        return redirect('category', category_id=category_id)
    category = Category.objects.get(id=category_id)
    form = ProductForm(request.POST, request.FILES) if request.POST else ProductForm()
    if request.POST and form.is_valid():
        image = save_image(request.FILES['image']) if 'image' in request.FILES else ''
        product = Product(
            name=form.cleaned_data.get('name'),
            price = form.cleaned_data.get('price'),
            description=form.cleaned_data.get('description'),
            image=image,
            category=category,
        )
        product.save()
        return redirect('category', category_id=category_id)
    return direct_to_template(
        request, 'add_product.html', {'form': form, 'category': category}
    )


def delete_product(request, product_id):
    if not request.user or not request.user.is_admin:
        return redirect('category', category_id=category_id)
    product = Product.objects.get(id=product_id)
    category_id = product.category.id
    remove_image(product.image)
    product.delete()
    return redirect('category', category_id=category_id)


def delete_product_image(request, product_id):
    if not request.user or not request.user.is_admin:
        return redirect('product', product_id=product_id)
    remove_image(Product.objects.get(id=product_id).image)
    return redirect('product', product_id=product_id)


def move_product(request, product_id):
    if not request.user or not request.user.is_admin:
        return redirect('product', product_id=product_id)
    product = Product.objects.get(id=product_id)
    form = MoveForm(request.POST or
        {'parent': product.category.name, 'parent_id': product.category.id}
    )
    if request.POST and form.is_valid():
        product.category = Category.objects.get(id=form.cleaned_data.get('parent_id'))
        product.save()
        return redirect('product', product_id=product_id)
    return direct_to_template(
        request, 'move_product.html', {'product': product, 'form': form}
    )


def add_to_basket(request, product_id):
    category = Product.objects.get(id=product_id).category
    def quantity_update(previous, new, maximum):
        return min(previous + new, maximum)
    process_product(request, product_id, quantity_update)
    return redirect('category', category_id=category.id)


def update_basket(request, product_id):
    def quantity_update(previous, new, maximum):
        return min(new, maximum)
    process_product(request, product_id, quantity_update)
    return HttpResponse(json.dumps(''), mimetype='application/json')


def remove_from_basket(request, product_id):
    Purchased.objects.filter(basket=request.basket).get(product=Product.objects.get(id=product_id)).delete()
    return redirect('basket', basket_id=request.basket.id)


def basket(request, basket_id):
    if int(basket_id) != request.basket.id:
        return redirect('basket', basket_id=request.basket.id)
    basket = Basket.objects.get(id=basket_id)
    products = basket.get_basket_goods()
    forms = []
    for p in products:
        forms.append(ProductChoiceForm({
            'product_id': p.product.id,
            'purchased_id': p.id,
            'name': p.product.name,
            'price': p.product.price,
            'quantity': p.quantity
        }))
    return direct_to_template(
        request, 'basket.html', { 'basket': basket, 'forms': forms }
    )


def order_basket(request, basket_id):
    if int(basket_id) != request.basket.id:
        return redirect('order_basket', basket_id=request.basket.id)
    basket = Basket.objects.get(id=basket_id)
    #if block is commented one can see that quantities are updated according to the final will
    #block set is_sent
    cursor = connection.cursor()
    cursor.execute('UPDATE market_purchased SET is_sent=1 WHERE basket_id=%s AND is_sent=0', [basket_id])
    transaction.commit_unless_managed()
    #endblock
    return redirect('basket', basket_id=request.basket.id)


def office_map(request):
    return direct_to_template(request, 'map.html')


def map_data(request):
    def make_address_str(a):
        return u'г. ' + a.city + u', ул. ' + a.street + u', дом ' + str(a.house)

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
