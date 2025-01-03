#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import INT, Column, ForeignKey, Integer, Table

from backend.common.model import MappedBase

sys_org_doc = Table(
    'sys_org_doc',
    MappedBase.metadata,
    Column('id', INT, primary_key=True, unique=True, index=True, autoincrement=True, comment='主键ID'),
    Column('org_id', Integer, ForeignKey('sys_org.id', ondelete='CASCADE'), primary_key=True, comment='组织ID'),
    Column('doc_id', Integer, ForeignKey('sys_doc.id', ondelete='CASCADE'), primary_key=True, comment='文档ID'),
)
