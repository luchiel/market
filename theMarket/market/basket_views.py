from django.db import connection, transaction
from django.utils import simplejson as json
from django.http import HttpResponse
from django.shortcuts import redirect
from market.models import Category, Product, Basket, Purchased
from market.forms import ProductChoiceForm
from market.shortcuts import direct_to_template
from market.process_product import process_product

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
