# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
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
                ('name', models.SlugField(help_text='unique identifier that appears in the URL. must be less than 50 characters long and no two areas can have the same name')),
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
                ('name', models.SlugField(help_text='unique identifier that appears in the URL. must be less than 50 characters long and no two charges can have the same name')),
                ('numeric_penal_code', models.FloatField(null=True, editable=False, blank=True)),
                ('description', models.TextField(default='', help_text='tips/strategies. if this is empty, it will inherit from its parent Charge', null=True, blank=True)),
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
                ('area', models.ForeignKey(to='law.Area', on_delete=django.db.models.deletion.CASCADE)),
                ('charge', models.ForeignKey(to='law.Charge', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChargeChildren',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('child', models.ForeignKey(related_name='child', to='law.Charge', on_delete=django.db.models.deletion.CASCADE)),
                ('parent', models.ForeignKey(related_name='parent', to='law.Charge', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChargeClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('certainty', models.CharField(max_length=16, choices=[('yes', 'Yes'), ('probably', 'Probably'), ('maybe', 'Maybe')])),
                ('charge', models.ForeignKey(to='law.Charge', on_delete=django.db.models.deletion.CASCADE)),
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
                ('child', models.ForeignKey(related_name='child', to='law.Classification', on_delete=django.db.models.deletion.CASCADE)),
                ('parent', models.ForeignKey(related_name='parent', to='law.Classification', on_delete=django.db.models.deletion.CASCADE)),
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
                ('certainty', models.CharField(default='yes', max_length=16, choices=[('yes', 'Yes'), ('probably', 'Probably'), ('maybe', 'Maybe')])),
                ('classification', models.ForeignKey(to='law.Classification', on_delete=django.db.models.deletion.CASCADE)),
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
                ('area', models.ForeignKey(editable=False, to='law.Area', on_delete=django.db.models.deletion.CASCADE)),
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
                ('note', models.TextField(default='', blank=True)),
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
                ('description', models.TextField(default='', blank=True)),
                ('status', models.CharField(default='in progress', max_length=256, choices=[('in progress', 'In Progress'), ('qa', 'In QA'), ('vetted', 'Vetted')])),
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
            field=models.ForeignKey(to='law.Snapshot', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='classificationconsequence',
            name='consequence',
            field=models.ForeignKey(to='law.Consequence', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='classification',
            name='snapshot',
            field=models.ForeignKey(editable=False, to='law.Snapshot', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chargeclassification',
            name='classification',
            field=models.ForeignKey(to='law.Classification', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charge',
            name='snapshot',
            field=models.ForeignKey(editable=False, to='law.Snapshot', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='area',
            name='snapshot',
            field=models.ForeignKey(editable=False, to='law.Snapshot', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
