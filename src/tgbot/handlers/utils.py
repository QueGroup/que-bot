import os

# TODO: Вынести в misc

def path_join(folder_path: str, file_name: str) -> str:
    return os.path.join(folder_path, file_name)
