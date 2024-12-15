#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.admin.schema.doc import CreateSysDocParam, UpdateSysDocParam
from backend.app.admin.schema.doc_data import CreateSysDocDataParam
from backend.app.admin.service.doc_service import sys_doc_service
from backend.common.response.response_schema import response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.utils.doc_utils import post_pdf_recog, post_imagesocr_recog, post_audios_recog, post_emails_recog, request_process_allkinds_filepath,get_llm_abstract, request_text_to_vector,request_rag_01

import os
import json
from fastapi import File, UploadFile
from pathlib import Path
import pandas as pd
import numpy as np
import asyncio
from io import BytesIO
from backend.common.log import log
import traceback
import zipfile
import os
from email import policy
from email.parser import BytesParser
from zipfile import ZipFile

router = APIRouter()

# 定义上传文件保存的目录
UPLOAD_DIRECTORY = "uploads"

# 创建上传文件的目录，如果不存在则创建
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1][1:]

def is_zip_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.zip']

def is_excel_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.xls', '.xlsx']

def is_csv_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.csv']

def is_pdf_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.pdf']

def is_picture_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.jpeg', '.jpg', '.png']

def is_media_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.mp4', '.mp3', '.flv', '.wav']

def is_text_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.txt', '.host', '.config',
                                             '.c', '.cpp', '.java', '.py', 'js', '.ts', '.rb', '.go']

def is_email_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ['.eml']

def get_filename(file_path: str):
    return os.path.basename(file_path)

def get_file_title(file_name: str):
    return os.path.splitext(file_name)[0]

file_type_handlers = {
    'excel': is_excel_file,
    'csv': is_csv_file,
    'picture': is_picture_file,
    'media': is_media_file,
    'text': is_text_file,
    'email': is_email_file,
    'pdf': is_pdf_file,
    'zip': is_zip_file
}
def get_file_type(file_name: str):
    for file_type, handler in file_type_handlers.items():
        if handler(file_name):
            return file_type
    return 'text'

@router.post("/", summary='上传文件', dependencies=[DependsJwtAuth])
async def upload_file(file: UploadFile = File(...)):
    log.info('上传文件')
    filename = file.filename
    resp = {"filename": file.filename}
    if is_excel_file(filename):
        log.info("read excel")
        await read_excel(file)
        return response_base.success(data=resp)
    
    if is_csv_file(filename):
        log.info("read csv")
        await read_text(file)
        return response_base.success(data=resp)
    
    if is_picture_file(filename):
        log.info("read picture")
        await read_picture(file)
        return response_base.success(data=resp)

    if is_media_file(filename):
        log.info("read media")
        await read_media(file)
        return response_base.success(data=resp)

    if is_text_file(filename):
        log.info("read text")
        await read_text(file)
        return response_base.success(data=resp)

    if is_email_file(filename):
        log.info("read email")
        await read_email(file)
        return response_base.success(data=resp)

    if is_pdf_file(filename):
        log.info("read pdf")
        await read_pdf(file)
        return response_base.success(data=resp)
    
    if is_zip_file(filename):
        log.info("read zip")
        await read_zip(file)
        return response_base.success(data=resp)

    log.info("no match, read text")
    await read_text(file)
    return response_base.success(data=resp)



async def read_text(file: UploadFile = File(...)):
    file_location, content = await save_file(file)
    name = get_filename(file.filename)
    title = get_file_title(name)
    loop = asyncio.get_running_loop()
    path = f"~/{file_location}"
    content_str = content.decode('utf-8')
    pdf_records = await loop.run_in_executor(None, request_process_allkinds_filepath, path)
    log.info(pdf_records)
    desc = ''
    if pdf_records:
        desc = pdf_records['abstract']
    vector_data = await loop.run_in_executor(None,request_text_to_vector,content_str)
    obj: CreateSysDocParam = CreateSysDocParam(title=title, name=name, type="text",content=content_str,
                                                file=file_location,desc=desc,text_embed=vector_data)
    
    await sys_doc_service.create(obj=obj)



