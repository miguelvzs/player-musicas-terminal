"""Repertório em 16 bits: clássicos em domínio público e temas de jogo originais.

Direitos autorais: só entram obras de compositores que morreram há mais de 70
anos (domínio público no Brasil, Lei 9.610/98, art. 41) e temas compostos para
este projeto. Os arranjos são escritos nota por nota aqui e tocados pelo
sintetizador de audio/chiptune.py. Nenhuma gravação foi usada.

Cada música tem canais, como nos chips de som dos videogames:
pulso (melodia), triângulo (baixo), bateria e, às vezes, um pulso fino de arpejo.
"""

from audio.chiptune import Canal, Trilha

ARTISTA = "Orquestra 16 Bits"
CLASSICOS = "Clássicos em 16 Bits"
JOGO = "Jogo Imaginário"

ARTISTAS = [(ARTISTA, "Brasil")]

# (título, ano, gênero, artista)
ALBUNS = [
    (CLASSICOS, 2026, "Chiptune 16 bits", ARTISTA),
    (JOGO, 2026, "Trilha de jogo", ARTISTA),
]


# ---------- pequenas funções para escrever os arranjos ----------

def oitava(nota, deslocamento=1):
    """oitava("E2") -> "E3"."""
    return f"{nota[:-1]}{int(nota[-1]) + deslocamento}"


def oitavas(nota, tempos):
    """Baixo de videogame: a nota e a oitava de cima, em colcheias."""
    return " ".join(f"{nota}:0.5 {oitava(nota)}:0.5" for _ in range(tempos))


def arpejo(notas, tempos):
    """Acorde tocado nota a nota, em semicolcheias (o "brilho" dos jogos de 16 bits)."""
    lista = notas.split()
    return " ".join(f"{lista[i % len(lista)]}:0.25" for i in range(tempos * 4))


def transpor(texto, deslocamento):
    """Sobe ou desce todas as notas do texto em oitavas (pausas ficam iguais)."""
    partes = []
    for item in texto.split():
        nome, tempos = item.split(":")
        if nome != "R":
            nome = oitava(nome, deslocamento)
        partes.append(f"{nome}:{tempos}")
    return " ".join(partes)


def canal(timbre, notas, volume=1.0, largura=0.5):
    return {"timbre": timbre, "notas": notas, "volume": volume, "largura": largura}


# ---------- Korobeiniki (folclore russo, séc. XIX) ----------
# A melodia popular que ficou famosa no Tetris.

KOROBEINIKI_A = (
    "E5:1 B4:0.5 C5:0.5 D5:1 C5:0.5 B4:0.5 "
    "A4:1 A4:0.5 C5:0.5 E5:1 D5:0.5 C5:0.5 "
    "B4:1.5 C5:0.5 D5:1 E5:1 "
    "C5:1 A4:1 A4:2 "
    "R:0.5 D5:1 F5:0.5 A5:1 G5:0.5 F5:0.5 "
    "E5:1.5 C5:0.5 E5:1 D5:0.5 C5:0.5 "
    "B4:1 B4:0.5 C5:0.5 D5:1 E5:1 "
    "C5:1 A4:1 A4:2"
)
KOROBEINIKI_B = (
    "E5:2 C5:2 D5:2 B4:2 C5:2 A4:2 G#4:2 B4:2 "
    "E5:2 C5:2 D5:2 B4:2 C5:1 E5:1 A5:2 G#5:4"
)
KOROBEINIKI_BAIXO = " ".join([
    oitavas("E2", 4), oitavas("A2", 4), oitavas("G#2", 2), oitavas("E2", 2), oitavas("A2", 4),
    oitavas("D2", 4), oitavas("C2", 4), oitavas("B1", 2), oitavas("E2", 2), oitavas("A2", 4),
] + [oitavas("A2", 4), oitavas("E2", 4)] * 4)

# ---------- Ode à Alegria (Beethoven, 9ª Sinfonia, 1824) ----------

