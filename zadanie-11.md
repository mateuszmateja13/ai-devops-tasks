# Zadanie 11 – test jednostkowy funkcji `sum` w Jest

## Czym jest Jest

Jest to framework do testowania kodu JavaScript, rozwijany przez Meta. Działa bez dodatkowej konfiguracji: sam wyszukuje pliki z końcówką `.test.js`, uruchamia je i pokazuje, które asercje przeszły. Ma wbudowane funkcje porównujące (np. `expect(...).toBe(...)`), mockowanie oraz raport pokrycia kodu.

## Testowana funkcja

Plik `sum.js` zawiera funkcję zwracającą sumę dwóch argumentów. Funkcja jest eksportowana przez `module.exports`, dzięki czemu plik testowy może ją zaimportować przez `require`.

```javascript
function sum(a, b) {
  return a + b;
}

module.exports = sum;
```

## Test jednostkowy

Plik `sum.test.js` grupuje testy w bloku `describe('sum', ...)` i sprawdza cztery przypadki: dodawanie liczb dodatnich, liczb ujemnych, dodawanie zera oraz ułamków. Przy ułamkach używane jest `toBeCloseTo`, ponieważ w arytmetyce zmiennoprzecinkowej `0.1 + 0.2` daje `0.30000000000000004`, więc porównanie `toBe(0.3)` by nie przeszło.

## Instalacja

Wymagany jest Node.js z menedżerem pakietów npm. W katalogu projektu należy utworzyć plik `package.json`, a następnie zainstalować Jest jako zależność deweloperską:

```bash
npm init -y
npm install --save-dev jest
```

Potem w `package.json` trzeba ustawić skrypt testowy:

```json
{
  "scripts": {
    "test": "jest"
  }
}
```

## Uruchomienie testu

```bash
npm test
```

Alternatywnie można użyć `npx jest`. Raport pokrycia kodu generuje polecenie `npx jest --coverage` (trafia do katalogu `coverage/`, który jest ignorowany w `.gitignore`).

Oczekiwany wynik:

```
 PASS  ./sum.test.js
  sum
    ✓ dodaje dwie liczby dodatnie
    ✓ obsługuje liczby ujemne
    ✓ dodaje zero bez zmiany wyniku
    ✓ dla ułamków porównuje wynik z tolerancją

Tests:       4 passed, 4 total
```

## Struktura plików projektu

```
ai-devops-tasks/
├── node_modules/      # zależności instalowane przez npm (ignorowane w .gitignore)
├── package.json       # konfiguracja projektu i skrypt "test"
├── package-lock.json  # zablokowane wersje zależności
├── sum.js             # testowana funkcja
├── sum.test.js        # testy jednostkowe
└── zadanie-11.md      # ten opis
```

W większym projekcie kod zwykle trafia do katalogu `src/`, a testy do `tests/` lub `__tests__/`. Jest znajdzie je tam automatycznie, wystarczy poprawić ścieżkę w `require`.

Uwaga: operator `+` w JavaScripcie przy argumencie tekstowym skleja wartości zamiast je dodawać, więc `sum("2", 3)` zwróci `"23"`. Jeśli funkcja ma przyjmować wyłącznie liczby, warto dodać walidację typów i osobny test tego przypadku.
