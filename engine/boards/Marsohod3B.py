from engine.boards.GenericBoard import GenericBoard
from engine.utils.log import LOGGER


class Marsohod3B(GenericBoard):
    """ Marsohod3Bis configs generator """

    def __init__(self) -> None:
        super(Marsohod3B, self).__init__(self.__class__.__name__)
        self.message = "THIS CLASS IS UNDER DEVELOPMENT: NO WARRANTY PROVIDED!"
        LOGGER.warning(self.message)
