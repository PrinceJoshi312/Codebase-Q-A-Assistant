import subprocess
import time
import sys
import os

def kill_port(port):
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

def start_backend():
    print("[*] Starting Backend on Port 12345...")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    # Log to file to avoid pipe deadlock in background
    with open("backend.log", "w") as f:
        return subprocess.Popen([sys.executable, "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "12345"], 
                                env=env,
                                stdout=f, 
                                stderr=f,
                                text=True)

def start_frontend():
    print("[*] Starting Frontend on Port 3000...")
    vite_path = os.path.join("node_modules", "vite", "bin", "vite.js")
    with open("frontend.log", "w") as f:
        return subprocess.Popen(["node", vite_path], 
                                cwd="frontend",
                                stdout=f, 
                                stderr=f,
                                text=True)

if __name__ == "__main__":
    kill_port(12345)
    kill_port(3000)
    
    backend = start_backend()
    time.sleep(5) 
    frontend = start_frontend()
    
    print("\n[!] SUCCESS: Servers are starting.")
    print("[!] Backend: http://localhost:12345")
    print("[!] Frontend: http://localhost:3000")
    
    try:
        while True:
            if backend.poll() is not None:
                print("\n[!] BACKEND CRASHED. Check backend.log")
                break
            if frontend.poll() is not None:
                print("\n[!] FRONTEND CRASHED. Check frontend.log")
                break
            time.sleep(5)
    except KeyboardInterrupt:
        backend.terminate()
        frontend.terminate()
