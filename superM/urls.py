from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('products.urls')),
    path('api/', include('suppliers.urls')),
    path('api/', include('shops.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('shopscollecte.urls')),
    path('api/', include('fourcollecte.urls'))
]