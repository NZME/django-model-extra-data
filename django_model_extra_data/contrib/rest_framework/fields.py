#!//usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 NZME

from __future__ import unicode_literals, absolute_import

from json_encoder import json
from rest_framework import serializers


class FormField(serializers.Field):
    """ default Rest framework field mapped to existing django form field """

    def __init__(self, form_field, *args, **kwargs):
        self.form_field = form_field
        super(FormField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        return json.dumps(value)

    def to_internal_value(self, data):
        return self.form_field.to_python(data)
