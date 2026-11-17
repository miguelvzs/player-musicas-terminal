"""O Player: fila, tocar, pausar, próxima, anterior, aleatório e repetir."""

import os
import random
import sqlite3
import time

# Estados possíveis do player
PARADO = "parado"
TOCANDO = "tocando"
PAUSADO = "pausado"

# Modos de repetição, na ordem em que o botão "repetir" alterna
REPETIR_DESLIGADO = "desligado"
REPETIR_FILA = "fila"
REPETIR_FAIXA = "faixa"
MODOS_REPETIR = [REPETIR_DESLIGADO, REPETIR_FILA, REPETIR_FAIXA]

SEGUNDOS_PARA_VOLTAR_AO_INICIO = 3


class Player:
    """Controla a reprodução.

    Associações (instância como atributo, Aula 14):
    - saida: um objeto SaidaAudio (simulada, winsound ou pygame);
    - historico: o HistoricoRepositorio, para registrar cada música tocada.

    Como medimos o tempo sem threads: guardamos o instante em que a música
    começou (time.time()) e quanto já tinha tocado antes da última pausa.
    Posição atual = acumulado + (agora - inicio).
    """

    def __init__(self, saida, historico=None, pasta_base=""):
        self.saida = saida
        self.historico = historico
        self.pasta_base = pasta_base          # pasta usada para achar arquivos de caminho relativo
        self.__fila_original = []             # ordem "normal" da fila
        self.__fila = []                      # ordem que está valendo (pode estar embaralhada)
        self.__indice = 0                     # posição da música atual em __fila
        self.__nome_fila = ""
        self.__estado = PARADO
        self.__aleatorio = False
        self.__repetir = REPETIR_DESLIGADO
        self.__inicio = 0.0
        self.__acumulado = 0.0
        self.__com_som = False                # a faixa atual está saindo na caixa de som?
        self.__aviso = ""                     # recado para a tela mostrar

    def _agora(self):
        """Relógio do player. Os testes sobrescrevem este método para controlar o tempo."""
        return time.time()

    # ------------------------------------------------------------------
    # Consultas (get)
    # ------------------------------------------------------------------

    def get_estado(self):
        return self.__estado

    def get_fila(self):
        return list(self.__fila)

    def get_indice(self):
        return self.__indice

    def get_nome_fila(self):
        return self.__nome_fila

    def esta_aleatorio(self):
        return self.__aleatorio

    def get_repetir(self):
        return self.__repetir

    def tem_fila(self):
        return len(self.__fila) > 0

    def esta_com_som(self):
        return self.__com_som

    def musica_atual(self):
        if not self.__fila:
            return None
        return self.__fila[self.__indice]

    def proxima_musica(self):
        """Qual música vem depois da atual (só para mostrar na tela)."""
        if not self.__fila:
            return None
        if self.__repetir == REPETIR_FAIXA:
            return self.musica_atual()
        if self.__indice + 1 < len(self.__fila):
            return self.__fila[self.__indice + 1]
        if self.__repetir == REPETIR_FILA:
            return self.__fila[0]
        return None

    def posicao(self):
        """Quantos segundos da música atual já tocaram."""
        musica = self.musica_atual()
        if musica is None or self.__estado == PARADO:
            return 0.0
        if self.__estado == TOCANDO:
            posicao = self.__acumulado + (self._agora() - self.__inicio)
        else:
            posicao = self.__acumulado
        return min(posicao, musica.get_duracao())

    def progresso(self):
        """Fração tocada, de 0.0 a 1.0 (para a barra de progresso)."""
        musica = self.musica_atual()
        if musica is None:
            return 0.0
        return self.posicao() / musica.get_duracao()

    def pegar_aviso(self):
        """Devolve o recado pendente (e limpa)."""
        aviso = self.__aviso
        self.__aviso = ""
        return aviso

    def caminho_do_arquivo(self, musica):
        if not musica.tem_arquivo():
            return None
        # Se o caminho gravado já for absoluto, o os.path.join devolve ele mesmo.
        # normpath acerta as barras (/ ou \) para o sistema em uso.
        return os.path.normpath(os.path.join(self.pasta_base, musica.get_arquivo()))

    # ------------------------------------------------------------------
    # Fila
    # ------------------------------------------------------------------

    def carregar_fila(self, musicas, nome, comecar_em=0):
        """Troca a fila inteira. Não começa a tocar: quem chama decide."""
        self.parar()
        self.__fila_original = list(musicas)
        self.__fila = list(musicas)
        self.__nome_fila = nome
        self.__indice = 0
        if not self.__fila:
            return False
        if comecar_em < 0 or comecar_em >= len(self.__fila):
            comecar_em = 0
        if self.__aleatorio:
            self.__embaralhar(self.__fila_original[comecar_em])
        else:
            self.__indice = comecar_em
        return True

    def __embaralhar(self, primeira):
        """Embaralha a fila (random.shuffle), mantendo 'primeira' no começo."""
        restantes = list(self.__fila_original)
        restantes.remove(primeira)
        random.shuffle(restantes)
        self.__fila = [primeira] + restantes
        self.__indice = 0

    def remover_da_fila(self, musica_id):
        """Tira uma música da fila (usado quando ela é excluída do banco)."""
        atual = self.musica_atual()
        era_a_atual = atual is not None and atual.get_id() == musica_id
        if era_a_atual:
            self.parar()
        nova_original = []
        for musica in self.__fila_original:
            if musica.get_id() != musica_id:
                nova_original.append(musica)
        nova_fila = []
        for musica in self.__fila:
            if musica.get_id() != musica_id:
                nova_fila.append(musica)
        self.__fila_original = nova_original
        self.__fila = nova_fila
        if atual is not None and not era_a_atual:
            self.__indice = self.__fila.index(atual)
        elif self.__indice >= len(self.__fila):
            self.__indice = max(0, len(self.__fila) - 1)

    def substituir_na_fila(self, musica_nova):
        """Troca a versão antiga de uma música pela editada (mesmo id)."""
        for lista in (self.__fila_original, self.__fila):
            for i in range(len(lista)):
                if lista[i].get_id() == musica_nova.get_id():
                    lista[i] = musica_nova

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------

    def tocar(self):
        """Toca a música atual desde o começo e registra no histórico."""
        musica = self.musica_atual()
        if musica is None:
            self.__aviso = "A fila está vazia. Escolha o que tocar primeiro."
            return False
        self.__parar_som()
        self.__acumulado = 0.0
        self.__inicio = self._agora()
        self.__estado = TOCANDO
        self.__iniciar_som(musica)
        if self.historico is not None:
            try:
                self.historico.registrar(musica)
            except sqlite3.Error:
                self.__aviso = "Não foi possível registrar esta música no histórico."
        return True

    def pausar(self):
        if self.__estado != TOCANDO:
            return False
        self.__acumulado += self._agora() - self.__inicio
        self.__estado = PAUSADO
        if self.__com_som:
            try:
                self.saida.pausar()
            except Exception:
                self.__com_som = False
        return True

    def continuar(self):
        if self.__estado != PAUSADO:
            return False
        self.__inicio = self._agora()
        self.__estado = TOCANDO
        if self.__com_som:
            try:
                caminho = self.caminho_do_arquivo(self.musica_atual())
                self.saida.continuar(caminho, self.__acumulado)
            except Exception as erro:
                self.__com_som = False
                self.__aviso = f"O áudio não voltou ({erro}). Seguindo em modo simulado."
        return True

    def tocar_ou_pausar(self):
        """Botão único: parado -> toca; tocando -> pausa; pausado -> continua."""
        if self.__estado == TOCANDO:
            return self.pausar()
        if self.__estado == PAUSADO:
            return self.continuar()
        return self.tocar()

    def parar(self):
        self.__parar_som()
        self.__estado = PARADO
        self.__acumulado = 0.0

    def proxima(self):
        """Vai para a próxima faixa. Devolve False quando a fila acabou."""
        if not self.__fila:
            self.__aviso = "A fila está vazia."
            return False
        if self.__indice + 1 < len(self.__fila):
            self.__indice += 1
        elif self.__repetir == REPETIR_FILA:
            self.__indice = 0
        else:
            self.parar()
            self.__aviso = "Fim da fila."
            return False
        return self.tocar()

    def anterior(self):
        """Volta uma faixa. Se a atual já passou de 3 s, volta ao começo dela."""
        if not self.__fila:
            self.__aviso = "A fila está vazia."
            return False
        no_comeco_da_fila = self.__indice == 0 and self.__repetir != REPETIR_FILA
        if self.posicao() > SEGUNDOS_PARA_VOLTAR_AO_INICIO or no_comeco_da_fila:
            return self.tocar()
        if self.__indice > 0:
            self.__indice -= 1
        else:
            self.__indice = len(self.__fila) - 1
        return self.tocar()

    def pular_para(self, numero):
        """Toca a música de número 'numero' da fila (começando em 1)."""
        if numero < 1 or numero > len(self.__fila):
            return False
        self.__indice = numero - 1
        return self.tocar()

    def alternar_aleatorio(self):
        self.__aleatorio = not self.__aleatorio
        atual = self.musica_atual()
        if atual is not None:
            if self.__aleatorio:
                self.__embaralhar(atual)
            else:
                self.__fila = list(self.__fila_original)
                self.__indice = self.__fila.index(atual)
        return self.__aleatorio

    def alternar_repetir(self):
        """desligado -> fila -> faixa -> desligado..."""
        posicao = MODOS_REPETIR.index(self.__repetir)
        self.__repetir = MODOS_REPETIR[(posicao + 1) % len(MODOS_REPETIR)]
        return self.__repetir

    def atualizar(self):
        """Confere o relógio: se a música acabou, segue para a próxima.

        Sem threads, o player não "acorda" sozinho: a tela chama este método
        a cada interação e várias vezes por segundo no modo "ouvir".
        Devolve True se trocou de música.
        """
        musica = self.musica_atual()
        if self.__estado != TOCANDO or musica is None:
            return False
        if self.posicao() < musica.get_duracao():
            return False
        if self.__repetir == REPETIR_FAIXA:
            self.tocar()
        else:
            self.proxima()
        return True

    # ------------------------------------------------------------------
    # Som (métodos fortemente privados)
    # ------------------------------------------------------------------

    def __iniciar_som(self, musica):
        """Tenta tocar o arquivo. Se não der, a música segue em modo simulado."""
        self.__com_som = False
        caminho = self.caminho_do_arquivo(musica)
        if caminho is None:
            if self.saida.emite_som():
                self.__aviso = "Esta música não tem arquivo de áudio: tocando em modo simulado."
            return
        if not os.path.exists(caminho):
            self.__aviso = f"Arquivo não encontrado ({caminho}): tocando em modo simulado."
            return
        if not self.saida.suporta(caminho):
            if self.saida.emite_som():
                self.__aviso = f"A saída {self.saida} não toca este formato: modo simulado."
            return
        try:
            self.saida.tocar(caminho)
            self.__com_som = True
        except Exception as erro:
            self.__aviso = f"Não foi possível tocar o áudio ({erro}). Seguindo em modo simulado."

    def __parar_som(self):
        if self.__com_som:
            try:
                self.saida.parar()
            except Exception:
                pass
        self.__com_som = False
