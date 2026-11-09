# Zadanie 12 – Optymalizacja funkcji `find_duplicates`

## Wersja oryginalna

```python
def find_duplicates(list_of_items):
    duplicates = []
    for i in range(len(list_of_items)):
        for j in range(i+1, len(list_of_items)):
            if list_of_items[i] == list_of_items[j] and list_of_items[i] not in duplicates:
                duplicates.append(list_of_items[i])
    return duplicates
```

Funkcja porównuje każdą parę elementów w dwóch zagnieżdżonych pętlach, co daje złożoność czasową O(n²). Dodatkowo warunek `not in duplicates` przeszukuje liniowo listę wyników, więc w najgorszym przypadku koszt rośnie do O(n² · k), gdzie k to liczba znalezionych duplikatów. Przy dużych zbiorach danych funkcja staje się bardzo wolna.

## Wersja zoptymalizowana

```python
from collections import Counter

def find_duplicates(list_of_items):
    """Zwraca elementy występujące więcej niż raz,
    w kolejności ich pierwszego pojawienia się na liście."""
    # Zliczenie wystąpień każdego elementu w jednym przejściu – O(n)
    counts = Counter(list_of_items)
    # Wybór elementów, które wystąpiły co najmniej dwukrotnie
    return [item for item, count in counts.items() if count > 1]
```

## Wyjaśnienie usprawnień

Zamiast porównywać wszystkie pary elementów, wersja zoptymalizowana wykonuje jedno przejście po liście i zlicza wystąpienia w słowniku (`Counter`), w którym wstawianie i odczyt mają średni koszt O(1). Złożoność czasowa spada z O(n²) do O(n), a złożoność pamięciowa wynosi O(n). Znika też kosztowne sprawdzanie `not in` na liście wyników, ponieważ każdy klucz w `Counter` występuje tylko raz.

`Counter` zachowuje kolejność pierwszego wystąpienia kluczy (od Pythona 3.7), dlatego wynik jest identyczny jak w wersji oryginalnej, np. dla `[1, 2, 2, 1]` obie zwracają `[1, 2]`. Kod jest też krótszy i czytelniejszy.

Ograniczeniem nowej wersji jest wymóg hashowalności elementów (liczby, napisy, krotki). Dla list zawierających np. słowniki lub listy należy pozostać przy wersji oryginalnej, a przy pracy na ramkach danych pandas prościej użyć `df[df.duplicated(keep=False)]`.

## Porównanie

| Cecha | Oryginał | Wersja zoptymalizowana |
|---|---|---|
| Złożoność czasowa | O(n²) (do O(n² · k)) | O(n) |
| Złożoność pamięciowa | O(k) | O(n) |
| Kolejność wyniku | pierwsze wystąpienie | pierwsze wystąpienie |
| Elementy niehashowalne | obsługiwane | nieobsługiwane |
