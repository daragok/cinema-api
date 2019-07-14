from rest_framework.routers import DefaultRouter

from main import views

router = DefaultRouter()
router.register('accounts', views.UserView, basename='accounts')
urlpatterns = router.urls
