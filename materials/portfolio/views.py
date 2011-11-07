# -*- coding: utf-8 -*-
# Create your views here.

import datetime
from hashlib import md5
import random
from StringIO import StringIO
import traceback

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django import forms
from django.forms.formsets import all_valid
from django.forms.models import modelformset_factory, BaseModelFormSet, inlineformset_factory
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import list_detail
from django.utils import translation
from django.utils.functional import SimpleLazyObject

from ho import pisa

from user_media.models import UserPhoto, UserVideo, UserAudio, UserGallery, UserPhotoPriority, UserVideoPriority, UserAudioPriority

from portfolio.forms import ContactForm, AlbumForm, NewsForm, TimedItemForm, EducationTimedItemForm, CVForm, EditContactForm
from portfolio.models import Portfolio, Relationship, Album, Favorite, Folder, School, PortfolioCategory, Region, TimedItem, ListItem
from portfolio import generic
from django.utils.decorators import method_decorator

FRIEND_CONFIRMATION_SUBJECT = u'Archirama.pl - potwierdzenie znajomości'
REGISTRATION_SUBJECT = u'Archirama.pl - aktywacja konta'
WORLD = SimpleLazyObject(lambda:Region.get_root_nodes()[0])

adv_context = {
    'adv_cat': 'archikracja',
    'adv_scat': 'portfolia_podstrony',
}
# autouzupelnianie

def autocomplete_folder_list(request, object_id):
    portfolio = get_object_or_404(Portfolio.objects.published(), pk=object_id)
    query = request.GET.get('q')
    if not query:
        raise Http404
    folders = list(portfolio.folder_set.filter(name__istartswith=query.strip(' ')).distinct())
    return HttpResponse('\n'.join([folder.name for folder in folders]))

def autocomplete_country_list(request):
    query = request.GET.get('q')
    if not query:
        raise Http404
    object_list = list(Region.objects.filter(type=Region.REGION_COUNTRY, name__istartswith=query.strip(' ')).distinct())
    return HttpResponse('\n'.join([obj.name for obj in object_list]))

def autocomplete_voyvodship_list(request):
    query = request.GET.get('q')
    if not query:
        raise Http404
    country = request.GET.get('country')
    queryset = Region.objects.all()
    if country:
        try:
            parent = queryset.get(type=Region.REGION_COUNTRY, name=country)
        except Region.DoesNotExist:
            pass
        else:
            queryset = parent.get_descendants()
    queryset = queryset.filter(type=Region.REGION_VOYVODSHIP, name__istartswith=query.strip(' ')).distinct()
    object_list = list(queryset)
    return HttpResponse('\n'.join([obj.name for obj in object_list]))

def autocomplete_city_list(request):
    query = request.GET.get('q')
    if not query:
        raise Http404
    country = request.GET.get('country')
    voyvodship = request.GET.get('voyvodship')
    queryset = Region.objects.all()
    if country:
        try:
            parent = queryset.get(type=Region.REGION_COUNTRY, name=country)
        except Region.DoesNotExist:
            pass
        else:
            queryset = parent.get_descendants()
    if voyvodship:
        try:
            parent = queryset.get(type=Region.REGION_VOYVODSHIP, name=voyvodship)
        except Region.DoesNotExist:
            pass
        else:
            queryset = parent.get_descendants()
    queryset = queryset.filter(type=Region.REGION_CITY, name__istartswith=query.strip(' ')).distinct()
    object_list = list(queryset)
    return HttpResponse('\n'.join([obj.name for obj in object_list]))

def autocomplete_object_list(request, model):
    query = request.GET.get('q')
    if not query:
        raise Http404
    object_list = list(model.objects.filter(name__istartswith=query.strip(' ')).distinct())
    return HttpResponse('\n'.join([obj.name for obj in object_list]))

# folder

def show_folder(request, object_id, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)
    template = 'portfolio/folder.html'
    context = adv_context.copy()
    context['folder'] = folder
    return list_detail.object_detail(request, queryset=Portfolio.objects.published().select_related('user'), object_id=object_id, template_name=template, extra_context=context)


# album

def _get_portfolio_or_404(request):
    if request.user.is_anonymous():
        raise Http404
    try:
        return request.user.profile
    except (AttributeError, Portfolio.DoesNotExist):
        raise Http404