ODE = (
    "F#5:1 F#5:1 G5:1 A5:1 A5:1 G5:1 F#5:1 E5:1 D5:1 D5:1 E5:1 F#5:1 F#5:1.5 E5:0.5 E5:2 "
    "F#5:1 F#5:1 G5:1 A5:1 A5:1 G5:1 F#5:1 E5:1 D5:1 D5:1 E5:1 F#5:1 E5:1.5 D5:0.5 D5:2 "
    "E5:1 E5:1 F#5:1 D5:1 E5:1 F#5:0.5 G5:0.5 F#5:1 D5:1 "
    "E5:1 F#5:0.5 G5:0.5 F#5:1 E5:1 D5:1 E5:1 A4:2 "
    "F#5:1 F#5:1 G5:1 A5:1 A5:1 G5:1 F#5:1 E5:1 D5:1 D5:1 E5:1 F#5:1 E5:1.5 D5:0.5 D5:2"
)
_D = "D2:1 A2:1 D3:1 A2:1"
_A = "A1:1 E2:1 A2:1 E2:1"
ODE_BAIXO = " ".join([_D, _A, _D, _A, _D, _A, _D, _D, _A, _D, _A, _A, _D, _A, _D, _D])

# ---------- Na Gruta do Rei da Montanha (Grieg, Peer Gynt, 1875) ----------
# A cada volta fica mais rápida, como no original.

REI_FRASE = (
    "A3:0.5 B3:0.5 C4:0.5 D4:0.5 E4:0.5 C4:0.5 E4:1 "
    "D#4:0.5 B3:0.5 D#4:1 D4:0.5 Bb3:0.5 D4:1 "
    "A3:0.5 B3:0.5 C4:0.5 D4:0.5 E4:0.5 C4:0.5 E4:0.5 A4:0.5 "
    "G4:0.5 E4:0.5 C4:0.5 E4:0.5 G4:2"
)
REI_BAIXO = " ".join(["A2:0.5 R:0.5"] * 4 + ["B2:0.5 R:0.5"] * 2 + ["Bb2:0.5 R:0.5"] * 2
                     + ["A2:0.5 R:0.5"] * 4 + ["C3:0.5 R:0.5"] * 2 + ["E2:0.5 R:0.5"] * 2)

# ---------- Can-can (Offenbach, Orfeu no Inferno, 1858) ----------

CANCAN = (
    "C5:1 D5:0.5 F5:0.5 E5:0.5 D5:0.5 G5:1 G5:1 G5:0.5 A5:0.5 E5:0.5 F5:0.5 D5:1 D5:1 "
    "D5:0.5 F5:0.5 E5:0.5 D5:0.5 C5:0.5 C6:0.5 B5:0.5 A5:0.5 G5:0.5 F5:0.5 E5:0.5 D5:0.5 C5:1"
)
_C = "C3:0.5 G3:0.5 E3:0.5 G3:0.5"
_G = "G2:0.5 D3:0.5 B2:0.5 D3:0.5"
CANCAN_BAIXO = " ".join([_C, _G, _G, _G, _G, _C, _G, _C])

# ---------- Para Elisa (Beethoven, 1810) ----------

ELISA = (
    "E5:0.25 D#5:0.25 "
    "E5:0.25 D#5:0.25 E5:0.25 B4:0.25 D5:0.25 C5:0.25 "
    "A4:0.5 R:0.25 C4:0.25 E4:0.25 A4:0.25 "
    "B4:0.5 R:0.25 E4:0.25 G#4:0.25 B4:0.25 "
    "C5:0.5 R:0.25 E4:0.25 E5:0.25 D#5:0.25 "
    "E5:0.25 D#5:0.25 E5:0.25 B4:0.25 D5:0.25 C5:0.25 "
    "A4:0.5 R:0.25 C4:0.25 E4:0.25 A4:0.25 "
    "B4:0.5 R:0.25 E4:0.25 C5:0.25 B4:0.25 "
    "A4:1 R:0.5"
)
_LA = "A2:0.25 E3:0.25 A3:0.25 R:0.75"
_MI = "E2:0.25 E3:0.25 G#3:0.25 R:0.75"
ELISA_BAIXO = " ".join(["R:0.5", "R:1.5", _LA, _MI, _LA, "R:1.5", _LA, _MI, _LA])

# ---------- Pequena Serenata Noturna (Mozart, 1787) ----------

SERENATA = (
    "G5:1 R:0.5 D5:0.5 G5:1 R:0.5 D5:0.5 "
    "G5:0.5 D5:0.5 G5:0.5 B5:0.5 D6:2 "
    "C6:1 R:0.5 A5:0.5 C6:1 R:0.5 A5:0.5 "
    "C6:0.5 A5:0.5 F#5:0.5 A5:0.5 D5:2"
)
SERENATA_BAIXO = (
    "G2:1 R:0.5 D2:0.5 G2:1 R:0.5 D2:0.5 "
    "G2:0.5 B2:0.5 D3:0.5 B2:0.5 G2:0.5 B2:0.5 D3:0.5 B2:0.5 "
    "C3:1 R:0.5 A2:0.5 C3:1 R:0.5 A2:0.5 "
    "D2:0.5 F#2:0.5 A2:0.5 F#2:0.5 D2:0.5 F#2:0.5 A2:0.5 C3:0.5"
)

