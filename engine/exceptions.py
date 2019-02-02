from typing import NoReturn


class InvalidProjectName(Exception):
    def __init__(self, project_name: str, *args, **kwargs) -> NoReturn:
        msg = f"Invalid project name '{project_name}'"
        super(InvalidProjectName, self).__init__(msg, *args, **kwargs)
        self.project_name = project_name
