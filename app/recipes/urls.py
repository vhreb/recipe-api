from django.urls import include, path

from rest_framework.routers import DefaultRouter

from recipes import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)

app_name = 'recipes'

urlpatterns = [
    path('', include(router.urls)),
]
