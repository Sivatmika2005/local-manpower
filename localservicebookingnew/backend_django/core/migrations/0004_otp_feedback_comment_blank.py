from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_booking_time'),
    ]

    operations = [
        # Allow blank comments on Feedback
        migrations.AlterField(
            model_name='feedback',
            name='comment',
            field=models.TextField(blank=True, default=''),
        ),
        # OTP model for phone login and email password reset
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255)),
                ('otp_code', models.CharField(max_length=6)),
                ('purpose', models.CharField(
                    choices=[('phone_login', 'Phone Login'), ('email_reset', 'Email Reset')],
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_used', models.BooleanField(default=False)),
            ],
        ),
    ]
