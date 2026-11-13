import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('symptoms', '0005_add_ten_more_disease_entries'),
        ('accounts', '0004_alter_user_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyWellnessCheckin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('sleep_hours', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(24)])),
                ('hydration_liters', models.DecimalField(decimal_places=1, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('exercise_minutes', models.PositiveIntegerField(default=0)),
                ('mood', models.CharField(choices=[('Very low', 'Very low'), ('Low', 'Low'), ('Okay', 'Okay'), ('Good', 'Good'), ('Excellent', 'Excellent')], default='Okay', max_length=20)),
                ('energy_level', models.PositiveSmallIntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wellness_checkins', to='accounts.user')),
            ],
            options={
                'ordering': ['-date'],
                'constraints': [models.UniqueConstraint(fields=('user', 'date'), name='unique_user_daily_wellness_checkin')],
            },
        ),
    ]
