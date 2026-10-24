from rest_framework.routers import DefaultRouter

from .views import EspacioViewSet


app_name = 'espacios'

router = DefaultRouter()
router.register('espacios', EspacioViewSet, basename='espacio')

urlpatterns = router.urls