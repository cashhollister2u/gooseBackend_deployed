from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('update/', views.ProfileUpdate.as_view(), name='update'),
    path('search/<str:username>/', views.SearchFunction.as_view(), name='Searh_Bar'),
    path('leaderboard/', views.LeaderboardView.as_view(), name ='LeaderBoard'),
    path('messages/<user_id>/<non_user_id>/<batch_number>/', views.MyInbox.as_view(), name ='Messages'),
    path('send-messages/', views.SendMessages.as_view(), name ='Send-Messages'),
    path('conversations/<user_id>/', views.ConversationList.as_view(), name ='conversations'),
    path('', views.getRoutes),
]   