def publish_album(request, portfolio_id, object_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    album = get_object_or_404(portfolio.album_set.all(), pk=object_id)
    album.active = True
    album.save()
    return HttpResponseRedirect(album.get_absolute_url())

class ProcessFormsetsView(generic.ProcessFormView):

    def get_formsets(self):
        return {}

    def get(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        formsets = self.get_formsets()
        return self.render_to_response(self.get_context_data(form=form, formsets=formsets, **kwargs))

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        formsets = self.get_formsets()
        if all_valid([form] + formsets.values()):
            return self.form_valid(form, formsets)
        else:
            return self.form_invalid(form, formsets)

class AlbumDetailMixin(object):

    def get_portfolio(self):
        try:
            return self._portfolio
        except AttributeError:
            self._portfolio = get_object_or_404(Portfolio.objects.published(), pk=self.kwargs['portfolio_id'])
            return self._portfolio

    def get_initial(self):
        return {'portfolio': self.get_portfolio()}

    def get_queryset(self):
        portfolio = self.get_portfolio()
        if self.request.GET.get('preview', False):
            queryset = portfolio.album_set.all()
        else:
            queryset = portfolio.album_set.published()
        return queryset

class AlbumModifyMixin(AlbumDetailMixin):
    def get_portfolio(self):
        try:
            return self._portfolio
        except AttributeError:
            self._portfolio = get_object_or_404(Portfolio.objects.published(), user=self.request.user, pk=self.kwargs['portfolio_id'])
            return self._portfolio

class AlbumCreateView(AlbumDetailMixin, ProcessFormsetsView):

    template = 'portfolio/album_form.html'
    form_class = AlbumForm

    def __init__(self, *args, **kwargs):
        super(AlbumCreateView, self).__init__(*args, **kwargs)
        PhotoFormset = modelformset_factory(UserPhoto, fields=('image', 'title'), extra=1, can_delete=True)
        VideoFormset = modelformset_factory(UserVideo, fields=('file', 'title'), extra=1, can_delete=True)
        AudioFormset = modelformset_factory(UserAudio, fields=('file', 'title', 'image'), extra=1, can_delete=True)
        self.gallery_data = {
            'photo': [PhotoFormset, UserPhoto, UserPhotoPriority],
            'video': [VideoFormset, UserVideo, UserVideoPriority],
            'audio': [AudioFormset, UserAudio, UserAudioPriority],
        }

    def get_formsets(self):
        formsets = {}
        if self.request.method == 'POST':
            for gallery_type, (formset_class, obj_class, priority_class) in self.gallery_data.iteritems():
                formsets[gallery_type] = formset_class(self.request.POST, self.request.FILES, prefix=gallery_type)
        else:
            for gallery_type, (formset_class, obj_class, priority_class) in self.gallery_data.iteritems():
                queryset = obj_class.objects.none()
                formsets[gallery_type] = formset_class(queryset=queryset, prefix=gallery_type)
        return formsets

    def form_valid(self, form, formsets):
        obj = form.save(commit=False)
        folder, created = Folder.objects.get_or_create(name=self.request.POST.get('folder'), portfolio=self.get_portfolio())
        obj.folder = folder
        for gallery_type in self.gallery_data.keys():
            gallery = getattr(obj, '%s_gallery' % gallery_type, None)
            if not gallery:
                setattr(obj, '%s_gallery' % gallery_type, UserGallery.objects.create(owner=self.request.user, title=obj.name))
        preview = self.request.POST.get('preview', False)
        if not preview:
            obj.active = True
            obj.folder.active = True
            obj.folder.save()
        obj.save()
        for gallery_type, (formset_class, obj_class, priority_class) in self.gallery_data.iteritems():
            for file_obj in formsets[gallery_type].save(commit=False):
                file_obj.owner = self.request.user
                file_obj.active = True
                file_obj.convert = True
                file_obj.save()
                gallery = getattr(obj, '%s_gallery' % gallery_type)
                kwargs = {'gallery': gallery, gallery_type: file_obj}
                priority_class.objects.get_or_create(**kwargs)
        if preview:
            return HttpResponseRedirect(obj.get_absolute_url() + '?preview=1')
        messages.info(self.request, u'News został zmieniony.')
        return HttpResponseRedirect(obj.get_absolute_url() + '?preview=1')

    def form_invalid(self, form, formsets):
        context = self.kwargs
        context.update(adv_context)
        return self.render_to_response(self.get_context_data(form=form, formsets=formsets, **context))

    def get_context_data(self, **kwargs):
        kwargs.update({
            'object': self.get_portfolio(),
        })
        return super(AlbumCreateView, self).get_context_data(**kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AlbumCreateView, self).dispatch(*args, **kwargs)

class AlbumUpdateView(AlbumModifyMixin, AlbumCreateView):

    template = 'portfolio/album_form.html'
    form_class = AlbumForm
    model = Album

    def get_object(self):
        try:
            return self.object
        except AttributeError:
            self.object = get_object_or_404(self.get_portfolio().album_set.all(), pk=self.kwargs['object_id'])
            return self.object

    def get_formsets(self):
        formsets = {}
        if self.request.method == 'POST':
            for gallery_type, (formset_class, obj_class, priority_class) in self.gallery_data.iteritems():
                formsets[gallery_type] = formset_class(self.request.POST, self.request.FILES, prefix=gallery_type)
        else:
            obj = self.get_object()
            for gallery_type, (formset_class, obj_class, priority_class) in self.gallery_data.iteritems():
                gallery = getattr(obj, '%s_gallery' % gallery_type, None)
                if gallery:
                    queryset = getattr(gallery, '%ss' % gallery_type).published()
                formsets[gallery_type] = formset_class(queryset=queryset, prefix=gallery_type)
        return formsets

    def get_form_kwargs(self):
        kwargs = super(AlbumCreateView, self).get_form_kwargs()
        instance = self.get_object()
        kwargs['instance'] = instance
        kwargs['initial'] = {'folder': instance.folder.name }
        return kwargs

class AlbumDetailView(AlbumDetailMixin, generic.DetailView):

    def get_object(self):
        self.kwargs['pk'] = self.kwargs['object_id']
        return super(AlbumDetailView, self).get_object()

    def get_queryset(self):
        return super(AlbumDetailView, self).get_queryset().select_related('folder', 'folder__portfolio', 'photo_gallery', 'video_gallery', 'audio_gallery').defer('photo_gallery__tags', 'video_gallery__tags')

    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        try:
            page_number = int(page)
        except ValueError:
            page_number = 1
        page = paginator.page(page_number)
        return (paginator, page, page.object_list, page.has_other_pages())

    def get_context_data(self, **kwargs):
        context = kwargs
        paginate_by = 15
        if self.object.album_type == Album.PHOTO_ALBUM:
            object_list = self.object.photo_gallery.photos.published().defer('tags')
            self.template = 'portfolio/album.html'
        elif self.object.album_type == Album.VIDEO_ALBUM:
            object_list = self.object.video_gallery.videos.published().defer('tags')
            self.template = 'portfolio/album_video.html'
        else:
            object_list = self.object.audio_gallery.audios.published()
            self.template = 'portfolio/album_audio.html'
            paginate_by = 5
        full_object_list = object_list
        paginator, page_obj, object_list, is_paginated = self.paginate_queryset(object_list, paginate_by)
        object_list = list(object_list)
        prev_page_image = None
        idx = page_obj.start_index() - 2
        if idx >= 0:
            try:
                prev_page_image = full_object_list[page_obj.start_index() - 2]
            except IndexError:
                prev_page_image = None
            else:
                if prev_page_image != object_list[0]:
                    object_list.insert(0, prev_page_image)
                else:
                    prev_page_image = None
        try:
            next_page_image = full_object_list[page_obj.end_index()]
        except IndexError:
            next_page_image = None
        else:
            if next_page_image != object_list[-1]:
                object_list.append(next_page_image)
            else:
                next_page_image = None
        context.update({
            'object_list': object_list,
            'paginator': paginator,
            'page_obj': page_obj,
            'is_paginated': is_paginated,
            'query_dict': self.request.GET.copy(),
            'page_name': 'page',
            'album': self.object,
            'object': self.get_portfolio(),
            'prev_page_image': prev_page_image,
            'next_page_image': next_page_image,
        })
        return super(AlbumDetailView, self).get_context_data(**context)

class AlbumDeleteView(AlbumModifyMixin, generic.DeleteView):

    template = 'portfolio/album_confirm_delete.html'

    def get_context_data(self, **kwargs):
        return super(AlbumDeleteView, self).get_context_data(next=self.request.GET.get('next', None), **kwargs)

    def get_success_url(self):
        success_url = self.request.POST.get('next', None)
        if success_url:
            return success_url
        return reverse('portfolio_profile', args=(self.kwargs.get('portfolio_id'),))

    def get_object(self):
        self.kwargs['pk'] = self.kwargs['object_id']
        obj = super(AlbumDeleteView, self).get_object()
        self.folder = obj.folder
        return obj

    def post(self, request, *args, **kwargs):
        result = super(AlbumDeleteView, self).post(request, *args, **kwargs)
        if self.folder and self.folder.album_set.published().count() == 0:
            self.folder.active = False
            self.folder.save()
        return result

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AlbumDeleteView, self).dispatch(*args, **kwargs)

# news
class NewsListMixin(object):

    def get_portfolio(self):
        try:
            return self._portfolio
        except AttributeError:
            self._portfolio = get_object_or_404(Portfolio.objects.published(), pk=self.kwargs['portfolio_id'])
            return self._portfolio

    def get_queryset(self):
        portoflio = self.get_portfolio()
        return portoflio.news_set.published().order_by('-pub_date')

class NewsCreateView(NewsListMixin, generic.MultipleObjectMixin, generic.ProcessFormView):

    paginate_by = 5
    template = 'portfolio/news.html'
    form_class = NewsForm

    def get_initial(self):
        return {'portfolio': self.get_portfolio()}

    def get_context_data(self, **kwargs):
        context = super(NewsCreateView, self).get_context_data(**kwargs)
        form = kwargs.pop('form')
        context['form'] = form
        context['object'] = self.get_portfolio()
        context['query_dict'] = self.request.GET.copy()
        context.update(adv_context)
        return context

    def get(self, request, *args, **kwargs):
        object_list = self.get_queryset()
        return super(NewsCreateView, self).get(request, *args, object_list=object_list, **kwargs)

    def post(self, request, *args, **kwargs):
        portfolio = self.get_portfolio()
        if request.user != portfolio.user:
            raise Http404
        return super(NewsCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        portfolio = self.get_portfolio()
        news = form.save(commit=False)
        news.portfolio = portfolio
        preview = self.request.POST.get('preview', False)
        news.active = not preview
        news.save()
        if news.active:
            return HttpResponseRedirect(reverse('portfolio_news', args=(portfolio.id,)))
        return HttpResponseRedirect(reverse('portfolio_edit_news', args=(portfolio.id, news.id)))

    def form_invalid(self, form):
        object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form, object_list=object_list, **self.kwargs))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NewsCreateView, self).dispatch(*args, **kwargs)

