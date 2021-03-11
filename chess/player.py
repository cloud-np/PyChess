"""Player module has all the information and connections to dbs to get the player's info."""

class Player:
    """Keep info about the player."""

    def __init__(self, id_, is_human=True):
        """Info for the player's.

        Parameters
        ----------
        id_ : int
            An identifier that is useful at runtime.
            Later on this will be the id from the db.
        is_human : bool
            Shows if the player is human or not, by default True
        """        
        self.id = id_
        self.is_pc = is_human