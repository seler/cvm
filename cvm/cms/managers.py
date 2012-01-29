from datetime import datetime
from django.db import models

class PageManager(models.Manager):

    def published(self):
        'Returns Page that are published and a publish date is in the past.'
        return self.get_query_set().filter(publish_date__lte=datetime.now(),
                                    published=True).order_by('-publish_date')