class NewsUpdateView(NewsCreateView):

    def get_queryset(self):
        portoflio = self.get_portfolio()
        return portoflio.news_set.order_by('-pub_date')

    def get_object(self):
        object_id = self.kwargs.get('object_id')
        portfolio = self.get_portfolio()
        return get_object_or_404(portfolio.news_set.all(), pk=object_id)

    def get_form_kwargs(self):
        kwargs = super(NewsUpdateView, self).get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

class NewsDeleteView(generic.DeleteView):

    template = 'portfolio/news_confirm_delete.html'

    def get_context_data(self, **kwargs):
        return super(NewsDeleteView, self).get_context_data(next=self.request.GET.get('next', None), **kwargs)

    def get_success_url(self):
        success_url = self.request.POST.get('next', None)
        if success_url:
            return success_url
        return reverse('portfolio_news', args=(self.kwargs.get('portfolio_id'),))

    def get_object(self):
        portfolio = _get_portfolio_or_404(self.request)
        object_id = self.kwargs.get('object_id')
        return get_object_or_404(portfolio.news_set.all(), pk=object_id)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NewsDeleteView, self).dispatch(*args, **kwargs)

# pdf
import os.path
def _fetch_resources(uri, rel):
    return os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))

def _generate_pdf(template, context):
    translation.activate(settings.LANGUAGE_CODE)
    context['MEDIA_ROOT'] = settings.MEDIA_ROOT
    context['MEDIA_URL'] = settings.MEDIA_URL
    context['is_pdf'] = True
    html = render_to_string(template, context)
    buf = StringIO()
    pdf = pisa.pisaDocument(StringIO(html.encode('utf-8')), buf, link_callback=_fetch_resources, path=settings.MEDIA_ROOT)
    return buf, pdf

