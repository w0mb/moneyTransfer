FROM python:3.11.9

WORKDIR /app

COPY requerments.txt requerments.txt
RUN pip install --no-cache-dir -r requerments.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]