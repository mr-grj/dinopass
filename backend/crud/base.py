from sqlalchemy.ext.asyncio import AsyncSession


class BaseCRUD:
    session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class DBNotFoundError(ValueError):
    """
    Could not find the entity in the database.
    """


class DBUnableToInsertError(ValueError):
    """
    Could not insert the entity to the database.
    """


class DBBadEncryptionKeyError(ValueError):
    """
    Invalid encryption key.
    """
