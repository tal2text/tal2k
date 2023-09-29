# Generated by Django 4.2.5 on 2023-09-18 12:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='audiofile',
            old_name='user',
            new_name='assigned_to',
        ),
        migrations.AddField(
            model_name='audiofile',
            name='audio_duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='audiofile',
            name='category',
            field=models.CharField(blank=True, choices=[('Indian', 'Indian'), ('Philippino', 'Philippino')], max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='audiofile',
            name='to_be_reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviewer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='audiofile',
            name='uploaded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transcription',
            name='old_text',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='transcription',
            name='review_status',
            field=models.CharField(blank=True, choices=[('GOOD', 'GOOD'), ('BAD', 'BAD'), ('unreviewed', 'unreviewed')], default='', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='transcription',
            name='reviewed',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='audiofile',
            name='audio_file',
            field=models.FileField(max_length=1024, upload_to=''),
        ),
        migrations.AlterField(
            model_name='audiofile',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
