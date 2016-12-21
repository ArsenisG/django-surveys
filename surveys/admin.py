# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib import admin

from founders.users.utils import get_user_type
from founders.utils.urls_resolvers import get_admin_change_url
from . import app_settings
from .constants import STAR_RATING_TYPE
from .models import RatingType, Rating, Review


@admin.register(RatingType)
class RatingTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_value', 'max_value')
    search_fields = ('name',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('value', 'type')
    list_filter = ('type',)


class BadRatingFilter(admin.SimpleListFilter):
    title = "Bad Reviews"
    parameter_name = 'bad_reviews'

    def lookups(self, request, model_admin):
        return [
            ('y', "Below 3 stars"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'y':
            return queryset.filter(rating__value__lt=3)
        return queryset


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'review_for',
        'item_type',
        'rating_value',
        'optout_link',
        'user',
        'user_type',
        'timestamp',
        'comment',
        'would_recommend',
    )
    list_filter = (
        BadRatingFilter,
        ('content_type', admin.RelatedOnlyFieldListFilter),
        ('rating', admin.RelatedOnlyFieldListFilter),
        'timestamp',
    )
    search_fields = ('user__first_name', 'user__last_name', 'comment')

    @property
    def media(self):
        media = super(ReviewAdmin, self).media
        fa_css = app_settings.SURVEYS_FONT_AWESOME_CSS
        media.add_css({'all': (fa_css,)} if fa_css else {})
        return media

    def item_type(self, obj):
        return "{0}".format(obj.content_type).capitalize()

    def review_for(self, obj):
        return "{0}".format(obj.content_object)

    def user_type(self, obj):
        return ', '.join([t.capitalize() for t in get_user_type(obj.user)])

    def optout_link(self, obj):
        try:
            optout = obj.content_object.speaker.optout.by_recent().first()
            url = get_admin_change_url(optout)
            return """<a href="{url}" target="_blank">link</a>""".format(url=url)
        except (TypeError, AttributeError):
            return ""

    optout_link.allow_tags = True

    def rating_value(self, obj):
        if obj.rating.type.name == STAR_RATING_TYPE:
            try:
                val = "".join(['<i class="fa fa-star"></i>' for _ in range(obj.rating.value)])
                return """<div style="min-width: {0}px;">{1}</div>""".format(obj.rating.value * 12, val)
            except TypeError:
                # None rating
                return "None"
        return obj.rating

    rating_value.allow_tags = True
    rating_value.short_description = "Rating"
    rating_value.admin_order_field = 'rating__value'