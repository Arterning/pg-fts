#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import TEXT

from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.model import Base, id_key


class SysDoc(Base):
    """文件"""

    __tablename__ = 'sys_doc'

    id: Mapped[id_key] = mapped_column(init=False)
    title: Mapped[str] = mapped_column(TEXT, default='', comment='标题')
    name: Mapped[str] = mapped_column(TEXT, default='', comment='名称')
    type: Mapped[str] = mapped_column(String(500), default=None, comment='类型')
    content: Mapped[str | None] = mapped_column(TEXT, default=None, comment='文件内容')
    desc: Mapped[str | None] = mapped_column(TEXT, default=None, comment='摘要')
    file: Mapped[str | None] = mapped_column(TEXT, default=None, comment='原文')

    doc_data: Mapped[list['SysDocData']] = relationship(init=False, back_populates='doc')