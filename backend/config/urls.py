from django.urls import path
import views

urlpatterns = [
    path('', views.index),
    path('api/stats', views.api_stats),
    path('api/buy-pension', views.api_buy_pension),
    path('api/pension-test', views.api_pension_test),
    path('api/generate', views.api_generate),
    path('api/balance', views.api_balance),
    path('api/buy', views.api_buy),
    path('api/save-credentials', views.api_save_credentials),
]
