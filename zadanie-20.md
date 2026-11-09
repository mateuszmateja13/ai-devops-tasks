# Zadanie 20 – Wyrażenie regularne walidujące adres IPv4

## Pliki

| Plik | Zawartość |
|------|-----------|
| `ipv4-validator.js` | Funkcja `isValidIPv4` oraz stała `IPV4_REGEX`; uruchomiony bezpośrednio wykonuje testy |

## Wyrażenie regularne

```regex
^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$
```

## Wyjaśnienie

Wyrażenie składa się z jednego wzorca oktetu (liczby 0–255), użytego cztery razy:

```regex
^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$
 │  │└───────────────── oktet 0–255 ──────────────┘ │ │   └───────────── ostatni oktet ─────────────────┘ │
 │  └── grupa: oktet + kropka ─────────────────────┘ └ powtórz 3 razy                          koniec ciągu ┘
 └ początek ciągu
```

### Wzorzec oktetu

Regex nie operuje na liczbach, tylko na znakach, dlatego zakres 0–255 jest rozpisany na warianty cyfra po cyfrze, połączone alternatywą `|`:

| Wariant | Znaczenie | Zakres |
|---------|-----------|--------|
| `25[0-5]` | „25” + cyfra 0–5 | 250–255 |
| `2[0-4][0-9]` | „2” + cyfra 0–4 + dowolna cyfra | 200–249 |
| `1[0-9]{2}` | „1” + dwie dowolne cyfry | 100–199 |
| `[1-9]?[0-9]` | opcjonalna cyfra 1–9 + dowolna cyfra | 0–99 |

Warianty razem pokrywają dokładnie 0–255. Ostatni wariant nie dopuszcza zera na początku liczby wielocyfrowej, więc `01` czy `007` są odrzucane. To celowe – część systemów interpretuje zera wiodące jako zapis ósemkowy (`010` = 8), co bywało źródłem luk bezpieczeństwa.

### Pozostałe elementy

| Element | Rola |
|---------|------|
| `(?: ... )` | Grupa nieprzechwytująca – grupuje elementy bez zapamiętywania dopasowania |
| `\.` | Dosłowna kropka; bez `\` znak `.` oznacza „dowolny znak” i przeszłoby np. `192a168b1c1` |
| `{3}` | Trzy powtórzenia grupy „oktet + kropka”; czwarty oktet występuje osobno, bez kropki |
| `^` i `$` | Kotwice początku i końca – cały ciąg musi być adresem, nie tylko jego fragment |
| `[0-9]` zamiast `\d` | W Pythonie i .NET `\d` dopasowuje też cyfry z innych alfabetów |

### Przykład odrzucenia – `256.1.1.1`

Silnik sprawdza warianty kolejno: `25[0-5]` dopasowuje „25”, ale „6” nie mieści się w `[0-5]`; `2[0-4][0-9]` odpada, bo „5” nie mieści się w `[0-4]`; `1[0-9]{2}` odpada, bo pierwszy znak to „2”; `[1-9]?[0-9]` dopasowuje „25”, ale następnym znakiem musi być kropka, a jest „6”. Po wycofaniu się (backtracking) z każdej ścieżki dopasowanie kończy się niepowodzeniem.

### Dlaczego nie prostsze wyrażenie

Popularny wzorzec `^(\d{1,3}\.){3}\d{1,3}$` sprawdza tylko liczbę cyfr, więc akceptuje m.in. `999.999.999.999` i `256.300.1.1`.

## Funkcja

```javascript
const { isValidIPv4 } = require('./ipv4-validator.js');

isValidIPv4('192.168.1.1');  // true
isValidIPv4('256.1.1.1');    // false
isValidIPv4(null);           // false – wartości niebędące tekstem są odrzucane
```

Funkcja najpierw sprawdza, czy argument jest tekstem. Bez tego `RegExp.test` niejawnie konwertuje argument na string, co przy nietypowych danych wejściowych mogłoby dać mylące wyniki.

## Testy

Uruchomienie: `node ipv4-validator.js`. Wszystkie 20 przypadków dało oczekiwany wynik.

### Adresy poprawne

| Wejście | Wynik | Uzasadnienie |
|---------|-------|--------------|
| `192.168.1.1` | ✅ true | typowy adres prywatny |
| `10.0.0.1` | ✅ true | zera jako pojedyncze cyfry są dozwolone |
| `172.16.254.99` | ✅ true | oktety z różnych wariantów |
| `0.0.0.0` | ✅ true | dolna granica zakresu |
| `255.255.255.255` | ✅ true | górna granica zakresu |
| `8.8.8.8` | ✅ true | oktety jednocyfrowe |

### Adresy niepoprawne

| Wejście | Wynik | Uzasadnienie |
|---------|-------|--------------|
| `256.1.1.1` | ❌ false | 256 > 255 |
| `999.999.999.999` | ❌ false | trzy cyfry, ale poza zakresem |
| `192.168.1` | ❌ false | tylko trzy oktety |
| `192.168.1.1.1` | ❌ false | pięć oktetów – odrzucone dzięki `$` |
| `192.168.01.1` | ❌ false | zero wiodące |
| `1..2.3` | ❌ false | pusty oktet |
| `a.b.c.d` | ❌ false | litery zamiast cyfr |
| `192.168.1.-1` | ❌ false | znak minus |
| ` 192.168.1.1` | ❌ false | spacja na początku – odrzucone dzięki `^` |
| `192.168.1.1/24` | ❌ false | notacja CIDR to nie sam adres |
| *(pusty ciąg)* | ❌ false | brak danych |
| `null`, `undefined` | ❌ false | brak wartości |
| `19216811` (liczba) | ❌ false | nie jest tekstem |

## Ograniczenia

Wyrażenie sprawdza wyłącznie **format**. Nie odróżnia adresów prywatnych, publicznych i zarezerwowanych – `0.0.0.0` i `127.0.0.1` są formalnie poprawne. Nie obsługuje też IPv6. W kodzie produkcyjnym warto rozważyć gotowe parsery: `net.isIPv4()` w Node.js lub moduł `ipaddress` w Pythonie (np. `ipaddress.ip_address(x).is_private`).

W Pythonie zamiast `re.match` z `^...$` należy używać `re.fullmatch`, ponieważ `$` w Pythonie dopasowuje się także przed końcowym znakiem nowej linii, przez co `"192.168.1.1\n"` zostałby zaakceptowany.
