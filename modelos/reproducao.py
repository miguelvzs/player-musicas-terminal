"""Modelo Reproducao (uma linha do histórico)."""

from datetime import datetime

from modelos.entidade import Entidade

FORMATO_BANCO = "%Y-%m-%d %H:%M:%S"     # como a data fica gravada no banco
FORMATO_TELA = "%d/%m/%Y %H:%M"         # como a data aparece para o usuário


class Reproducao(Entidade):
    """Registro de que uma música tocou em uma data e hora."""

    def __init__(self, musica, tocada_em=None, id=None):
        super().__init__(id)
        if musica is None:
            raise ValueError("A reprodução precisa de uma música.")
        self.musica = musica
        if tocada_em is None:
            # Valor padrão: agora (módulo datetime, Aula 11).
            tocada_em = datetime.now().strftime(FORMATO_BANCO)
        self.tocada_em = tocada_em

    def data_formatada(self):
        """Converte "2026-11-16 21:05:00" em "16/11/2026 21:05"."""
        try:
            data = datetime.strptime(self.tocada_em, FORMATO_BANCO)
        except ValueError:
            return self.tocada_em
        return data.strftime(FORMATO_TELA)

    def __str__(self):
        return f"{self.data_formatada()}  {self.musica}"
