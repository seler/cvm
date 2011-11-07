# -*- coding: utf-8 -*- 

from django import template
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.core.cache import cache
from django.db import models

from cms_local.templatetags.util_tags import set_tag

from user_media.models import UserPhoto, UserVideo, UserAudio

from portfolio.forms import ContactForm, FilterForm
from portfolio.models import Album, Portfolio, PortfolioCategory, School, Relationship, Region

register = template.Library()

@register.inclusion_tag('portfolio/tags/menu.html')
def portfolio_menu(selected):
    stats_dict = _get_stats()
    return {'MEDIA_URL': settings.MEDIA_URL, 'selected': selected, 'portfolios_num': stats_dict['portfolios_num']}

ORDER_BY = {
    'najlepsze': ('-rating_last_month', '-rating_curr_month', '-rating_total'),
    'najnowsze': ('-user__date_joined',),
    'komentowane': ('-comments_num',),
    'ulubione': ('-favorite__pub_date',),
    'znajomi': ('-friends__pub_date',),
}

FILTERS = {
    'work_type': 'portfoliocategory__work_type__in',
    'category': 'portfoliocategory__category__in',
    'country': 'region',
    'voyvodship': 'region',
    'city': 'region',
    'school': 'school',
}

def _prepare_query_filters(filters):
    query_filters = {}
    text_query = None
    region_query = models.Q()
    for name, value in filters.iteritems():
        if value:
            if name != 'query':
                key = FILTERS.get(name, None)
                if key == 'region':
                    try:
                        region = Region.objects.get(pk=value)
                    except Region.DoesNotExist:
                        pass
                    else:
                        region_query &= models.Q(region__path__startswith=region.path)
                elif key and value:
                    if isinstance(value, list):
                        value = [v for v in value if v]
                    if value:
                        query_filters[key] = value
            elif value != 'szukaj w portfolio':
                text_query = models.Q(user__first_name__istartswith=value)
                text_query |= models.Q(user__last_name__istartswith=value)
                text_query |= models.Q(who_am_i__icontains=value)
                text_query |= models.Q(what_am_i_doing__icontains=value)
    return text_query, region_query, query_filters

def _prepare_filters(query_dict):
    filters = {}
    filters['work_type'] = query_dict.getlist('work_type')
    filters['category'] = query_dict.getlist('category')
    filters['country'] = query_dict.get('country', None)
    filters['voyvodship'] = query_dict.get('voyvodship', None)
    filters['city'] = query_dict.get('city', None)
    filters['school'] = query_dict.get('school', None)
    filters['query'] = query_dict.get('query', None)
    return filters

@register.inclusion_tag('portfolio/tags/lead.html', takes_context=True)
def portfolio_lead(context, lead_type, limit=3):
    request = context.get('request')
    order_by = ORDER_BY.get(lead_type)
    filters = {}
    if request.method == 'POST':
        filters = _prepare_filters(request.POST)
    text_query, region_query, query_filters = _prepare_query_filters(filters)
    object_list = Portfolio.objects.published().filter(lead_photo__isnull=False, **query_filters)
    if text_query:
        object_list = object_list.filter(text_query)
    if region_query:
        object_list = object_list.filter(region_query)
    object_list = object_list.select_related('user', 'country', 'voyvodship', 'city').distinct().order_by(*order_by)[:limit]
    return {'MEDIA_URL': settings.MEDIA_URL, 'object_list': object_list, 'title': lead_type, 'request': request}

@register.inclusion_tag('portfolio/tags/top.html', takes_context=True)
def portfolio_top(context, lead_type, paginate_by=10):
    request = context.get('request')
    order_by = ORDER_BY.get(lead_type)
    filters = {}
    if request.method == 'POST':
        filters = _prepare_filters(request.POST)
    text_query, region_query, query_filters = _prepare_query_filters(filters)
    object_list = Portfolio.objects.published().filter(lead_photo__isnull=False, **query_filters)
    if text_query:
        object_list = object_list.filter(text_query)
    if region_query:
        object_list = object_list.filter(region_query)
    if lead_type == 'ulubione' and request.user.is_authenticated():
        object_list = object_list.filter(favorite__user=request.user)
    elif lead_type == 'znajomi' and request.user.is_authenticated():
        object_list = object_list.filter(rev_friends__confirmed=True, rev_friends__owner__user=request.user)
    object_list = object_list.select_related('user').distinct().order_by(*order_by)
    paginator = Paginator(object_list, paginate_by)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    page_obj = paginator.page(page)
    return {'MEDIA_URL': settings.MEDIA_URL, 'object_list': page_obj.object_list, 'page_obj': page_obj, 'query_dict': request.GET.copy(), 'title': lead_type}

