from engine.boards.GenericBoard import GenericBoard


# [feature] TODO: add filtering
class ManualBoard(object):
    """ Boart which accepts manual configuration files """

    def __init__(self, config_path: str=None, static: dict=None) -> None:
        if config_path is not None:
            super(ManualBoard, self).__init__(config_path)
        else:
            assert isinstance(static, dict)
            super(ManualBoard, self).__init__()
            self._static = static
        self.message = None
