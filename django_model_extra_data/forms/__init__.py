#!//usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 NZME

from __future__ import unicode_literals, absolute_import
import datetime
import logging

from django import forms
from django.core.exceptions import ValidationError
from django.utils import six
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.encoding import force_text

logger = logging.getLogger(__name__)


def log_strptime_format(cls, format):
    logger.info('{}.{}.strptime(format={!r}) used'.format(
        cls.__module__, cls.__name__, format
    ))


def parse_date_as_datetime(string, default_time=None):
    value = parse_date(string)
    if isinstance(value, datetime.date):
        value = datetime.datetime.combine(
            value, default_time or datetime.time(0)
        )

    return value


def parse_datetime_or_date(string, default_time=None):
    """
    Convert string into datetime.datetime object (aware if timezone in present)
    :param string: iso8601 datetime string
    :param default_time: instance of datetime.time as default for date only
    :return: datetime.datetime or None
    """
    if len(string) <= 10:  # len(string) <= len('2016-02-29')
        value = parse_date_as_datetime(string, default_time)

    else:
        value = parse_datetime(string)

    return value


class DateField(forms.DateField):
    input_formats = ('%Y-%m-%d', )

    def strptime(self, value, format):
        value = super(DateField, self).strptime(value, format)
        log_strptime_format(type(self), format)
        return value


class TimeField(forms.TimeField):
    input_formats = ('%H:%M:%S', '%H:%M', '%H:%M:%S.%f')

    def strptime(self, value, format):
        value = super(TimeField, self).strptime(value, format)
        log_strptime_format(type(self), format)
        return value


class DateTimeField(forms.DateTimeField):

    default_time_for_date = datetime.time(0)

    def prepare_value(self, value):
        return value

    def to_python(self, value):
        """
        Validates that the input can be converted to a time.
        Returns a Python datetime.datetime object.
        """
        if value in self.empty_values:
            return None

        if isinstance(value, datetime.datetime):
            return value

        if isinstance(value, datetime.date):
            return datetime.datetime.combine(value, self.default_time_for_date)

        # Try to coerce the value to unicode.
        unicode_value = force_text(value, strings_only=True)
        if not isinstance(unicode_value, six.text_type):
            raise ValidationError(self.error_messages['invalid'],
                                  code='invalid')

        try:
            value = parse_datetime_or_date(unicode_value.strip(),
                                           self.default_time_for_date)
            if isinstance(value, datetime.datetime):
                return value

        except ValueError:
            pass  # we will raise error on the end of function

        raise ValidationError(self.error_messages['invalid'], code='invalid')
