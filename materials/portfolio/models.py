# -*- coding: utf-8 -*-

from hashlib import md5
import time

from django.db import models
#from django.db.models import signals
from django.contrib.auth.models import User
from django.contrib.comments.signals import comment_was_posted
from treebeard.mp_tree import MP_Node

from murator.gallery.fields import CropImageField
from user_media.models import UserGallery
from vbulletin.models import VBulletinUserField

from portfolio.manager import PortfolioManager, AlbumManager, FolderManager, NewsManager

# Create your models here.

class Region(MP_Node):
    REGION_CONTINENT = 1
    REGION_COUNTRY = 2
    REGION_VOYVODSHIP = 3
    REGION_CITY = 4
    REGION_TYPE = (
        (0, u'Świat'),
        (REGION_CONTINENT, u'Kontynent'),
        (REGION_COUNTRY, u'Kraj'),
        (REGION_VOYVODSHIP, u'Województwo'),
        (REGION_CITY, u'Miasto'),
    )
    name = models.CharField('Nazwa', max_length=100, help_text=u"""<p>
        - podaj swoją lokalizację (miejsce zamieszkania lub prowadzonej 
        działalności), by łatwiej mogli Cię znaleźć inni użytkownicy serwisu 
        Portfolia lub pracodawca.
    </p>""")
    type = models.PositiveSmallIntegerField('Rodzaj', choices=REGION_TYPE)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regiony'
        ordering = ['path']

class School(models.Model):
    name = models.CharField(verbose_name=u'Nazwa', max_length=64)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Szkoła'
        verbose_name_plural = u'Szkoły'

