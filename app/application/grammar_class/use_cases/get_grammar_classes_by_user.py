from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.word.WordModel import GrammarClass, UserWord, WordGrammarClass
from app.modules.grammar_class.GrammarClassSchema import GrammarClassListItem


class GetGrammarClassesByUserUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, user_id: str) -> list[GrammarClassListItem]:
        count_stmt = (
            select(GrammarClass.slug, func.count(func.distinct(WordGrammarClass.word_id)))
            .select_from(GrammarClass)
            .join(WordGrammarClass, WordGrammarClass.grammar_class_id == GrammarClass.id, isouter=True)
            .join(UserWord, UserWord.word_id == WordGrammarClass.word_id, isouter=True)
            .where((UserWord.user_id == user_id) | (UserWord.user_id.is_(None)))
            .group_by(GrammarClass.slug)
        )
        count_result = await self.db.execute(count_stmt)
        counts = {slug: int(total) for slug, total in count_result.all()}

        classes_stmt = select(GrammarClass).order_by(GrammarClass.name)
        classes_result = await self.db.execute(classes_stmt)
        classes = classes_result.scalars().all()

        return [
            GrammarClassListItem(
                slug=item.slug,
                name=item.name,
                description=item.description,
                wordsCount=counts.get(item.slug, 0),
            )
            for item in classes
        ]
