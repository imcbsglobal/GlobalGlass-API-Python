from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Clear endpoints (DELETE requests)
    path('clear/products', views.clear_products, name='clear_products'),
    path('clear/productbatches', views.clear_productbatches, name='clear_productbatches'),
    path('clear/masters', views.clear_masters, name='clear_masters'),
    path('clear/users', views.clear_users, name='clear_users'),
    
    # Chunk insert endpoints (POST requests - no clearing)
    path('sync/products/chunk', views.sync_products_chunk, name='sync_products_chunk'),
    path('sync/productbatches/chunk', views.sync_productbatches_chunk, name='sync_productbatches_chunk'),
    path('sync/masters/chunk', views.sync_masters_chunk, name='sync_masters_chunk'),
    path('sync/users/chunk', views.sync_users_chunk, name='sync_users_chunk'),
    
    # Original v2 endpoints (for backward compatibility - clear and insert in one operation)
    path('sync/products/v2', views.sync_products_v2, name='sync_products_v2'),
    path('sync/productbatches/v2', views.sync_productbatches_v2, name='sync_productbatches_v2'),
    path('sync/masters/v2', views.sync_masters_v2, name='sync_masters_v2'),
    path('sync/users/v2', views.sync_users_v2, name='sync_users_v2'),
]