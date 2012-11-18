from django.core.urlresolvers import reverse
from django import template


register = template.Library()


@register.inclusion_tag('postorius/menu/list_nav.html', takes_context=True)
def list_nav(context, current, title=None):
    if title is None:
        title = ''
    return dict(list=context['list'],
                current=current,
                user=context['request'].user,
                title=title)


@register.inclusion_tag('postorius/menu/mm_user_nav.html', takes_context=True)
def user_nav(context, current, title=None):
    if title is None:
        title = ''
    return dict(mm_user=context['mm_user'],
                current=current,
                user=context['request'].user,
                title=title)


@register.inclusion_tag('postorius/menu/users_nav.html', takes_context=True)
def users_nav(context, current, title=None):
    if title is None:
        title = ''
    return dict(current=current,
                user=context['request'].user,
                title=title)


@register.simple_tag
def page_url(view_name, *args, **kwargs):
    return reverse(view_name, *args, **kwargs)


@register.simple_tag(takes_context=True)
def nav_active_class(context, current, view_name):
    if current == view_name:
        return 'mm_active'
    return ''
