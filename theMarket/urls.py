from django.conf.urls.defaults import *
import settings

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    (r'^theMarket/', include('market.urls')),
#    (r'^admin/', include(admin.site.urls)),
#    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'^media/(?P<path>.*)$',
            'serve',
            {
                'document_root': settings.MEDIA_ROOT
            }
        ),
    )