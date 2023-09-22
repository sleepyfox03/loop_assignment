# basic URL Configurations
from django.urls import include, path
# import routers
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
# import everything from views
from .views import *

# define the router
router = routers.DefaultRouter()

# define the router path and viewset to be used
router.register(r'api', ReportViewSet)

# specify URL Path for rest_framework
urlpatterns = [
	path('', include(router.urls)),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)