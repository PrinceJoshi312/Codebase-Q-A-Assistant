import subprocess
import time
import sys
import os

def start_backend():
    print("[*] Starting Backend (8000)...")
    # Using the verified start_backend.py logic
    return subprocess.Popen([sys.executable, "start_backend.py"], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT,
                            text=True)

def start_frontend():
    print("[*] Starting Frontend (3000)...")
    # Vite is inside the frontend folder, and we are already setting cwd="frontend"
    vite_path = os.path.join("node_modules", "vite", "bin", "vite.js")
    return subprocess.Popen(["node", vite_path], 
                            cwd="frontend",
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT,
                            text=True)

if __name__ == "__main__":
    # Ensure current dir is in path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    backend = start_backend()
    time.sleep(5) # Give backend time to init ML models
    frontend = start_frontend()
    
    print("[!] Both servers are starting. Keep this terminal open.")
    print("[!] Backend: http://localhost:8000")
    print("[!] Frontend: http://localhost:3000")
    
    try:
        while True:
            # Check if processes are still alive
            if backend.poll() is not None:
                print("\n[!] BACKEND CRASHED:")
                print(backend.stdout.read())
                break
            if frontend.poll() is not None:
                print("\n[!] FRONTEND CRASHED:")
                print(frontend.stdout.read())
                break
                
            # Optional: stream logs
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        backend.terminate()
        frontend.terminate()
