#!//usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 NZME

from __future__ import unicode_literals, absolute_import

import logging
import warnings

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.lru_cache import lru_cache
from django_model_extra_data.managers import PolymorphicManager
from json_encoder import json

from django_model_extra_data.forms.utils import validate_form, form_data


logger = logging.getLogger(__name__)


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


def find_class(cls, class_type_id):
    for c in cls.class_descendants(include_self=True):
        if c.content_type().id == class_type_id:
            return c

    return cls


def all_subclasses(cls):
    for sub_class in cls.__subclasses__():
        yield sub_class
        for sub_sub_class in all_subclasses(sub_class):
            yield sub_sub_class


class PolymorphicModel(models.Model):
    class_type = models.ForeignKey(ContentType, editable=False)

    objects = PolymorphicManager()

    class Meta(object):
        abstract = True

    def __init__(self, *args, **kwargs):
        super(PolymorphicModel, self).__init__(*args, **kwargs)
        # set class_type to current class if empty.
        if not getattr(self, 'class_type', None):
            self.class_type = self.content_type()

    @classmethod
    def class_descendants(cls, include_self=False):
        if include_self:
            yield cls

        for sub_class in all_subclasses(cls):
            yield sub_class

    @classmethod
    def content_type(cls):
        return ContentType.objects.get_for_model(cls, for_concrete_model=False)

    @classmethod
    def from_db(cls, db, field_names, values):
        base = cls
        try:
            class_type_index = field_names.index('class_type_id')
        except ValueError:
            logger.error("Can't find 'class_type_id' in field_names {!r}".format(
                field_names
            ))
        else:
            try:
                class_type_id = values[class_type_index]
            except IndexError:
                logger.error(
                    "Can't find class_type value in values {!r} for index {!r}"
                    .format(values, class_type_index)
                )
            else:
                base = find_class(cls, class_type_id)
                if base is not cls and not base._meta.proxy:
                    warnings.warn(
                        'Only child proxy models are supported',
                        RuntimeWarning
                    )

        return super(PolymorphicModel, base).from_db(db, field_names, values)