# ---------- Assim Falou Zaratustra (Richard Strauss, 1896) ----------
# A abertura que ficou famosa no filme 2001: Uma Odisseia no Espaço.

ZARATUSTRA = (
    "C4:2 G4:2 C5:2 E5:0.5 Eb5:3.5 R:2 "
    "C4:2 G4:2 C5:2 Eb5:0.5 E5:3.5 R:2 "
    "C4:2 G4:2 C5:2 E5:0.5 F5:0.5 G5:1 A5:1 B5:1 C6:6"
)
_TIMPANO = "C2:6 R:4 " + " ".join(["C2:0.25 G1:0.25"] * 4)
ZARATUSTRA_BAIXO = f"{_TIMPANO} {_TIMPANO} C2:6 F2:2 G2:2 C2:6"

# ---------- Temas originais de um jogo imaginário (compostos para este projeto) ----------

TITULO = (
    "C5:1 G4:0.5 C5:0.5 E5:1 G5:1 F5:0.5 E5:0.5 D5:0.5 E5:0.5 C5:2 "
    "A4:1 C5:0.5 F5:0.5 A5:1 G5:1 F5:0.5 E5:0.5 D5:0.5 C5:0.5 D5:2 "
    "C5:1 G4:0.5 C5:0.5 E5:1 G5:1 C6:1 B5:0.5 A5:0.5 G5:1 E5:1 "
    "F5:1 A5:0.5 G5:0.5 F5:0.5 E5:0.5 D5:0.5 B4:0.5 C5:4"
)
TITULO_BAIXO = " ".join([oitavas("C2", 4), oitavas("C2", 4), oitavas("F2", 4), oitavas("G2", 4),
                         oitavas("C2", 4), oitavas("A2", 4), oitavas("F2", 2), oitavas("G2", 2),
                         oitavas("C2", 4)])
TITULO_ARPEJO = " ".join([arpejo("C4 E4 G4 C5", 4), arpejo("C4 E4 G4 C5", 4),
                          arpejo("F4 A4 C5 F5", 4), arpejo("G4 B4 D5 G5", 4),
                          arpejo("C4 E4 G4 C5", 4), arpejo("A4 C5 E5 A5", 4),
                          arpejo("F4 A4 C5 F5", 2), arpejo("G4 B4 D5 G5", 2),
                          arpejo("C4 E4 G4 C5", 4)])

FASE1 = (
    "F5:0.5 F5:0.5 R:0.5 A5:0.5 R:0.5 C6:0.5 A5:1 "
    "G5:0.5 F5:0.5 R:0.5 G5:0.5 A5:1 F5:1 "
    "Bb5:0.5 Bb5:0.5 R:0.5 A5:0.5 R:0.5 G5:0.5 F5:1 "
    "E5:0.5 F5:0.5 R:0.5 G5:0.5 C5:2 "
    "F5:0.5 F5:0.5 R:0.5 A5:0.5 R:0.5 C6:0.5 A5:1 "
    "D6:0.5 C6:0.5 R:0.5 A5:0.5 F5:1 D5:1 "
    "Bb4:0.5 D5:0.5 F5:0.5 Bb5:0.5 A5:0.5 F5:0.5 G5:0.5 E5:0.5 "
    "F5:4"
)
FASE1_BAIXO = " ".join([oitavas("F2", 4), oitavas("F2", 4), oitavas("Bb1", 4), oitavas("C2", 4),
                        oitavas("F2", 4), oitavas("D2", 4), oitavas("Bb1", 2), oitavas("C2", 2),
                        oitavas("F2", 4)])
FASE1_ARPEJO = " ".join([arpejo("F4 A4 C5", 4), arpejo("F4 A4 C5", 4), arpejo("Bb3 D4 F4", 4),
                         arpejo("C4 E4 G4", 4), arpejo("F4 A4 C5", 4), arpejo("D4 F4 A4", 4),
                         arpejo("Bb3 D4 F4", 2), arpejo("C4 E4 G4", 2), arpejo("F4 A4 C5", 4)])

