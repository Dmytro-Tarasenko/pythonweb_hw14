"""Main app routes"""
from django.contrib.auth.views import (PasswordResetDoneView,
                                       PasswordResetConfirmView,
                                       PasswordResetCompleteView)
from django.urls import path
from . import views

app_name = "app_quotes"

urlpatterns = [
    path('', views.index, name='home'),
    path('authors/', views.authors, name='authors'),
    path('author/<str:name>', views.author_name, name='author'),
    path('addauthor/', views.add_author, name='addauthor'),
    path('addquote/', views.add_quote, name='addquote'),
    path('tags/', views.tags, name='tags'),
    path('quotes/<str:tag>', views.quotes, name='quotes'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.register, name='register'),
    path('reset-password/',
         views.ResetPasswordView.as_view(),
         name='password_reset'),
    path('reset-password/done/',
         PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                          success_url='/reset-password/complete/'),
         name='password_reset_confirm'),
    path('reset-password/complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete')
]
