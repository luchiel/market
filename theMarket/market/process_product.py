from market.models import Category, Product, Purchased
from market.forms import ProductChoiceForm

def process_product(request, product_id, update_function):
    product = Product.objects.get(id=product_id)
    category = product.category
    form = ProductChoiceForm(request.POST or None)
    if form.is_valid():
        if Purchased.objects.filter(product=product, basket=request.basket, is_sent=False).exists():
            p = Purchased.objects.get(product=product, basket=request.basket, is_sent=False)
            p.quantity = update_function(p.quantity, form.cleaned_data['quantity'], p.get_max())
            p.save()
        else:
            p = Purchased(product=product, basket=request.basket, quantity=form.cleaned_data['quantity'])
            p.save()
