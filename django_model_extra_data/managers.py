#!//usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 NZME

from __future__ import unicode_literals, absolute_import

from operator import methodcaller

from django.db.models import Manager, QuerySet


class PolymorphicManager(Manager):
    """
    polymorphic manager
    """

    def get_queryset(self):
        queryset = super(PolymorphicManager, self).get_queryset()
        return queryset.filter(class_type__in=map(
            methodcaller('content_type'),
            self.model.class_descendants(include_self=True)
        ))
