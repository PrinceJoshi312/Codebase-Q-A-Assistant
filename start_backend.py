import os
import sys
import subprocess
import uvicorn

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def kill_port(port):
    """Forcefully kill any process on the given port (Windows)."""
    try:
        output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
        for line in output.strip().split('\n'):
            parts = line.split()
            if len(parts) > 4:
                pid = parts[-1]
                print(f"[*] Killing process {pid} on port {port}")
                os.system(f'taskkill /F /PID {pid}')
    except:
        pass

if __name__ == "__main__":
    port = 8000
    print(f"[*] Clearing port {port}...")
    kill_port(port)
    
    print(f"[*] Starting Code Intelligence Backend on http://0.0.0.0:{port}")
    # Run the FastAPI app
    uvicorn.run("src.api:app", host="0.0.0.0", port=port, reload=False)
