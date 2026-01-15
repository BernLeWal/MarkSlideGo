""" Utility functions for file operations """
import os
import zipfile


def remove_dir_recursively(path:str) -> None:
    """ Remove a directory and all its contents recursively """
    if os.path.exists(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)


def remove_file_if_exists(filepath:str) -> None:
    """ Remove a file if it exists """
    if os.path.exists(filepath):
        os.remove(filepath)


def zip_current_directory(extension:str = ".zip") -> None:
    archive_filename = os.path.basename(os.getcwd()) + extension
    zip_path = os.path.join("..", archive_filename)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, ".")
                zipf.write(file_path, arcname)


