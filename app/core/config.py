import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

load_dotenv()

DB_CONFIG = os.getenv("DATABASE_URL")


class AsyncDatabaseSession:
    def __init__(self):
        self.engine = None
        self.async_session = None

    def init(self):
        self.engine = create_async_engine(
            DB_CONFIG,
            echo=True,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
        )
        self.async_session = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    def get_session(self) -> AsyncSession:
        if self.async_session is None:
            raise RuntimeError("O banco de dados não foi inicializado. Chame db.init() no startup.")
        return self.async_session()

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def run_migrations(self):
        async with self.engine.begin() as conn:
            dialect = conn.dialect.name

            if dialect != "postgresql":
                return

            await conn.execute(text("ALTER TABLE words ADD COLUMN IF NOT EXISTS owner_user_id VARCHAR"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_words_owner_user_id ON words (owner_user_id)"))
            await conn.execute(
                text(
                    """
                    DO $$
                    DECLARE constraint_name text;
                    DECLARE index_name text;
                    BEGIN
                        FOR constraint_name IN
                            SELECT c.conname
                            FROM pg_constraint c
                            JOIN pg_class t ON c.conrelid = t.oid
                            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
                            WHERE t.relname = 'words'
                              AND c.contype = 'u'
                              AND a.attname = 'english'
                        LOOP
                            EXECUTE format('ALTER TABLE words DROP CONSTRAINT %I', constraint_name);
                        END LOOP;

                        FOR index_name IN
                            SELECT i.indexname
                            FROM pg_indexes i
                            WHERE i.schemaname = ANY (current_schemas(false))
                              AND i.tablename = 'words'
                              AND i.indexdef ILIKE 'CREATE UNIQUE INDEX % ON %words% (english)%'
                        LOOP
                            EXECUTE format('DROP INDEX IF EXISTS %I', index_name);
                        END LOOP;
                    END $$;
                    """
                )
            )
            await conn.execute(text("DROP INDEX IF EXISTS ix_words_english"))
            await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_words_english ON words (english)"))

    async def warmup(self):
        async with self.get_session() as session:
            await session.execute(text("SELECT 1"))


db = AsyncDatabaseSession()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = db.get_session()
    try:
        yield session
    finally:
        await session.close()


async def commit_rollback(session: AsyncSession):
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        print(f"Ocorreu um erro: {e}")
        raise
