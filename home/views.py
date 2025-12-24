from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from accounts.models import HotelUser,HotelVendor,Hotel,Ameneties,HotelImages,HotelManager,HotelBooking
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login,logout
import random
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.views.decorators.cache import cache_page
# Create your views here.
@cache_page(60 * 1,)  # Cache the index view for 15 minutes
def index(request):
    hotels = Hotel.objects.all().select_related('hotel_owner').prefetch_related('ameneties', 'hotel_images')
    if request.GET.get('search'):
        hotels = hotels.filter(hotel_name__icontains = request.GET.get('search'))

    if request.GET.get('sort_by'):
        sort_by = request.GET.get('sort_by')
        if sort_by == "sort_low":
            hotels = hotels.order_by('hotel_offer_price')
        elif sort_by == "sort_high":
            hotels = hotels.order_by('-hotel_offer_price')
    return render(request, 'utils/index.html', context={'hotels': hotels[:50]})


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


    return render(request, 'utils/hotel_detail.html', context = {'hotel' : hotel})