CHEFAO = (
    "D5:0.5 D5:0.5 F5:0.5 D5:0.5 G#5:0.5 D5:0.5 A5:1 "
    "D5:0.5 D5:0.5 F5:0.5 D5:0.5 C6:0.5 Bb5:0.5 A5:1 "
    "D5:0.5 D5:0.5 F5:0.5 D5:0.5 G#5:0.5 D5:0.5 A5:0.5 Bb5:0.5 "
    "A5:0.5 G5:0.5 F5:0.5 E5:0.5 D5:2 "
    "Bb4:0.5 Bb4:0.5 D5:0.5 Bb4:0.5 F5:1 E5:1 "
    "A4:0.5 A4:0.5 C#5:0.5 A4:0.5 E5:1 G5:1 "
    "D5:0.5 F5:0.5 A5:0.5 D6:0.5 C#6:1 A5:1 "
    "D6:4"
)
CHEFAO_BAIXO = " ".join([oitavas("D2", 4)] * 4 + [oitavas("Bb1", 4), oitavas("A1", 4),
                                                  oitavas("D2", 2), oitavas("A1", 2),
                                                  oitavas("D2", 4)])

VITORIA = (
    "G4:0.5 C5:0.5 E5:0.5 G5:0.5 C6:1 G5:0.5 C6:0.5 E6:2 R:1 "
    "D6:0.5 E6:0.5 F6:0.5 D6:0.5 E6:0.5 C6:0.5 D6:0.5 B5:0.5 C6:4 R:1"
)
VITORIA_BAIXO = "C3:1 C3:1 E3:1 G3:1 C3:2 R:1 G2:1 G2:1 F2:1 G2:2 C3:4"

ROCK = "K:1 H:0.5 H:0.5 S:1 H:0.5 H:0.5"

