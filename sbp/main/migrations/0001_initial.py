# Generated by Django 4.1.4 on 2022-12-30 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Records',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_spb', models.CharField(max_length=128)),
                ('shopid', models.IntegerField()),
                ('op_merch', models.CharField(max_length=128)),
                ('op_date', models.DateTimeField()),
                ('day_shift', models.DateField()),
                ('op_sum', models.DecimalField(decimal_places=2, max_digits=15)),
                ('op_com', models.DecimalField(decimal_places=2, max_digits=15)),
            ],
            options={
                'db_table': 'sbp_operations',
                'ordering': ['day_shift'],
                'managed': False,
            },
        ),
    ]
