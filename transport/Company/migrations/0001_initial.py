# Generated by Django 4.0 on 2023-08-20 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Compagnie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_E', models.CharField(max_length=50)),
                ('siren', models.BigIntegerField()),
            ],
            options={
                'verbose_name': 'Compagnie',
                'verbose_name_plural': 'Compagnies',
            },
        ),
        migrations.CreateModel(
            name='Transporteurs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50)),
                ('date_de_naissance', models.DateField()),
                ('adresse', models.TextField()),
                ('ville', models.CharField(max_length=30)),
                ('permis', models.CharField(default='', max_length=5)),
                ('phone', models.CharField(max_length=60)),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
                'verbose_name': 'Transporteur',
                'verbose_name_plural': 'Transporteurs',
                'ordering': ['nom', 'prenom'],
            },
        ),
        migrations.CreateModel(
            name='Voyageurs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_V', models.CharField(max_length=50)),
                ('prenom_V', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
                'verbose_name': 'Voyageur',
                'verbose_name_plural': 'Voyageurs',
            },
        ),
        migrations.CreateModel(
            name='Voyages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_depart', models.DateTimeField()),
                ('date_arrivee', models.DateTimeField()),
                ('ville_depart', models.CharField(max_length=50)),
                ('ville_arrivee', models.CharField(max_length=50)),
                ('prix_unitaire', models.FloatField()),
                ('transporteurs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Company.transporteurs')),
            ],
            options={
                'verbose_name': 'Voyage',
                'verbose_name_plural': 'Voyages',
            },
        ),
        migrations.CreateModel(
            name='Transports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marque', models.CharField(max_length=50)),
                ('matricule', models.CharField(default='', max_length=50)),
                ('nombre_de_place', models.IntegerField()),
                ('compagnie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Company.compagnie')),
                ('voyages', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Company.voyages')),
            ],
            options={
                'verbose_name': 'Transport',
                'verbose_name_plural': 'Transports',
            },
        ),
        migrations.AddField(
            model_name='compagnie',
            name='transporteurs',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Company.transporteurs'),
        ),
        migrations.CreateModel(
            name='Asso_trans_voyageur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transporteurs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Company.transporteurs')),
                ('voyageurs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Company.voyageurs')),
            ],
        ),
    ]
