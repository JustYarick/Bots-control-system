from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Boolean,
    Integer,
    ForeignKey,
    UniqueConstraint,
    text,
    DateTime,
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


class BotFunction(Base):
    __tablename__ = "bot_function"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    message: Mapped[str | None] = mapped_column(String(256))
    fee_uses: Mapped[int | None] = mapped_column(Integer)

    base_settings_links: Mapped[list["BaseSettingsFunction"]] = relationship(
        back_populates="function", cascade="all, delete-orphan"
    )


class BotBaseSettings(Base):
    __tablename__ = "bot_base_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_free_mode_enable: Mapped[bool] = mapped_column(Boolean, default=False)
    is_collect_metrics_enable: Mapped[bool] = mapped_column(Boolean, default=True)

    functions: Mapped[list["BaseSettingsFunction"]] = relationship(
        back_populates="base_settings", cascade="all, delete-orphan"
    )


class BaseSettingsFunction(Base):
    __tablename__ = "base_settings_function"
    __table_args__ = (
        UniqueConstraint("base_settings_id", "function_id", name="uix_settings_func"),
    )

    base_settings_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bot_base_settings.id", ondelete="CASCADE"),
        primary_key=True,
    )
    function_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bot_function.id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    base_settings: Mapped["BotBaseSettings"] = relationship(back_populates="functions")
    function: Mapped["BotFunction"] = relationship(back_populates="base_settings_links")


class BotConfig(Base):
    __tablename__ = "bot_config"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32))
    version: Mapped[str] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    versions: Mapped[list["ConfigVersion"]] = relationship(
        back_populates="config", cascade="all, delete-orphan"
    )

    # Исправленное поле с timezone
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    active_version: Mapped["ConfigVersion"] = relationship(uselist=False, viewonly=True)


class ConfigVersion(Base):
    __tablename__ = "config_version"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bot_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bot_config.id", ondelete="CASCADE"),
        index=True,
    )
    bot_base_settings_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bot_base_settings.id", ondelete="RESTRICT"),
    )
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))

    config: Mapped["BotConfig"] = relationship(back_populates="versions")
    base_settings: Mapped["BotBaseSettings"] = relationship(uselist=False)
