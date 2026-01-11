from database.models import async_session, User, Blacklist
from sqlalchemy import or_, and_, select, update, delete
import secrets
import string


def generate_unique_link_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits  # a-zA-Z0-9
    return "".join(secrets.choice(characters) for _ in range(length))


async def create_user_profile(new_user_id):
    """Создание пользователя в бд (вызывается только по команде /start)"""
    try:
        async with async_session() as session:
            new_user = User(user_id=new_user_id)

            session.add(new_user)
            await session.commit()
    except Exception as e:
        print(f"Ошибка при создании пользователя: {e}")
        await session.rollback()


async def get_link(user_id):
    async with async_session() as session:
        result = await session.execute(
            select(User.link_code).where(User.user_id == user_id)
        )
        link_code = result.scalar()
        return link_code


async def check_user_exists(new_user_id) -> bool:
    """Проверка существования анкеты"""
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == new_user_id))
        return user is not None


async def check_user_VIP(new_user_id) -> bool:
    async with async_session() as session:
        result = await session.scalar(select(User.vip).where(User.user_id == new_user_id))
        return result if result is not None else False


async def check_user_link(code) -> str:
    async with async_session() as session:
        result = await session.execute(
            select(User.user_id).where((User.link_code == code))
        )
        User_receiver = result.scalar()
        return User_receiver
    
async def block_user(owner_user_id, blocked_user_id):
    async with async_session() as session:
        new_user = Blacklist(owner_id=owner_user_id, blocked_user_id = blocked_user_id)
        session.add(new_user)
        await session.commit()

async def clean_blacklist(owner_user_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(Blacklist).where(Blacklist.owner_id == owner_user_id).limit(1)
        )
        entry = result.scalar_one_or_none()
        if entry is None:
            return False

        await session.execute(
            delete(Blacklist).where(Blacklist.owner_id == owner_user_id)
        )
        await session.commit()
        return True


async def check_if_user_blocked(
    blocked_user_id: int,
    owner_user_id: int | None = None
) -> bool:

    async with async_session() as session:
        result = await session.execute(
            select(1)
            .where(
                Blacklist.owner_id == owner_user_id,
                Blacklist.blocked_user_id == blocked_user_id,
            )
            .limit(1)
        )
        return result.scalar() is not None
     

