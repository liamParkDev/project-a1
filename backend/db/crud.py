# db/crud.py
from datetime import datetime
from sqlalchemy.orm import Session
from core.security import hash_password, verify_password
from db.models import User, UserProvider, Product


# =======================================
# USERS
# =======================================

def _generate_unique_nickname(db: Session, base_nickname: str) -> str:
    candidate = base_nickname
    suffix = 1
    while db.query(User).filter(User.nickname == candidate).first():
        suffix += 1
        candidate = f"{base_nickname}{suffix}"
    return candidate


def create_user(
    db: Session,
    email: str,
    password: str | None,
    nickname: str,
    provider: str | None = None,
    provider_user_id: str | None = None,
    profile_complete: bool = True,
):
    """
    회원가입: User 생성 (로컬/소셜 공용)
    """
    hashed = hash_password(password) if password else None
    nickname = _generate_unique_nickname(db, nickname)

    user = User(
        email=email,
        password_hash=hashed,
        nickname=nickname,
        profile_complete=1 if profile_complete else 0,
        is_active=1,
    )

    if provider and provider_user_id:
        user.providers.append(
            UserProvider(
                provider=provider,
                provider_user_id=provider_user_id,
                email=email,
            )
        )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_oauth_user(
    db: Session,
    provider: str,
    provider_user_id: str,
    email: str | None,
    nickname: str | None,
    profile_complete: bool = False,
):
    """
    소셜 로그인 신규 가입
    """
    nickname = nickname or f"{provider}_{provider_user_id[:6]}"
    return create_user(
        db=db,
        email=email or f"{provider_user_id}@{provider}.local",
        password=None,
        nickname=nickname,
        provider=provider,
        provider_user_id=provider_user_id,
        profile_complete=profile_complete,
    )


def get_user_by_provider(db: Session, provider: str, provider_user_id: str):
    return (
        db.query(User)
        .join(UserProvider)
        .filter(
            UserProvider.provider == provider,
            UserProvider.provider_user_id == provider_user_id,
        )
        .first()
    )


def authenticate_user(db: Session, email: str, password: str):
    """
    로그인: 이메일/비밀번호 검증
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if user.deleted_at:
        return None
    if not user.is_active:
        return None
    if user.suspended_until and user.suspended_until > datetime.utcnow():
        return None
    if not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def link_provider_to_user(
    db: Session,
    user: User,
    provider: str,
    provider_user_id: str,
    email: str | None,
):
    """
    로컬 계정과 소셜 계정 연결
    """
    existing_link = db.query(UserProvider).filter(
        UserProvider.provider == provider,
        UserProvider.provider_user_id == provider_user_id,
    ).first()
    if existing_link and existing_link.user_id != user.id:
        raise ValueError("provider_link_in_use")

    if existing_link is None:
        link = UserProvider(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
        )
        db.add(link)
    db.commit()
    db.refresh(user)
    return user


def disconnect_provider(
    db: Session,
    user: User,
    provider: str,
):
    """
    소셜 계정 연결 해제 (다른 로그인 수단이 없으면 차단)
    """
    link = (
        db.query(UserProvider)
        .filter(UserProvider.user_id == user.id, UserProvider.provider == provider)
        .first()
    )
    if not link:
        raise ValueError("provider_not_linked")

    remaining_methods = len(user.providers) - 1
    has_password = bool(user.password_hash)
    if remaining_methods <= 0 and not has_password:
        raise ValueError("no_other_login_method")

    db.delete(link)
    db.commit()
    db.refresh(user)
    return user


# =======================================
# PRODUCTS
# =======================================

def get_product(db: Session, product_id: int):
    """
    상품 1개 조회
    """
    return db.query(Product).filter(Product.id == product_id).first()


def search_products(db: Session, keyword: str):
    """
    상품 검색 (title LIKE 검색)
    """
    q = f"%{keyword}%"
    return db.query(Product).filter(Product.title.like(q)).all()


# =======================================
# (선택) Product 생성/수정/삭제도 여기에 추가 예정
# =======================================

def create_product(db: Session, seller_id: int, title: str, price: int, description: str = None):
    """
    상품 등록
    """
    product = Product(
        seller_id=seller_id,
        title=title,
        price=price,
        description=description
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
