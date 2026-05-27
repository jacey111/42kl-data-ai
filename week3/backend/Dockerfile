FROM python:3.14.4-bookworm

WORKDIR /app

RUN pip install uv==0.8.13

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync

COPY . .

EXPOSE 8001

ENTRYPOINT ["uv", "run", "uvicorn"]

CMD ["src.app:app", "--host", "0.0.0.0", "--port", "8001"]