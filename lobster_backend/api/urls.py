from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.UserSignup.as_view(), name="user-signup"),
    path("signin/", views.UserSignin.as_view(), name="user-signin"),
    path("profile/", views.MyProfile.as_view(), name="user-profile"),
    path("profile/<username>/", views.UserProfile.as_view(), name="user-profile"),
    path("logout/", views.UserLogout.as_view(), name="user-logout"),
    path("follow/", views.UserRelation.as_view(), name="relations"),
    path("posts/", views.Posts.as_view(), name="posts"),
    path("posts/<int:page>/<int:offset>/", views.Posts.as_view(), name="posts"),
    path("posts/<int:page>/<int:offset>/<username>/", views.Posts.as_view(), name="my-posts"),
    path("test/", views.test, name="test")
]