from fastapi import APIRouter, HTTPException, status, Depends, File, Form, UploadFile
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from api.crud import ProspectFileCrud
from api.dependencies.db import get_db
from os import path, makedirs
from uuid import uuid4
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api", tags=["prospects_files"])
parent_dir_path = path.dirname(path.realpath(__file__)) # routes
parent_dir_path = path.dirname(parent_dir_path) # api
parent_dir_path = path.dirname(parent_dir_path) # server


@router.post("/prospects_files", response_model=schemas.ProspectFileResponse)
async def upload_prospect_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Get a single page of prospects"""
    # raise HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED, detail=f"filename {file.filename}"
    # )
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )
    dir_path = f"{parent_dir_path}/storage/{uuid4()}"
    makedirs(dir_path)
    file_path = f"{dir_path}/{file.filename}"
    file_size = 0
    preview: List[schemas.ProspectFile] = []
    with open(file_path, "wb+") as file_object:
        line_count = 0
        for line in file.file:
            # 0th line is column header
            if line_count >= 1 and line_count <= 20:
                fields = line.split(b',')
                record: schemas.ProspectFile = {
                    "id": line_count,
                    "email": fields[0],
                    "first_name": fields[1],
                    "last_name": fields[2],
                    "user_id": current_user.id,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                preview.append(record)
            line_count += 1
            file_size += len(line)
            file_object.write(line)
        file_object.close()
    prospectFile = ProspectFileCrud.create_prospect_file(db, current_user.id, file_path, file_size)
    return {"id": prospectFile.id, "preview": preview}