# biogram
@login_required
def edit_cv(request):
    ''' Formularz tworzenia/edycji portfolio. '''
#    if request.user.is_anonymous():
#        return HttpResponseRedirect('/')
    CategoryFormset = modelformset_factory(PortfolioCategory, exclude=('portfolio',), extra=0, can_delete=True, formset=BaseCategoryFormSet)
    EducationFormset = inlineformset_factory(Portfolio, TimedItem, form=EducationTimedItemForm, exclude=('portfolio', 'item_type'), extra=0)
    TrainingFormset = inlineformset_factory(Portfolio, TimedItem, form=TimedItemForm, exclude=('portfolio', 'item_type'), extra=0)
    ExperienceFormset = inlineformset_factory(Portfolio, TimedItem, form=TimedItemForm, exclude=('portfolio', 'item_type'), extra=0)
    AchivementFormset = inlineformset_factory(Portfolio, ListItem, exclude=('portfolio', 'item_type'), extra=0)
    QualificationFormset = inlineformset_factory(Portfolio, ListItem, exclude=('portfolio', 'item_type'), extra=0)
    HobbyFormset = inlineformset_factory(Portfolio, ListItem, exclude=('portfolio', 'item_type'), extra=0)
    timeditem_data = [('education', EducationFormset),
                ('training', TrainingFormset),
                ('experience', ExperienceFormset)]
    listitem_data = [('achivement', AchivementFormset),
                ('qualification', QualificationFormset),
                ('hobby', HobbyFormset)]
    item_type_map = {
        'education': TimedItem.ITEM_EDUCATION,
        'training': TimedItem.ITEM_TRAINING,
        'experience': TimedItem.ITEM_EXPERIENCE,
        'achivement': ListItem.ITEM_ACHIVEMENT,
        'qualification': ListItem.ITEM_QUALIFICATION,
        'hobby': ListItem.ITEM_HOBBY,
    }

    portfolio = None
    if request.method == 'POST':
        try:
            portfolio = request.user.profile
        except (AttributeError, Portfolio.DoesNotExist):
            portfolio = None
        if not portfolio:
            portfolio_form = CVForm(request.POST, request.FILES)
            formsets = {
                'category': CategoryFormset(request.POST, request.FILES, prefix='category'),
            }
            for prefix, formset_class in timeditem_data:
                formsets[prefix] = formset_class(request.POST, request.FILES, prefix=prefix)
            for prefix, formset_class in listitem_data:
                formsets[prefix] = formset_class(request.POST, request.FILES, prefix=prefix)
        else:
            portfolio_form = CVForm(request.POST, request.FILES, instance=portfolio)
            formsets = {
                'category': CategoryFormset(request.POST, request.FILES, prefix='category'),
            }
            for prefix, formset_class in timeditem_data:
                formsets[prefix] = formset_class(request.POST, request.FILES, instance=portfolio, prefix=prefix)
            for prefix, formset_class in listitem_data:
                formsets[prefix] = formset_class(request.POST, request.FILES, instance=portfolio, prefix=prefix)
        if all_valid([portfolio_form] + formsets.values()):
            try:
                portfolio = portfolio_form.save(False)
                if portfolio:
                    region = WORLD
                    country = portfolio_form.cleaned_data['country']
                    if country:
                        try:
                            region = region.get_descendants().get(type=Region.REGION_COUNTRY, name=country)
                        except Region.DoesNotExist:
                            region = region.add_child(type=Region.REGION_COUNTRY, name=country)
                    voyvodship = portfolio_form.cleaned_data['voyvodship']
                    if voyvodship:
                        try:
                            region = region.get_children().get(type=Region.REGION_VOYVODSHIP, name=voyvodship)
                        except Region.DoesNotExist:
                            region = region.add_child(type=Region.REGION_VOYVODSHIP, name=voyvodship)
                    city = portfolio_form.cleaned_data['city']
                    if city:
                        try:
                            region = region.get_children().get(type=Region.REGION_CITY, name=city)
                        except Region.DoesNotExist:
                            region = region.add_child(type=Region.REGION_CITY, name=city)
                    school = portfolio_form.cleaned_data['school']
                    if school:
                        portfolio.school, created = School.objects.get_or_create(name=school)
                    portfolio.region = region
                    portfolio.user = request.user
                    portfolio.save()
                    for key, formset in formsets.iteritems():
                        instances = formset.save(commit=False)
                        for formset_obj in instances:
                            if key != 'category':
                                formset_obj.item_type = item_type_map.get(key)
                            formset_obj.portfolio = portfolio
                            formset_obj.save()
            except Exception, e:
                messages.error(request, u'Przepraszamy. Wystąpił problem przy zapisie danych. Spróbuj ponownie lub skontaktuj się z <a href="mailto:%s">administratorem</a> serwisu.' % settings.ADMINS[0][1])
                mail_admins('Error - rejestracja', traceback.format_exc(e), fail_silently=True)
            else:
                messages.info(request, 'Dane zostały zmienione.')
                return HttpResponseRedirect(reverse('portfolio_admin'))
    else:
        try:
            portfolio = request.user.profile
        except (AttributeError, Portfolio.DoesNotExist):
            portfolio = None
        if portfolio:
            initial = {}
            if portfolio.region:
                ancestors = dict([(ancestor.type, ancestor.name) for ancestor in portfolio.region.get_ancestors()])
                ancestors[portfolio.region.type] = portfolio.region
                initial['country'] = ancestors.get(Region.REGION_COUNTRY, '')
                initial['voyvodship'] = ancestors.get(Region.REGION_VOYVODSHIP, '')
                initial['city'] = ancestors.get(Region.REGION_CITY, '')
            portfolio_form = CVForm(instance=portfolio, initial=initial)
            formsets = {
                'category': CategoryFormset(prefix='category', queryset=portfolio.portfoliocategory_set.all()),
            }
            for prefix, formset_class in timeditem_data:
                formsets[prefix] = formset_class(prefix=prefix, instance=portfolio, queryset=portfolio.timeditem_set.filter(item_type=item_type_map.get(prefix)))
            for prefix, formset_class in listitem_data:
                formsets[prefix] = formset_class(prefix=prefix, instance=portfolio, queryset=portfolio.listitem_set.filter(item_type=item_type_map.get(prefix)))
        else:
            portfolio_form = CVForm()
            formsets = {
                'category': CategoryFormset(prefix='category', queryset=PortfolioCategory.objects.none()),
            }
            for prefix, formset_class in timeditem_data:
                formsets[prefix] = formset_class(prefix=prefix, queryset=TimedItem.objects.none())
            for prefix, formset_class in listitem_data:
                formsets[prefix] = formset_class(prefix=prefix, queryset=ListItem.objects.none())
    context = {
        'portfolio_form': portfolio_form,
        'formsets': formsets,
        'object': portfolio,
    }
    context.update(adv_context)
    template = 'portfolio/cv_form.html'
    return render_to_response(template, context, context_instance=RequestContext(request))

