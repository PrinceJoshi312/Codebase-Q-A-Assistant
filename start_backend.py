import os
import sys
import subprocess

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
    import uvicorn
    print("[*] Clearing port 12345...")
    kill_port(12345)
    
    print("[*] Starting stable backend on http://127.0.0.1:12345")
    # No reload, explicit loopback IP
    uvicorn.run("src.api:app", host="127.0.0.1", port=12345, reload=False)
