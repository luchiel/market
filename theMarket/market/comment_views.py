from django.utils import simplejson as json
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import get_template
from market.models import Product, Comment
from market.forms import CommentForm
from market.shortcuts import direct_to_template


def mark_details(request, product_id):
    return direct_to_template(request, 'mark_details.html', { 'product': Product.objects.get(id=product_id) })


def comments(request, product_id):
    return direct_to_template(
        request, 'comments.html', {
            'product': Product.objects.get(id=product_id),
            'form': CommentForm(),
        }
    )


def add_comment(request, product_id):
    form = CommentForm(
        data=(request.POST or None),
        instance=Comment(
            product=Product.objects.get(id=product_id),
            user = request.user if request.user else None,
        ),
    )
    if form.is_valid():
        form.save()
    else:
        return HttpResponse(
            json.dumps({
                'result': 'error',
                'mark_error': form.errors.get('mark'),
                'comment_error': form.errors.get('comment'),
            }), mimetype='application/json'
        )
    page = get_template('single_comment.html')
    context = RequestContext(request, { 'comment': form.instance })
    return HttpResponse(
        json.dumps({
            'result': 'ok',
            'page': page.render(context),
        }), mimetype='application/json'
    )


def delete_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if not request.user or (not request.user.is_admin and (comment.user and request.user != comment.user)):
        return HttpResponse(json.dumps({ 'result': 'error' }), mimetype='application/json')
    comment.delete()
    return HttpResponse(json.dumps({ 'result': 'ok' }), mimetype='application/json')


def add_vote(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if not request.user or (comment.user and request.user == comment.user):
        return HttpResponse(json.dumps(comment.rating), mimetype='application/json')
    comment.rating = comment.rating + int(request.POST['vote'])
    comment.save()
    return HttpResponse(json.dumps(comment.rating), mimetype='application/json')
