import os
import shutil
import git
from pathlib import Path
from typing import List, Optional

class RepoIngestor:
    """Handles GitHub repository cloning and file filtering for the Codebase Q&A Assistant."""

    def __init__(self, temp_dir: str = "./_repo_temp"):
        self.temp_dir = Path(temp_dir)
        self.exclude_dirs = {
            '.git', 'node_modules', 'dist', '__pycache__', 
            '.venv', 'venv', 'target', 'build', '.idea', '.vscode'
        }
        self.exclude_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', 
            '.tar', '.gz', '.mp4', '.mov', '.exe', '.dll', '.so'
        }

    def clone_repository(self, repo_url: str, branch: Optional[str] = None) -> Path:
        """Clones a GitHub repository to the local temp directory."""
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = self.temp_dir / repo_name

        if repo_path.exists():
            print(f"[*] Repository {repo_name} already exists. Removing for fresh clone...")
            shutil.rmtree(repo_path)

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
            # In-place modification to skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() not in self.exclude_extensions:
                    code_files.append(file_path)
        
        print(f"[*] Found {len(code_files)} relevant code files in {repo_path}.")
        return code_files

    def cleanup(self):
        """Removes the temporary repository folder."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
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
