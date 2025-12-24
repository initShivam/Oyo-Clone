from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import HotelUser,HotelVendor,Hotel,Ameneties,HotelImages,HotelManager,HotelBooking
from django.db.models import Q
from django.http import HttpResponseRedirect
from .utils import generateRandomToken, sendEmailToken, sendOTPtoEmail
from django.contrib.auth import authenticate, login,logout
import random
from django.contrib.auth.decorators import login_required
from .utils import generateSlug
from datetime import datetime

def login_page(request):    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        hotel_user = HotelUser.objects.filter(
            email = email)
        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/accounts/login/')
        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/accounts/login/')
        hotel_user = authenticate(username = hotel_user[0].username , password=password)
        if hotel_user:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('index')
        messages.warning(request, "Invalid credentials")
        return redirect('/accounts/login/')
    return render(request, 'login.html')

def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number  = phone_number)
        )
        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('/accounts/register/')
        hotel_user = HotelUser.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()
        sendEmailToken(email , hotel_user.email_token)
        messages.success(request, "An email Sent to your Email")
        return redirect('/accounts/register/')
    return render(request, 'register.html')

def verify_email_token(request, token):
    try:
        hotel_user = HotelUser.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email verified")
        return redirect('/accounts/login/')
    except HotelUser.DoesNotExist:
        return HttpResponse("Invalid Token")

def send_otp(request, email):
    hotel_user = HotelUser.objects.filter(
            email = email)
    if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/accounts/login/')
    otp =  random.randint(1000 , 9999)
    hotel_user.update(otp =otp)
    sendOTPtoEmail(email , otp)
    return redirect(f'/accounts/verify-otp/{email}/')

def verify_otp(request , email):
    if request.method == "POST":
        otp  = request.POST.get('otp')
        hotel_user = HotelUser.objects.get(email = email)
        if otp == hotel_user.otp:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/accounts/login/')
        messages.warning(request, "Wrong OTP")
        return redirect(f'/accounts/verify-otp/{email}/')
    return render(request , 'verify_otp.html')

def login_vendor(request):    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        hotel_user = HotelVendor.objects.filter(
            email = email)
        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('accounts/login_vendor/')
        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('accounts/login_vendor/')
        hotel_user = authenticate(username = hotel_user[0].username , password=password)
        if hotel_user:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/accounts/dashboard/')  
        messages.warning(request, "Invalid credentials")
        return redirect('accounts/login_vendor/')
    return render(request, 'login_vendor.html')

def register_vendor(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number  = phone_number)
        )
        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('accounts/register_vendor/')
        hotel_user = HotelVendor.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            business_name = business_name,
            email_token = generateRandomToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()
        sendEmailToken(email , hotel_user.email_token)
        messages.success(request, "An email Sent to your Email")
        return redirect('register_vendor')
    return render(request, 'register_vendor.html')

@login_required(login_url='login_vendor')
def dashboard(request):
    # Retrieve hotels owned by the current vendor
    hotels = Hotel.objects.filter(hotel_owner=request.user)
    context = {'hotels': hotels}
    return render(request, 'dashboard.html', context)

@login_required(login_url='login_vendor')
def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price= request.POST.get('hotel_price')
        hotel_offer_price= request.POST.get('hotel_offer_price')
        hotel_location= request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)    
        ameneties = Ameneties.objects.all()
        ameneties = request.POST.getlist('amenities')
        for ameneti in ameneties:
            ameneti = Ameneties.objects.get(id = ameneti)
            hotel_obj.ameneties.add(ameneti)
            hotel_obj.save()
        hotel_vendor = HotelVendor.objects.get(id = request.user.id)
        hotel_obj = Hotel.objects.create(
            hotel_name = hotel_name,
            hotel_description = hotel_description,
            hotel_price = hotel_price,
            hotel_offer_price = hotel_offer_price,
            hotel_location = hotel_location,
            hotel_slug = hotel_slug,
            hotel_owner = hotel_vendor
        )
        messages.success(request, "Hotel Created")
        return redirect('/accounts/dashboard/')
    ameneties = Ameneties.objects.all()
    return render(request, 'add_hotel.html', context = {'ameneties' : ameneties})

@login_required(login_url='login_vendor')
def upload_images(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.method == "POST":
        image = request.FILES['image']
        print(image)
        HotelImages.objects.create(
        hotel = hotel_obj,
        image = image
        )
        return HttpResponseRedirect(request.path_info)
    return render(request, 'upload_images.html', context = {'images' : hotel_obj.hotel_images.all()})

@login_required(login_url='login_vendor')
def delete_image(request, id):
    print(id)
    print("#######")
    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Hotel Image deleted")
    return redirect('/accounts/dashboard/')

@login_required(login_url='login_vendor')
def edit_hotel(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug=slug)    
    # Check if the current user is the owner of the hotel
    if request.user.id != hotel_obj.hotel_owner.id:
        return HttpResponse("You are not authorized")
    if request.method == "POST":
        # Retrieve updated hotel details from the form
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        # Update hotel object with new details
        hotel_obj.hotel_name = hotel_name
        hotel_obj.hotel_description = hotel_description
        hotel_obj.hotel_price = hotel_price
        hotel_obj.hotel_offer_price = hotel_offer_price
        hotel_obj.hotel_location = hotel_location
        hotel_obj.save()
        messages.success(request, "Hotel Details Updated")
        return HttpResponseRedirect(request.path_info)
    # Retrieve amenities for rendering in the template
    ameneties = Ameneties.objects.all()
    # Render the edit_hotel.html template with hotel and amenities as context
    return render(request, 'edit_hotel.html', context={'hotel': hotel_obj, 'ameneties': ameneties})

def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')

def hotel_details(request, slug):
    hotel = Hotel.objects.get(hotel_slug = slug)
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date = datetime.strptime(start_date , '%Y-%m-%d')
        end_date = datetime.strptime(end_date , '%Y-%m-%d')
        days_count = (end_date - start_date).days
        if days_count <= 0:
            messages.warning(request, "Invalid Booking Date.")
            return HttpResponseRedirect(request.path_info)
        HotelBooking.objects.create(
            hotel = hotel,
            booking_user = HotelUser.objects.get(id = request.user.id),
            booking_start_date = start_date,
            booking_end_date =end_date,
            price = hotel.hotel_offer_price * days_count
        )
        messages.warning(request, "Booking Captured.")
        return HttpResponseRedirect(request.path_info)
    return render(request, 'hotel_detail.html', context = {'hotel' : hotel})

from .models import Author
def get_authors_books():
    authors = Author.objects.all()
    for author in authors:
        books = author.book_set.all()
        for book in books:
            print(book.title)
            authors = Author.objects.all()