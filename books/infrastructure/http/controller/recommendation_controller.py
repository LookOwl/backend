from fastapi import APIRouter, Depends, HTTPException, Query
from books.infrastructure.http.dtos.book_dto import BookDto
from books.application.use_cases.get_query_recommendations import GetQueryRecommendations
from books.infrastructure.di import get_query_recommendations_uc

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/by-query")
async def recommend_by_query(
    query: str = Query(..., min_length=1, description="Search query text"),
    limit: int = Query(default=15, ge=1, le=50),
    get_recommendations: GetQueryRecommendations = Depends(
        get_query_recommendations_uc
    ),
):
    try:
        books = await get_recommendations.execute(
            query=query,
            num_recommendations=limit,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {"recommendations": [BookDto.to_dto(b) for b in books]}
