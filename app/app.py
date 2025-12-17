import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Form
from app.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate
from app.db import Post, User, create_db_and_tables, get_async_session
from app.users import auth_backend, fastapi_users, current_active_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from app.images import imagekit
from imagekitio.types import FileUploadResponse
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path
import shutil
import os
import uuid
import tempfile

# Load environment variables for public_key
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


# 1. Definimos el ciclo de vida (lifespan) para crear las tablas
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Esto ocurre al arrancar el servidor
    await create_db_and_tables()
    yield
    # Aquí podrías poner lógica de apagado si fuera necesaria

# 2. Inicializamos FastAPI con el lifespan
app = FastAPI(lifespan=lifespan)

# Routers de autenticación
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)




@app.get("/Hello World")
def hello_World():
    return {"message": "Hello World"}


@app.post("/upload", response_model=PostResponse)
async def upload_file(
    file: UploadFile = File(..., description="Archivo de imagen a subir"),
    caption: Optional[str] = Form(None, description="Pie de foto opcional"),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Sube un archivo a ImageKit y guarda la referencia en la base de datos.
    Requiere autenticación.
    """
    if caption is None:
        caption = ""
    temp_file_path = None
    try:
        # Todo este bloque tiene 4 espacios de sangría
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        with open(temp_file_path, "rb") as img_file:
            upload_result = imagekit.files.upload(
                file=img_file,
                file_name=file.filename,
                use_unique_file_name=True,
                tags=["backend_upload"]
            )

        if upload_result and hasattr(upload_result, 'url'):
            nuevo_post = Post(
                caption=caption,
                url=upload_result.url,
                file_type="photo",
                file_name=file.filename,
                user_id=str(user.id)  # Asociar al usuario logueado
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


@app.get("/feed", response_model=list[PostResponse])
async def get_feed(session: AsyncSession = Depends(get_async_session)):
    """Obtiene todos los posts del feed, ordenados del más reciente al más antiguo"""
    result = await session.execute(
        select(Post).order_by(Post.created_at.desc())
    )
    posts = result.scalars().all()
    return posts


@app.delete("/post/{post_id}")
async def delete_post(
    post_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Elimina un post de la base de datos por su ID.
    Solo el propietario del post puede eliminarlo.
    """
    # Buscar el post en la base de datos
    result = await session.execute(
        select(Post).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()

    # Si no existe, devolver error 404
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    # Verificar que el usuario es el propietario
    if post.user_id != str(user.id):
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este post")

    # Eliminar el post
    await session.delete(post)
    await session.commit()

    return {"message": "Post eliminado exitosamente", "id": post_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)