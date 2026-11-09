# Zadanie 22 – README projektu generowane przez AI

## Pliki

| Plik | Zawartość |
|------|-----------|
| `project-readme.md` | README projektu Simple Task API z sekcjami: opis, instalacja, użycie, endpointy API |

## Dane wejściowe

Model otrzymał nazwę projektu (Simple Task API), jednozdaniowy opis (REST API do zarządzania zadaniami w Node.js, Express i MongoDB) oraz trzy główne funkcje: CRUD zadań, filtrowanie według statusu i priorytetu oraz prostą autoryzację użytkowników. Polecenie wymagało czterech sekcji: opis, instalacja, użycie i endpointy API.

## Uwagi dotyczące jakości

### Co wypadło dobrze

**Zgodność z poleceniem.** README zawiera wszystkie cztery wymagane sekcje w logicznej kolejności – od tego, czym jest projekt, przez uruchomienie, po szczegóły API. Nie dodano zbędnych sekcji, co odpowiada prośbie o „prosty” plik.

**Praktyczna sekcja instalacji.** Wymagania (wersja Node.js, MongoDB) są wymienione przed krokami, a każdy krok zawiera gotowe polecenie do skopiowania. Przykładowy plik `.env` pokazuje wszystkie potrzebne zmienne, a `JWT_SECRET` ma wartość, która wprost sugeruje konieczność zmiany.

**Sekcja użycia jako scenariusz.** Przykłady `curl` tworzą spójny przepływ: rejestracja → logowanie → utworzenie zadania z tokenem → filtrowanie. Czytelnik widzi nie tylko pojedyncze wywołania, ale też jak się ze sobą łączą, w szczególności skąd wziąć token.

**Czytelne tabele.** Endpointy, model zadania i kody odpowiedzi zostały przedstawione w tabelach, co ułatwia szybkie wyszukiwanie informacji. Rozdzielenie endpointów autoryzacji od endpointów zadań jasno pokazuje, które wymagają tokenu.

**Spójność wewnętrzna.** Wartości użyte w przykładach (`in-progress`, `high`, `todo`) zgadzają się z dozwolonymi wartościami z tabeli modelu zadania, a ścieżki w przykładach odpowiadają tabeli endpointów.

### Słabe strony i ryzyka

**Większość treści to założenia.** Opis wejściowy był bardzo ogólny, więc model musiał dopowiedzieć ścieżki endpointów, mechanizm autoryzacji (JWT), nazwy zmiennych środowiskowych, pola modelu zadania, dozwolone wartości statusu i priorytetu oraz wartości domyślne. Założenia są typowe i rozsądne, ale w pliku nie są oznaczone – czytelnik uzna je za fakty. Ostrzeżenie o założeniach pojawiło się tylko w odpowiedzi w czacie, a nie w samym README.

**Niezweryfikowane polecenia.** Nie ma kodu projektu, więc nie wiadomo, czy `npm start` jest zdefiniowany w `package.json`, czy aplikacja czyta zmienne z `.env` (np. przez pakiet `dotenv`) ani czy wymagana wersja Node.js jest właściwa. README może opisywać kroki, które w rzeczywistym repozytorium nie zadziałają.

**Placeholder w adresie repozytorium.** Adres `https://github.com/<uzytkownik>/simple-task-api.git` wymaga ręcznego uzupełnienia, a nazwa katalogu może nie odpowiadać rzeczywistej.

**Brakujące informacje.** Pominięto przykładowe odpowiedzi dla operacji na zadaniach (widać tylko odpowiedź logowania), format komunikatów błędów, informację o tym, czy użytkownik widzi tylko swoje zadania, sposób uruchomienia testów, tryb deweloperski (np. `npm run dev`), uruchomienie przez Docker oraz licencję. Dla „prostego” README to akceptowalne, ale w realnym projekcie warto je uzupełnić.

**Kwestie bezpieczeństwa.** Przykłady przesyłają hasło w treści żądania przez HTTP na `localhost`, co jest w porządku lokalnie, ale README nie wspomina, że w produkcji API musi działać przez HTTPS. Nie ma też uwagi, aby nie commitować pliku `.env` do repozytorium.

**Drobna niespójność terminologiczna.** Sekcja nazywa się „Autoryzacja”, a opisane w niej endpointy realizują uwierzytelnianie (potwierdzenie tożsamości). Wynika to z danych wejściowych („prosta autoryzacja użytkowników”), ale w dokumentacji technicznej warto te pojęcia rozróżniać.

### Ocena ogólna

README jest dobrze zorganizowane, czytelne i od razu użyteczne jako szablon. Model sprawnie przekształcił kilka zdań opisu w kompletny, spójny dokument. Jego wartość merytoryczna zależy jednak w pełni od weryfikacji z kodem – bez niej dokument może wprowadzać w błąd, bo dopowiedziane szczegóły wyglądają równie wiarygodnie jak te wynikające z opisu.

## Wnioski

| Wniosek | Zastosowanie w praktyce |
|---------|-------------------------|
| Jakość dokumentacji AI zależy od kontekstu | Przekazywać modelowi `package.json`, pliki tras i modele danych zamiast samego opisu |
| Założenia muszą być widoczne | Prosić o oznaczanie niepewnych fragmentów w samym dokumencie (np. komentarzem `<!-- TODO: zweryfikować -->`) |
| Polecenia w README trzeba przetestować | Wykonać instrukcję instalacji od zera na czystym środowisku przed publikacją |
| README to część kodu | Aktualizować je razem ze zmianami w API i sprawdzać w code review |
| Dokumentacja endpointów może być generowana | Dla pełnej specyfikacji API lepiej użyć OpenAPI/Swagger generowanego z kodu, a w README zostawić tylko przegląd i link |
