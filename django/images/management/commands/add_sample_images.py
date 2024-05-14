from django.core.management.base import BaseCommand
from images.models import Image, Rectangle, ImageTag
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Adds n random images to database'

    def add_arguments(self, parser):
        parser.add_argument('n', type=int, help='Number of images to add')

    def generate_random_image(self, name):
        colors = ['red', 'blue', 'green']

        img_height = random.randint(1, 5) * 100
        img_width = random.randint(1, 5) * 100
        pub_date = timezone.now()

        image = Image.objects.create(
            image_title=name, 
            pub_date=pub_date, 
            width=img_width,
            height = img_height,
        )

        rect_cnt = random.randint(1, 5)
        for r in range(rect_cnt):
            x_pos = random.randint(0, img_width - 1)
            y_pos = random.randint(0, img_height - 1)
            width = random.randint(1, img_width - x_pos)
            height = random.randint(1, img_height - y_pos)
            fill_color = random.choice(colors)
            time_added = timezone.now()

            Rectangle.objects.create(
                image=image, 
                x_pos=x_pos, 
                y_pos=y_pos, 
                width=width, 
                height=height, 
                fill_color=fill_color, 
                time_added=time_added,
            )


    def handle(self, *args, **kwargs):
        n = kwargs['n']
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        for i in range(n):
            name = f'random{i}_{timestamp}'
            self.generate_random_image(name)
        self.stdout.write(self.style.SUCCESS(f'Successfully added {n} images'))