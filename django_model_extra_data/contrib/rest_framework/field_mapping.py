#!//usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 NZME

from __future__ import unicode_literals, absolute_import

from django import forms
from django.utils.six import PY34
from rest_framework import serializers

from django_model_extra_data.contrib.rest_framework.fields import FormField

if PY34:
    from functools import singledispatch
else:
    from singledispatch import singledispatch


@singledispatch
def map_form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(form_field_kwargs(form_field))
    return FormField, field_kwargs


@map_form_to_serializer.register(forms.BooleanField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.pop('allow_null', None)  # not valid for BooleanField
    return serializers.BooleanField, field_kwargs


@map_form_to_serializer.register(forms.CharField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(char_field_kwargs(form_field))
    return serializers.CharField, field_kwargs


@map_form_to_serializer.register(forms.ChoiceField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(choice_field_kwargs(form_field))
    return serializers.ChoiceField, field_kwargs


@map_form_to_serializer.register(forms.DateField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    return serializers.DateField, field_kwargs


@map_form_to_serializer.register(forms.DateTimeField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    return serializers.DateTimeField, field_kwargs


@map_form_to_serializer.register(forms.DecimalField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(integer_field_kwargs(form_field))
    field_kwargs.update(decimal_field_kwargs(form_field))
    return serializers.DecimalField, field_kwargs


@map_form_to_serializer.register(forms.EmailField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(char_field_kwargs(form_field))
    return serializers.EmailField, field_kwargs


@map_form_to_serializer.register(forms.FileField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(file_field_kwargs(form_field))
    return serializers.FileField, field_kwargs


@map_form_to_serializer.register(forms.FilePathField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(choice_field_kwargs(form_field))
    field_kwargs.update(file_path_field_kwargs(form_field))
    return serializers.FilePathField, field_kwargs


@map_form_to_serializer.register(forms.FloatField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(integer_field_kwargs(form_field))
    return serializers.FloatField, field_kwargs


@map_form_to_serializer.register(forms.ImageField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(file_field_kwargs(form_field))
    return serializers.ImageField, field_kwargs


@map_form_to_serializer.register(forms.IntegerField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(integer_field_kwargs(form_field))
    return serializers.IntegerField, field_kwargs


@map_form_to_serializer.register(forms.GenericIPAddressField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(char_field_kwargs(form_field))
    field_kwargs.update(ip_address_field_kwargs(form_field))
    return serializers.IPAddressField, field_kwargs


@map_form_to_serializer.register(forms.NullBooleanField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    return serializers.NullBooleanField, field_kwargs


@map_form_to_serializer.register(forms.SlugField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(char_field_kwargs(form_field))
    return serializers.SlugField, field_kwargs


@map_form_to_serializer.register(forms.TimeField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    return serializers.TimeField, field_kwargs


@map_form_to_serializer.register(forms.URLField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    field_kwargs.update(char_field_kwargs(form_field))
    return serializers.URLField, field_kwargs


@map_form_to_serializer.register(forms.UUIDField)
def form_to_serializer(form_field):
    field_kwargs = field_common_kwargs(form_field)
    return serializers.UUIDField, field_kwargs


def field_common_kwargs(form_field):
    is_required = bool(form_field.required)
    has_initial = form_field.initial is not None
    kwargs = {
        'required': is_required,
        'allow_null': not (is_required or has_initial),
    }
    if form_field.label:
        kwargs['label'] = form_field.label

    if has_initial:
        kwargs['initial'] = form_field.initial
        if not is_required:
            # use initial value as default value
            # different from django form behaviour
            kwargs['default'] = form_field.initial

    if form_field.help_text:
        kwargs['help_text'] = form_field.help_text

    return kwargs


def form_field_kwargs(form_field):
    return {'form_field': form_field}


def char_field_kwargs(form_field):
    is_required = bool(form_field.required)
    has_initial = form_field.initial is not None
    return {
        'max_length': form_field.max_length,
        'min_length': form_field.min_length,
        'allow_null': False,  # CharField uses emtpy string be default
        'allow_blank': not (is_required or has_initial),
    }


def choice_field_kwargs(form_field):
    return {'choices': form_field.choices}


def file_field_kwargs(form_field):
    return {
        'max_length': form_field.max_length,
        'allow_empty_file': form_field.allow_empty_file,
    }


def integer_field_kwargs(form_field):
    return {
        'max_value': form_field.max_value,
        'min_value': form_field.min_value,
    }


def decimal_field_kwargs(form_field):
    return {
        'max_digits': form_field.max_digits,
        'decimal_places': form_field.decimal_places,
    }


def file_path_field_kwargs(form_field):
    return {
        'path': form_field.path,
        'match': form_field.match,
        'recursive': form_field.recursive,
        'allow_files': form_field.allow_files,
        'allow_folders': form_field.allow_folders,
    }


def ip_address_field_kwargs(form_field):
    return {'protocol': form_field.protocol}
