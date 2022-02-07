from django.urls import path, include
from .views import save, compare

urlpatterns = [
    # path('', CheckerView.as_view()),
    path('save/', save),
    path('compare/', compare)
]