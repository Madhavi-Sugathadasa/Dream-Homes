from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("forgot_password", PasswordResetView.as_view(), name="forgot_password"),
    path("password_reset_confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password_reset_done", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password_reset_complete", PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("autocomplete_location", views.autocomplete_location, name="autocomplete_location"),
    path("ad_more_details/<int:ad_id>/<ad_type>", views.ad_more_details, name="ad_more_details"),
    path("send_message", views.send_message, name="send_message"),
    path("post_ad", views.post_ad, name="post_ad"),
    path("payment/<ad_type>/<int:ad_id>/<payment_pkg>", views.payment, name="payment"),
    path("payment_success", views.payment_success, name="payment_success"),
    path("payment_cancel", views.payment_cancel, name="payment_cancel"),
    path("my_ads", views.view_my_ads, name="my_ads"),
    path("view_my_saved_ads", views.view_my_saved_ads, name="view_my_saved_ads"),
    path("my_ad_more_details/<int:ad_id>/<ad_type>", views.my_ad_more_details, name="my_ad_more_details"),
    path("my_saved_ad_more_details/<int:ad_id>/<ad_type>", views.my_saved_ad_more_details, name="my_saved_ad_more_details"),
    path("edit_ad/<int:ad_id>/<ad_type>", views.edit_ad, name="edit_ad"),
    path("edit_saved_ad/<int:ad_id>/<ad_property_type>", views.edit_saved_ad, name="edit_saved_ad"),
    path("delete_pic/<int:ad_id>/<ad_type>/<int:pic_id>/<pic_type>", views.delete_pic, name="delete_pic"),
    path("payment_packages/<int:ad_id>/<ad_type>", views.payment_packages, name="payment_packages"),
    path("delete_floorplan/<int:ad_id>/<ad_type>/<pic_type>", views.delete_floorplan, name="delete_floorplan"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

