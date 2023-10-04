import uvicorn
import os

if __name__ == "__main__":
    uvicorn.run("main:app", host=os.environ['LISTEN_ADDR'], port=int(os.environ['LISTEN_PORT']), reload=True)
