# Generated migration for index additions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_chat_field_updates'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='chat',
            index=models.Index(fields=['user', 'is_active'], name='idx_chats_user_active'),
        ),
        migrations.AddIndex(
            model_name='chat',
            index=models.Index(fields=['type', 'platform_chat_id'], name='idx_chats_type_platform'),
        ),
        migrations.AddIndex(
            model_name='userstate',
            index=models.Index(fields=['external_user_id', 'trusted'], name='idx_user_states_extuser_trusted'),
        ),
        migrations.AlterField(
            model_name='chat',
            name='platform_chat_id',
            field=models.BigIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='external_user_id',
            field=models.BigIntegerField(db_index=True),
        ),
    ]
