# Generated by Django 5.0.14 on 2025-06-25 17:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0008_transports_transporteur'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoriqueImport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier', models.CharField(max_length=255)),
                ('date_import', models.DateTimeField(auto_now_add=True)),
                ('feuilles_importees', models.TextField()),
                ('dimensions', models.TextField()),
                ('utilisateur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Historique d'import",
                'verbose_name_plural': "Historiques d'import",
            },
        ),
    ]