@set_tag
def portfolio_num(filter_name, value, filters=None):
    filters = filters if filters is not None else {}
    filters = filters.copy()
    if filter_name in ('work_type', 'category'):
        filters[filter_name] = filters.get(filter_name, []) + [value] # nie mozna uzyc setdefault(filter_name, []).append(value), aby nie modyfikowac filtrow w innym miejscu - deepcopy tutaj nie dziala :(
    else:
        if value:
            filters[filter_name] = value
    text_query, region_query, query_filters = _prepare_query_filters(filters)
    num = Portfolio.objects.published().filter(**query_filters)
    if text_query:
        num = num.filter(text_query)
    if region_query:
        num = num.filter(region_query)
    return num.distinct().count()
register.tag('portfolio_num', portfolio_num)

@register.filter
def portfolio_append_filters(value, filters):
    value.field.widget._filters = filters
    return value

def _filter_to_name(key, value):
    if key == 'work_type':
        return u'Rodzaj', PortfolioCategory.WORK_TYPE_DICT.get(value)
    elif key == 'category':
        return u'Kategoria', PortfolioCategory.CATEGORY_DICT.get(value)
    elif key == 'country':
        return u'Państwo', Region.objects.get(pk=value).name
    elif key == 'voyvodship':
        return u'Województwo/okręg', Region.objects.get(pk=value).name
    elif key == 'city':
        return u'Miasto', Region.objects.get(pk=value).name
    elif key == 'school':
        return u'Szkoła', School.objects.get(pk=value).name
    return None, None

@register.inclusion_tag('portfolio/tags/filters.html', takes_context=True)
def portfolio_filters(context):
    request = context.get('request')
    filters = {}
    if request.method == 'POST':
        filters = _prepare_filters(request.POST)
    data = request.POST.copy()
    data['filters'] = filters
    filters_named = []
    for key, values in filters.iteritems():
        if isinstance(values, list):
            for value in values:
                if value:
                    key_named, value_named = _filter_to_name(key, int(value))
                    if key_named and value_named:
                        filters_named.append((key, value, key_named, value_named))
        elif key != 'query':
            value = values
            if value:
                key_named, value_named = _filter_to_name(key, int(value))
                if key_named and value_named:
                    filters_named.append((key, value, key_named, value_named))
    filters_named.sort()
    if request.method == 'POST':
        form = FilterForm(data)
    else:
        form = FilterForm()
    return {'MEDIA_URL': settings.MEDIA_URL, 'filters': filters, 'filters_named': filters_named, 'form': form}

@register.inclusion_tag('portfolio/tags/contact_form.html')
def portfolio_contact_form(portfolio):
    return {'form': ContactForm(initial={'portfolio': portfolio.id})}

@register.inclusion_tag('portfolio/tags/folders.html')
def portfolio_folders(portfolio):
    return {'folders': portfolio.folder_set.published().order_by('sort_order')}

@register.inclusion_tag('portfolio/tags/header.html', takes_context=True)
def portfolio_header(context, portfolio, selected):
    request = context.get('request', None)
    user = None
    if request:
        user = request.user
    return {'portfolio': portfolio, 'MEDIA_URL': settings.MEDIA_URL, 'selected': selected, 'user': user}

@register.inclusion_tag('portfolio/tags/slideshow.html', takes_context=True)
def portfolio_slideshow(context, portfolio, limit=6):
    request = context.get('request', None)
    object_list = Album.objects.published().filter(portfolio=portfolio, user_selected=True, lead_photo__isnull=False).order_by('-pub_date')[:limit]
    return {'request': request, 'portfolio': portfolio, 'MEDIA_URL': settings.MEDIA_URL, 'object_list': object_list}

@register.inclusion_tag('portfolio/tags/slideshow_sg.html', takes_context=True)
def portfolio_slideshow_sg(context, limit=6):
    request = context.get('request', None)
    object_list = Portfolio.objects.published().select_related('user', 'country', 'voyvodship', 'city').order_by(*ORDER_BY.get('najlepsze'))[:limit]
    return {'request': request, 'MEDIA_URL': settings.MEDIA_URL, 'object_list': object_list}

@register.inclusion_tag('portfolio/tags/friends.html')
def portfolio_friends(portfolio):
    object_list = Portfolio.objects.filter(user__is_active=True, rev_friends__confirmed=True, rev_friends__owner=portfolio).select_related('user')
    return {'MEDIA_URL': settings.MEDIA_URL, 'object_list': object_list}

