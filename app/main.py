import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from app.schemas import PostCreate, PostResponse
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from app.images import imagekit
from imagekitio.models.upload_file_response import UploadFileResponse
import shutil
import os
import uuid
import tempfile


# 1. Definimos el ciclo de vida (lifespan) para crear las tablas
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Esto ocurre al arrancar el servidor
    await create_db_and_tables()
    yield
    # Aquí podrías poner lógica de apagado si fuera necesaria

# 2. Inicializamos FastAPI con el lifespan
app = FastAPI(lifespan=lifespan)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = "",
    session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None
    try:
        # Todo este bloque tiene 4 espacios de sangría
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        with open(temp_file_path, "rb") as img_file:
            upload_result = imagekit.upload_file(
                file=img_file,
                file_name=file.filename,
                options={
                    "use_unique_file_name": True,
                    "tags": ["backend_upload"]
                }
            )

        if upload_result and hasattr(upload_result, 'url'):
            nuevo_post = Post(
                caption=caption,
                url=upload_result.url,
                file_type="photo",
                file_name=file.filename
            )
            session.add(nuevo_post)
            await session.commit()
            await session.refresh(nuevo_post)
            return nuevo_post
        else:
            raise HTTPException(status_code=500, detail="Error en ImageKit")

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        await file.close()

    return {"posts": post_data}

if __name__ == "__main__":
    # Nota: reload=True solo es válido si pasas la app como string "app.main:app"
    # Para ejecutarlo con python main.py usamos la instancia directamente
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
