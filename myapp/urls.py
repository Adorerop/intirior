from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('designer_index/',views.designer_index,name='designer_index'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('services/',views.services,name='services'),
    path('login/',views.login,name='login'),
    path('signup01/',views.signup01,name='signup01'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('signup/',views.signup,name='signup'),
    path('logout/',views.logout,name='logout'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('verify_otppassword/',views.verify_otppassword,name='verify_otppassword'),
    path('new_password/',views.new_password,name='new_password'),
    path('profile/',views.profile,name='profile'),
    path('profile/change_password/',views.change_password,name='change_password'),
    path('estimate/<int:pk>/',views.estimate,name='estimate'),
    path('your_design_details/<str:cat>/',views.your_design_details,name='your_design_details'),
    path('add_your_designs/',views.add_your_designs,name='add_your_designs'),
    path('update_design/<str:cat>/',views.update_design,name='update_design'),
    path('design_details/<str:cat>/<int:pk>/',views.design_details,name='design_details'),
    path('inquery/<int:pk>/',views.inquery,name='inquery'),
    path('pay/<int:pk>/',views.initiate_payment,name='pay'),
    path('callback/',views.callback,name='callback'),
    path('inquery_for_you/',views.inquery_for_you,name='inquery_for_you'),
]