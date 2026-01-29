from django.db import connection


def install_triggers():
    """Install PostgreSQL triggers for automatic updated_at maintenance."""
    with connection.cursor() as cursor:
        # Create trigger function (idempotent)
        cursor.execute("""
            CREATE OR REPLACE FUNCTION set_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # List of tables that need updated_at triggers
        tables = [
            'users',
            'chats',
            'prompts',
            'custom_prompts',
            'user_states',
            'chat_prompts',
            'chat_custom_prompts',
            'runtime_statistics',
        ]

        for table in tables:
            trigger_name = f'trigger_{table}_updated_at'
            
            # Drop existing trigger if it exists
            cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table};")
            
            # Create trigger
            cursor.execute(f"""
                CREATE TRIGGER {trigger_name}
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION set_updated_at();
            """)
