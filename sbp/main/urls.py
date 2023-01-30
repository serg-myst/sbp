from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('', SbpHome.as_view(), name='home'),
    path('operation/<int:shop>/', ShowShopDetails.as_view(), name='shop_operations'),
    path('operation/<str:year>/<str:month>/<str:day>/<str:bank>/', ShowDetails.as_view(), name='show_details'),
    path('operation/<str:year>/<str:month>/<str:day>/<str:bank>/<int:shop>/', ShowShopOperations.as_view(),
         name='show_details_shop'),
    path('search', SearchHome.as_view(), name='search'),
    path('change-operation', change_operation, name='change_operation'),
    path('show-details/<str:year>/<str:month>/<str:day>/<str:bank>/', show_details, name='show-details'),
    path('show-details-total/<str:year>/<str:month>/<str:day>/<str:bank>/', show_details_total, name='show-details-total'),
]
