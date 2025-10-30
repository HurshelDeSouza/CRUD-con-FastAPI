from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.models import Post, User, Tag
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])

# Type aliases
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo post",
    description="Crea un nuevo post asociado al usuario autenticado"
)
async def create_post(post_data: PostCreate, current_user: CurrentUser, db: DBSession):
    """
    Crear un nuevo post.
    
    - **title**: Título del post (1-200 caracteres)
    - **content**: Contenido del post
    - **tag_ids**: Lista opcional de IDs de tags existentes
    """
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        author_id=current_user.id
    )
    
    # Agregar tags si se proporcionaron
    if post_data.tag_ids:
        result = await db.execute(
            select(Tag).where(
                Tag.id.in_(post_data.tag_ids),
                Tag.is_deleted == False
            )
        )
        tags = result.scalars().all()
        if len(tags) != len(post_data.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tag IDs are invalid"
            )
        new_post.tags = list(tags)
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, ["tags"])
    
    return new_post


@router.get(
    "",
    response_model=List[PostResponse],
    summary="Listar posts",
    description="Obtiene lista paginada de posts activos"
)
async def get_posts(
    db: DBSession,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros")
):
    """
    Obtener lista de posts con paginación.
    
    - **skip**: Offset para paginación (default: 0)
    - **limit**: Límite de resultados (default: 10, max: 100)
    """
    result = await db.execute(
        select(Post)
        .where(Post.is_deleted == False)
        .options(selectinload(Post.tags))
        .order_by(Post.created_at.desc())  # Ordenar por más recientes
        .offset(skip)
        .limit(limit)
    )
    posts = result.scalars().all()
    return posts


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Obtener post",
    description="Obtiene un post específico por ID"
)
async def get_post(post_id: int, db: DBSession):
    result = await db.execute(
        select(Post)
        .where(Post.id == post_id, Post.is_deleted == False)
        .options(selectinload(Post.tags))
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="Actualizar post",
    description="Actualiza un post existente (solo el autor)"
)
async def update_post(post_id: int, post_data: PostUpdate, current_user: CurrentUser, db: DBSession):
    """
    Actualizar un post existente.
    
    Solo el autor del post puede actualizarlo.
    Todos los campos son opcionales.
    """
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.is_deleted == False)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Verificar autorización
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    # Actualizar solo campos proporcionados
    update_data = post_data.model_dump(exclude_unset=True)
    
    if "title" in update_data:
        post.title = update_data["title"]
    if "content" in update_data:
        post.content = update_data["content"]
    
    # Actualizar tags si se proporcionaron
    if "tag_ids" in update_data and update_data["tag_ids"] is not None:
        result = await db.execute(
            select(Tag).where(
                Tag.id.in_(update_data["tag_ids"]),
                Tag.is_deleted == False
            )
        )
        tags = result.scalars().all()
        if len(tags) != len(update_data["tag_ids"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tag IDs are invalid"
            )
        post.tags = list(tags)
    
    await db.commit()
    await db.refresh(post, ["tags"])
    
    return post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar post",
    description="Elimina un post (soft delete, solo el autor)"
)
async def delete_post(post_id: int, current_user: CurrentUser, db: DBSession):
    """
    Eliminar un post (soft delete).
    
    Solo el autor del post puede eliminarlo.
    El post se marca como eliminado pero no se borra de la base de datos.
    """
    result = await db.execute(
        select(Post).where(Post.id == post_id, Post.is_deleted == False)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Verificar autorización
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    # Soft delete
    post.soft_delete()
    await db.commit()
    
    return None
