@router.post("/run-scrape")
async def run_scrape_manually(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):