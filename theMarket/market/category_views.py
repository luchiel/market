import re
from django.utils import simplejson as json
from django.http import HttpResponse
from django.shortcuts import redirect
from market.models import Category, Product
from market.forms import CategoryForm, MoveForm
from market.forms import ProductChoiceForm
from market.shortcuts import direct_to_template


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
