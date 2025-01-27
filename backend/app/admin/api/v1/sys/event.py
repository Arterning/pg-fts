#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.app.admin.schema.event import CreateEventParam, GetEventListDetails, UpdateEventParam
from backend.app.admin.service.event_service import event_service
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import ResponseModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db_pg import CurrentSession

router = APIRouter()


@router.get('/{pk}', summary='获取详情', dependencies=[DependsJwtAuth])
async def get_event(pk: Annotated[int, Path(...)]) -> ResponseModel:
    event = await event_service.get(pk=pk)
    return response_base.success(data=event)


@router.get(
    '',
    summary='（模糊条件）分页获取所有',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_event(db: CurrentSession) -> ResponseModel:
    event_select = await event_service.get_select()
    page_data = await paging_data(db, event_select, GetEventListDetails)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建',
    dependencies=[
        Depends(RequestPermission(':add')),
        DependsRBAC,
    ],
)
async def create_event(obj: CreateEventParam) -> ResponseModel:
    await event_service.create(obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新',
    dependencies=[
        Depends(RequestPermission(':edit')),
        DependsRBAC,
    ],
)
async def update_event(pk: Annotated[int, Path(...)], obj: UpdateEventParam) -> ResponseModel:
    count = await event_service.update(pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='（批量）删除',
    dependencies=[
        Depends(RequestPermission(':del')),
        DependsRBAC,
    ],
)
async def delete_event(pk: Annotated[list[int], Query(...)]) -> ResponseModel:
    count = await event_service.delete(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()