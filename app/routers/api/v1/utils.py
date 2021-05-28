from . import v1

@utils_router.post("/test-email", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_active_superuser),
):
    """test emails server"""
    background_tasks.add_task(send_test_email, email_to=email_to)
    return {"msg": "Test email sent"}


@utils_router.post("/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(get_current_user)) -> Any:
    """test token"""
    return current_user


@utils_router.get("/lunar", response_model=schemas.Lunar)
def lunar(
    current_user: models.User = Depends(get_current_confirm_user),
) -> Any:
    """get current date in lunar"""

    lunar = Lunar.fromDate(datetime.now())
    return {
        "date": f"{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
        "ganzhi_year": lunar.getYearInGanZhi(),
        "ganzhi_month": lunar.getMonthInGanZhi(),
        "ganzhi_day": lunar.getDayInGanZhi(),
        "shengxiao": lunar.getYearShengXiao(),
    }