async def read_picture(file: UploadFile):
    file_location, _ = await save_file(file)
    name = get_filename(file.filename)
    title = get_file_title(name)
    loop = asyncio.get_running_loop()
    path = f"~/{file_location}"
    # pdf_records = await loop.run_in_executor(None, post_imagesocr_recog, path, "~/uploads/result/", "zhen_light")
    pdf_records = await loop.run_in_executor(None, request_process_allkinds_filepath, path)
    content = ''
    desc = ''
    if pdf_records:
        content = pdf_records['content']
        desc = pdf_records['abstract']
    vector_data = await loop.run_in_executor(None,request_text_to_vector,content)   
    obj: CreateSysDocParam = CreateSysDocParam(title=title, name=name, type="picture",content=content,
                                                file=file_location, desc=desc,text_embed=vector_data)
    await sys_doc_service.create(obj=obj)

async def read_media(file: UploadFile):
    file_location, _ = await save_file(file)
    name = get_filename(file.filename)
    title = get_file_title(name)
    loop = asyncio.get_running_loop()
    path = f"~/{file_location}"
    # pdf_records = await loop.run_in_executor(None, post_imagesocr_recog, path, "~/uploads/result/", "zhen_light")
    pdf_records = await loop.run_in_executor(None, request_process_allkinds_filepath, path)
    content = ''
    desc = ''
    if pdf_records:
        content = pdf_records['content']
        desc = pdf_records['abstract']
    vector_data = await loop.run_in_executor(None,request_text_to_vector,content)
    obj: CreateSysDocParam = CreateSysDocParam(title=title, name=name, type="media",content=content,
                                                file=file_location,desc=desc,text_embed=vector_data)
    await sys_doc_service.create(obj=obj)


async def read_email(file: UploadFile):
    file_location, _ = await save_file(file)
    name = get_filename(file.filename)
    title = get_file_title(name)
    loop = asyncio.get_running_loop()
    path = f"~/{file_location}"
    # pdf_records = await loop.run_in_executor(None, post_emails_recog, path, "~/uploads/附录下载目录/", "~/uploads/附录二次识别输出目录", "zhen_light", "zhen")
    pdf_records = await loop.run_in_executor(None, request_process_allkinds_filepath, path)
    content = ''
    desc = ''
    email_subject, email_from, email_to, email_time = '', '', '', ''
    if pdf_records:
        
        content = pdf_records['content']
        email_subject = content['subject']
        email_from = content['from']
        email_to = content['to']
        email_time = content['date']
        email_body = content['body']
        desc = pdf_records['abstract']
        # for record in pdf_records:
            # co = record["content"]
            # if isinstance(co, str):
            #     content += co
            # if isinstance(co, dict):
            #     email_subject = co["subject"]
            #     email_from = co["from"]
            #     email_to = co["to"]
            #     email_time = co["date"]
    vector_data = await loop.run_in_executor(None,request_text_to_vector,json.dumps(str(content),ensure_ascii=False,indent=4))
    obj: CreateSysDocParam = CreateSysDocParam(title=title, name=name, type="email",content=email_body,
                                               email_subject=email_subject,email_from=email_from,
                                               email_to=email_to, email_time=email_time, file=file_location,desc=desc,text_embed=vector_data)
    doc = await sys_doc_service.create(obj=obj)
    # 获取邮件的id
    doc_id = doc.id
    # 获取附件，下载附件
    await emailfile_attachments_downloads(eml_file=file_location , download_folder="uploads",belong=doc_id)




async def read_pdf(file: UploadFile = File(...)):
    file_location, _ = await save_file(file)
    name = get_filename(file.filename)
    title = get_file_title(name)
    
    path = f"~/{file_location}"
    loop = asyncio.get_running_loop()
    log.info("******************")
    log.info(path)
    # pdf_records = await loop.run_in_executor(None, post_imagesocr_recog, path, "~/uploads/result/", "zhen_light")
    pdf_records = await loop.run_in_executor(None, request_process_allkinds_filepath, path)
    content = ''
    desc = ''
    log.info(f"pdfrecord{pdf_records}")
    if pdf_records:
        content = pdf_records['content']
        desc = pdf_records['abstract']
    vector_data = await loop.run_in_executor(None,request_text_to_vector,content)
    obj: CreateSysDocParam = CreateSysDocParam(title=title, name=name, type="pdf",content=content,
                                                file=file_location,desc=desc,text_embed=vector_data)
    # await sys_doc_service.create(obj=obj)
    doc = await sys_doc_service.create(obj=obj)

    log.info(doc.id)


