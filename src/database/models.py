from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    String,
    Boolean,
    Integer,
    ForeignKey,
    UniqueConstraint,
    text,
    DateTime,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    DeclarativeBase,
)
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


class Environment(str, Enum):
    """Доступные окружения"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class FeatureFlag(Base):
    """Модель функции (feature flag)"""

    __tablename__ = "feature_flag"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(256))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    config_features: Mapped[list["FeatureConfigFlag"]] = relationship(
        back_populates="feature", cascade="all, delete-orphan"
    )


class FeatureConfig(Base):
    """Модель конфигурации окружения"""

    __tablename__ = "feature_config"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    environment: Mapped[Environment] = mapped_column(SQLEnum(Environment), nullable=False)
    description: Mapped[str | None] = mapped_column(String(256))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Отношения
    features: Mapped[list["FeatureConfigFlag"]] = relationship(
        back_populates="config", cascade="all, delete-orphan"
    )
    versions: Mapped[list["FeatureConfigVersion"]] = relationship(
        back_populates="config", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("name", "environment", name="uix_config_name_env"),)


class FeatureConfigFlag(Base):
    """Связь между конфигурацией и функцией с настройками"""

    __tablename__ = "feature_config_flag"
    __table_args__ = (UniqueConstraint("config_id", "feature_id", name="uix_config_feature"),)

    config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feature_config.id", ondelete="CASCADE"),
        primary_key=True,
    )
    feature_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feature_flag.id", ondelete="CASCADE"),
        primary_key=True,
    )

    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_free: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    disabled_message: Mapped[str | None] = mapped_column(String(256), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )

    config: Mapped["FeatureConfig"] = relationship(back_populates="features")
    feature: Mapped["FeatureFlag"] = relationship(back_populates="config_features")


class FeatureConfigVersion(Base):
    """Версии конфигураций"""

    __tablename__ = "feature_config_version"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("feature_config.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    changelog: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )

    # Отношения
    config: Mapped["FeatureConfig"] = relationship(back_populates="versions")

    __table_args__ = (UniqueConstraint("config_id", "version_number", name="uix_config_version"),)
