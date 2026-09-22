from src.config.settings import settings


def main():
    """Apply Alembic migrations (preferred over raw create_all)."""
    from alembic import command
    from alembic.config import Config

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(cfg, "head")
    print("Database migrated to head")


if __name__ == "__main__":
    main()
