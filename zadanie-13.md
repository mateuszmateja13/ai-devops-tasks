# Zadanie 13 – dokumentacja funkcji w formacie JSDoc

## Czym jest JSDoc

JSDoc to standard dokumentowania kodu JavaScript za pomocą komentarzy blokowych zaczynających się od `/**`. W komentarzu opisuje się działanie funkcji oraz, przy użyciu znaczników (np. `@param`, `@returns`), typy argumentów i zwracanej wartości. Edytory takie jak VS Code odczytują te komentarze i podpowiadają typy oraz opisy podczas pisania kodu, a narzędzie `jsdoc` potrafi wygenerować z nich dokumentację w formacie HTML.

## Pliki

Plik `fetch-user.js` zawiera oryginalną funkcję `fetchUserData`, która pobiera dane użytkownika z API przy użyciu łańcucha `.then()` i zwraca obiekt z imieniem, adresem e-mail oraz datą ostatniego logowania.

Plik `fetch-user-documented.js` zawiera tę samą funkcję przepisaną na `async/await` i opatrzoną komentarzami JSDoc. Przy okazji wprowadzono dwie poprawki: identyfikator użytkownika jest kodowany przez `encodeURIComponent`, a brak pola `lastLoginTimestamp` daje `null` zamiast obiektu `Invalid Date`.

## Użyte znaczniki JSDoc

`@typedef` i `@property` definiują typ `UserData`, czyli kształt obiektu zwracanego przez funkcję. `@async` oznacza, że funkcja jest asynchroniczna. `@param` opisuje argument `userId` i jego dopuszczalne typy. `@returns` określa, że funkcja zwraca `Promise` rozwiązywany do `UserData` albo `null`. `@example` pokazuje przykładowe wywołanie.

Znacznik `@throws` został pominięty, ponieważ funkcja przechwytuje wszystkie błędy w bloku `try/catch` i zwraca `null`, więc wyjątek nigdy nie trafia do kodu wywołującego.

## Generowanie dokumentacji HTML (opcjonalnie)

```bash
npm install --save-dev jsdoc
npx jsdoc fetch-user-documented.js -d docs
```

Wygenerowana dokumentacja trafia do katalogu `docs/`.
