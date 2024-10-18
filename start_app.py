import uvicorn
from services.service_gateway.main import app as service_gateway_app

if __name__ == "__main__":
    uvicorn.run(service_gateway_app, host="0.0.0.0", port=8000)

