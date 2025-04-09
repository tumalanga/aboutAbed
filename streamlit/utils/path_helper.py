from pathlib import Path

def from_root(*path_parts) -> Path:
    """
    Return path from the root of the project, no matter where the current file is.
    Usage:
        from_root("assets", "logo.png") -> Path to /project_root/assets/logo.png
    """
    project_root = Path(__file__).resolve().parent.parent
    return project_root.joinpath(*path_parts)
