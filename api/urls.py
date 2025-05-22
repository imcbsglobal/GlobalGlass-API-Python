from django.urls import path
from . import views

urlpatterns = [
    path('sync/products', views.sync_products),
    path('sync/products/clear', views.clear_products),
    path('sync/productbatches', views.sync_productbatches),
    path('sync/productbatches/clear', views.clear_productbatches),
    path('sync/masters', views.sync_masters),
    path('sync/masters/clear', views.clear_masters),
    path('sync/users', views.sync_users),
    path('sync/users/clear', views.clear_users),
]
