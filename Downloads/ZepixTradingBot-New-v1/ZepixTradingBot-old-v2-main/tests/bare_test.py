import os,sys,traceback,asyncio
from fastapi import FastAPI
import uvicorn
orig_exit = sys.exit

def logged_exit(code=0):
    print(f"[EXIT-CALL] sys.exit({code}) stack:")
    traceback.print_stack()
    orig_exit(code)
sys.exit = logged_exit
app = FastAPI()
@app.get('/ping')
async def ping():
    return {'ok': True}
if __name__=='__main__':
    print('[TEST] Starting bare uvicorn server')
    uvicorn.run(app, host='0.0.0.0', port=5020, log_level='debug', access_log=False)
