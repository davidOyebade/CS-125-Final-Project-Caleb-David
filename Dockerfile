# Westmont College CS 125 Database Design Fall 2025
# Final Project
# Assistant Professor Mike Ryu
# Caleb Song & David Oyebade
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]