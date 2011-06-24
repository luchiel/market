from django.utils import simplejson as json
from django.http import HttpResponse
from django.shortcuts import redirect
from market.models import User, Category, Product, Basket, Purchased, Address
from market.forms import MoveForm
from market.forms import ProductForm, ProductChoiceForm
from market.shortcuts import direct_to_template
from market.image_utils import save_image, remove_image

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


def product(request, product_id):
    product = Product.objects.get(id=product_id)
    form = ProductForm(request.POST, request.FILES) if request.POST else ProductForm({
            'name': product.name,
            'price': product.price,
            'category': product.category,
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