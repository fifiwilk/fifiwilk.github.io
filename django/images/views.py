from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.core.paginator import Paginator
from .models import *

def generate_miniature(image: Image):
    rectangles = Rectangle.objects.filter(image=image).order_by('time_added')

    svg_data = f'<a href="view/{image.id}" style="display: inline-block; border: 1px solid black;">\n'
    svg_data += f'<svg width="100" height="100" \
        viewBox="0 0 {image.width} {image.height}" version="1.1" xmlns="http://www.w3.org/2000/svg">\n'
        # xmlns:xlink="http://www.w3.org/1999/xlink">\n \
        # <a xlink:href="view/{image.id}">\n'

    for r in rectangles:
        svg_data += f'<rect x="{r.x_pos}" y="{r.y_pos}" width="{r.width}" \
            height="{r.height}" fill="{r.fill_color}"></rect>\n'

    svg_data += '</svg></a>\n'
    return svg_data


def index(request):
    images = Image.objects.order_by('-pub_date')

    chosen_tag = request.GET.get('tag')
    if chosen_tag:
        images = images.filter(tags__tag=chosen_tag)
    else:
        chosen_tag = 'All'

    sort_by = request.GET.get('sort_by', 'pub_dec')
    if sort_by == 'pub_asc':
        images = images.order_by('pub_date')
    if sort_by == 'pub_dec':
        images = images.order_by('-pub_date')

    template = loader.get_template('images/index.html')

    items = [(img, generate_miniature(img)) for img in images]

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page', 1)
    page_images = paginator.get_page(page_number)

    tags = ImageTag.objects.all().order_by('tag')

    context = {
        'images': page_images,
        'tags': tags,
        'chosen_tag': chosen_tag,
        'sort_by': sort_by,
    }

    return HttpResponse(template.render(context, request))


def view_image(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    rectangles = Rectangle.objects.filter(image=image).order_by('time_added')

    context = {'image': image, 'rectangles': rectangles}

    template = loader.get_template('images/view_image.html')
    if request.user.is_superuser or request.user in image.editors.all():
        template = loader.get_template('images/edit_image.html')
    return HttpResponse(template.render(context, request))


def add_rectangle(request):
    assert ('image_id' in request.POST)

    image_id = request.POST.get('image_id')
    image = get_object_or_404(Image, pk=image_id)

    required_fileds = ['x', 'y', 'width', 'height', 'color']
    assert all(field in request.POST for field in required_fileds)
    if not all(field in request.POST for field in required_fileds):
        return redirect(f'/images/edit/{image_id}')

    image_id = request.POST.get('image_id')
    image = get_object_or_404(Image, pk=image_id)

    def verify_rectangle_data(x, y, width, height, color, time_added):
        try:
            x = int(x)
            y = int(y)
            width = int(width)
            height = int(height)
        except ValueError:
            return False, "x, y, width, and height must be numbers"
    
        if x < 0 or x + width > image.width:
            return False, "Rectangle must fit in the image"

        if y < 0 or y + height > image.height:
            return False, "Rectangle must fit in the image"
    
        if not isinstance(color, str):
            return False, "color must be a string"
    
        if not isinstance(time_added, timezone.datetime):
            return False, "time_added must be a proper date"
    
        return True, None


    x = request.POST.get('x')
    y = request.POST.get('y')
    width = request.POST.get('width')
    height = request.POST.get('height')
    color = request.POST.get('color')
    time_added = timezone.now()

    is_valid, error_msg = verify_rectangle_data(x, y, width, height, color, time_added)
    if not is_valid:
        print('error: ', error_msg)
        return redirect(f'/images/edit/{image_id}')

    Rectangle.objects.create(
        image=image,
        x_pos=x,
        y_pos=y,
        width=width,
        height=height,
        fill_color=color,
        time_added=time_added,
    )

    return redirect(f'/images/edit/{image_id}')


def delete_rectangle(request, image_id, rectangle_id):
    rectangle = get_object_or_404(Rectangle, pk=rectangle_id)
    rectangle.delete()
    return redirect(f'/images/edit/{image_id}')


def editors_panel(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    rectangles = Rectangle.objects.filter(image=image).order_by('time_added')

    template = loader.get_template('images/edit_image.html')
    context = {'image': image, 'rectangles': rectangles}

    return HttpResponse(template.render(context, request))

