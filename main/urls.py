from django.urls import path
from rest_framework.routers import DefaultRouter

from main import views

router = DefaultRouter()
router.register('accounts', views.UserView, basename='accounts')
router.register('theater-rooms', views.TheaterRoomListView, basename='theater-room')
router.register('movies', views.MovieViewSet, basename='movies')
router.register('screenings', views.ScreeningViewSet, basename='screenings')

urlpatterns = router.urls

urlpatterns += path('screenings/<int:pk>/available-seats', views.AvailableScreeningSeatsView.as_view(),
                    name='available-seats'),
