#!//usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 NZME

from __future__ import unicode_literals, absolute_import

from django_model_extra_data.models import PolymorphicModel


class PolymorphicTestModel(PolymorphicModel):
    """
    concrete model for tests
    """


class Child1Model(PolymorphicModel):

    class Meta(object):
        proxy = True


class Child2Model(PolymorphicModel):

    class Meta(object):
        proxy = True


class Child3Model(PolymorphicModel):

    class Meta(object):
        proxy = True


class Child11Model(Child1Model):

    class Meta(object):
        proxy = True


class Child12Model(Child1Model):

    class Meta(object):
        proxy = True


class Child121Model(Child1Model):

    class Meta(object):
        proxy = True