def get_cv(request, object_id):
    portfolio = get_object_or_404(Portfolio.objects.published(), pk=object_id)
    context = {'object': portfolio}
    template = 'portfolio/cv_pdf.html'
    buf, pdf = _generate_pdf(template, context)
    if not pdf.err:
        return HttpResponse(buf.getvalue(), mimetype='application/pdf')
    raise Http404

def get_portfolio(request, object_id):
    portfolio = get_object_or_404(Portfolio.objects.published(), pk=object_id)
    context = {'object': portfolio}
    template = 'portfolio/portfolio_pdf.html'
    buf, pdf = _generate_pdf(template, context)
    if not pdf.err:
        return HttpResponse(buf.getvalue(), mimetype='application/pdf')
    raise Http404

# kontakt
@login_required
def edit_contact(request):
    ''' Formularz edycji kontaktu. '''
#    if request.user.is_anonymous():
#        return HttpResponseRedirect('/')
    try:
        portfolio = request.user.profile
    except (AttributeError, Portfolio.DoesNotExist):
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        portfolio_form = EditContactForm(request.POST, request.FILES, instance=portfolio)
        if portfolio_form.is_valid():
            try:
                portfolio = portfolio_form.save()
            except Exception, e:
                messages.error(request, u'Przepraszamy. Wystąpił problem przy zapisie danych. Spróbuj ponownie lub skontaktuj się z <a href="mailto:%s">administratorem</a> serwisu.' % settings.ADMINS[0][1])
                mail_admins('Error - rejestracja', traceback.format_exc(e), fail_silently=True)
            else:
                messages.info(request, 'Dane zostały zmienione.')
                return HttpResponseRedirect(reverse('portfolio_admin'))
    else:
        portfolio_form = EditContactForm(instance=portfolio)
    context = {
        'portfolio_form': portfolio_form,
        'object': portfolio,
    }
    context.update(adv_context)
    template = 'portfolio/contact_form.html'
    return render_to_response(template, context, context_instance=RequestContext(request))

