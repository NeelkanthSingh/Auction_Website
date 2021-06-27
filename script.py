from datetime import datetime, time
import os
import django
from datetime import datetime, timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_web_app.settings") # Replace with your app name.
django.setup()


from django.db import connection
from django.core.management import call_command
from django.core.mail import send_mail
from django.conf import settings
from blog.models import Post
from blog.models import ArchivePost

joe = Post.objects.all()
for i in joe:
    x =datetime.now(timezone.utc) - i.date_posted
    # print(x.days)
    if (x.days >= 1):
        new = ArchivePost(id=i.id,title=i.title,file=i.file,content=i.content,date_posted=i.date_posted,price=i.price,increment=i.increment,author=i.author,bidder=i.bidder)
        new.save()
        i.delete()

        subject='This is your reciving, Take it!'
        message=f'Thank you bitch, this is his email - {i.author.email}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [i.bidder]
        send_mail(subject,message,email_from,recipient_list)

        subject='This is your reciving, Take it!'
        message=f'Thank you bitch, this is his email - {i.bidder}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [i.author.email]
        send_mail(subject,message,email_from,recipient_list)
