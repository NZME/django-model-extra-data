#!//usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 NZME

from __future__ import unicode_literals, absolute_import

from django.utils.lru_cache import lru_cache
from json_encoder import json

from django_model_extra_data.forms.utils import validate_form, form_data


class ExtraDataModelMixin(object):

    extra_form_class = None  # form class defines extra data
    extra_data_field = None  # model field to store extra data json string

    def __init__(self, *args, **kwargs):
        if kwargs:
            # set extra data to instance, it's possible for named arguments only
            for name in self.extra_form_fields():
                if name in kwargs:
                    setattr(self, name, kwargs.pop(name))

        super(ExtraDataModelMixin, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name in self.extra_form_fields():
            extra_data = self.extra_data_parsed()
            for key in set(self.extra_form_fields()) - set(dir(self)):
                # set extra data for missing instance attributes only
                setattr(self, key, extra_data[key])

            return extra_data[name]

        return super(ExtraDataModelMixin, self).__getattr__(name)

    @classmethod
    def extra_form_fields(cls):
        return cls.extra_form_class.base_fields.keys()

    def extra_data_parsed(self):
        extra_data = self.extra_data_loads(self.extra_data, validate=False)
        return extra_data

    @property
    def extra_data(self):
        return getattr(self, self.extra_data_field, None)

    @extra_data.setter
    def extra_data(self, value):
        setattr(self, self.extra_data_field, value)

    @classmethod
    @lru_cache()
    def extra_data_loads(cls, json_string, validate=True):
        form = cls.extra_form_class(data=json.loads(json_string or '{}'))
        validate_form(form) if validate else form.full_clean()
        return form_data(form)

    @classmethod
    def extra_data_dumps(cls, data, validate=True):
        form = cls.extra_form_class(data=data)
        validate_form(form) if validate else form.full_clean()
        return json.dumps(form_data(form))

    def extra_data_from_attributes(self):
        return {name: getattr(self, name) for name in self.extra_form_fields()}

    def extra_data_in_attributes(self):
        attributes = dir(self)
        return any(name in attributes for name in self.extra_form_fields())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.extra_data or self.extra_data_in_attributes():
            self.extra_data = self.extra_data_dumps(
                self.extra_data_from_attributes()
            )

        return super(ExtraDataModelMixin, self).save(
            force_insert, force_update, using, update_fields
        )
