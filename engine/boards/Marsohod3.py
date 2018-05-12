from engine.boards.GenericBoard import GenericBoard
from engine.utils.log import LOGGER


class Marsohod3(GenericBoard):
    """ Marsohod3 configs generator """

    def __init__(self) -> None:
        super(Marsohod3, self).__init__(self.__class__.__name__)
        self.message = "THIS CLASS IS UNDER DEVELOPMENT: NO WARRANTY PROVIDED!"
        LOGGER.warning(self.message)
