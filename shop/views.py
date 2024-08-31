#from ast import Order
from email import message
from functools import total_ordering
from http.client import HTTPResponse
from itertools import product
import json
from os import name
import re
from django.http import HttpResponse, JsonResponse
from django.shortcuts import  redirect, render
from shop.form import CustomUserForm

from . models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout 
from django.contrib.auth.models import User

import random


#stripe.api_key = settings.STRIPE_SECRET_KEY

#import json
#home page function
def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{"products":products})

def index(request):
    rawcart=Cart.objects.filter(user=request.user)
    for item in rawcart:
        if item.product_qty > item.product.quantity:
            Cart.objects.delete(id=item.id)
    cartitems=Cart.objects.filter(user=request.user)        
    total_price=0
    for item in cartitems:
        total_price=total_price + item.product.selling_price * item.product_qty

    userprofile=Profile.objects.filter(user=request.user).first()

    context={'cartitems':cartitems,'total_price':total_price,'userprofile':userprofile}
    return render(request,"shop/checkout.html",context)


def placeorder(request):
    if request.method == 'POST':

        currentuser=User.objects.filter(id=request.user.id).first()
        if not currentuser.first_name:
            currentuser.first_name=request.POST.get('fname')
            currentuser.last_name=request.POST.get('lname')
            currentuser.save()

        if not Profile.objects.filter(user=request.user):
            userprofile=Profile()
            userprofile.user=request.user    
            userprofile.phone=request.POST.get('phone')
            userprofile.address=request.POST.get('address')
            userprofile.city=request.POST.get('city')
            userprofile.state=request.POST.get('state')
            userprofile.country=request.POST.get('country')
            userprofile.pincode=request.POST.get('pincode')
            userprofile.save()

        neworder=Itemorder()
        neworder.user=request.user
        neworder.fname=request.POST.get('fname')
        neworder.lname=request.POST.get('lname')
        neworder.email=request.POST.get('email')
        neworder.phone=request.POST.get('phone')
        neworder.address=request.POST.get('address')
        neworder.city=request.POST.get('city')
        neworder.state=request.POST.get('state')
        neworder.country=request.POST.get('country')
        neworder.pincode=request.POST.get('pincode')

        neworder.payment_mode=request.POST.get('payment_mode')
        neworder.payment_id=request.POST.get('payment_id')

        cart=Cart.objects.filter(user=request.user)
        cart_total_price=0
        for item in cart:
            cart_total_price=cart_total_price + item.product.selling_price*item.product_qty

        neworder.total_price=cart_total_price    
        trackno='karthika'+str(random.randint(1111111,9999999))
        while Itemorder.objects.filter(tracking_no=trackno) is None:
            trackno='karthika'+str(random.randint(1111111,9999999))

        neworder.tracking_no=trackno
        neworder.save()    

        neworderitems=Cart.objects.filter(user=request.user)
        for item in neworderitems:
            OrderItems.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.product_qty
            )
            #decrease the product quantity
            orderproduct=Product.objects.filter(id=item.product_id).first()
            orderproduct.quantity=orderproduct.quantity - item.product_qty
            orderproduct.save()

        Cart.objects.filter(user=request.user).delete()
        messages.success(request,"your order has been placed success")    

        payMode = request.POST.get('payment_mode')
        if (payMode == "Paid by razorpay"):
            return JsonResponse({'status':"your order has been placed success"})

    return redirect("/")    

def Razorpay(request):
    cart=Cart.objects.filter(user=request.user)
    total_price=0
    for item in cart:
        total_price=total_price + item.product.selling_price * item.product_qty
    return JsonResponse({
        'total_price':total_price
    })    


def orders(request):
    return HttpResponse("my orders page")

def favviewpage(request):
    if request.user.is_authenticated:
        fav=Favourite.objects.filter(user=request.user)
        return render(request,"shop/fav.html",{"fav":fav})
    else:
        return redirect("/")

def remove_fav(request,fid):
    item=Favourite.objects.get(id=fid)
    item.delete()
    return redirect("/favviewpage")

#cart page create function
def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,"shop/cart.html",{"cart":cart})
    else:
        return redirect("/")
    
# remove butten click panna remove aaga    
def remove_cart(request,cid):
    cartitem=Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("/cart")

def fav_page(request):
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:       
            data=json.load(request)
            product_id = data['pid']
            # user already login pannatha check panna if condition
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id,product_id=product_id):
                    return JsonResponse({'status':'Product Already in Favorite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user,product_id=product_id)
                    return JsonResponse({'status':'product Added to Favourite'}, status=200)
        else:
            return JsonResponse({'status':'Login to Add Favourite'}, status=200)
    else:
        return JsonResponse({'status':'Invaild Access'}, status=200)

def add_to_cart(request):
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:       #user login panirukagala check panna
            data=json.load(request)
            #print(data['product_qty'])
            #print(data['pid']) 
        # database use panna new variable store pananum    
            product_qty = data['product_qty']
            product_id = data['pid']
            
            #print(request.user.id)
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id,product_id=product_id):
                      return JsonResponse({'status':'Product Already in Cart'}, status=200)
                else:
                    if product_status.quantity>=product_qty:
                        Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
                        return JsonResponse({'status':'Product Added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status':'Product Stack Not Available'}, status=200)
        else:
            return JsonResponse({'status':'Login to Add cart'}, status=200)
    else:
        return JsonResponse({'status':'Invaild Access'}, status=200)


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logout successful")
    return redirect("/")    

def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=='POST':
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfuly")
                return redirect("/")
            else:
                messages.error(request,"Invaild User Name or Password")
                return redirect("/login")
        
        return render(request,"shop/login.html")

#register page function
def register(request):
    form=CustomUserForm()
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration Success You can Login Now...")
            return redirect('/login')    
            
    return render(request,"shop/register.html",{'form':form})

#collection page
def collections(request):
    category=Catagory.objects.filter(status=0)
    return render(request,"shop/collections.html",{"catagory":category})

def collectionsview(request,name):
    if(Catagory.objects.filter(name=name,status=0)):
        products=Product.objects.filter(category__name=name)
        return render(request,"shop/products/index.html",{"products":products,"category_name":name})
    else:
        messages.warning(request, "No such catagory found")
        return redirect('collections')

def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request,"shop/products/productdetails.html",{"products":products})
        else:
            messages.error(request,"No such product found")
            return redirect('collections')
    else:
        messages.error(request,"No such catagory name")
        return redirect('collections')