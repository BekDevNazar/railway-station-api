from django.urls import path

from user.views import UserCreateView, ManageUserView

app_name = "user"

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="create"),
    path("me/", ManageUserView.as_view(), name="manage"),
]
