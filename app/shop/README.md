# Running the Shop Service

To run the shop service, open a terminal (DOS) and use the following command from the top level directory:

```cmd
.venv\Scripts\python.exe -m uvicorn app.server.shop_service:app --reload

Swagger API documentation served here: http://127.0.0.1:8000/docs
