from constants.environment_variables import LISTEN_ADDR, LISTEN_PORT
import uvicorn
import os

if __name__ == "__main__":
    uvicorn.run("main:app", host=LISTEN_ADDR, port=int(LISTEN_PORT), reload=True)
