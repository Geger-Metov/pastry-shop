from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.use_cases.leads import LeadInputError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(LeadInputError)
    async def lead_input_error(_: Request, exc: LeadInputError) -> JSONResponse:
        # тот же формат, что у ошибок валидации FastAPI: фронтенд разбирает их одинаково
        loc = ["body", exc.field] if exc.field else ["body"]
        detail = [{"loc": loc, "msg": str(exc), "type": "value_error"}]
        return JSONResponse(status_code=422, content={"detail": detail})
