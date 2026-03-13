import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel

load_dotenv()

DB_CONFIG = os.getenv("DATABASE_URL")


class AsyncDatabaseSession:
    def __init__(self):
        self.engine = None
        self.async_session = None

    def init(self):
        """Inicializa o banco de dados e cria a sessão assíncrona."""
        self.engine = create_async_engine(
            DB_CONFIG,
            echo=True,  # Troque para False em produção
            future=True,
            pool_size=5,        # número de conexões “ativas” no pool
            max_overflow=10,    # conexões extras se necessário
            pool_timeout=30     # timeout para pegar conexão do pool
        )
        self.async_session = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    def get_session(self) -> AsyncSession:
        """Retorna uma sessão assíncrona."""
        if self.async_session is None:
            raise RuntimeError("O banco de dados não foi inicializado. Chame db.init() no startup.")
        return self.async_session()

    async def create_all(self):
        """Cria as tabelas no banco de dados."""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def warmup(self):
        """Realiza uma query inicial para 'acordar' o banco e inicializar o pool."""
        async with self.get_session() as session:
            await session.execute(text("SELECT 1"))


db = AsyncDatabaseSession()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Função para injeção de dependência no FastAPI."""
    session = db.get_session()
    try:
        yield session
    finally:
        await session.close()


async def commit_rollback(session: AsyncSession):
    """Confirma a transação ou faz rollback em caso de erro."""
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        print(f"Ocorreu um erro: {e}")
        raise
