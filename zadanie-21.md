# Zadanie 21 – Konwersja danych z JSON do CSV

## Pliki

| Plik | Zawartość |
|------|-----------|
| `users.json` | Dane źródłowe – obiekt z tablicą `users` |
| `users.csv` | Wynik konwersji z kolumnami `id`, `name`, `email`, `roles` |

## Proces konwersji

### 1. Analiza struktury źródłowej

JSON zawiera obiekt z jedną tablicą `users`. Każdy element ma cztery pola:

| Pole | Typ w JSON | Uwagi |
|------|------------|-------|
| `id` | number | wartość skalarna |
| `name` | string | może zawierać spacje |
| `email` | string | wartość skalarna |
| `roles` | array of string | **struktura zagnieżdżona** – nie ma bezpośredniego odpowiednika w CSV |

### 2. Mapowanie na kolumny

Każdy obiekt z tablicy `users` staje się jednym wierszem, a każde pole – kolumną. Kolejność kolumn ustalono jawnie (`id, name, email, roles`), zamiast polegać na kolejności kluczy w obiekcie, która w ogólnym przypadku nie musi być identyczna w każdym rekordzie. Obiekt opakowujący (`{ "users": [...] }`) jest pomijany – CSV przechowuje tylko listę rekordów.

### 3. Spłaszczenie tablicy `roles`

Tablica ról została połączona w jeden tekst separatorem `;`: `["admin", "user"]` → `admin;user`.

### 4. Escaping pól

Każda wartość jest sprawdzana pod kątem znaków specjalnych CSV (przecinek, cudzysłów, nowa linia). Jeśli występują, pole jest otaczane cudzysłowami, a cudzysłowy wewnątrz podwajane (zgodnie z RFC 4180). W tych danych żadne pole tego nie wymagało.

### 5. Wynik

```csv
id,name,email,roles
1,Jan Kowalski,jan@example.com,admin;user
2,Anna Nowak,anna@example.com,user
```

### Kod konwersji

```javascript
const fs = require('fs');

// Zamienia wartość na bezpieczne pole CSV (RFC 4180)
function escapeCsv(value) {
  const text = String(value ?? '');
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function usersToCsv(data, rolesSeparator = ';') {
  const columns = ['id', 'name', 'email', 'roles'];
  const rows = data.users.map((user) =>
    columns
      .map((col) => escapeCsv(col === 'roles' ? (user.roles ?? []).join(rolesSeparator) : user[col]))
      .join(',')
  );
  return [columns.join(','), ...rows].join('\n') + '\n';
}

const data = JSON.parse(fs.readFileSync('users.json', 'utf8'));
fs.writeFileSync('users.csv', usersToCsv(data));
```

Wynik uruchomienia tego kodu na `users.json` jest identyczny z zawartością `users.csv`.

## Potencjalne wyzwania

### Reprezentacja tablicy `roles`

CSV to format płaski – jedna komórka przechowuje jedną wartość tekstową. Tablicę można zapisać na kilka sposobów:

| Sposób | Przykład | Zalety | Wady |
|--------|----------|--------|------|
| **Łączenie separatorem `;`** (wybrany) | `admin;user` | czytelny, nie wymaga cudzysłowów, łatwy do rozbicia (`split(';')`) | separator nie może występować w nazwie roli; typ „tablica” ginie |
| Łączenie przecinkiem w cudzysłowie | `"admin,user"` | naturalny zapis listy | wymaga poprawnego escapingu; łatwo o błąd przy ręcznej edycji |
| JSON w komórce | `"[""admin"",""user""]"` | zachowuje pełną strukturę, odwracalny bez strat | nieczytelny, podwojone cudzysłowy |
| Kolumna na każdą rolę (one-hot) | `is_admin=1, is_user=1` | wygodny do analiz i filtrowania w Excelu | trzeba znać wszystkie role z góry; nowa rola = nowa kolumna |
| Osobny wiersz na rolę | `1,…,admin` i `1,…,user` | w pełni płaski, jak tabela w bazie | duplikacja danych użytkownika; inna liczba wierszy niż rekordów |
| Osobny plik relacji | `user_roles.csv`: `user_id,role` | znormalizowany model, jak w bazie relacyjnej | dwa pliki zamiast jednego |

Wybór zależy od odbiorcy pliku: do przeglądania przez człowieka sprawdza się separator, do analiz – kolumny one-hot, do importu do bazy – osobny plik relacji.

### Utrata typów danych

CSV nie przechowuje typów – wszystko jest tekstem. Przy imporcie `id` może zostać odczytane jako tekst, a tablica `roles` wraca jako zwykły ciąg znaków. Konwersja **CSV → JSON** wymaga więc wiedzy o schemacie, której sam plik nie zawiera.

### Znaki specjalne i escaping

Wartości zawierające przecinek (np. `"Kowalski, Jan"`), cudzysłów lub nową linię muszą być otoczone cudzysłowami, a cudzysłowy wewnętrzne podwojone. Ręczne sklejanie tekstu przez `join(',')` bez escapingu prowadzi do przesunięcia kolumn i uszkodzonego pliku.

### Brakujące i dodatkowe pola

W JSON rekordy mogą mieć różne pola. Trzeba zdecydować, co wpisać przy braku wartości (pusta komórka, `null`, `N/A`) i czy ignorować pola spoza listy kolumn. W kodzie brak pola daje pustą komórkę (`value ?? ''`), a brak `roles` – pustą listę.

### Głębsze zagnieżdżenia

Obiekty zagnieżdżone (np. `address: { city, zip }`) zwykle spłaszcza się do kolumn z kropką: `address.city`, `address.zip`. Tablice obiektów są znacznie trudniejsze i często wymagają osobnego pliku.

### Kodowanie i ustawienia regionalne

Polskie znaki wymagają UTF-8. Excel w Windows bez znacznika BOM może otworzyć plik w złym kodowaniu, a w polskich ustawieniach regionalnych domyślnym separatorem kolumn jest średnik, nie przecinek. Bezpieczniej importować plik przez Dane → Z tekstu/CSV i jawnie wybrać kodowanie oraz separator.

### Bezpieczeństwo – CSV injection

Wartość zaczynająca się od `=`, `+`, `-` lub `@` może zostać potraktowana przez arkusz kalkulacyjny jako formuła. Jeśli dane pochodzą od użytkowników, takie pola warto poprzedzić apostrofem lub odrzucić.

## Wnioski

Konwersja JSON → CSV jest prosta dla płaskich danych, ale traci informacje przy strukturach zagnieżdżonych. Kluczowa decyzja to sposób spłaszczenia tablic – powinna wynikać z tego, kto i jak będzie używał pliku – oraz poprawny escaping, którego nie należy implementować przez proste sklejanie tekstu. Przy bardziej złożonych danych lepiej użyć sprawdzonej biblioteki (np. `csv-stringify` w Node.js lub `pandas.json_normalize` w Pythonie).
