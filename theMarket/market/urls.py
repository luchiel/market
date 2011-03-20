from django.conf.urls.defaults import *

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('theMarket.market.views',
    (r'^$', 'index', None, 'index'),
    (r'^product(?P<product_id>\d+)/$', 'product'),
    (r'^users/$', 'users'),
    (r'^login/$', 'login'),
    (r'^logout/$', 'logout'),
    (r'^registration/$', 'registration'),
    (r'^account/(?P<user_login>[a-zA-Z0-9_-]+)/$', 'account'),
    (r'^account/basket/$', 'basket'),
    (r'^users/add/$', 'add'),
)