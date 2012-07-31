# flake8: noqa
# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Charge.description'
        db.add_column('law_charge', 'description', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Charge.description'
        db.delete_column('law_charge', 'description')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'law.area': {
            'Meta': {'object_name': 'Area'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'snapshot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Snapshot']"})
        },
        'law.charge': {
            'Meta': {'ordering': "('numeric_penal_code', 'penal_code', 'label')", 'object_name': 'Charge'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'numeric_penal_code': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'penal_code': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'snapshot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Snapshot']"})
        },
        'law.chargearea': {
            'Meta': {'object_name': 'ChargeArea'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Area']"}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Charge']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'law.chargechildren': {
            'Meta': {'object_name': 'ChargeChildren'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child'", 'to': "orm['law.Charge']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent'", 'to': "orm['law.Charge']"})
        },
        'law.chargeclassification': {
            'Meta': {'object_name': 'ChargeClassification'},
            'certainty': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Charge']"}),
            'classification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Classification']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'law.classification': {
            'Meta': {'object_name': 'Classification'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'snapshot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Snapshot']"})
        },
        'law.classificationchild': {
            'Meta': {'object_name': 'ClassificationChild'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child'", 'to': "orm['law.Classification']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinality': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent'", 'to': "orm['law.Classification']"})
        },
        'law.classificationconsequence': {
            'Meta': {'object_name': 'ClassificationConsequence'},
            'certainty': ('django.db.models.fields.CharField', [], {'default': "'yes'", 'max_length': '16'}),
            'classification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Classification']"}),
            'consequence': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Consequence']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinality': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'law.consequence': {
            'Meta': {'object_name': 'Consequence'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Area']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'law.event': {
            'Meta': {'object_name': 'Event'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'snapshot': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['law.Snapshot']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'law.snapshot': {
            'Meta': {'object_name': 'Snapshot'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'in progress'", 'max_length': '256'})
        }
    }

    complete_apps = ['law']