class Portfolio(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    avatar = CropImageField(verbose_name=u'Zdjęcie profilowe',
                            upload_to='portfolio_avatars',
                            help_text=u"""<p>
            - to Twoje zdjęcie, które będzie umieszczone w bloku informacji o 
            Twoim portfolio. To pierwsza rzecz, jaką zobaczą inni użytkownicy, 
            zaraz obok okładki Twojego portfolio.
        </p>
        <p>
            <i>Serwis archirama.pl zabrania zamieszczać zdjęcia osób trzecich 
            (podszywać się pod inne osoby), bądź zamieszczać zdjęcia o 
            charakterze pornograficznym lub rasistowskim.</i>
        </p>""",)
    photo = CropImageField(verbose_name=u'Zdjęcie profilowe w biogramie', upload_to='portfolio_users',
                            help_text=u"""<p>
            - to Twoje zdjęcie, które będzie umieszczone w zakładce biogram, 
            gdzie piszesz o sobie oraz gdzie możesz zamieścić swoje CV. To 
            zdjęcie zobaczą tylko osoby, które będą wejdą na stronę Twojego 
            portfolio. W zależności od tego w jaki sposób chcesz wykorzystać 
            swoje portfolio – czy w celu znalezienia pracodawcy, czy by poznać 
            ciekawych ludzi – tak też może różnić się charakter Twojego zdjęcia
            w biogramie. 
        </p>
        <p>
            <i>Serwis archirama.pl zabrania zamieszczać zdjęcia osób trzecich 
            (podszywać się pod inne osoby), bądź zamieszczać zdjęcia o 
            charakterze pornograficznym lub rasistowskim.</i>
        </p>""",)
    lead_photo = CropImageField(verbose_name=u'Zdjęcie na okładkę portfolia', upload_to='portfolio_lead',
                            help_text=u"""<p>
            - to zdjęcie, które będzie stanowić okładkę Twojego portfolio. 
            Okładka portfolia to Twoja wizytówka, którą zobaczą wszyscy. W 
            zależności od charakteru Twojego portfolio – może to być Twoja 
            najlepsza praca, którą chcesz się pochwalić albo zdjęcie 
            charakteryzujące Twoją pasję/pracę.
        </p>
        <p>
            <i>Serwis archirama.pl zabrania zamieszczać zdjęcia osób trzecich 
            (podszywać się pod inne osoby), bądź zamieszczać zdjęcia o 
            charakterze pornograficznym lub rasistowskim. Zabrania też 
            wykorzystywać zdjęcia, projekty, pliki graficzne, muzyczne bądź 
            filmowe, do których praw nie ma użytkownik danego portfolio.</i>
        </p>""",)
    region = models.ForeignKey(Region, verbose_name=u'Region', null=True, blank=True)
    who_am_i = models.TextField(verbose_name=u'Kim jestem', blank=True,
                            help_text=u"""<p>
            - napisz kilka słów o sobie. To początek Twojego biogramu, pierwsze
            słowa, jakie przeczytają inni. Możesz tutaj ogólnie przedstawić się
            i napisać w kilku słowach, czym się zajmujesz i interesujesz.
        </p>
        <p>
            <i>Wszelkie dane w biogramie możesz w każdej chwili ponownie 
            aktualizować naciskając przycisk „edytuj biogram” na dole biogramu 
            lub w pasku administracji menu głównego.</i>
        </p>""",)
    school = models.ForeignKey(School, verbose_name=u'Szkoła', null=True, blank=True,
                            help_text=u"""<p>
            - podaj nazwę swojej szkoły (której jesteś uczniem, studentem, lub
            absolwentem), by łatwiej mogli Cię znaleźć inni użytkownicy serwisu
            Portfolia lub pracodawca.
        </p>""",)
    who_am_i = models.TextField(verbose_name=u'Kim jestem', blank=True,
                            help_text=u"""<p>
            - napisz kilka słów o sobie. To początek Twojego biogramu, pierwsze
            słowa, jakie przeczytają inni. Możesz tutaj ogólnie przedstawić się
            i napisać w kilku słowach, czym się zajmujesz i interesujesz.
        </p>
        <p>
            <i>Wszelkie dane w biogramie możesz w każdej chwili ponownie 
            aktualizować naciskając przycisk „edytuj biogram” na dole biogramu 
            lub w pasku administracji menu głównego.</i>
        </p>""",)
    what_am_i_doing = models.TextField(verbose_name=u'Co robię', blank=True,
                            help_text=u"""<p>
            - możesz tutaj bardziej szczegółowo napisać, czym się zajmujesz i 
            interesujesz. Opisz co potrafisz, co umiesz.
        </p>
        <p>
            <i>Wszelkie dane w biogramie możesz w każdej chwili ponownie 
            aktualizować naciskając przycisk „edytuj biogram” na dole biogramu 
            lub w pasku administracji menu głównego.</i>
        </p>""",)
    clients = models.TextField(verbose_name=u'Dotychczasowi klienci', blank=True,
                            help_text=u"""<p>
            - możesz tutaj wymienić ludzi i firmy, z którymi współpracowałeś. 
            To ważne, jeżeli chcesz by Twoje portfolio była atrakcyjne dla 
            potencjalnych pracodawców.
        </p>
        <p>
            <i>Wszelkie dane w biogramie możesz w każdej chwili ponownie 
            aktualizować naciskając przycisk „edytuj biogram” na dole biogramu 
            lub w pasku administracji menu głównego.</i>
        </p>""",)
    address = models.TextField(verbose_name=u'Adres', blank=True)
    phone = models.CharField(verbose_name=u'Telefon', max_length=16, blank=True)
    fax = models.CharField(verbose_name=u'Faks', max_length=16, blank=True)
    facebook = models.CharField(verbose_name=u'Facebook', max_length=255, blank=True)
    www = models.CharField(verbose_name=u'Strona www', max_length=255, blank=True)
    pub_date = models.DateTimeField(verbose_name=u'Data', auto_now=True)

    MAX_POINTS = 5
    votes_total = models.PositiveIntegerField(verbose_name=u'Wszystkich głosów', default=0, blank=True)
    rating_total = models.FloatField(verbose_name=u'Rating', default=0.0, blank=True)
    votes_curr_month = models.PositiveIntegerField(verbose_name=u'Głosy w bieżącym miesiącu', default=0, blank=True)
    rating_curr_month = models.FloatField(verbose_name=u'Rating w bieżącym miesiącu', default=0.0, blank=True)
    rating_last_month = models.FloatField(verbose_name=u'Rating w ostatnim miesiącu', default=0.0, blank=True)
    comments_num = models.PositiveIntegerField(verbose_name=u'Liczba komentarzy', default=0, blank=True)
    hash = models.CharField(u'Klucz rejestracji', max_length=32, blank=True, null=True)

    objects = PortfolioManager()

    def get_full_name(self):
        try:
            user_field = VBulletinUserField.objects.get(user=self.user.userprofile.vbuser)
        except Exception:
            return self.user.get_full_name()
        else:
            return '%s %s' % (user_field.first_name, user_field.surname)

    def get_email(self):
        try:
            vbuser = self.user.userprofile.vbuser
        except Exception:
            return self.user.email
        else:
            return vbuser.email

    def __unicode__(self):
        if self.user:
            return u'Portfolio %s' % self.user.username
        return u'Portfolio'

    @models.permalink
    def get_absolute_url(self):
        return ('portfolio_profile', (self.id,))

    def save(self, force_insert=False, force_update=False, **kwargs):
        if not self.hash:
            self.hash = md5(self.user.username.encode('latin2') + str(time.time())).hexdigest()
        super(Portfolio, self).save(force_insert, force_update, **kwargs)

    class Meta:
        verbose_name = u'Portfolio'
        verbose_name_plural = u'Portfolia'

    def get_work_num(self):
        return self.album_set.published().count()

    def get_total_rating(self):
        return int(round(self.rating_total))

    def get_rating(self):
        value = self.get_total_rating()
        return [True] * value + [False] * (self.MAX_POINTS - value)

    def get_timed_items(self):
        try:
            return self._timed_items
        except AttributeError:
            self._timed_items = self.timeditem_set.order_by('active', '-end', '-start')
            return self._timed_items

    def get_education(self):
        return [item for item in self.get_timed_items() if item.item_type == TimedItem.ITEM_EDUCATION]

    def get_training(self):
        return [item for item in self.get_timed_items() if item.item_type == TimedItem.ITEM_TRAINING]

    def get_experience(self):
        return [item for item in self.get_timed_items() if item.item_type == TimedItem.ITEM_EXPERIENCE]

    def get_list_items(self):
        try:
            return self._list_items
        except AttributeError:
            self._list_items = self.listitem_set.all()
            return self._list_items

    def get_qualifications(self):
        return [item for item in self.get_list_items() if item.item_type == ListItem.ITEM_QUALIFICATION]

    def get_achivements(self):
        return [item for item in self.get_list_items() if item.item_type == ListItem.ITEM_ACHIVEMENT]

    def get_hobby(self):
        return [item for item in self.get_list_items() if item.item_type == ListItem.ITEM_HOBBY]

    def get_categories(self):
        try:
            return self._categories
        except AttributeError:
            self._categories = self.portfoliocategory_set.all()
            return self._categories

    def get_profesional_categories(self):
        return [category for category in self.get_categories() if category.work_type == PortfolioCategory.WORK_PROFESIONAL]

    def get_hobby_categories(self):
        return [category for category in self.get_categories() if category.work_type == PortfolioCategory.WORK_HOBBY]

def create_portfolio(sender, instance, created, **kwargs):
    if created:
        Portfolio.objects.create(user=instance)

#signals.post_save.connect(create_portfolio, sender=User)

class Relationship(models.Model):
    confirmed = models.BooleanField(default=False)
    relation_hash = models.CharField(max_length=32, db_index=True)
    owner = models.ForeignKey(Portfolio, related_name='friends')
    friend = models.ForeignKey(Portfolio, related_name='rev_friends')
    pub_date = models.DateField(verbose_name=u'Data', auto_now=True)

    class Meta:
        unique_together = ('owner', 'friend')

class TimedItem(models.Model):
    ITEM_EDUCATION = 1
    ITEM_TRAINING = 2
    ITEM_EXPERIENCE = 3
    ITEM_TYPE = [(ITEM_EDUCATION, 'wykształcenie'), (ITEM_TRAINING, 'szkolenia'), (ITEM_EXPERIENCE, 'doświadczenie zawodowe')]
    portfolio = models.ForeignKey(Portfolio)
    item_type = models.PositiveSmallIntegerField(choices=ITEM_TYPE)
    active = models.BooleanField(verbose_name=u'Aktualnie')
    start = models.DateField(verbose_name=u'Początek')
    end = models.DateField(verbose_name=u'Koniec', null=True, blank=True)
    name = models.TextField(verbose_name=u'Miejsce')

    def __unicode__(self):
        to_date = 'aktualnie' if self.active else self.end
        return '%s: %s -> %s - %s' % (self.get_item_type_display(), self.start, to_date, self.name[:20])

    def get_subitems(self):
        return self.timeditemsubitem_set.order_by('-sort_order')

class TimedItemSubitem(models.Model):
    item = models.ForeignKey(TimedItem)
    name = models.CharField(verbose_name=u'Funkcja', max_length=255)
    body = models.TextField(verbose_name=u'Podpunkty')
    sort_order = models.PositiveSmallIntegerField()

    def get_points(self):
        try:
            return self._points
        except AttributeError:
            self._points = self.body.split('\n')
            return self._points

class ListItem(models.Model):
    ITEM_ACHIVEMENT = 1
    ITEM_QUALIFICATION = 2
    ITEM_HOBBY = 3
    ITEM_TYPE = [(ITEM_ACHIVEMENT, 'osiągnięcia'), (ITEM_QUALIFICATION, 'kwalifikacje'), (ITEM_HOBBY, 'zainteresowania')]
    portfolio = models.ForeignKey(Portfolio)
    item_type = models.PositiveSmallIntegerField(choices=ITEM_TYPE)
    name = models.CharField(verbose_name=u'Nazwa', max_length=16)
    description = models.TextField(verbose_name=u'Opis')

    def __unicode__(self):
        return '%s: %s' % (self.get_item_type_display(), self.name)

class PortfolioCategory(models.Model):
    WORK_PROFESIONAL = 1
    WORK_HOBBY = 2
    WORK_TYPE = [(WORK_PROFESIONAL, 'profesja'), (WORK_HOBBY, 'pasja')]
    WORK_TYPE_DICT = dict(WORK_TYPE)
    CATEGORY = list(enumerate([u'architektura', u'architektura wnętrz', u'wizualizacje', u'design', u'grafika', u'sztuki piękne', u'fotografia', u'moda', u'film', u'muzyka', u'słowo', u'architektura krajobrazu']))
    CATEGORY_DICT = dict(CATEGORY)
    portfolio = models.ForeignKey(Portfolio)
    category = models.PositiveSmallIntegerField(verbose_name=u'Kategoria', choices=CATEGORY, help_text=u"""<p>
        - portfolia w serwisie Archirama.pl są kategoryzowane w zależności od 
        dyscypliny, którą zajmują się jego użytkownicy. Do wyboru jest 12 
        kategorii:
    </p><ul>
        <li>architektura (projektowanie budynków, urbanistyka itp.)</li>
        <li>architektura wnętrz (projektowanie wnętrz mieszkalny i usługowych itp.)</li>
        <li>architektura krajobrazu (projektowanie krajobrazu, projektowanie ogrodów itp.)</li>
        <li>wizualizacje (wizualizacje architektoniczne, wizualizacje produktu itp.)</li>
        <li>design (projektowanie przedmiotów, produktu, wzornictwo przemysłowe itp.)</li>
        <li>grafika (typografia, projektowanie graficzne, web design itp.)</li>
        <li>sztuki piękne (malarstwo, rzeźba, grafika tradycyjna, teatr, performance itp.)</li>
        <li>fotografia (studio fotograficzne, fotografia cyfrowa itp.)</li>
        <li>moda (modeling, stylizacje, projektowanie ubioru itp.)</li>
        <li>film (kręcenie filmów, montaż, produkcja filmowa itp.)</li>
        <li>muzyka (gra na instrumentach, kompozycja, śpiew, zespoły muzyczne, produkcja muzyczna itp.)</li>
        <li>słowo (dziennikarstwo, literatura, poezja, copywriting, działalność wydawnicza itp.)</li> 
    </ul>""")
    work_type = models.PositiveSmallIntegerField(verbose_name=u'Typ', choices=WORK_TYPE, help_text=u"""<p>
        - portfolia w serwisie Archirama.pl są dzielona na dwa podstawowe typy: 
        PROFESJA lub PASJA. W zależności czym się zajmujesz, może to być Twój 
        zawód albo hobby. Np. możesz zajmować się zawodowo architekturą (Typ: 
        PROFESJA, Kategoria: architektura), ale interesujesz się amatorsko 
        fotografią (Typ: PASJA, Kategoria: fotografia). Podział na typy – 
        PROFESJA i PASJA – ma ułatwić użytkownikom serwisu Portfolia spotykanie
        ludzi z tą samą PASJĄ, lub PROFESJĄ, jest też wyjściem naprzeciw 
        oczekiwaniom pracodawców, którzy mogą wykorzystywać serwis Portfolia do
        wyszukiwania potencjalnych pracowników.
    </p>""")

    def __unicode__(self):
        return '%s %s' % (self.get_work_type_display(), self.get_category_display())

    class Meta:
        verbose_name = u'Kategoria portfolio'
        verbose_name_plural = u'Kategorie portfolio'

class Folder(models.Model):
    portfolio = models.ForeignKey(Portfolio)
    name = models.CharField(verbose_name=u'Nazwa', max_length=64)
    active = models.BooleanField(default=False, verbose_name=u'Aktywny')
    sort_order = models.PositiveSmallIntegerField(default=1, verbose_name=u'Kolejność')

    objects = FolderManager()

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('portfolio_show_folder', (self.portfolio_id, self.id))

    class Meta:
        verbose_name = u'Folder'
        verbose_name_plural = u'Foldery'
        ordering = ('sort_order',)

class Album(models.Model):
    PHOTO_ALBUM = 1
    VIDEO_ALBUM = 2
    AUDIO_ALBUM = 3
    ALBUM_TYPE = [(PHOTO_ALBUM, u'Zdjęcia'), (VIDEO_ALBUM, u'Wideo'), (AUDIO_ALBUM, u'Audio')]
    folder = models.ForeignKey(Folder)
    portfolio = models.ForeignKey(Portfolio)
    name = models.CharField(verbose_name=u'Nazwa albumu', max_length=64)
    photo_gallery = models.OneToOneField(UserGallery, null=True, blank=True, related_name='photo_gallery')
    video_gallery = models.OneToOneField(UserGallery, null=True, blank=True, related_name='video_gallery')
    audio_gallery = models.OneToOneField(UserGallery, null=True, blank=True, related_name='audio_gallery')
    lead_photo = CropImageField(verbose_name=u'Zdjęcie na okładkę', upload_to='portfolio_album')
    description = models.TextField(verbose_name=u'Opis', blank=True)
    pub_date = models.DateTimeField(verbose_name=u'Data', auto_now=True)
    user_selected = models.BooleanField(verbose_name=u'Wyświetl na stronie głównej', default=False)
    album_type = models.PositiveIntegerField(verbose_name=u'Typ albumu', choices=ALBUM_TYPE, default=PHOTO_ALBUM)
    comment_count = models.PositiveIntegerField(verbose_name=u'Liczba komentarzy', default=0, blank=True)
    active = models.BooleanField(default=False, verbose_name="Aktywny")

    objects = AlbumManager()

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('portfolio_album', (self.portfolio_id, self.id,), {})

    class Meta:
        verbose_name = u'Album'
        verbose_name_plural = u'Albumy'

    def get_photos(self):
        return []

class Favorite(models.Model):
    user = models.ForeignKey(User)
    portfolio = models.ForeignKey(Portfolio)
    pub_date = models.DateField(verbose_name=u'Data', auto_now=True)

class News(models.Model):
    portfolio = models.ForeignKey(Portfolio)
    title = models.CharField(verbose_name=u'Tytuł', max_length=255)
    description = models.TextField(verbose_name=u'Opis')
    photo = CropImageField(verbose_name=u'Zdjęcie', upload_to='portfolio_news', null=True, blank=True)
    photo_author = models.CharField(verbose_name=u'Autor zdjęcia', max_length=255, null=True, blank=True)
    photo_description = models.TextField(verbose_name=u'Opis zdjęcia', null=True, blank=True)
    pub_date = models.DateTimeField(verbose_name=u'Data', auto_now=True, blank=True)
    active = models.BooleanField(default=False, verbose_name="Aktywny")

    objects = NewsManager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('portfolio_show_news', (self.portfolio_id, self.id))

    class Meta:
        verbose_name = u'Wpis'
        verbose_name_plural = u'Wpisy'

def on_comment_was_posted(sender, comment, request, **kwargs):
    obj = comment.content_object
    if isinstance(obj, Album):
        obj.portfolio.comments_num += 1
        obj.portfolio.save()
comment_was_posted.connect(on_comment_was_posted)

