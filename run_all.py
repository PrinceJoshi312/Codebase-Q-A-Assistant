import subprocess
import time
import sys
import os
import webbrowser

def start_backend():
    print("[*] Launching Code Intelligence Engine (Port 8000)...")
    return subprocess.Popen([sys.executable, "start_backend.py"], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT,
                            text=True)

def start_frontend():
    print("[*] Launching Neural Interface (Port 5173)...")
    # Vite default port is 5173
    # Use shell=True on Windows to find npx in PATH
    return subprocess.Popen(["npx", "vite"], 
                            cwd="frontend",
                            shell=True,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT,
                            text=True)

if __name__ == "__main__":
    # Ensure current dir is in path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    os.chdir(current_dir)
    
    backend = start_backend()
    
    print("[!] Wait... Initializing Neural Engine...")
    time.sleep(6) # Give Gemini & Vector DB time to init
    
    frontend = start_frontend()
    
    print("\n" + "="*50)
    print("🚀 CODEBASE Q&A ASSISTANT IS LIVE")
    print("="*50)
    print("🧠 Backend: http://localhost:8000")
    print("🖥️  Frontend: http://localhost:5173")
    print("="*50)
    print("[!] Keep this terminal open to maintain the link.")
    
    # Auto-launch browser
    time.sleep(2)
    webbrowser.open("http://localhost:5173")
    
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
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down Neural Bridge...")
        backend.terminate()
        frontend.terminate()
        print("[*] Done.")
