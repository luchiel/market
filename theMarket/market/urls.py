from django.conf.urls.defaults import *

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('theMarket.market.views',
    (r'^$', 'index'),
    (r'^product(?P<product_id>\d+)/$', 'product'),
    (r'^users/$', 'users'),
    (r'^login/$', 'login'),
    (r'^logout/$', 'logout'),
    (r'^registration/$', 'registration'),
    (r'^account/$', 'account'),
    (r'^account/basket/$', 'basket'),
)