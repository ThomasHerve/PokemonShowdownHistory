# Generated by Django 3.2.4 on 2021-06-27 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Month',
            fields=[
                ('url', models.CharField(max_length=1000, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1000)),
                ('order', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PokemonMaster',
            fields=[
                ('name', models.CharField(max_length=1000, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Tier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=1000)),
                ('name', models.CharField(max_length=1000)),
                ('is_last', models.BooleanField(default=False)),
                ('category', models.CharField(default=None, max_length=15, null=True)),
                ('elo', models.IntegerField(default=None, null=True)),
                ('month', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.month')),
            ],
            options={
                'unique_together': {('url', 'month')},
            },
        ),
        migrations.CreateModel(
            name='TierPokemonMonth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.month')),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.pokemonmaster')),
                ('tier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.tier')),
            ],
        ),
        migrations.CreateModel(
            name='Pokemon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField()),
                ('usage', models.FloatField()),
                ('name', models.CharField(max_length=1000)),
                ('master', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='stats.pokemonmaster')),
                ('tier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stats.tier')),
            ],
            options={
                'unique_together': {('name', 'tier')},
            },
        ),
    ]