# znajomi

@login_required
def add_friend(request, object_id):
    ''' Wysyla prosbe o akceptacje znajomosci. '''
    try:
        friend = Portfolio.objects.get(pk=object_id)
    except User.DoesNotExist:
        messages.error(request, u'Użytkownik nie istnieje.')
    else:
        try:
            owner = request.user.profile
        except (AttributeError, Portfolio.DoesNotExist):
            messages.warning(request, u'Musisz mieć portfolio, aby dodać użytkownika do znajomych.')
            return HttpResponseRedirect(reverse('portfolio_edit_cv'))

        relation_hash = md5('%s' % (friend.id + owner.id + random.random())).hexdigest()
        relationship, created = Relationship.objects.get_or_create(friend=friend, owner=owner, defaults={'relation_hash': relation_hash})
        if created:
            confirmation_link = reverse('portfolio_confirm_friend', args=(relation_hash,))
            context = {
                'host': settings.SITE_HOST,
                'confirmation_link': confirmation_link,
                'friend': friend,
                'owner': owner,
            }
            context.update(adv_context)
            message_text = render_to_string('portfolio/mail/friend_confirmation.txt', context, context_instance=RequestContext(request))
            message_html = render_to_string('portfolio/mail/friend_confirmation.html', context, context_instance=RequestContext(request))
            msg = EmailMultiAlternatives(FRIEND_CONFIRMATION_SUBJECT, message_text, settings.DEFAULT_FROM_EMAIL, [friend.user.email])
            msg.attach_alternative(message_html, "text/html")
            msg.send(fail_silently=True)
            messages.info(request, u'Wysłano prośbę o potwierdzenie znajomości.')
        else:
            messages.warning(request, u'Prośba o potwierdzenie znajomości została już wysłana wcześniej.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('portfolio_index')))

@login_required
def remove_friend(request, object_id):
    ''' Usuwa uzytkownika ze znajomych. '''
    Relationship.objects.filter(friend__id=object_id, owner=request.user.profile).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('portfolio_index')))

