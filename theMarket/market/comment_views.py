from django.utils import simplejson as json
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import get_template
from market.models import Product, Comment
from market.forms import CommentForm
from market.shortcuts import direct_to_template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def mark_details(request, product_id):
    return direct_to_template(request, 'mark_details.html', { 'product': Product.objects.get(id=product_id) })


def comments(request, product_id):
    return direct_to_template(
        request, 'comments.html', {
            'product': Product.objects.get(id=product_id),
            'form': CommentForm(),
        }
    )


def get_comments(request, product_id):
    product = Product.objects.get(id=product_id)
    comments = product.get_comments()
    comment_list = [{
        'id': comment.id,
        'parent': comment.get_parent_id(),
        'block': direct_to_template(
            request, 'single_comment.html',
            { 'comment': comment, 'product': product }
        ).content
    } for comment in comments]
    return HttpResponse(
        json.dumps({'comment_list': comment_list}), mimetype='application/json'
    )


def add_comment_field(request, product_id, comment_id):
    form = CommentForm()
    comment_depth = -1 if comment_id == '0' else Comment.objects.get(id=comment_id).depth
    product = Product.objects.get(id=product_id)
    new_comment = get_template('single_comment_field.html')
    context = RequestContext(request, { 'form': form, 'product': product })
    return HttpResponse(
        json.dumps({
            'form': new_comment.render(context), 'depth': comment_depth + 1
        }), mimetype='application/json'
    )


def add_comment(request, product_id):
    product = Product.objects.get(id=product_id)
    form = CommentForm(
        data=(request.POST or None),
        instance=Comment(
            product=product,
            user = request.user if request.user else None,
        ),
    )
    if form.is_valid():
        form.save()
        form.instance.make_path_and_depth(request.POST['response_to_id'])
        form.save()
    else:
        return HttpResponse(
            json.dumps({
                'result': 'error',
                'comment_error': form.errors.get('comment'),
            }), mimetype='application/json'
        )
    page = get_template('single_comment.html')
    context = RequestContext(request, { 'comment': form.instance, 'product': product })
    return HttpResponse(
        json.dumps({
            'result': 'ok',
            'comment': page.render(context),
        }), mimetype='application/json'
    )


def delete_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if not request.user or (not request.user.is_admin and (comment.user and request.user != comment.user)):
        return HttpResponse(json.dumps({ 'result': 'error' }), mimetype='application/json')
    comment.get_responds().delete()
    comment.delete()
    return HttpResponse(json.dumps({ 'result': 'ok' }), mimetype='application/json')


def add_vote(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if not request.user or (comment.user and request.user == comment.user):
        return HttpResponse(json.dumps(comment.rating), mimetype='application/json')
    comment.rating = comment.rating + int(request.POST['vote'])
    comment.save()
    return HttpResponse(json.dumps(comment.rating), mimetype='application/json')
