from django.db import connection

UPDATED_AT_FUNCTION_SQL = r"""
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def _table_has_column(table_name: str, column_name: str) -> bool:
    with connection.cursor() as cur:
        cur.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
              AND column_name = %s
            LIMIT 1
            """,
            [table_name, column_name],
        )
        return cur.fetchone() is not None


def _create_trigger_for_table(table_name: str) -> None:
    trigger_name = f"trg_{table_name}_updated_at"
    with connection.cursor() as cur:
        # idempotent: drop + create
        cur.execute(
            f'DROP TRIGGER IF EXISTS "{trigger_name}" ON "{table_name}";'
        )
        cur.execute(
            f"""
            CREATE TRIGGER "{trigger_name}"
            BEFORE UPDATE ON "{table_name}"
            FOR EACH ROW
            EXECUTE FUNCTION set_updated_at();
            """
        )


def ensure_updated_at_triggers(sender, **kwargs):
    """
    Runs after migrations. Ensures:
    1) function set_updated_at exists
    2) every table in this app that has updated_at column
    has BEFORE UPDATE trigger
    """
    # 1) ensure function exists
    with connection.cursor() as cur:
        cur.execute(UPDATED_AT_FUNCTION_SQL)

    # 2) for all tables created by this app
    # Django gives us all model tables through sender.get_models()
    app_models = sender.get_models()

    for model in app_models:
        table = model._meta.db_table

        # if table exists and has updated_at column -> create trigger
        try:
            if _table_has_column(table, "updated_at"):
                _create_trigger_for_table(table)
        except Exception:
            # if table doesn't exist yet or permissions, ignore and continue
            # (normally should not happen after migrate)
            continue
