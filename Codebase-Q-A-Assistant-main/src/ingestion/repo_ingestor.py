import os
import shutil
import git
from pathlib import Path
from typing import List, Optional

class RepoIngestor:
    """Handles GitHub repository cloning and file filtering for the Codebase Q&A Assistant."""

    # NEW: Safety constraints for indexing to prevent crashes and memory issues
    ALLOWED_CODE_EXTENSIONS = [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", 
        ".cpp", ".c", ".md", ".json", ".yaml", ".yml", ".txt"
    ]

    IGNORED_EXTENSIONS = [
        ".csv", ".pkl", ".pickle", ".ipynb", ".h5", ".pt", ".onnx", 
        ".parquet", ".feather"
    ]

    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

    def __init__(self, temp_dir: str = "./_repo_temp"):
        self.temp_dir = Path(temp_dir)
        self.exclude_dirs = {
            '.git', 'node_modules', 'dist', '__pycache__', 
            '.venv', 'venv', 'target', 'build', '.idea', '.vscode'
        }
        # Retained for general filtering, but ALLOWED_CODE_EXTENSIONS takes precedence
        self.exclude_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', 
            '.tar', '.gz', '.mp4', '.mov', '.exe', '.dll', '.so'
        }

    def _on_rm_error(self, func, path, exc_info):
        """Error handler for shutil.rmtree to handle read-only files on Windows."""
        import stat
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def clone_repository(self, repo_url: str, branch: Optional[str] = None) -> Path:
        """Clones a GitHub repository to the local temp directory."""
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = self.temp_dir / repo_name

        if repo_path.exists():
            print(f"[*] Repository {repo_name} already exists. Removing for fresh clone...")
            shutil.rmtree(repo_path, onerror=self._on_rm_error)

        print(f"[*] Cloning {repo_url} into {repo_path}...")
        try:
            repo = git.Repo.clone_from(repo_url, repo_path, branch=branch)
            print(f"[*] Successfully cloned {repo_name}.")
            return repo_path
        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")

    def get_codebase_files(self, repo_path: Path) -> List[Path]:
        """Traverses the repository and returns a filtered list of code files."""
        code_files = []
        for root, dirs, files in os.walk(repo_path):
            # In-place modification to skip excluded directories (Step 6.1, 6.2)
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                file_path = Path(root) / file
                suffix = file_path.suffix.lower()

                # Step 6.4: Ignore files listed in IGNORED_EXTENSIONS
                if suffix in self.IGNORED_EXTENSIONS:
                    if suffix in [".csv", ".parquet", ".feather"]:
                        print(f"[!] Skipping dataset file: {file}")
                    elif suffix in [".pkl", ".pickle", ".h5", ".pt", ".onnx"]:
                        print(f"[!] Skipping binary file: {file}")
                    else:
                        print(f"[!] Skipping ignored extension: {file}")
                    continue

                # Step 6.3: Ignore files not in ALLOWED_CODE_EXTENSIONS
                if suffix not in self.ALLOWED_CODE_EXTENSIONS:
                    # Silently skip common non-code extensions if not explicitly in ALLOWED
                    continue

                # Step 6.5: Ignore files larger than MAX_FILE_SIZE
                try:
                    file_size = file_path.stat().st_size
                    if file_size > self.MAX_FILE_SIZE:
                        print(f"[!] Skipping large file: {file} (size exceeds limit)")
                        continue
                except OSError:
                    # Skip files that can't be accessed
                    continue

                code_files.append(file_path)
        
        print(f"[*] Found {len(code_files)} relevant code files in {repo_path}.")
        return code_files

    def get_repo_structure(self, repo_path: Path) -> str:
        """Recursively scans the repository and returns a formatted directory tree."""
        tree = []
        repo_path = Path(repo_path)
        
        # Exclude common noisy directories
        noisy_dirs = {'.git', 'node_modules', '__pycache__', 'venv', '.venv'}
        
        def _build_tree(current_path: Path, prefix: str = ""):
            # Get list of entries, filtered and sorted
            entries = sorted(
                [e for e in current_path.iterdir() if e.name not in noisy_dirs and e.name not in self.exclude_dirs],
                key=lambda x: (not x.is_dir(), x.name.lower())
            )
            
            for i, entry in enumerate(entries):
                is_last = (i == len(entries) - 1)
                connector = "└ " if is_last else "├ "
                
                if entry.is_dir():
                    tree.append(f"{prefix}{connector}{entry.name}/")
                    new_prefix = prefix + ("  " if is_last else "│ ")
                    _build_tree(entry, new_prefix)
                else:
                    tree.append(f"{prefix}{connector}{entry.name}")

        tree.append(f"{repo_path.name}/")
        _build_tree(repo_path)
        return "\n".join(tree)

    def detect_entry_point(self, repo_path: Path) -> str:
        """Detects likely entry point files in the repository."""
        # Candidates for entry points
        candidates = ["main.py", "app.py", "server.py", "index.js", "__main__.py", "run.py", "manage.py"]
        
        found = []
        for root, dirs, files in os.walk(repo_path):
            # Skip noisy dirs
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs and d not in {'.git', 'node_modules'}]
            
            for file in files:
                if file.lower() in candidates:
                    # Return relative path
                    rel_path = Path(root).relative_to(repo_path) / file
                    found.append(str(rel_path))
        
        if found:
            # Prioritize root level if multiple exist
            found.sort(key=lambda x: x.count(os.sep))
            return found[0]
        
        return "None detected"

    def cleanup(self):
        """Removes the temporary repository folder."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, onerror=self._on_rm_error)
            print("[*] Cleanup: Removed temporary repository folder.")

if __name__ == "__main__":
    # Quick test for US.1 (Cloning a GitHub URL)
    ingestor = RepoIngestor()
    test_repo = "https://github.com/django/django" # Sample large public repo
    try:
        path = ingestor.clone_repository(test_repo, branch="main")
        files = ingestor.get_codebase_files(path)
        # ingestor.cleanup() # Keep for now to verify
    except Exception as e:
        print(f"[!] Error during test: {e}")