# Cada música: título, álbum, faixa, arquivo, andamento e os canais.
TRILHAS = [
    {"titulo": "Korobeiniki (folclore russo)", "album": CLASSICOS, "faixa": 1,
     "arquivo": "16bits_korobeiniki.wav", "bpm": 144, "repeticoes": 2, "acelerar": 0.15,
     "eco": 0.2, "origem": "Canção popular russa do século XIX (domínio público)",
     "canais": [canal("pulso", KOROBEINIKI_A + " " + KOROBEINIKI_B, 0.55, 0.25),
                canal("triangulo", KOROBEINIKI_BAIXO, 0.9),
                canal("bateria", ROCK, 0.6)]},
    {"titulo": "Ode à Alegria (Beethoven)", "album": CLASSICOS, "faixa": 2,
     "arquivo": "16bits_ode_a_alegria.wav", "bpm": 120, "repeticoes": 1, "acelerar": 0.0,
     "eco": 0.25, "origem": "Ludwig van Beethoven, 1824 (domínio público)",
     "canais": [canal("pulso", ODE, 0.55, 0.5),
                canal("triangulo", ODE_BAIXO, 0.9),
                canal("bateria", "K:1 H:1 S:1 H:1", 0.45)]},
    {"titulo": "Na Gruta do Rei da Montanha (Grieg)", "album": CLASSICOS, "faixa": 3,
     "arquivo": "16bits_rei_da_montanha.wav", "bpm": 112, "repeticoes": 4, "acelerar": 0.25,
     "eco": 0.15, "origem": "Edvard Grieg, 1875 (domínio público)",
     "canais": [canal("pulso", transpor(REI_FRASE, 1) + " " + transpor(REI_FRASE, 2), 0.5, 0.25),
                canal("triangulo", REI_BAIXO, 0.9),
                canal("bateria", "K:0.5 R:0.5 S:0.5 R:0.5", 0.5)]},
    {"titulo": "Can-can (Offenbach)", "album": CLASSICOS, "faixa": 4,
     "arquivo": "16bits_cancan.wav", "bpm": 152, "repeticoes": 4, "acelerar": 0.08,
     "eco": 0.15, "origem": "Jacques Offenbach, 1858 (domínio público)",
     "canais": [canal("pulso", CANCAN, 0.55, 0.25),
                canal("triangulo", CANCAN_BAIXO, 0.9),
                canal("bateria", "K:0.5 H:0.5 S:0.5 H:0.5", 0.55)]},
    {"titulo": "Para Elisa (Beethoven)", "album": CLASSICOS, "faixa": 5,
     "arquivo": "16bits_para_elisa.wav", "bpm": 72, "repeticoes": 3, "acelerar": 0.0,
     "eco": 0.3, "origem": "Ludwig van Beethoven, 1810 (domínio público)",
     "canais": [canal("pulso", ELISA, 0.5, 0.25),
                canal("triangulo", ELISA_BAIXO, 0.9)]},
    {"titulo": "Pequena Serenata Noturna (Mozart)", "album": CLASSICOS, "faixa": 6,
     "arquivo": "16bits_serenata_noturna.wav", "bpm": 128, "repeticoes": 3, "acelerar": 0.0,
     "eco": 0.25, "origem": "Wolfgang Amadeus Mozart, 1787 (domínio público)",
     "canais": [canal("pulso", SERENATA, 0.55, 0.5),
                canal("triangulo", SERENATA_BAIXO, 0.9)]},
    {"titulo": "Assim Falou Zaratustra (Richard Strauss)", "album": CLASSICOS, "faixa": 7,
     "arquivo": "16bits_zaratustra.wav", "bpm": 72, "repeticoes": 1, "acelerar": 0.0,
     "eco": 0.35, "origem": "Richard Strauss, 1896 (domínio público desde 2020)",
     "canais": [canal("pulso", ZARATUSTRA, 0.55, 0.5),
                canal("triangulo", ZARATUSTRA_BAIXO, 1.0),
                canal("bateria", "R:36 X:4", 0.7)]},
    {"titulo": "Tela de Título", "album": JOGO, "faixa": 1,
     "arquivo": "16bits_tela_de_titulo.wav", "bpm": 120, "repeticoes": 2, "acelerar": 0.0,
     "eco": 0.25, "origem": "Tema original do projeto",
     "canais": [canal("pulso", TITULO, 0.55, 0.5),
                canal("triangulo", TITULO_BAIXO, 0.9),
                canal("pulso", TITULO_ARPEJO, 0.2, 0.125),
                canal("bateria", "K:1 H:0.5 H:0.5 S:1 H:0.5 K:0.5", 0.55)]},
    {"titulo": "Fase 1: Campos de Bits", "album": JOGO, "faixa": 2,
     "arquivo": "16bits_fase_1.wav", "bpm": 150, "repeticoes": 2, "acelerar": 0.0,
     "eco": 0.2, "origem": "Tema original do projeto",
     "canais": [canal("pulso", FASE1, 0.55, 0.25),
                canal("triangulo", FASE1_BAIXO, 0.9),
                canal("pulso", FASE1_ARPEJO, 0.18, 0.125),
                canal("bateria", "K:0.5 H:0.5 S:0.5 H:0.5 K:0.5 K:0.5 S:0.5 H:0.5", 0.55)]},
    {"titulo": "Chefão Final", "album": JOGO, "faixa": 3,
     "arquivo": "16bits_chefao_final.wav", "bpm": 168, "repeticoes": 2, "acelerar": 0.06,
     "eco": 0.15, "origem": "Tema original do projeto",
     "canais": [canal("pulso", CHEFAO, 0.55, 0.125),
                canal("triangulo", CHEFAO_BAIXO, 1.0),
                canal("bateria", "K:0.5 K:0.5 S:0.5 K:0.5 K:0.5 K:0.5 S:0.5 H:0.5", 0.6)]},
    {"titulo": "Vitória!", "album": JOGO, "faixa": 4,
     "arquivo": "16bits_vitoria.wav", "bpm": 140, "repeticoes": 1, "acelerar": 0.0,
     "eco": 0.3, "origem": "Tema original do projeto",
     "canais": [canal("pulso", VITORIA, 0.55, 0.25),
                canal("triangulo", VITORIA_BAIXO, 0.9),
                canal("bateria", "R:12 S:0.25 S:0.25 S:0.25 S:0.25 X:3", 0.6)]},
]

# (nome, descrição, títulos das músicas na ordem)
PLAYLISTS = [
    ("16 bits", "Clássicos e trilha de jogo em chiptune",
     [trilha["titulo"] for trilha in TRILHAS]),
]


def montar_trilha(dados):
    """Cria a Trilha (com os Canais) a partir do dicionário da música."""
    canais = [Canal(c["timbre"], c["notas"], volume=c["volume"], largura=c["largura"])
              for c in dados["canais"]]
    return Trilha(canais, bpm=dados["bpm"], repeticoes=dados["repeticoes"],
                  acelerar=dados["acelerar"], eco=dados["eco"])
