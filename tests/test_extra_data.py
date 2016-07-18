#!//usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 NZME

from __future__ import unicode_literals, absolute_import

from decimal import Decimal

import datetime

import pytest
from django import forms
from django.db import models
from django.utils.timezone import utc

from django_model_extra_data.forms import DateField, TimeField, DateTimeField
from django_model_extra_data.forms.utils import FormValidationError
from django_model_extra_data.models import ExtraDataModelMixin


class FakeModel(models.Model):

    class Meta(object):
        abstract = True
        app_label = 'test'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        return  # stop model saving


class ExtraForm(forms.Form):
    date = DateField()
    time = TimeField()
    datetime = DateTimeField()
    number = forms.DecimalField(
        initial=Decimal('0.1'), max_digits=6, decimal_places=2
    )
    string = forms.CharField(max_length=23, required=False)


class ExtraModel(ExtraDataModelMixin, FakeModel):
    data = models.TextField(editable=False)

    extra_form_class = ExtraForm
    extra_data_field = 'data'


def test_initial_extra_data():
    instance = ExtraModel()
    assert instance.date is None
    assert instance.time is None
    assert instance.datetime is None
    assert instance.number == Decimal('0.1')
    assert instance.string == ''


def test_set_extra_data():
    date = datetime.date(2016, 2, 29)
    time = datetime.time(1, 2, 3)
    dt = datetime.datetime.combine(date, time).replace(tzinfo=utc)
    instance = ExtraModel(date=date, time=time, datetime=dt)
    assert instance.date == date
    assert instance.time == time
    assert instance.datetime == dt
    assert instance.number == Decimal('0.1')
    assert instance.string == ''

    instance = ExtraModel()
    instance.date = date
    instance.time = time
    instance.datetime = dt
    assert instance.date == date
    assert instance.time == time
    assert instance.datetime == dt
    assert instance.number == Decimal('0.1')
    assert instance.string == ''


def test_edit_some_extra_data():
    instance = ExtraModel()
    instance.string = 'test'
    assert instance.date is None
    assert instance.time is None
    assert instance.datetime is None
    assert instance.number == Decimal('0.1')
    assert instance.string == 'test'


def test_load_extra_data():
    date = datetime.date(2016, 2, 29)
    time = datetime.time(1, 2, 3)
    dt = datetime.datetime.combine(date, time).replace(tzinfo=utc)
    instance = ExtraModel(
        data='{"date": "2016-02-29", "time": "01:02:03", '
             '"datetime": "2016-02-29T01:02:03Z", "number": 0.2, '
             '"string": "testing string"}'
    )
    assert instance.date == date
    assert instance.time == time
    assert instance.datetime == dt
    assert instance.number == Decimal('0.2')
    assert instance.string == 'testing string'


def test_save_extra_data():
    instance = ExtraModel()
    instance.date = datetime.date(2016, 2, 29)
    instance.time = datetime.time(1, 2, 3)
    instance.datetime = datetime.datetime.combine(
        instance.date, instance.time
    ).replace(tzinfo=utc)
    instance.number = Decimal('0.2')
    instance.string = 'testing string'

    assert instance.data == ''
    instance.save()  # fake save by FakeModel
    data = '{"date": "2016-02-29", "time": "01:02:03", ' \
           '"datetime": "2016-02-29T01:02:03+00:00", "number": 0.2, ' \
           '"string": "testing string"}'

    assert instance.data == data


def test_create_with_extra_data():
    instance = ExtraModel.objects.create(
        date=datetime.date(2016, 2, 29),
        time=datetime.time(1, 2, 3),
        datetime=datetime.datetime(2016, 2, 29, 1, 2, 3, tzinfo=utc),
        number=Decimal('0.2'),
        string='testing string'
    )
    data = '{"date": "2016-02-29", "time": "01:02:03", ' \
           '"datetime": "2016-02-29T01:02:03+00:00", "number": 0.2, ' \
           '"string": "testing string"}'

    assert instance.data == data


def test_extra_data_validation():
    instance = ExtraModel()
    msg = "This field is required."
    with pytest.raises(FormValidationError) as exc_info:
        instance.save()

    messages = exc_info.value.message_dict
    assert 'time' in messages
    assert msg == messages['time'][0]
    assert 'date' in messages
    assert msg == messages['date'][0]
    assert 'datetime' in messages
    assert msg == messages['datetime'][0]
