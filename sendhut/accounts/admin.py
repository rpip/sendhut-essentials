# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import User, Address


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'password',
        'is_superuser',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
        'date_joined',
        'created',
        'updated',
        'deleted',
        'phone',
        'last_login',
        'identity_verified',
    )
    list_filter = (
        'is_superuser',
        'is_staff',
        'is_active',
        'date_joined',
        'created',
        'last_login',
        'identity_verified',
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'user',
        'postcode',
        'county',
        'city',
        'location',
        'address_1',
        'address_2',
        'address_3',
    )
    list_filter = ('created',)
