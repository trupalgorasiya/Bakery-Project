"""
URL configuration for sweetdelights project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sweetdelightsapp1 import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # HTML PAGES 
    path('', views.Homepage, name='Homepage'),
    path('Homepage.html', views.Homepage, name='Homepage'),
    path('FAQ.html', views.FAQ, name='FAQ'),
    path('Gallery.html', views.Gallery, name='Gallery'),
    path('PartipationForm.html', views.PartipationForm, name='PartipationForm'),
    path('PartyProps.html', views.PartyProps, name='PartyProps'),
    path('Ourservices.html', views.Ourservices, name='Ourservices'),
    path('about/', views.about, name='about'),

    #Products Pages
    path('Cakes.html', views.Cakes, name='Cakes'),
    path('cakes/subcategory/<int:subcategory_id>/', views.cakes_by_subcategory, name='cakes_by_subcategory'),
    path('Pastries.html', views.Pastries, name='Pastries'),
    path('Cupcakes.html', views.Cupcakes, name='Cupcakes'),
    path('Cookies.html', views.Cookies, name='Cookies'),
    path('Donuts.html', views.Donuts, name='Donuts'),
    path('Waffles.html', views.Waffles, name='Waffles'),
    path('Breads.html', views.Breads, name='Breads'),
    path('Others.html', views.Others, name='Others'),

    #Search 
    path("search/", views.search_results, name="search_results"),

    #Product Details Pages
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.submit_review, name='submit_review'),
    path("review/edit/<int:review_id>/", views.edit_review, name="edit_review"),
    path("review/delete/<int:review_id>/", views.delete_review, name="delete_review"),
    path('submit-inquiry/<int:product_id>/', views.submit_inquiry, name='submit_inquiry'),

    #Discount 
    path("apply-discount/", views.apply_discount, name="apply_discount"),
    path("discounts/", views.discount_list, name="discount_list"),
    path('cart/remove_discount/', views.remove_discount, name='remove_discount'),

    #User Authentication 
    path('Registration.html', views.registration, name='registration'),
    path('registrationverify.html', views.verify_otp, name='registrationverify'),
    path('verify-otp/', views.verify_otp, name='VerifyOtp'),
    path('Login.html', views.Login, name='Login'),
    path('change-password/', views.change_password, name='Changepassword'),
    path('Forgotpassword.html', views.Forgotpassword, name='Forgotpassword'),
    path('Verifyotp.html', views.Verifyotp, name='Verifyotp'),
    path('Forgotpasswordupdate.html', views.Forgotpasswordupdate, name='Forgotpasswordupdate'),
    path('UserDetails.html', views.UserDetails, name='UserDetails'),
    path('UserDetailsUpdate.html', views.UserDetailsUpdate, name='UserDetailsUpdate'),
    path('Logout.html', views.Logout, name='Logout'),

    #wishlist
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'), 
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    #Cart
    path('add_to_cart/<int:id>/',views.add_to_cart,name='add_to_cart'),
    path('cart/',views.cart_view,name='cart_view'),
    path('remove_from_cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:product_id>/<path:selected_price_option>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),

    #Customize Cake
    path('Customizeorder', views.Customizeorder, name='Customizeorder'),
    path("custom-checkout/<int:order_id>/", views.CustomCakeCheckout, name="CustomCakeCheckout"), 
    path('Customizeorder.html', views.Customizeorder, name='Customizeorder'),
    path('Customorderhis/', views.Customorderhis, name='Customorderhis'),
    path("check-coupon/", views.check_coupon, name="check_coupon"),
    path('Trackcustomorder/<int:order_id>/', views.Trackcustomorder, name='Trackcustomorder'),
    path('custom-order/<int:order_id>/', views.custom_order_details, name='custom_order_details'),

    #order
    path('Checkout.html',views.Checkout, name='Checkout'),
    path('checkout/', views.Checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path("order-confirmation/<int:order_id>/", views.order_confirmation, name="order_confirmation"),
    path('Myorder.html', views.Myorder, name='Myorder'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('order-details/<int:order_id>/', views.order_details, name='order_details'),
    path('cancel_order/<str:order_id>/', views.cancel_order, name='cancel_order'),
    path('order/<int:order_id>/cancel/', views.cancel_order_page, name='cancel_order_page'),
    path('order/<int:order_id>/process_cancel/', views.process_cancel_order, name='process_cancel_order'),
    path('return_order/<int:order_id>/', views.return_order_page, name="return_order_page"),
    path('process_return/<int:order_id>/', views.process_return_order, name="process_return_order"),
    path('order-success/', views.order_success, name='order_success'),

    #Download
    path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('view-invoice/<int:order_id>/', views.view_invoice, name='view_invoice'),
    path('invoice/<int:order_id>/', views.invoice_view, name='invoice_view'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)