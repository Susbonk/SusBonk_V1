from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        # Enable UUID extension
        migrations.RunSQL(
            sql='CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
            reverse_sql='DROP EXTENSION IF EXISTS "uuid-ossp";'
        ),
        
        # Create users table
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('updated_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('username', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('password_hash', models.CharField(blank=True, max_length=255, null=True)),
                ('telegram_user_id', models.BigIntegerField(blank=True, null=True, unique=True)),
                ('discord_user_id', models.BigIntegerField(blank=True, null=True, unique=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        
        # Create chats table
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('updated_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('type', models.CharField(choices=[('telegram', 'Telegram'), ('discord', 'Discord')], max_length=16)),
                ('platform_chat_id', models.BigIntegerField()),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('chat_link', models.CharField(blank=True, max_length=512, null=True)),
                ('enable_ai_check', models.BooleanField(default=False)),
                ('prompts_threshold', models.FloatField(default=0.35)),
                ('custom_prompt_threshold', models.FloatField(default=0.35)),
                ('cleanup_mentions', models.BooleanField(default=False)),
                ('cleanup_emojis', models.BooleanField(default=False)),
                ('cleanup_links', models.BooleanField(default=False)),
                ('allowed_link_domains', models.JSONField(blank=True, null=True)),
                ('processed_messages', models.IntegerField(default=0)),
                ('spam_detected', models.IntegerField(default=0)),
                ('messages_deleted', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats', to='core.user')),
            ],
            options={
                'db_table': 'chats',
            },
        ),
        
        # Create prompts table
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('updated_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('prompt_text', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'prompts',
            },
        ),
        
        # Create custom_prompts table
        migrations.CreateModel(
            name='CustomPrompt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('updated_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('prompt_text', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_prompts', to='core.user')),
            ],
            options={
                'db_table': 'custom_prompts',
            },
        ),
        
        # Create user_states table
        migrations.CreateModel(
            name='UserState',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('updated_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('external_user_id', models.BigIntegerField()),
                ('trusted', models.BooleanField(db_index=True, default=False)),
                ('joined_at', models.DateTimeField(blank=True, null=True)),
                ('valid_messages', models.IntegerField(default=0)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_states', to='core.chat')),
            ],
            options={
                'db_table': 'user_states',
            },
        ),
        
        # Create chat_prompts table
        migrations.CreateModel(
            name='ChatPrompt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('updated_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('priority', models.IntegerField(blank=True, null=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_prompts', to='core.chat')),
                ('prompt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_prompts', to='core.prompt')),
            ],
            options={
                'db_table': 'chat_prompts',
            },
        ),
        
        # Create chat_custom_prompts table
        migrations.CreateModel(
            name='ChatCustomPrompt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('updated_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('priority', models.IntegerField(blank=True, null=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_custom_prompts', to='core.chat')),
                ('custom_prompt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_custom_prompts', to='core.customprompt')),
            ],
            options={
                'db_table': 'chat_custom_prompts',
            },
        ),
        
        # Create runtime_statistics table
        migrations.CreateModel(
            name='RuntimeStatistics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('updated_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('name', models.CharField(default='default_stats', max_length=100, unique=True)),
                ('messages_checked', models.IntegerField(default=0)),
                ('ai_requests_made', models.IntegerField(default=0)),
                ('messages_deleted', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'runtime_statistics',
                'verbose_name_plural': 'Runtime Statistics',
            },
        ),
        
        # Add constraints
        migrations.AddConstraint(
            model_name='chat',
            constraint=models.UniqueConstraint(fields=('type', 'platform_chat_id'), name='uk_chats_type_platform_chat_id'),
        ),
        migrations.AddConstraint(
            model_name='chatprompt',
            constraint=models.UniqueConstraint(fields=('chat', 'prompt'), name='uk_chat_prompts_chat_id_prompt_id'),
        ),
        migrations.AddConstraint(
            model_name='chatcustomprompt',
            constraint=models.UniqueConstraint(fields=('chat', 'custom_prompt'), name='uk_chat_custom_prompts_chat_id_custom_prompt_id'),
        ),
        
        # Add UserState composite index
        migrations.AddIndex(
            model_name='userstate',
            index=models.Index(fields=['chat', 'external_user_id'], name='idx_user_states_chat_extuser'),
        ),
        
        # Add additional indexes
        migrations.RunSQL(
            sql='''
            CREATE INDEX idx_users_telegram ON users(telegram_user_id) WHERE telegram_user_id IS NOT NULL;
            CREATE INDEX idx_users_discord ON users(discord_user_id) WHERE discord_user_id IS NOT NULL;
            ''',
            reverse_sql='''
            DROP INDEX IF EXISTS idx_users_telegram;
            DROP INDEX IF EXISTS idx_users_discord;
            '''
        ),
        
        # Create trigger function for updated_at
        migrations.RunSQL(
            sql='''
            CREATE OR REPLACE FUNCTION set_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
              NEW.updated_at = NOW();
              RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            ''',
            reverse_sql='DROP FUNCTION IF EXISTS set_updated_at();'
        ),
        
        # Create triggers for all tables
        migrations.RunSQL(
            sql='''
            CREATE TRIGGER trg_users_updated_at
                BEFORE UPDATE ON users
                FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            
            CREATE TRIGGER trg_chats_updated_at
                BEFORE UPDATE ON chats
                FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            
            CREATE TRIGGER trg_prompts_updated_at
                BEFORE UPDATE ON prompts
                FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            
            CREATE TRIGGER trg_custom_prompts_updated_at
                BEFORE UPDATE ON custom_prompts
                FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            
            CREATE TRIGGER trg_user_states_updated_at
                BEFORE UPDATE ON user_states
                FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            
            CREATE TRIGGER trg_chat_prompts_updated_at
                BEFORE UPDATE ON chat_prompts
                FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            
            CREATE TRIGGER trg_chat_custom_prompts_updated_at
                BEFORE UPDATE ON chat_custom_prompts
                FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            
            CREATE TRIGGER trg_runtime_statistics_updated_at
                BEFORE UPDATE ON runtime_statistics
                FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            ''',
            reverse_sql='''
            DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
            DROP TRIGGER IF EXISTS trg_chats_updated_at ON chats;
            DROP TRIGGER IF EXISTS trg_prompts_updated_at ON prompts;
            DROP TRIGGER IF EXISTS trg_custom_prompts_updated_at ON custom_prompts;
            DROP TRIGGER IF EXISTS trg_user_states_updated_at ON user_states;
            DROP TRIGGER IF EXISTS trg_chat_prompts_updated_at ON chat_prompts;
            DROP TRIGGER IF EXISTS trg_chat_custom_prompts_updated_at ON chat_custom_prompts;
            DROP TRIGGER IF EXISTS trg_runtime_statistics_updated_at ON runtime_statistics;
            '''
        ),
    ]
