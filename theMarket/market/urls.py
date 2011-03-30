from django.conf.urls.defaults import *

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('theMarket.market.views',
    url(r'^$', 'index', name='index'),
    url(r'^product(?P<product_id>\d+)/$', 'product', name='product'),
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^register/$', 'register', name='register'),
    url(r'^users/$', 'users', name='users'),
    url(r'^users/delete/(?P<user_id>\d+)/$', 'delete_user', name='delete_user'),
    url(r'^users/edit/(?P<user_id>\d+)/$', 'edit_user', name='edit_user'),
    url(r'^(?P<user_id>\d+)/basket/$', 'basket', name='basket'),
    url(r'^categories/(?P<parent_id>\d+)/addcategory/$', 'add_category', name='add_category'),
    url(r'^categories/(?P<category_id>\d+)/$', 'category', name='category'),
    url(r'^categories/(?P<category_id>\d+)/deletecategory/$', 'delete_category', name='delete_category'),
    url(r'^.*category_tree/(?P<location>.*)/$', 'category_tree', name='category_tree'),
    #url(r'^.*category_tree/$', 'category_tree', name='category_tree'),
)
