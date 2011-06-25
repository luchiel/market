from django.conf.urls.defaults import *

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('theMarket.market.views',
    url(r'^$', 'index', name='index'),
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^register/$', 'register', name='register'),    
    url(r'^users/$', 'users', name='users'),
    url(r'^users/delete/(?P<user_id>\d+)/$', 'delete_user', name='delete_user'),
    url(r'^users/edit/(?P<user_id>\d+)/$', 'edit_user', name='edit_user'),
    url(r'^users/edit/(?P<user_id>\d+)/edit_user_address/$', 'edit_user_address', name='edit_user_address'),
)

urlpatterns += patterns('theMarket.market.office_views',
    url(r'^office_map/$', 'office_map', name='office_map'),
    url(r'^map_data/$', 'map_data', name='map_data'),
    url(r'^offices/$', 'offices', name='offices'),
    url(r'^offices/(?P<office_id>\d+)/edit_office/$', 'edit_office', name='edit_office'),
    url(r'^offices/(?P<office_id>\d+)/delete_office/$', 'delete_office', name='delete_office'),
)

urlpatterns += patterns('theMarket.market.product_views',
    url(r'^.*product_grid/(?P<location>.*)/(?P<category_id>\d+)/$', 'product_grid', name='product_grid'),
    url(r'^products/(?P<product_id>\d+)/moveproduct/$', 'move_product', name='move_product'),
    url(r'^products/(?P<product_id>\d+)/deleteproductimage/$', 'delete_product_image', name='delete_product_image'),
    url(r'^products/(?P<category_id>\d+)/addproduct/$', 'add_product', name='add_product'),
    url(r'^products/(?P<product_id>\d+)/deleteproduct/$', 'delete_product', name='delete_product'),
    url(r'^products/(?P<product_id>\d+)/$', 'product', name='product'),
    url(r'^products/(?P<product_id>\d+)/mark/$', 'product_mark', name='product_mark'),
)

urlpatterns += patterns('theMarket.market.basket_views',
    url(r'^products/(?P<product_id>\d+)/add_to_basket/$', 'add_to_basket', name='add_to_basket'),
    url(r'^products/(?P<product_id>\d+)/update_basket/$', 'update_basket', name='update_basket'),
    url(r'^products/(?P<product_id>\d+)/remove_from_basket/$', 'remove_from_basket', name='remove_from_basket'),
    url(r'^basket/(?P<basket_id>\d+)/$', 'basket', name='basket'),
    url(r'^basket/(?P<basket_id>\d+)/order_basket/$', 'order_basket', name='order_basket'),
)

urlpatterns += patterns('theMarket.market.comment_views',
    url(r'^products/(?P<product_id>\d+)/comments/$', 'comments', name='comments'),
    url(r'^products/(?P<product_id>\d+)/get_comments/$', 'get_comments', name='get_comments'),
    url(r'^products/(?P<product_id>\d+)/comments/add_comment_field/(?P<comment_id>\d+)/$', 'add_comment_field', name='add_comment_field'),
    url(r'^products/(?P<product_id>\d+)/comments/add_comment/$', 'add_comment', name='add_comment'),
    url(r'^products/comments/(?P<comment_id>\d+)/delete_comment/$', 'delete_comment', name='delete_comment'),
    url(r'^products/(?P<product_id>\d+)/mark_details/$', 'mark_details', name='mark_details'),
    url(r'^add_vote/(?P<comment_id>\d+)/$', 'add_vote', name='add_vote'),
)

urlpatterns += patterns('theMarket.market.category_views',
    url(r'^.*category_tree/(?P<location>.*)/(?P<category_id>\d+)/$', 'category_tree', name='category_tree'),
    url(r'^categories/(?P<category_id>\d+)/movecategory/$', 'move_category', name='move_category'),
    url(r'^categories/(?P<parent_id>\d+)/addcategory/$', 'add_category', name='add_category'),
    url(r'^categories/(?P<category_id>\d+)/deletecategory/$', 'delete_category', name='delete_category'),
    url(r'^categories/(?P<category_id>\d+)/$', 'category', name='category'),
)

urlpatterns += patterns('theMarket.market.report_views',
    url(r'^reports/$', 'reports', name='reports'),
    url(r'^reports/extend_params/(?P<is_column>\d+)/$', 'extend_params', name='extend_params'),
    url(r'^reports/output/$', 'output_report', name='output_report'),
    url(r'^reports/output/(?P<report_index>\d+)/$', 'report', name='report'),
    url(r'^reports/histo/$', 'output_histo', name='output_histo'),
    url(r'^reports/histo/(?P<histogram_index>\d+)/$', 'histogram', name='histogram'),
)