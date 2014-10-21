# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=256)),
                ('name', models.SlugField(help_text=b'unique identifier that appears in the URL. must be less than 50 characters long and no two areas can have the same name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=256)),
                ('penal_code', models.CharField(max_length=256)),
                ('name', models.SlugField(help_text=b'unique identifier that appears in the URL. must be less than 50 characters long and no two charges can have the same name')),
                ('numeric_penal_code', models.FloatField(null=True, editable=False, blank=True)),
                ('description', models.TextField(default=b'', help_text=b'tips/strategies. if this is empty, it will inherit from its parent Charge', null=True, blank=True)),
            ],
            options={
                'ordering': ('numeric_penal_code', 'penal_code', 'label'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChargeArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('area', models.ForeignKey(to='law.Area')),
                ('charge', models.ForeignKey(to='law.Charge')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChargeChildren',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('child', models.ForeignKey(related_name=b'child', to='law.Charge')),
                ('parent', models.ForeignKey(related_name=b'parent', to='law.Charge')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChargeClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('certainty', models.CharField(max_length=16, choices=[(b'yes', b'Yes'), (b'probably', b'Probably'), (b'maybe', b'Maybe')])),
                ('charge', models.ForeignKey(to='law.Charge')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=256)),
                ('name', models.SlugField()),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClassificationChild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordinality', models.IntegerField(default=1)),
                ('child', models.ForeignKey(related_name=b'child', to='law.Classification')),
                ('parent', models.ForeignKey(related_name=b'parent', to='law.Classification')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClassificationConsequence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordinality', models.IntegerField(default=1)),
                ('certainty', models.CharField(default=b'yes', max_length=16, choices=[(b'yes', b'Yes'), (b'probably', b'Probably'), (b'maybe', b'Maybe')])),
                ('classification', models.ForeignKey(to='law.Classification')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Consequence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True)),
                ('name', models.SlugField()),
                ('area', models.ForeignKey(editable=False, to='law.Area')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('note', models.TextField(default=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Snapshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=256)),
                ('description', models.TextField(default=b'', blank=True)),
                ('status', models.CharField(default=b'in progress', max_length=256, choices=[(b'in progress', b'In Progress'), (b'qa', b'In QA'), (b'vetted', b'Vetted')])),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='snapshot',
            field=models.ForeignKey(to='law.Snapshot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='classificationconsequence',
            name='consequence',
            field=models.ForeignKey(to='law.Consequence'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='classification',
            name='snapshot',
            field=models.ForeignKey(editable=False, to='law.Snapshot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chargeclassification',
            name='classification',
            field=models.ForeignKey(to='law.Classification'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charge',
            name='snapshot',
            field=models.ForeignKey(editable=False, to='law.Snapshot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='area',
            name='snapshot',
            field=models.ForeignKey(editable=False, to='law.Snapshot'),
            preserve_default=True,
        ),
    ]
