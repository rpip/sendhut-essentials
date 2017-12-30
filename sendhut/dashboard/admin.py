# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Company, Employee, Allowance, Invite


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'user',
        'name',
        'address',
    )
    list_filter = ('created',)
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'user',
        'role',
        'company',
        'allowance',
    )
    list_filter = ('created',)


@admin.register(Allowance)
class AllowanceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'created_by',
        'name',
        'frequency',
        'limit',
        'company',
    )
    list_filter = ('created',)
    search_fields = ('name',)


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'token',
        'date_joined',
        'email',
        'role',
        'company',
    )
    list_filter = (
        'created',
        'date_joined',
        'company',
    )
