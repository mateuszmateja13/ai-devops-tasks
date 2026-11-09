# Zadanie 15 – Refaktoryzacja funkcji `getEnvironmentConfig`

## Pliki

| Plik | Zawartość |
|------|-----------|
| `config.js` | Oryginalna funkcja oparta na łańcuchu `if / else if / else` |
| `config-refactored.js` | Zrefaktoryzowana funkcja oparta na tabeli konfiguracji |

## Problem w wersji oryginalnej

Funkcja wybierała konfigurację za pomocą pięciu gałęzi warunkowych, z których każda zwracała pełny obiekt z trzema polami. Prowadziło to do kilku problemów:

- **Duplikacja kodu** – gałęzie `development` i `else` były identyczne, a `testing` różniło się od nich tylko adresem `apiUrl`. Te same wartości (`debug: true`, `timeout: 5000`) powtarzały się wielokrotnie.
- **Trudne utrzymanie** – zmiana wspólnej wartości (np. domyślnego timeoutu) wymagała edycji w kilku miejscach, co sprzyja błędom i niespójnościom.
- **Słaba czytelność** – aby porównać środowiska, trzeba było przeczytać ok. 40 linii zagnieżdżonych warunków.
- **Słaba rozszerzalność** – każde nowe środowisko oznaczało kolejną gałąź `else if` z pełnym obiektem.

## Wprowadzone zmiany

1. **Obiekt bazowy `BASE_CONFIG`** – zawiera wartości wspólne (domyślnie konfigurację deweloperską). Jest jednym źródłem prawdy dla wartości domyślnych.
2. **Mapa `ENV_OVERRIDES`** – każde środowisko definiuje wyłącznie te pola, którymi różni się od bazy. Logika warunkowa została zastąpiona strukturą danych (*replace conditional with lookup table*).
3. **Scalanie przez spread** – `{ ...BASE_CONFIG, ...overrides }` buduje wynikowy obiekt w jednej linii.
4. **Bezpieczny fallback** – nieznane środowisko otrzymuje konfigurację deweloperską, tak jak gałąź `else` w oryginale. Użycie `Object.hasOwn` chroni przed przypadkowym trafieniem w klucze z prototypu (np. `'toString'`).
5. **Niemutowalność** – stałe są zamrożone `Object.freeze`, a funkcja zwraca nowy obiekt przy każdym wywołaniu, więc kod wywołujący nie zmodyfikuje współdzielonej konfiguracji.
6. **Dokumentacja JSDoc** – opis parametrów i typu zwracanego ułatwia pracę w IDE.

## Korzyści

- **Czytelność** – wszystkie środowiska i ich różnice widać w kilku linijkach, w formie tabeli.
- **Mniej duplikacji (zasada DRY)** – wspólne wartości są zdefiniowane raz.
- **Łatwiejsze utrzymanie** – zmiana wartości domyślnej to edycja jednego miejsca.
- **Rozszerzalność (zasada Open/Closed)** – dodanie środowiska to jedna linia w `ENV_OVERRIDES`, bez dotykania logiki funkcji.
- **Bezpieczeństwo** – brak ryzyka mutacji współdzielonych obiektów i fałszywych trafień w klucze prototypu.
- **Testowalność** – dane konfiguracyjne są oddzielone od logiki, więc łatwo je sprawdzić i podmienić.

## Weryfikacja zgodności zachowania

Obie wersje zostały porównane dla 9 przypadków wejściowych: `development`, `testing`, `staging`, `production`, nieznanej nazwy (`unknown`), `undefined`, pustego ciągu, `toString` oraz `__proto__`. We wszystkich przypadkach wyniki są identyczne, co potwierdza, że refaktoryzacja nie zmieniła zachowania funkcji.

```bash
node -e "
const a = require('./config.js').getEnvironmentConfig;
const b = require('./config-refactored.js').getEnvironmentConfig;
const envs = ['development','testing','staging','production','unknown',undefined,'','toString','__proto__'];
for (const e of envs) console.assert(JSON.stringify(a(e)) === JSON.stringify(b(e)), e);
console.log('OK');
"
```
