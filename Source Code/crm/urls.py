from django.urls import path
from . import views
urlpatterns=[path('',views.dashboard,name='dashboard'),path('operations/',views.operations,name='operations'),path('<str:kind>/',views.listing,name='listing'),path('<str:kind>/new/',views.edit,name='create'),path('<str:kind>/<int:pk>/',views.detail,name='detail'),path('<str:kind>/<int:pk>/edit/',views.edit,name='edit'),path('<str:kind>/<int:pk>/delete/',views.delete,name='delete'),path('<str:kind>/export/<str:fmt>/',views.export,name='export')]