def confirm_friend(request, relation_hash):
    ''' Potwierdza znajomosc. '''
    try:
        relationship = Relationship.objects.get(relation_hash=relation_hash)
    except Relationship.DoesNotExist:
        messages.warning(request, u'Potwierdzenie nie zostało uznane.')
    else:
        relationship.confirmed = True
        relationship.save()
        messages.warning(request, u'Potwierdzono znajomość.')
        return HttpResponseRedirect(relationship.friend.get_absolute_url())
    return HttpResponseRedirect(reverse('portfolio_index'))

def send_message(request):
    ''' Wysyla wiadomosc do wlasciciela portfolio. '''
    if request.method == 'POST':
        portfolio_id = request.POST.get('portfolio')
        try:
            portfolio = Portfolio.objects.select_related('user').get(pk=portfolio_id)
        except Portfolio.DoesNotExist:
            messages.error(request, u'Portfolio nie istnieje.')
        else:
            form = ContactForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data['subject']
                body = form.cleaned_data['body']
                msg = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, [portfolio.user.email])
                msg.send(fail_silently=True)
                messages.info(request, u'Wysłano wiadomość.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('portfolio_index')))

# ulubione

@login_required
def add_favorite(request, object_id):
    portfolio = get_object_or_404(Portfolio, pk=object_id)
    Favorite.objects.create(user=request.user, portfolio=portfolio)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('portfolio_index')))

