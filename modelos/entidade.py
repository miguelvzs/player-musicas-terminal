"""Classe-mãe de todos os modelos (Aula 14: herança)."""


class Entidade:
    """Tudo o que é guardado no banco tem um id. Essa parte comum fica aqui.

    Artista, Album, Musica, Playlist e Reproducao herdam desta classe e chamam
    super().__init__(id) no próprio __init__.
    """

    def __init__(self, id=None):
        # Fracamente privado (um underscore): é só um aviso para não mexer de fora.
        # Quem define o id é o banco (AUTOINCREMENT); o repositório usa set_id().
        self._id = id

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id

    def esta_salva(self):
        """True se o objeto já foi gravado no banco (já tem id)."""
        return self._id is not None

    def __repr__(self):
        """Representação para o programador (debug). Ex.: <Artista id=3>."""
        return f"<{self.__class__.__name__} id={self._id}>"
