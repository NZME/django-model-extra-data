#!//usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 NZME

from __future__ import unicode_literals, absolute_import

from django_model_extra_data.contrib.rest_framework.field_mapping import \
    map_form_to_serializer


class ExtraDataSerializerMixin(object):

    def build_property_field(self, field_name, model_class):
        """
        some model properties can be extra data fields
        """
        if field_name in model_class.extra_form_fields():
            return self.build_extra_form_field(field_name, model_class)

        return super(ExtraDataSerializerMixin, self).build_property_field(
            field_name, model_class
        )

    def build_unknown_field(self, field_name, model_class):
        """
        some unknown fields can be extra data fields
        """
        if field_name in model_class.extra_form_fields():
            return self.build_extra_form_field(field_name, model_class)

        return super(ExtraDataSerializerMixin, self).build_unknown_field(
            field_name, model_class
        )

    def build_extra_form_field(self, field_name, model_class):
        """
        map django form field into rest framework serializer field
        """
        form_field_class = model_class.extra_form_class.base_fields[field_name]
        field_class, field_kwargs = map_form_to_serializer(form_field_class)
        return field_class, field_kwargs
