from __future__ import unicode_literals
from django_daraja.mpesa import  utils
from django.http import HttpResponse, JsonResponse
from django.views import View
from django_daraja.mpesa.core import MpesaClient
from decouple import config
from datetime import datetime


from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Product

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return  redirect('register')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def add_product(request):
    #Check if the form submitted has a method post
    if request.method == "POST":
        # start receiving data from the form
        p_name = request.POST.get('jina')
        p_quantity = request.POST.get('kiasi')
        p_price = request.POST.get('bei')

        # Finally save the data in your table called products
        product = Product(prod_name=p_name, prod_quantity=p_quantity, prod_price=p_price)
        product.save()
        # Redirect back with a success message
        messages.success(request, 'product saved successfully')
        return  redirect('add-product')
    return render(request, 'add-produt.html')


@login_required
def view_products(request):
    # Select all the products to be displayed
    products = Product.objects.all()
    return render(request, 'products.html', {'products' : products})


@login_required
def supplier_details(request):
    #Check if the form submitted has a method post
    if request.method == "POST":
        # start receiving data from the form
        p_supplied = request.POST.get('jina')
        p_quantity = request.POST.get('kiasi')
        p_cost = request.POST.get('bei')

        # Finally save the data in your table called products
        product = Product(prod_supplied=p_supplied, prod_quantity=p_quantity, prod_cost=p_cost)
        product.save()
        # Redirect back with a success message
        messages.success(request, 'Supplier details saved successfully')
        return  redirect('supplier')
    return render(request, 'supplier.html')


@login_required
def delete_product(request, id):
    # Fetch the product to be deleted
    product = Product.objects.get(id=id)
    # Delete the product
    product.delete()
    # Redirect back to products page with a success message
    messages.success(request, 'Product deleted successfully')
    return redirect('product')


@login_required
def update_product(request, id):
    # Fetch the product to be updated
    product = Product.objects.get(id=id)
    # Check if the form submitted has a method post
    if request.method =="POST":
        # Receive data from the form
        updated_name = request.POST.get('jina')
        updated_quantity = request.POST.get('kiasi')
        updated_price = request.POST.get('bei')


        # Update the product with the received updated data
        product.prod_name = updated_name
        product.prod_quantity = updated_quantity
        product.prod_price = updated_price


        # Return the data back to the database and redirect back
        # to products page with a success message
        product.save()
        messages.success(request, 'product updated successfully')
        return redirect('product')
    return render(request, 'update-product.html', {'product': product})

# Initiate the MpesaClient
cl = MpesaClient()
# Set up callbacks
stk_callback_url = "https://api.darajambili.com/express-payment"
b2c_callback_url = "https://api.darajambili.com/b2c/result"

#Generate the transaction access_token
def auth_success(request):
    token = cl.access_token()
    return JsonResponse(token,safe=False)

@login_required
def payment(request, id):
    # select the product to be paid
    product = Product.objects.get(id=id)
    if request.method == "POST":
        phone_number = request.POST.get('nambari')
        amount = request.POST.get('bei')
        # Convert the amount to be an integer
        amount = int(amount)
        account_ref = 'WANYAMA001'
        transaction_desc = 'paying for a product'
        transaction = cl.stk_push(phone_number, amount, account_ref, transaction_desc, stk_callback_url)
        return JsonResponse(transaction.response_description, safe=False)
    return render(request, 'payment.html', {'product': product})