async def read_excel(file: UploadFile = File(...)):
    # 读取 Excel 文件并解析为 DataFrame
    file_content = await file.read()
    file_bytes = BytesIO(file_content)
    try:
        df = pd.read_excel(file_bytes, nrows=10, header=None)
    except Exception as e:
        raise e

    for i, row in df.iterrows():
        if not row.isna().any():
            head = i
            break
    df = pd.read_excel(file_bytes, header=head)

    # 替换 NaN 为 None（可以避免 PostgreSQL 插入错误）
    df = df.where(pd.notnull(df), None)
    df.replace([np.nan, np.inf, -np.inf], None, inplace=True)

    # 将 DataFrame 转换为 JSON 格式
    data_json = df.to_dict(orient="records")
    # 构建文件保存路径
    file_location, _ = await save_file(file)

    # 将数据存入数据库
    name = get_filename(file.filename)
    title = get_file_title(name)
    content = ''

    path = f"~/{file_location}"
    loop = asyncio.get_running_loop()
    data_input = df.head(5).to_string(index=False, header=True)
    log.info(data_input)
    excel_records = await loop.run_in_executor(None, get_llm_abstract, data_input)
    log.info(excel_records)
    if excel_records:
        desc = excel_records
        
    
    for excel_data in data_json:
        strings = dict_to_string(excel_data)
        row = strings + '\n'
        content += row
    content = content.replace("Unnamed", "").replace("None", "")
    vector_data = await loop.run_in_executor(None,request_text_to_vector,json.dumps(content))
    doc_param = CreateSysDocParam(title=title, name=name, type='excel', 
                                  c_token=content, content=content, file=file_location,desc=desc,text_embed=vector_data)
    doc = await sys_doc_service.create(obj=doc_param)

    for excel_data in data_json:
        param = CreateSysDocDataParam(doc_id=doc.id, excel_data=excel_data)
        await sys_doc_service.create_doc_data(obj=param)
    return response_base.success(data=doc.id)


def dict_to_string(input_dict):
    return ' '.join(f"{key} {value}" for key, value in input_dict.items())

async def save_file(file: UploadFile = File(...)):
    # 构建文件保存路径
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)

    # 提取目录部分并创建目录（如果不存在）
    directory = os.path.dirname(file_location)
    os.makedirs(directory, exist_ok=True)

    # 将上传的文件保存到指定目录
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return file_location, content



def support_gbk(zip_file: ZipFile):
    name_to_info = zip_file.NameToInfo
    # copy map first
    for name, info in name_to_info.copy().items():
        real_name = name.encode('cp437').decode('gbk')
        if real_name != name:
            info.filename = real_name
            del name_to_info[name]
            name_to_info[real_name] = info
    return zip_file


async def read_zip(file: UploadFile = File(...)):
    file_location, _ = await save_file(file)
    with support_gbk(ZipFile(file_location, "r")) as zip_ref:
        name_list = zip_ref.namelist()
        for file_name in name_list:
            with zip_ref.open(file_name) as single_file:
                try:
                    name = os.path.basename(file_name)
                    title = get_file_title(name)
                    log.info(f"Start read {title}")
                    file_content = single_file.read()
                    # 创建BytesIO对象，模拟上传文件
                    file_bytes = BytesIO(file_content)
                    file_upload_file = UploadFile(
                            file_bytes,
                            filename=file_name,
                    )
                    if is_pdf_file(name):
                        await read_pdf(file_upload_file)
                    if is_excel_file(name):
                        await read_excel(file_upload_file)
                    if is_csv_file(name):
                        await read_text(file)
                    if is_picture_file(name):
                        await read_picture(file_upload_file)
                    if is_media_file(name):
                        await read_media(file_upload_file)
                    if is_text_file(name):
                        await read_text(file_upload_file)
                    if is_email_file(name):
                        await read_email(file_upload_file)
                    log.info(f"Success read {title}")
                except Exception as e:
                    traceback.print_exc()
        os.remove(file_location)





