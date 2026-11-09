# Zadanie 23 – Analiza złożoności i optymalizacja algorytmu `findPairs`

## Pliki

| Plik | Zawartość |
|------|-----------|
| `find-pairs.js` | Oryginalny algorytm – dwie zagnieżdżone pętle |
| `find-pairs-optimized.js` | `findPairsOptimized` (wszystkie pary, mapa skrótów) oraz `findUniquePairs` (unikalne pary wartości) |

## Analiza złożoności wersji oryginalnej

### Złożoność czasowa: O(n²)

Pętla zewnętrzna przechodzi po każdym z `n` elementów, a wewnętrzna po wszystkich elementach za nim. Liczba porównań wynosi:

```
(n − 1) + (n − 2) + … + 1 = n(n − 1) / 2  →  O(n²)
```

| n | Liczba porównań |
|---|-----------------|
| 1 000 | ~500 tys. |
| 10 000 | ~50 mln |
| 100 000 | ~5 mld |

Algorytm wykonuje pełną liczbę porównań niezależnie od danych – nie ma przypadku optymistycznego, w którym kończy pracę wcześniej.

### Złożoność pamięciowa: O(1) dodatkowej pamięci + rozmiar wyniku

Poza licznikami pętli algorytm nie przechowuje żadnych struktur pomocniczych. Należy jednak uwzględnić wynik: w najgorszym przypadku, np. `[3, 3, 3, …]` z sumą 6, każda para indeksów jest poprawna, więc tablica `pairs` ma n(n − 1)/2 elementów, czyli **O(n²)**.

### Dolna granica

Ponieważ funkcja zwraca każdą parę indeksów osobno, w skrajnym przypadku sam wynik ma rozmiar O(n²). Żaden algorytm nie może być szybszy niż czas potrzebny na wypisanie wyniku. Optymalizacja polega więc na uzależnieniu czasu od **liczby znalezionych par (k)**, a nie od kwadratu rozmiaru wejścia. W typowych danych k jest dużo mniejsze niż n².

## Optymalizacja 1 – mapa skrótów: `findPairsOptimized`

### Idea

Zamiast dla każdego elementu sprawdzać wszystkie późniejsze („który późniejszy element pasuje do bieżącego?”), algorytm przechodzi tablicę raz i pyta: „ile **wcześniejszych** elementów jest dopełnieniem bieżącego?”. Dopełnienie to `targetSum − value`. Mapa `seen` przechowuje, ile razy dana wartość już wystąpiła.

### Przebieg dla `arr = [1, 5, 3, 2, 4]`, `targetSum = 6`

| Element | Dopełnienie | `seen` przed krokiem | Nowe pary |
|---------|-------------|----------------------|-----------|
| 1 | 5 | `{}` | — |
| 5 | 1 | `{1:1}` | `[1, 5]` |
| 3 | 3 | `{1:1, 5:1}` | — |
| 2 | 4 | `{1:1, 5:1, 3:1}` | — |
| 4 | 2 | `{1:1, 5:1, 3:1, 2:1}` | `[2, 4]` |

Wynik: `[[1, 5], [2, 4]]` – taki sam jak w oryginale.

### Złożoność

| | Oryginał | `findPairsOptimized` |
|---|----------|----------------------|
| Czas | O(n²) | **O(n + k)** – jeden przebieg, wyszukiwanie w `Map` średnio O(1), plus koszt dopisania k par |
| Pamięć dodatkowa | O(1) | **O(n)** – mapa wystąpień |
| Pamięć na wynik | O(k) | O(k) |

To klasyczna **wymiana pamięci na czas** (*space–time trade-off*).

### Zachowanie semantyki

Licznik wystąpień (zamiast zbioru `Set`) sprawia, że duplikaty są obsłużone tak samo jak w oryginale: dla `[3, 3, 3]` i sumy 6 obie wersje zwracają trzy pary `[3, 3]`. Element o mniejszym indeksie zawsze jest na pierwszej pozycji pary. Różnić się może jedynie **kolejność par** w tablicy wynikowej – oryginał porządkuje je według pierwszego elementu pary, wersja zoptymalizowana według drugiego.

## Optymalizacja 2 – unikalne pary wartości: `findUniquePairs`

