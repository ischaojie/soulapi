@v1.post("/", response_model=schemas.Word)
def create_word(
    *,
    db: Session = Depends(get_db),
    word: schemas.WordCreate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """create word, but only superuser can create."""

    word_db = crud.word.get_by_origin(db, origin=word.origin)
    if word_db:
        raise HTTPException(status_code=400, detail="Word already exists")
    return crud.word.create(db, obj=word)


@v1.delete("/{wid}", response_model=schemas.Word)
def delete_word(
    *,
    db: Session = Depends(get_db),
    wid: int,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """delete an word"""
    word_in_db = crud.word.get(db, wid)
    if not word_in_db:
        raise HTTPException(status_code=404, detail="word not found")
    word = crud.word.remove(db, id=wid)
    return word


@v1.get("/daily", response_model=schemas.Word)
def read_word_daily(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_db),
    current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """read word random every day"""

    db_word = crud.word.get_word_daily(db, redis)
    if not db_word:
        raise HTTPException(status_code=404, detail="word not found")
    return db_word


@v1.get("/{wid}", response_model=schemas.Word)
def read_word(
    *,
    db: Session = Depends(get_db),
    wid: int,
    current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """get word by id"""
    db_word = crud.psychology.get(db, wid)
    if not db_word:
        raise HTTPException(status_code=404, detail="Word not found")
    return db_word