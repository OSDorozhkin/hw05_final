# Generated by Django 2.2.6 on 2021-01-15 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created']},
        ),
    ]
