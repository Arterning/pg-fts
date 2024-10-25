#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from sqlalchemy import Select

from backend.app.admin.crud.crud_doc import sys_doc_dao
from backend.app.admin.crud.crud_doc_data import sys_doc_data_dao
from backend.app.admin.model import SysDoc
from backend.app.admin.model import SysDocData
from backend.app.admin.schema.doc import CreateSysDocParam, UpdateSysDocParam
from backend.common.exception import errors
from backend.database.db_pg import async_db_session
from backend.app.admin.schema.doc_data import CreateSysDocDataParam
import jieba

class SysDocService:
    @staticmethod
    async def get(*, pk: int) -> SysDoc:
        async with async_db_session() as db:
            sys_doc = await sys_doc_dao.get(db, pk)
            if not sys_doc:
                raise errors.NotFoundError(msg='文件不存在')
            return sys_doc

    # @staticmethod
    # async def token_search(tokens: str = None) -> list[int]:
    #     async with async_db_session() as db:
    #         res = await sys_doc_dao.token_search(db, tokens)
    #         return res

    @staticmethod
    async def update_tokens(doc: SysDoc, a_tokens: str = None, b_tokens: str = None) -> list[int]:
        async with async_db_session() as db:
            res = await sys_doc_dao.update_tokens(db, doc, a_tokens, b_tokens)
            return res

    @staticmethod
    async def get_select(*, name: str = None, type: str = None, tokens: str = None, ids: list[int] = None) -> Select:
        return await sys_doc_dao.get_list(name=name, type=type, tokens=tokens, ids=ids)

    @staticmethod
    async def get_all() -> Sequence[SysDoc]:
        async with async_db_session() as db:
            sys_docs = await sys_doc_dao.get_all(db)
            return sys_docs

    @staticmethod
    async def create(*, obj: CreateSysDocParam) -> SysDoc:
        doc = None
        async with async_db_session.begin() as db:
            # sys_doc = await sys_doc_dao.get_by_name(db, obj.name)
            # if sys_doc:
            #     raise errors.ForbiddenError(msg='文件已存在')
            doc = await sys_doc_dao.create(db, obj)
        title = doc.title
        content = doc.content
        a_tokens = ''
        b_tokens = ''
        if title:
            a_seg_list = jieba.cut(title, cut_all=True)
            a_tokens =  " ".join(a_seg_list) 
        if content:
            b_seg_list = jieba.cut(content, cut_all=True)
            b_tokens = " ".join(b_seg_list)
        await sys_doc_service.update_tokens(doc, a_tokens, b_tokens)
        return doc


    @staticmethod
    async def create_doc_data(*, obj: CreateSysDocDataParam) -> SysDocData:
        async with async_db_session.begin() as db:
            return await sys_doc_data_dao.create(db, obj)

    @staticmethod
    async def update(*, pk: int, obj: UpdateSysDocParam) -> int:
        async with async_db_session.begin() as db:
            count = await sys_doc_dao.update(db, pk, obj)
            sys_doc = await sys_doc_dao.get(db, pk)
            if not sys_doc:
                raise errors.NotFoundError(msg='文件不存在')
            title = sys_doc.title
            content = sys_doc.content
            a_tokens = ''
            b_tokens = ''
            if title:
                a_seg_list = jieba.cut(title, cut_all=True)
                a_tokens =  " ".join(a_seg_list) 
            if content:
                b_seg_list = jieba.cut(content, cut_all=True)
                b_tokens = " ".join(b_seg_list)
            await sys_doc_dao.update_tokens(db, sys_doc, a_tokens, b_tokens)
            return count

    @staticmethod
    async def delete(*, pk: list[int]) -> int:
        async with async_db_session.begin() as db:
            count = await sys_doc_dao.delete(db, pk)
            return count


sys_doc_service = SysDocService()
