from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.views.decorators.csrf import csrf_exempt
from . import views
from . import auth

router = DefaultRouter()
router.register(r'destinations', views.DestinationViewSet)
router.register(r'attractions', views.AttractionViewSet)
router.register(r'itineraries', views.ItineraryViewSet, basename='itinerary')
router.register(r'itinerary-days', views.ItineraryDayViewSet, basename='itineraryday')
router.register(r'itinerary-items', views.ItineraryItemViewSet, basename='itineraryitem')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
router.register(r'tags', views.TagViewSet)
router.register(r'comments', views.CommentViewSet, basename='comment')

# API URLs
urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Auth URLs
    path('auth/token/', csrf_exempt(TokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('auth/token/refresh/', csrf_exempt(TokenRefreshView.as_view()), name='token_refresh'),
    path('auth/register/', csrf_exempt(auth.register), name='register'),
    path('auth/user/', auth.get_user_info, name='user_info'),
    path('test/', views.TestView.as_view(), name='test'),
] 