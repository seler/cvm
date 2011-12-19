import os
import re

from django import template
from django.conf import settings
from django.core.files.storage import get_storage_class

import Image, ImageDraw, ImageFont
from StringIO import StringIO
from django.core.files.base import ContentFile

register = template.Library()

def generate_image_path(mode, width, height, path):
    return os.path.join('images', str(mode), str(width), str(height), os.path.basename(path))

def generate_error_image(width, height, text=None):
    return 'no-image'

def resize_image(image, mode, width, height):
    original_width, original_height = image.size

    ratio = 1.0
    ratio_w = float(width) / original_width
    ratio_h = float(height) / original_height
    ratio_max = max(ratio_w, ratio_h)

    if mode == 1:
        # crop

        crop_width = width / ratio_max
        crop_height = height / ratio_max

        width_offset = (original_width - crop_width) / 2.
        height_offset = (original_height - crop_height) / 2.

        image = image.crop(map(int, (width_offset, height_offset, crop_width + width_offset, crop_height + height_offset)))

    if mode == 2:
        # reduce

        if ratio_max < 1.0:
            ratio = ratio_max
        else:
            ratio = min(ratio, ratio_w, ratio_h)

        ratio = min(ratio, ratio_w, ratio_h)

        width = original_width * ratio
        height = original_height * ratio

    # crop, reduce, stretch
    return image.resize(map(int, (width, height)), Image.ANTIALIAS).copy()

def generate_new_image(original_image_path, image_path, mode, width, height):
    storage = get_storage_class(settings.DEFAULT_FILE_STORAGE)()

    image_file = storage.open(original_image_path)
    image = Image.open(image_file)

    new_image = resize_image(image, mode, width, height)

    # saving image
    fp = StringIO()
    fp.name = image_path
    new_image.save(fp, image.format)
    fp.seek(0)
    cf = ContentFile(fp.read())

    image_path = storage.save(image_path, cf)

    return image_path

def process_image(original_image, width, height, mode):
    if original_image:
        original_image_path = original_image.name
    else:
        original_image_path = 'noimage.jpg'

    image_path = os.path.join(settings.MEDIA_ROOT, generate_image_path(mode, width, height, original_image_path))

    storage = get_storage_class(settings.DEFAULT_FILE_STORAGE)()

    if not storage.exists(image_path):
        if not storage.exists(original_image_path):
            image_path = generate_error_image(width, height, getattr(settings, 'IMAGE_ERROR_TEXT'), None)
        else:
            image_path = generate_new_image(original_image_path, image_path , mode, width, height)

    return settings.MEDIA_URL + generate_image_path(mode, width, height, image_path)

class ImageNode(template.Node):
    def __init__(self, original_image, width=None, height=None, mode=None, context_name=None):
        self.original_image = template.Variable(original_image)
        self.width = width
        self.height = height
        self.mode = mode
        self.context_name = context_name

    def render(self, context):

        result = process_image(self.original_image.resolve(context), self.width, self.height, self.mode)

        if self.context_name:
            context[self.context_name] = result
            return ''
        else:
            return result

@register.tag
def image(parser, token):
    """Template tags that allows you to.

    Syntax::

        {% image <image> [<width>x<height> <mode>] [as <context_name>] %}
        
    :image: instance of ImageField
    :width and height: divided by non-digit character integers are dimensions of resulting image
    :mode: string representing mode
    :context_name: context name that image url will be returned to

    Available modes:

        - reduce

            Reduces original image to given size while maintaining aspect ratio. Given ``width`` and ``height`` are treated as maximal values.

        - crop

            Crops original image to given size.

        - stretch

            Stretches original image to given size discarding aspect ratio.

    Example usage:
    
        ``{% image object.image %}``
        
            Returns url to original sized image.
        
        ``{% image object.image as image_url %}``
        
            Puts url to original sized image into contex as ``image_url``.
            
        ``{% image object.image 100x100 reduce %}``
        
            Return url to reduced image.
            
        ``{% image object.image 100x100 crop as cropped_image_url %}``
        
            Puts url to cropped image into context as ``cropped_image_url``.
        
        ``{% image object.image 100x100 stretch %}``"""

    bits = token.split_contents()

    image = bits[1]

    modes = {'reduce':2, 'crop':1, 'stretch':3}

    if len(bits) == 2:
        return ImageNode(image)
    if len(bits) == 4 and bits[3] == 'as':
        return ImageNode(image, context_name=bits[4])
    if re.match('^\d+[^\d]+\d+$', bits[2]) and len(bits) in (4, 6) and bits[3] in modes:
        width, height = map(int, re.split('[^\d]+', bits[2]))
        if bits[-2] == 'as':
            context_name = bits[-2]
        else:
            context_name = None
        return ImageNode(image, width=width, height=height, mode=modes[bits[3]], context_name=context_name)
    raise template.TemplateSyntaxError('image tag expects a syntax of {% image <image> [<width>x<height> <mode>] [as <context_name>] %}')
