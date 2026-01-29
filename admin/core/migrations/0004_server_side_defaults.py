from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_runtimestatistics_chat_messages_deleted'),
    ]

    operations = [
        # Set server-side defaults for timestamp fields
        migrations.RunSQL(
            sql="""
                ALTER TABLE users 
                    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
                    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;
                
                ALTER TABLE chats 
                    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
                    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;
                
                ALTER TABLE prompts 
                    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
                    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;
                
                ALTER TABLE custom_prompts 
                    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
                    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;
                
                ALTER TABLE user_states 
                    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
                    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;
                
                ALTER TABLE chat_prompts 
                    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
                    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;
                
                ALTER TABLE chat_custom_prompts 
                    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
                    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;
                
                ALTER TABLE runtime_statistics 
                    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
                    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;
            """,
            reverse_sql="""
                ALTER TABLE users 
                    ALTER COLUMN created_at DROP DEFAULT,
                    ALTER COLUMN updated_at DROP DEFAULT;
                
                ALTER TABLE chats 
                    ALTER COLUMN created_at DROP DEFAULT,
                    ALTER COLUMN updated_at DROP DEFAULT;
                
                ALTER TABLE prompts 
                    ALTER COLUMN created_at DROP DEFAULT,
                    ALTER COLUMN updated_at DROP DEFAULT;
                
                ALTER TABLE custom_prompts 
                    ALTER COLUMN created_at DROP DEFAULT,
                    ALTER COLUMN updated_at DROP DEFAULT;
                
                ALTER TABLE user_states 
                    ALTER COLUMN created_at DROP DEFAULT,
                    ALTER COLUMN updated_at DROP DEFAULT;
                
                ALTER TABLE chat_prompts 
                    ALTER COLUMN created_at DROP DEFAULT,
                    ALTER COLUMN updated_at DROP DEFAULT;
                
                ALTER TABLE chat_custom_prompts 
                    ALTER COLUMN created_at DROP DEFAULT,
                    ALTER COLUMN updated_at DROP DEFAULT;
                
                ALTER TABLE runtime_statistics 
                    ALTER COLUMN created_at DROP DEFAULT,
                    ALTER COLUMN updated_at DROP DEFAULT;
            """
        ),
    ]
