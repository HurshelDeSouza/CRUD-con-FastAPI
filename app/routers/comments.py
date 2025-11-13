from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import Comment, User, Post
from app.schemas.comment import CommentCreate, CommentResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])

# Type aliases
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CommentId = Annotated[int, Path(gt=0, description="ID del comentario")]
PostId = Annotated[int, Path(gt=0, description="ID del post")]
Skip = Annotated[int, Query(ge=0, le=1000, description="Número de registros a saltar para paginación")]
Limit = Annotated[int, Query(ge=1, le=100, description="Número máximo de registros a retornar")]


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear comentario",
    description="Crea un nuevo comentario en un post"
)
async def create_comment(comment_data: CommentCreate, current_user: CurrentUser, db: DBSession):
    # Verificar que el post existe
    result = await db.execute(
        select(Post).where(Post.id == comment_data.post_id, Post.is_deleted == False)
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    new_comment = Comment(
        content=comment_data.content,
        post_id=comment_data.post_id,
        author_id=current_user.id
    )
    
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    
    return new_comment


@router.get(
    "/post/{post_id}",
    response_model=List[CommentResponse],
    summary="Listar comentarios de un post",
    description="Obtiene todos los comentarios de un post específico"
)
async def get_comments_by_post(
    post_id: PostId,
    db: DBSession,
    skip: Skip = 0,
    limit: Limit = 10
):
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id, Comment.is_deleted == False)
        .offset(skip)
        .limit(limit)
    )
    comments = result.scalars().all()
    return comments


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar comentario",
    description="Elimina un comentario (soft delete, solo el autor)"
)
async def delete_comment(comment_id: CommentId, current_user: CurrentUser, db: DBSession):
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.is_deleted == False)
    )
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Verificar que el usuario sea el autor
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    # Soft delete
    comment.soft_delete()
    await db.commit()
    
    return None
