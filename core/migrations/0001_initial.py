# Generated by Django 2.1.1 on 2019-07-15 23:39

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PostingCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Course')),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TutorContacts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TutorPosting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('post_text', models.CharField(max_length=300)),
                ('degree', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Degree')),
            ],
        ),
        migrations.CreateModel(
            name='TutorReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_text', models.CharField(blank=True, max_length=400)),
                ('rating', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('user_type', models.CharField(choices=[('student', 'student'), ('tutor', 'tutor')], max_length=10)),
                ('phone_number', models.CharField(max_length=10)),
                ('firebase_id', models.CharField(default='', max_length=128, unique=True)),
                ('lat', models.FloatField(blank=True, null=True)),
                ('lon', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.School')),
            ],
        ),
        migrations.AddField(
            model_name='tutorreview',
            name='tutor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tutorreview_review_for', to='core.UserInformation'),
        ),
        migrations.AddField(
            model_name='tutorreview',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tutorreview_review_created', to='core.UserInformation'),
        ),
        migrations.AddField(
            model_name='tutorposting',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.UserInformation'),
        ),
        migrations.AddField(
            model_name='tutorcontacts',
            name='tutor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tutorcontacts_contactee', to='core.UserInformation'),
        ),
        migrations.AddField(
            model_name='tutorcontacts',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tutorcontacts_contacted', to='core.UserInformation'),
        ),
        migrations.AddField(
            model_name='postingcourse',
            name='tutor_posting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.TutorPosting'),
        ),
        migrations.AddField(
            model_name='degree',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.School'),
        ),
        migrations.AddField(
            model_name='course',
            name='degree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Degree'),
        ),
    ]
