# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-alpine

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN  python -m pip install pipenv && pipenv install --system --deploy

# # Copy the requirements file to the working directory
# COPY requirements.txt .

# # Install Python dependencies from requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app
RUN mkdir -pv log

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "carbon_calculator.wsgi:application", "--log-level", "info", "--access-logfile", "-"]
