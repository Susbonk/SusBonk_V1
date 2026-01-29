from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_server_side_defaults'),
    ]

    operations = [
        # Add allowed_mentions field to Chat
        migrations.AddField(
            model_name='chat',
            name='allowed_mentions',
            field=models.JSONField(blank=True, null=True),
        ),
        
        # Rename cleanup fields for consistency
        migrations.RenameField(
            model_name='chat',
            old_name='cleanup_mentions',
            new_name='clean_up_mentions',
        ),
        migrations.RenameField(
            model_name='chat',
            old_name='cleanup_emojis',
            new_name='clean_up_emojis',
        ),
        migrations.RenameField(
            model_name='chat',
            old_name='cleanup_links',
            new_name='clean_up_links',
        ),
        
        # Remove deprecated threshold fields from Chat
        migrations.RemoveField(
            model_name='chat',
            name='custom_prompt_threshold',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='prompts_threshold',
        ),
        
        # Add enable_ai_moderation field
        migrations.AddField(
            model_name='chat',
            name='enable_ai_moderation',
            field=models.BooleanField(default=True),
        ),
    ]
