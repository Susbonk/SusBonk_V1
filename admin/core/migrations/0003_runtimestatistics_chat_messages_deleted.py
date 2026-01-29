from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_default_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='runtimestatistics',
            name='chat_messages_deleted',
            field=models.IntegerField(default=0),
        ),
    ]
