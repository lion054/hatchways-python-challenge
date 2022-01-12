from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile, BackgroundTasks
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.crud import ProspectCrud, ProspectFileCrud
from api.dependencies.db import get_db
import os
from uuid import uuid4
from typing import List

router = APIRouter(prefix="/api", tags=["prospects_files"])
parent_dir_path = os.path.dirname(os.path.realpath(__file__)) # routes
parent_dir_path = os.path.dirname(parent_dir_path) # api
parent_dir_path = os.path.dirname(parent_dir_path) # server

MAX_PREVIEW_LINES = 20

@router.post("/prospects_files", response_model=schemas.ProspectFileResponse)
async def upload_prospect_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Upload CSV file for importing of prospects"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Please log in"
        )
    dir_path = f"{parent_dir_path}/storage/{uuid4()}"
    os.makedirs(dir_path)
    file_path = f"{dir_path}/{file.filename}"
    file_size = 0
    preview: List[schemas.ProspectRow] = []
    with open(file_path, "wb+") as file_object:
        line_count = 0
        for line in file.file:
            # 0th line is column header
            if line_count <= MAX_PREVIEW_LINES:
                fields = line.split(b',')
                record: schemas.ProspectRow = {
                    "email": fields[0],
                    "first_name": fields[1],
                    "last_name": fields[2]
                }
                preview.append(record)
            line_count += 1
            file_size += len(line)
            file_object.write(line)
        file_object.close()
    prospect_file = ProspectFileCrud.create_prospect_file(db, current_user.id, file_path, file_size)
    return {"id": prospect_file.id, "preview": preview}


def import_prospects_from_file(
    path: str,
    data: schemas.ImportProspects,
    file_id: int,
    current_user: schemas.User,
    db: Session
):
    """Parse the uploaded CSV and import prospects to DB"""
    with open(path, mode="r") as csv_file:
        line_count = 0
        while True:
            line = csv_file.readline().strip() # get line without line feed
            if line == "":
                break
            if not data.has_headers or line_count > 0:
                fields = line.split(',')
                ProspectCrud.import_prospect(db, current_user.id, schemas.ProspectCreate(
                    email = fields[data.email_index],
                    first_name = fields[data.first_name_index],
                    last_name = fields[data.last_name_index],
                ), data.force)
            line_count += 1
            done = csv_file.tell()
            ProspectFileCrud.advance_importing_progress(db, file_id, done)
            db.commit() # write immediately for progress tracking
        csv_file.close()
    ProspectFileCrud.delete_prospect_file(db, file_id)
    db.commit()
    # delete csv file
    os.unlink(path)
    # delete directory if empty
    dir_path = os.path.dirname(path)
    os.rmdir(dir_path)


@router.post("/prospects_files/{file_id}/prospects", response_model=schemas.ProspectFile)
async def start_importing_prospects(
    data: schemas.ImportProspects,
    file_id: int,
    background_tasks: BackgroundTasks,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start the importing process of uploaded CSV in background task"""
    prospect_file = ProspectFileCrud.get_by_id(db, file_id)
    if not prospect_file:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Prospect file with id {file_id} does not exist",
        )

    if prospect_file.user_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail=f"You do not have access to that prospect file",
        )

    background_tasks.add_task(
        import_prospects_from_file,
        prospect_file.path,
        data,
        file_id,
        current_user,
        db
    )

    return {
        "id": prospect_file.id,
        "path": prospect_file.path,
        "total": prospect_file.total,
        "done": prospect_file.done,
        "created_at": prospect_file.created_at,
        "updated_at": prospect_file.updated_at
    }


@router.get("/prospects_files/{file_id}/progress", response_model=schemas.ProspectFileProgressResponse)
async def track_importing_progress(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Get the progress percentage of CSV importing process"""
    prospect_file = ProspectFileCrud.get_by_id(db, file_id)
    return {
        "total": prospect_file.total,
        "done": prospect_file.done
    }
