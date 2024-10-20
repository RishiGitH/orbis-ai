# Generated by Django 5.1.2 on 2024-10-18 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dispute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('resolved', 'Resolved')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trainer_reward', models.DecimalField(decimal_places=6, max_digits=18)),
                ('reviewer_reward', models.DecimalField(decimal_places=6, max_digits=18)),
                ('is_released', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_data', models.JSONField(default=dict)),
                ('result_data', models.JSONField(default=dict)),
                ('review_data', models.JSONField(default=dict)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('reviewed', 'Reviewed'), ('disputed', 'Disputed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('on_chain_signature', models.CharField(blank=True, max_length=132, null=True)),
            ],
        ),
    ]
