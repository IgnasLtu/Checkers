# Šaškės – OOP Kursinis Darbas

## Turinys
1. [Įvadas](#1-įvadas)
2. [Analizė](#2-analizė)
3. [Rezultatai ir išvados](#3-rezultatai-ir-išvados)

---

## 1. Įvadas

### Kas yra ši programa?

Tai šaškių žaidimas, parašytas Python kalba kaip objektinio programavimo kursinis darbas. Žaidimas palaiko tris režimus: žmogus prieš žmogų, žmogus prieš kompiuterį ir kompiuteris prieš kompiuterį. Žaidimas laikosi klasikinių lietuviškų šaškių taisyklių — paprastų žetonai juda tik į priekį, damos juda laisvai per kelis laukus, grandininis kirtimas.

### Kaip paleisti programą?

**Reikalavimai:** Python 3.10 ar naujesnė versija.

```bash
python checkers.py
```

Visas programos kodas yra viename faile: `checkers.py`. Vienetų testai yra `tests/test_checkers.py`.

Testų paleidimas:

```bash
python -m unittest tests/test_checkers.py -v
```

### Kaip naudotis programa?

Paleidus programą, pasirodo meniu:

```
Menu 
[1] New game
[2] Load saved game
[3] Exit
```

Kiekvienam žaidėjui pasirenkamas tipas (`human` arba `ai`) ir vardas. Žaidimo metu žetonai rodomi tokiais simboliais:

| Simbolis | Reikšmė |
|----------|---------|
| `w` | Baltas žetonas |
| `b` | Juodas žetonas |
| `W` | Balta dama |
| `B` | Juoda dama |
| `_` | Tuščias tamsus laukelis |
| `.` | Tuščias šviesus laukelis |

Savo ėjimo metu programa išvardija visus galimus ėjimus sunumeruotus `[0]`, `[1]` ir t.t. Kad pasirinkti ėjimą įvedamas numeris. Žaidimo metu taip pat galima naudoti šias komandas:

| Komanda | Veiksmas |
|---------|---------|
| `save` | Išsaugoti žaidimą į CSV failą |
| `quit` | Išeiti iš žaidimo |
| `board` | Iš naujo parodyti lentą |
| `help` | Parodyti galimas komandas |

---

## 2. Analizė

### Projekto struktūra

Visas kodas yra `checkers.py` faile, surikiuotas tokia tvarka:

```
checkers.py
├── GamePiece      (abstrakti bazinė klasė)
├── Piece          (paprastas žetonas)
├── King           (dama)
├── Board          (žaidimo lenta)
├── Player         (abstrakti bazinė klasė)
├── HumanPlayer    (skaito konsolės įvestį)
├── AIPlayer       (atsitiktinių ėjimų AI)
├── PlayerFactory  (Factory Method šablonas)
├── FileHandler    (CSV išsaugojimas / užkrovimas)
├── Game           (pagrindinis žaidimo valdytojas)
└── main()         (įėjimo taškas)
```

---

### OOP Pirmasis Pilioras – Abstrakcija

Abstrakcija – tai principas, kai iš vartotojo slepiamos vidinės realizacijos detalės, o matomais paliekami tik esminiai metodai. Šiame projekte tai pasiekiama per dvi abstrakčias bazes, sukurtas su Python `abc` moduliu.

`GamePiece` nusako, kokius metodus privalo turėti kiekvienas žetonas, tačiau nepasako, kaip jie turi veikti:

```python
class GamePiece(ABC):
    @abstractmethod
    def get_possible_moves(self, board) -> list:
        pass

    @abstractmethod
    def get_captures(self, board, skip=None) -> list:
        pass

    @abstractmethod
    def symbol(self) -> str:
        pass
```

`Player` nustato bendrą sąsają visiems žaidėjams — nesvarbu ar tai žmogus, ar kompiuteris, `Game` klasė su jais bendrauja vienodai:

```python
class Player(ABC):
    @abstractmethod
    def make_move(self, board) -> tuple:
        pass

    @abstractmethod
    def choose_chain_capture(self, piece, moves) -> tuple:
        pass
```

---

### OOP Antrasis Pilioras – Inkapsuliacija

Inkapsuliacija užtikrina, kad objekto vidiniai duomenys nebūtų tiesiogiai pasiekiami iš išorės. Projekte visi atributai žymimi `_` simboliu, o norint juos skaityti ar keisti — naudojami `@property` dekoratoriai.

```python
class GamePiece(ABC):
    def __init__(self, color: str, row: int, col: int):
        self._color = color   # apsaugotas
        self._row = row
        self._col = col

    @property
    def color(self) -> str:
        return self._color

    @row.setter
    def row(self, value: int):
        self._row = value
```

`Board` klasėje lenta ir žetonų sąrašai taip pat yra apsaugoti — joks išorinis kodas negali jų pakeisti tiesiogiai:

```python
class Board:
    def __init__(self):
        self._grid = [[None] * self.SIZE for _ in range(self.SIZE)]
        self._white_pieces: list = []
        self._black_pieces: list = []
```

---

### OOP Trečiasis Pilioras – Paveldimumas

Paveldimumas suteikia galimybę naujai klasei perimti tėvinės klasės savybes ir prireikus jas papildyti arba pakeisti. Šiame projekte veikia dvi atskiros hierarchijos.

**Žetonų hierarchija:**

```
GamePiece (ABC)
    └── Piece       (paprastas žetonas)
            └── King    (dama)
```

`King` perima `Piece` klasės logiką, tačiau pakeičia judėjimo metodus — dama gali laisvai kirsti lentą įstrižai per kiek nori laukelių:

```python
class King(Piece):
    def _get_steps(self, board) -> list:
        moves = []
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                r, c = self._row + dr, self._col + dc
                while board.in_bounds(r, c) and board.get_piece(r, c) is None:
                    moves.append((r, c, None))
                    r += dr
                    c += dc
        return moves
```

**Žaidėjų hierarchija:**

```
Player (ABC)
    ├── HumanPlayer   (konsolės įvestis)
    └── AIPlayer      (atsitiktinis ėjimo pasirinkimas)
```

---

### OOP Ketvirtasis Pilioras – Polimorfizmas

Polimorfizmas reiškia, kad skirtingi objektai gali reaguoti į tą patį iškvietimą skirtingai. `Game` klasė kviečia `make_move()` ir `choose_chain_capture()` kiekvieną kartą vienodai — tačiau rezultatas priklauso nuo to, ar žaidėjas yra žmogus, ar kompiuteris:

```python
result = self._current_player.make_move(self._board)
```

`HumanPlayer.make_move()` laukia vartotojo įvesties konsolėje, o `AIPlayer.make_move()` savarankiškai išrenka ėjimą. Analogiškai veikia ir grandininio kirtimo metodas:

```python
def choose_chain_capture(self, piece, moves) -> tuple:
    idx = int(input("Choose a number: "))
    return moves[idx]

def choose_chain_capture(self, piece, moves) -> tuple:
    chosen = random.choice(moves)
    print(f"{self._name} (AI) captures again: ...")
    return chosen
```

---

### Factory Method

**Factory Method**  leidžia atskirti objektų kūrimo logiką nuo likusio kodo. Žaidėjai nekuriami tiesiogiai `main()` funkcijoje — už tai atsakinga `PlayerFactory.create_player()`:

```python
class PlayerFactory:
    @staticmethod
    def create_player(player_type: str, name: str, color: str) -> Player:
        player_type = player_type.lower().strip()
        if player_type == "human":
            return HumanPlayer(name, color)
        elif player_type == "ai":
            return AIPlayer(name, color)
        else:
            raise ValueError(f"Unknown player type: '{player_type}'")
```

Šis pasirinkimas pagrįstas keliais argumentais: `Game` klasė remiasi tik abstrakčia `Player` sąsaja ir nežino apie konkrečias realizacijas. Jei ateityje reikėtų pridėti naują žaidėjo tipą, pakaktų išplėsti tik fabriką — visa kita veiktų be pakeitimų.

---

### Kompozicija ir Agregacija

**Kompozicija** pasireiškia tada, kai vienas objektas yra neatskiriamai susijęs su kitu ir negali egzistuoti savarankiškai. `Board` objektas visada sukuriamas `Game` viduje ir be jo neturi prasmės:

```python
class Game:
    def __init__(self, player1: Player, player2: Player):
        self._board = Board()   # Kompozicija — Board sukuriamas čia
```

**Agregacija** skiriasi tuo, kad susijęs objektas gali gyvuoti ir be talpinančiojo. `Player` objektai sukuriami per `PlayerFactory` dar prieš kuriant `Game` — ir perduodami į konstruktorių iš išorės:

```python
class Game:
    def __init__(self, player1: Player, player2: Player):
        self._player1 = player1   # Agregacija — perduodama iš išorės
        self._player2 = player2
```

---

### Skaitymas iš failo ir rašymas į failą

`FileHandler` klasė yra atsakinga už žaidimo būsenos įrašymą ir atkūrimą CSV formatu. Faile pirmiausia įrašoma metainformacija — kieno eilė — o toliau seka po vieną eilutę kiekvienam žetonui:

```
meta,current_turn,white
row,col,color,type
5,0,white,piece
5,2,white,piece
...
```

Išsaugojimo metodas:

```python
def save_game(self, board, current_color: str, filename: str = None) -> str:
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["meta", "current_turn", current_color])
        writer.writerow(["row", "col", "color", "type"])
        for item in piece_data:
            writer.writerow([item["row"], item["col"], item["color"], item["type"]])
```

Užkrovimo metodas:

```python
def load_game(self, filepath: str) -> tuple:
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == "meta":
                current_color = row[2]
            elif row[0] != "row":
                piece_data.append({
                    "row": int(row[0]), "col": int(row[1]),
                    "color": row[2], "type": row[3]
                })
    return piece_data, current_color
```

Be to, kiekvieno žaidimo pabaigoje visa ėjimų istorija automatiškai įrašoma į atskirą `history.csv` failą.

---

### Testavimas

Testavimui naudojamas Python standartinis `unittest` pagrindas. Viso parašyti 40 testų, kurie patikrina visas pagrindines programos klases ir suskirstyti į 6 grupes:

| Testų klasė | Kas testuojama |
|---|---|
| `TestPiece` | Žetono kūrimas, simboliai, kirtimas, setter'iai |
| `TestBoard` | Pradinė padėtis, judėjimas, kirtimas, paaukštinimas, ribos |
| `TestPieceMoves` | Ėjimai į priekį, kirtimai atgal, grandininis kirtimas, damos kirtimas iš toli |
| `TestPlayerFactory` | Žmogaus/AI kūrimas, netinkamas tipas, didžiosios raidės |
| `TestFileHandler` | Išsaugojimas, užkrovimas, apvaliasis testas, klaida kai failas nerastas |
| `TestGame` | Laimėtojo aptikimas, žaidėjų keitimas, ėjimų istorija |

Žemiau pateikiamas testo pavyzdys:

```python
def test_chain_capture_follow_up(self):
    board = Board()
    white = Piece("white", 4, 4)
    black1 = Piece("black", 3, 3)
    black2 = Piece("black", 1, 1)
    board._grid[4][4] = white
    board._grid[3][3] = black1
    board._grid[1][1] = black2
    board._white_pieces.append(white)
    board._black_pieces.extend([black1, black2])
    board.move_piece(white, 2, 2, black1)
    follow_ups = white.get_captures(board)
    self.assertTrue(len(follow_ups) > 0)
    self.assertEqual(follow_ups[0][:2], (0, 0))
```

---

## 3. Rezultatai ir išvados

### Rezultatai

- Sukurtas veikiantis šaškių žaidimas konsolėje, kuris leidžia žaisti trijuose skirtinguose režimuose: du žmonės, žmogus su kompiuteriu arba du kompiuteriai tarpusavyje.
- Visi keturi objektinio programavimo principai buvo pritaikyti — abstrakcija, inkapsuliacija, paveldimumas ir polimorfizmas .
- Realizuotos autentiškos lietuviškos šaškių taisyklės: paprastas žetonas eina tik į priekį, dama juda laisvai bet kuria įstrižaine, kirtimai privalomi, o grandininis kirtimas galimas visomis keturiomis kryptimis.
- - Factory metodas leido atskirti žaidėjų kūrimą nuo žaidimo valdymo logikos, ateityje galima būtų pritaikyti ir naujų tipų.
- Parašyti 40 automatinių testų, kurie tikrina žetonų judėjimą, kirtimus, damos paaukštinimą, žaidimo išsaugojimą bei užkrovimą ir laimėjimo sąlygos nustatymą.

### Išvados

Kursinio darbo metu pavyko sukurti visiškai veikiantį šaškių žaidimą, kuriame visi OOP principai pritaikyti praktiškai. Kiekviena klasė atlieka vieną konkrečią funkciją: `Board` saugo lentos būseną, `Piece` ir `King` aprašo judėjimo taisykles, `Player` poklasiai valdo įvestį, o `Game` sujungia viską į vieną veikiantį ciklą.

Programą ateityje galima toliau tobulinti įvairiais būdais. Vizualinė sąsaja su `pygame` biblioteka pakeistų tekstinį rodymą į grafinį. Protingesnis AI, pagrįstas Minimax algoritmu, suteiktų realų iššūkį žaidėjui. 

---