@login_required
def remove_favorite(request, object_id):
    portfolio = get_object_or_404(Portfolio, pk=object_id)
    Favorite.objects.filter(user=request.user, portfolio=portfolio).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('portfolio_index')))

# ocena portfolio

def rate(request, object_id):
    portfolio = get_object_or_404(Portfolio, pk=object_id)
    vote_id = 'archiramaportfoliovote' + str(portfolio.id)
    response = HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('portfolio_index')))
    rating = request.POST.get('rating', None)
    if request.method == 'POST' and rating is not None and vote_id not in request.COOKIES:
        new_rating = float(rating)
        portfolio.rating_total = (portfolio.rating_total * portfolio.votes_total + new_rating) / (portfolio.votes_total + 1)
        portfolio.votes_total += 1
        portfolio.rating_curr_month = (portfolio.rating_curr_month * portfolio.votes_curr_month + new_rating) / (portfolio.votes_curr_month + 1)
        portfolio.votes_curr_month += 1
        portfolio.save()
        max_age = 30 * 24 * 60 * 60 # miesiac
        expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
        response.set_cookie(vote_id, rating, max_age, expires)
    return response

# rejestracja i edycja

class BaseCategoryFormSet(BaseModelFormSet):
    def clean(self):
        super(BaseModelFormSet, self).clean()
        if not (self.total_form_count() >= 1 and self.forms[0].is_valid() and self.forms[0].cleaned_data):
            raise forms.ValidationError(u'Musisz wybrać przynajmniej jedną kategorię')

# admin
@login_required
def admin(request):
    try:
        portfolio = request.user.profile
    except (AttributeError, Portfolio.DoesNotExist):
        if 'forum' in request.META.get('HTTP_REFERER', '/'):
            return HttpResponseRedirect(reverse('portfolio_admin'))
        return HttpResponseRedirect(reverse('portfolio_edit_cv'))
    portfolio_queryset = Portfolio.objects.published().select_related('user', 'country', 'voyvodship', 'city')
    context = {
        'adv_cat': 'archikracja',
        'adv_scat': 'portfolia_podstrony',
    }
    return list_detail.object_detail(request, object_id=portfolio.id, queryset=portfolio_queryset, template_name='portfolio/profile.html', extra_context=context)

def ajax_is_logged(request):
    context = {
    }
    object_id = request.GET.get('object_id')
    if object_id:
        try:
            context['object'] = Portfolio.objects.published().get(pk=object_id)
        except:
            pass
    try:
        portfolio = request.user.profile
    except (AttributeError, Portfolio.DoesNotExist):
        portfolio = None
    context['has_portfolio'] = bool(portfolio)
    template = 'portfolio/_messages.html'
    return render_to_response(template, context, context_instance=RequestContext(request))

def login(request, *args, **kwargs):
    if request.method == 'POST':
        if not request.POST.get('remember_me', None):
            request.session.set_expiry(0)
    return auth_views.login(request, *args, **kwargs)

def folders_order(request):
    if request.user.is_anonymous():
        return HttpResponse('')
    FolderFormset = inlineformset_factory(Portfolio, Folder, fields=('name',), extra=0, can_order=True, can_delete=False)
    try:
        portfolio = request.user.profile
    except:
        return HttpResponse('')

    if request.method == 'POST':
        formset = FolderFormset(request.POST, instance=portfolio)
        if formset.is_valid():
            for form in formset.ordered_forms:
                order = form.cleaned_data['ORDER']
                folder = form.save(commit=False)
                folder.sort_order = order
                folder.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('portfolio_index')))
    else:
        formset = FolderFormset(instance=portfolio, queryset=portfolio.folder_set.order_by('sort_order'))
        context = {
            'formset': formset,
        }
        template = 'portfolio/folders_order.html'
        return render_to_response(template, context, context_instance=RequestContext(request))

def admin_menu(request):
    user = request.user
    portfolio = None
    if user.is_authenticated():
        portfolio = user.profile
    return render_to_response('portfolio/admin_menu.html', {'portfolio': portfolio}, RequestContext(request))
