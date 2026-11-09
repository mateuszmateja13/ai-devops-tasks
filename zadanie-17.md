# Zadanie 17 – Funkcja filtrująca ukończone zadania

## Pliki

| Plik | Zawartość |
|------|-----------|
| `task-filter.js` | Funkcja `getCompletedTaskTitles` eksportowana jako moduł CommonJS |

## Wymagania

Funkcja ma przyjąć tablicę obiektów zadań z polami `id`, `title` i `status`, wybrać tylko zadania o statusie `"completed"`, posortować je rosnąco według `id` i zwrócić tablicę samych tytułów.

## Opis rozwiązania

Funkcja jest łańcuchem trzech metod tablicowych, z których każda realizuje jedno wymaganie:

1. **`filter`** – zostawia obiekty, dla których `task.status === 'completed'`. Użyto ścisłego porównania `===`, więc status musi dokładnie odpowiadać tekstowi `completed` (np. `Completed` nie zostanie uwzględniony).
2. **`sort`** – porządkuje wynik komparatorem `(a, b) => a.id - b.id`. Komparator liczbowy jest konieczny, bo domyślny `sort()` porównuje wartości jako tekst i ustawiłby `10` przed `2`.
3. **`map`** – zamienia każdy obiekt na jego `title`.

**Kolejność operacji.** Filtrowanie wykonywane jest przed sortowaniem. `filter` zwraca nową tablicę, więc `sort`, który modyfikuje tablicę w miejscu, działa na kopii i nie zmienia danych przekazanych przez wywołującego. Dodatkowo sortowanych jest mniej elementów.

**Walidacja.** Jeśli argument nie jest tablicą, funkcja rzuca `TypeError` z czytelnym komunikatem zamiast niejasnego błędu typu `tasks.filter is not a function`.

**Dokumentacja.** Komentarz JSDoc opisuje typ parametru i wartości zwracanej, co ułatwia pracę w IDE.

## Przykład użycia

```javascript
const { getCompletedTaskTitles } = require('./task-filter.js');

const tasks = [
  { id: 3, title: 'Napisać testy',     status: 'completed' },
  { id: 1, title: 'Skonfigurować CI',  status: 'completed' },
  { id: 2, title: 'Code review',       status: 'in-progress' },
  { id: 4, title: 'Deploy na staging', status: 'pending' },
];

console.log(getCompletedTaskTitles(tasks));
// [ 'Skonfigurować CI', 'Napisać testy' ]

console.log(getCompletedTaskTitles([]));
// []

getCompletedTaskTitles(null);
// TypeError: Argument tasks musi być tablicą
```

## Weryfikacja

Funkcja została sprawdzona dla przykładu powyżej, dla identyfikatorów wielocyfrowych (`10, 2, 3, 1` – sortowanie liczbowe, nie tekstowe), dla pustej tablicy i dla argumentu `null`. Sprawdzono też, że tablica wejściowa pozostaje niezmieniona po wywołaniu.

```bash
node -e "
const { getCompletedTaskTitles: f } = require('./task-filter.js');
const tasks = [
  { id: 10, title: 'Deploy', status: 'completed' },
  { id: 2,  title: 'Testy', status: 'pending' },
  { id: 3,  title: 'Code review', status: 'completed' },
  { id: 1,  title: 'Setup CI', status: 'completed' },
];
const before = JSON.stringify(tasks);
console.assert(JSON.stringify(f(tasks)) === JSON.stringify(['Setup CI', 'Code review', 'Deploy']));
console.assert(JSON.stringify(tasks) === before, 'tablica wejściowa została zmieniona');
console.log('OK');
"
```
