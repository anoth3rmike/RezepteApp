# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

WORKDIR /app



# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1



COPY . /app
#COPY docker-entrypoint.sh docker-entrypoint.sh
#COPY app.py app.py
#COPY config.py config.py
#COPY requirements.txt requirements.txt


# Install pip requirements
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt



RUN chmod a+x ./ls.sh

EXPOSE 5000
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser
ENTRYPOINT ["./ls.sh"]
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