@register.inclusion_tag('portfolio/tags/folder.html', takes_context=True)
def portfolio_folder(context, folder):
    paginate_by = 6
    request = context.get('request')
    object_list = folder.album_set.published().all()
    paginator = Paginator(object_list, paginate_by)
    page_name = 'page%s' % folder.id
    try:
        page = int(request.GET.get(page_name, 1))
    except ValueError:
        page = 1
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        folder = None
        page_obj = None
    return {'object': folder, 'page_obj': page_obj, 'query_dict': request.GET.copy(), 'page_name': page_name}

ADJACENT_PAGES = getattr(settings, 'ADJACENT_PAGES', 2)
def portfolio_paginator_tag_query(page_obj, query_dict, pager_name='page', template_name="paginator/default.html"):
    query_dict = query_dict.copy()
    try:
        del query_dict[pager_name]
    except KeyError:
        pass

    if not page_obj:
        return {'MEDIA_URL': settings.MEDIA_URL, 'query_dict': query_dict, 'page_name': page_name, 'template_name': template_name}

    page_numbers = [ n for n in range(page_obj.number - ADJACENT_PAGES, page_obj.number + ADJACENT_PAGES + 1) if n > 0 and n <= page_obj.paginator.num_pages ]
    show_last = page_obj.paginator.num_pages not in page_numbers
    show_first = 1 not in page_numbers
    return {'MEDIA_URL': settings.MEDIA_URL, 'query_dict': query_dict, 'pager_name': pager_name, 'page_numbers': page_numbers, 'show_first': show_first, 'show_last': show_last, 'page_obj': page_obj, 'template_name': template_name}
register.inclusion_tag('paginator/base.html')(portfolio_paginator_tag_query)

@register.filter
def is_friend(user, portfolio):
    ''' Zwraca True, gdy jest znajomym, False, gdy nie jest, None gdy sprawdza samego siebie lub oczekujemy na potwierdzenie znajomosci. '''
    if user.id == portfolio.user_id:
        return None
    try:
        relation = portfolio.rev_friends.get(owner__user=user)
    except Relationship.DoesNotExist:
        return False
    else:
        if relation.confirmed:
            return True
        return None

@register.filter
def is_favorite(user, portfolio):
    if user.is_authenticated():
        return user.favorite_set.filter(portfolio=portfolio).exists()
    return False

STATS_KEY = 'portfolio_stats'
def _get_stats():
    stats_dict = cache.get(STATS_KEY)
    if not stats_dict:
        latest = list(Portfolio.objects.published().filter(lead_photo__isnull=False).select_related('user').order_by('-rating_last_month').only('lead_photo', 'user__username')[:4])
        if len(latest) < 4:
            if latest:
                latest += [latest[0]] * (4 - len(latest))
        stats_dict = {
            'latest': latest,
            'portfolios_num': Portfolio.objects.published().count(),
            'projects_num': Album.objects.published().count(),
            'photos_num': UserPhoto.objects.published().count(),
            'videos_num': UserVideo.objects.published().count(),
            'audios_num': UserAudio.objects.published().count(),
        }
        cache.set(STATS_KEY, stats_dict, 900)
    return stats_dict

@register.inclusion_tag('portfolio/tags/login.html', takes_context=True)
def portfolio_login(context):
    new_context = _get_stats()
    new_context['MEDIA_URL'] = settings.MEDIA_URL
    new_context['object'] = context.get('object')
    new_context['request'] = context['request']
    return new_context

@register.inclusion_tag('portfolio/tags/admin_albums.html', takes_context=True)
def portfolio_admin_albums(context, portfolio):
    paginate_by = 6
    request = context.get('request')
    object_list = portfolio.album_set.published(False).order_by('-pub_date')
    paginator = Paginator(object_list, paginate_by)
    page_name = 'page_album'
    try:
        page = int(request.GET.get(page_name, 1))
    except ValueError:
        page = 1
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = None
    return {'object': portfolio, 'page_obj': page_obj, 'query_dict': request.GET.copy(), 'page_name': page_name}

@register.inclusion_tag('portfolio/tags/admin_news.html', takes_context=True)
def portfolio_admin_news(context, portfolio):
    paginate_by = 6
    request = context.get('request')
    object_list = portfolio.news_set.published(active=False).order_by('-pub_date')
    paginator = Paginator(object_list, paginate_by)
    page_name = 'page_news'
    try:
        page = int(request.GET.get(page_name, 1))
    except ValueError:
        page = 1
    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = None
    return {'object': portfolio, 'page_obj': page_obj, 'query_dict': request.GET.copy(), 'page_name': page_name}

@register.inclusion_tag('portfolio/tags/stats.html')
def portfolio_stats():
    context = _get_stats()
    context['MEDIA_URL'] = settings.MEDIA_URL
    return context

@register.filter
def get_type(value):
    return type(value)
