# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Snapshot'
        db.create_table('law_snapshot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='in progress', max_length=256)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('law', ['Snapshot'])

        # Adding model 'Event'
        db.create_table('law_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snapshot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Snapshot'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('law', ['Event'])

        # Adding model 'Charge'
        db.create_table('law_charge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('penal_code', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('snapshot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Snapshot'])),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('numeric_penal_code', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('law', ['Charge'])

        # Adding model 'ChargeChildren'
        db.create_table('law_chargechildren', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parent', to=orm['law.Charge'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='child', to=orm['law.Charge'])),
        ))
        db.send_create_signal('law', ['ChargeChildren'])

        # Adding model 'Classification'
        db.create_table('law_classification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snapshot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Snapshot'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('law', ['Classification'])

        # Adding model 'Area'
        db.create_table('law_area', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snapshot', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Snapshot'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('law', ['Area'])

        # Adding model 'Consequence'
        db.create_table('law_consequence', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Area'])),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('law', ['Consequence'])

        # Adding model 'ChargeClassification'
        db.create_table('law_chargeclassification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Charge'])),
            ('classification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Classification'])),
            ('certainty', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('law', ['ChargeClassification'])

        # Adding model 'ClassificationChild'
        db.create_table('law_classificationchild', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parent', to=orm['law.Classification'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='child', to=orm['law.Classification'])),
            ('ordinality', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('law', ['ClassificationChild'])

        # Adding model 'ClassificationConsequence'
        db.create_table('law_classificationconsequence', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('classification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Classification'])),
            ('consequence', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Consequence'])),
            ('ordinality', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('certainty', self.gf('django.db.models.fields.CharField')(default='yes', max_length=16)),
        ))
        db.send_create_signal('law', ['ClassificationConsequence'])

        # Adding model 'ChargeArea'
        db.create_table('law_chargearea', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Charge'])),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['law.Area'])),
        ))
        db.send_create_signal('law', ['ChargeArea'])


    def backwards(self, orm):
        
        # Deleting model 'Snapshot'
        db.delete_table('law_snapshot')

        # Deleting model 'Event'
        db.delete_table('law_event')

        # Deleting model 'Charge'
        db.delete_table('law_charge')

        # Deleting model 'ChargeChildren'
        db.delete_table('law_chargechildren')

        # Deleting model 'Classification'
        db.delete_table('law_classification')

        # Deleting model 'Area'
        db.delete_table('law_area')

        # Deleting model 'Consequence'
        db.delete_table('law_consequence')

        # Deleting model 'ChargeClassification'
        db.delete_table('law_chargeclassification')

        # Deleting model 'ClassificationChild'
        db.delete_table('law_classificationchild')

        # Deleting model 'ClassificationConsequence'
        db.delete_table('law_classificationconsequence')

        # Deleting model 'ChargeArea'
        db.delete_table('law_chargearea')


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
