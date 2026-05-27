FROM python:3.14.4-bookworm

# set working directory
WORKDIR /app

# install uv
RUN pip install uv==0.8.13

# copy dependency files first
COPY pyproject.toml uv.lock .python-version ./

# install dependencies
RUN uv sync

# copy source code
COPY . .

# expose container port
EXPOSE 8000

# run frontend server
ENTRYPOINT ["uv", "run", "uvicorn"]

CMD ["src.app:app", "--host", "0.0.0.0", "--port", "8000"]