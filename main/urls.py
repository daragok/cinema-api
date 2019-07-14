from rest_framework.routers import DefaultRouter

from main import views

router = DefaultRouter()
router.register('accounts', views.UserView, basename='accounts')
router.register('theater-rooms', views.TheaterRoomListView, basename='theater-room')
router.register('movies', views.MovieViewSet, basename='movies')
urlpatterns = router.urls