W wielu zastosowaniach interesują nas pary **wartości**, a nie indeksów – dla `[3, 3, 3]` wystarczy jedna para `[3, 3]`. Wtedy wynik ma co najwyżej n elementów i cały algorytm działa w **O(n)** czasu i **O(n)** pamięci. Zbiór `seen` przechowuje widziane wartości, a mapa `found` z kluczem `"a,b"` (gdzie `a ≤ b`) eliminuje duplikaty par.

```javascript
findUniquePairs([1, 5, 3, 3, 2, 4, 1], 6); // [[1, 5], [3, 3], [2, 4]]
```

Ta funkcja **zmienia semantykę** względem oryginału, więc nie jest jego bezpośrednim zamiennikiem – trzeba ją wybrać świadomie.

## Alternatywa – sortowanie i dwa wskaźniki

Po posortowaniu tablicy jeden wskaźnik startuje od początku, drugi od końca. Jeśli suma jest za mała, przesuwa się lewy wskaźnik, jeśli za duża – prawy. Czas wynosi **O(n log n)** (dominuje sortowanie), a pamięć dodatkowa **O(1)** przy sortowaniu w miejscu. Podejście ma sens, gdy pamięć jest ograniczona lub dane są już posortowane. Wadą jest modyfikacja (lub kopiowanie) danych wejściowych i utrata oryginalnych indeksów.

## Porównanie podejść

| Podejście | Czas | Pamięć dodatkowa | Wynik | Kiedy stosować |
|-----------|------|------------------|-------|----------------|
| Oryginał (pętle zagnieżdżone) | O(n²) | O(1) | wszystkie pary indeksów | bardzo małe tablice, prostota |
| `findPairsOptimized` | O(n + k) | O(n) | wszystkie pary indeksów | zamiennik oryginału dla większych danych |
| `findUniquePairs` | O(n) | O(n) | unikalne pary wartości | gdy duplikaty par są niepotrzebne |
| Sortowanie + dwa wskaźniki | O(n log n) | O(1) | unikalne pary wartości | ograniczona pamięć, dane posortowane |

## Weryfikacja

### Poprawność

Obie wersje porównano na 5000 losowych tablicach (0–14 elementów, wartości od −3 do 7, w tym duplikaty i liczby ujemne). We wszystkich przypadkach `findPairs` i `findPairsOptimized` zwróciły ten sam zbiór par.

```bash
node -e "
const { findPairs } = require('./find-pairs.js');
const { findPairsOptimized } = require('./find-pairs-optimized.js');
const norm = (p) => p.map((x) => x.join(',')).sort().join('|');
for (let t = 0; t < 5000; t++) {
  const arr = Array.from({ length: Math.floor(Math.random() * 15) }, () => Math.floor(Math.random() * 11) - 3);
  const sum = Math.floor(Math.random() * 13) - 3;
  if (norm(findPairs(arr, sum)) !== norm(findPairsOptimized(arr, sum))) throw new Error(JSON.stringify({ arr, sum }));
}
console.log('OK – ten sam zbiór par we wszystkich testach');
"
```

### Wydajność

Pomiar dla tablicy `[0, 1, …, n − 1]` i `targetSum = n` (Node.js, pojedyncze uruchomienie, wartości orientacyjne):

| n | Oryginał | `findPairsOptimized` |
|---|----------|----------------------|
| 2 000 | ~1,9 ms | ~0,4 ms |
| 8 000 | ~33 ms | ~1,2 ms |

Czterokrotne zwiększenie n wydłużyło czas oryginału ok. 17 razy, co jest zgodne ze wzrostem kwadratowym (teoretycznie 16 razy). Czas wersji zoptymalizowanej rośnie w przybliżeniu liniowo.

## Wnioski

Oryginalny algorytm jest poprawny i czytelny, ale jego czas rośnie kwadratowo. Zastąpienie wewnętrznej pętli wyszukiwaniem w mapie skrótów skraca czas do O(n + k) kosztem O(n) dodatkowej pamięci, przy zachowaniu tego samego zbioru wyników. Przed optymalizacją warto doprecyzować wymagania – jeśli potrzebne są tylko unikalne pary wartości, można osiągnąć czysto liniowe O(n).
