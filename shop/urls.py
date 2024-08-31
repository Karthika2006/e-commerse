from django.urls import path
from . import views

#from shop import checkout

urlpatterns = [
    path('',views.home,name="home"), #home page
    path('register',views.register,name="register"), #register page
    path('login',views.login_page,name="login"),
    path('logout',views.logout_page,name="logout"),
    path('cart',views.cart_page,name="cart"),
    path('fav',views.fav_page,name="fav"),
    path('favviewpage',views.favviewpage,name="favviewpage"),
    path('remove_fav/<str:fid>',views.remove_fav,name="remove_fav"),
    path('remove_cart/<str:cid>',views.remove_cart,name="remove_cart"),
    path('collections',views.collections,name="collections"), #collection page
    path('collections/<str:name>',views.collectionsview,name="collections"),
    path('collections/<str:cname>/<str:pname>',views.product_details,name="product_details"),
    path('addtocart',views.add_to_cart,name="addtocart"),
   # path('buy',views.buy_now,name="buy"),
   path('checkout',views.index,name='checkout'),
   path('placeorder',views.placeorder,name='placeorder'),

   path('proceed-to-pay',views.Razorpay),
   path('my-orders',views.orders)

]