# 3.1 获取邮件正文
def get_email_body(msg):
    """提取邮件正文，支持纯文本和HTML格式，并从HTML中提取纯文本。"""
    body = {'plain': '', 'html': ''}
    if msg.is_multipart():
        for part in msg.iter_parts():
            content_type = part.get_content_type()
            charset = part.get_content_charset() or 'utf-8'
            if content_type == 'text/plain':
                body['plain'] += part.get_payload(decode=True).decode(charset)
            elif content_type == 'text/html':
                # 提取HTML并转换为纯文本
                html_content = part.get_payload(decode=True).decode(charset)
                soup = BeautifulSoup(html_content, 'html.parser')
                body['html'] += soup.get_text()  # 从HTML提取纯文本
    else:
        # 非 multipart 邮件
        content_type = msg.get_content_type()
        charset = msg.get_content_charset() or 'utf-8'
        if content_type == 'text/plain':
            body['plain'] = msg.get_payload(decode=True).decode(charset)
        elif content_type == 'text/html':
            # 提取HTML并转换为纯文本
            html_content = msg.get_payload(decode=True).decode(charset)
            soup = BeautifulSoup(html_content, 'html.parser')
            body['html'] = soup.get_text()  # 从HTML提取纯文本
    return body



# 3.2 保存附件并记录路径
async def save_attachments(msg, download_folder, belong):
    """保存附件并返回附件文件路径的列表。"""
    attachments = []
    for part in msg.iter_attachments():
        filename = part.get_filename()
        if filename:
            file_path = os.path.join(download_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(part.get_payload(decode=True))

            title = get_file_title(filename)
            path = f"~/{file_path}"
            loop = asyncio.get_running_loop()
            records = await loop.run_in_executor(
                None, request_process_allkinds_filepath, path
            )
            content = ''
            desc = ''
            if records:
                if 'content' not in records:
                    log.warning(f"{filename}没有content或者不能处理，跳过")
                    continue
                content = records['content']
                desc = records['abstract']
            vector_data = await loop.run_in_executor(None,request_text_to_vector,content)
            file_type = get_file_type(filename)
            obj: CreateSysDocParam = CreateSysDocParam(
                title=title,
                name=filename,
                type=file_type,
                content=content,
                file=file_path,
                desc=desc,
                belong=belong,
                text_embed=vector_data
            )
            await sys_doc_service.create(obj=obj)

            attachments.append(file_path)
    return attachments






# 3.3 单个邮件附件下载到指定目录，并处理其中所有附件。连同邮件正文一起组合
async def  emailfile_attachments_downloads( eml_file, download_folder,belong):
    """
    解析 .eml 文件，提取邮件头、正文、附件，并将结果存储为字典。
    附件会保存到指定的文件夹。
    
    参数:
        eml_file (str): .eml 文件的路径
        download_folder (str): 保存附件的文件夹路径 (默认为 "attachments")
    
    返回:
        list[dict]: 邮件内容 + 邮件附件内容
    """
    download_folder = Path(download_folder)
    # 确保保存附件的文件夹存在
    if not os.path.exists(download_folder):
        
        download_folder.mkdir(exist_ok=True,parents=True)

    
    # 读取并解析 .eml 文件
    with open(eml_file, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    # 存储邮件信息的字典
    email_data = {
        
    }

    # 获取邮件头信息
    email_data['subject'] = msg['subject']
    email_data['from'] = msg['from']
    email_data['to'] = msg['to']
    email_data['cc'] = msg['cc']
    email_data['bcc'] = msg['bcc']
    email_data['date'] = msg['date']
    email_data['message-id'] = msg['message-id']
    
    
    body_content = get_email_body(msg)
    body_content = body_content["plain"] + body_content["html"] ## 合并文本类型数据和html数据
    email_data["body"] = body_content
    # 下载附件
    email_data['attachments'] = await save_attachments(msg, download_folder,belong) 

