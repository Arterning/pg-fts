#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from pydantic import ConfigDict

from backend.common.schema import SchemaBase


class SysDocSchemaBase(SchemaBase):
    title: str
    name: str | None = None
    type: str | None = None
    content: str | None = None
    desc: str | None = None
    file: str | None = None
    email_subject: str | None = None
    email_from: str | None = None
    email_to: str | None = None
    email_time: str | None = None


class CreateSysDocParam(SysDocSchemaBase):
    pass


class UpdateSysDocParam(SchemaBase):
    title: str | None = None
    name: str | None = None
    type: str | None = None
    content: str | None = None
    desc: str | None = None


class GetSysDocListDetails(SysDocSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None


class GetDocDetail(SysDocSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_time: datetime
    updated_time: datetime | None = None
    doc_data: list[dict]
