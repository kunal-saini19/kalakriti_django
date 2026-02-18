from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kalakriti', '0002_seller_product_seller_userprofile_productactivity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='terms_accepted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='terms_version',
            field=models.CharField(default='v1', max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='seller_verified',
            field=models.BooleanField(default=False),
        ),
    ]
