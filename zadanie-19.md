# Zadanie 19 – Dokumentacja endpointu API generowana przez AI

## Pliki

| Plik | Zawartość |
|------|-----------|
| `api-docs.md` | Dokumentacja endpointu `GET /api/users` w formacie Markdown |

## Dane wejściowe

Model otrzymał krótki opis: endpoint `GET /api/users` zwracający listę użytkowników, z trzema parametrami zapytania – `page` (domyślnie 1), `limit` (domyślnie 10, maksymalnie 100) i opcjonalnym filtrem `role`. Polecenie wymagało opisu, parametrów, przykładowego żądania i odpowiedzi.

## Refleksje na temat jakości

### Mocne strony

**Kompletność względem polecenia.** Dokumentacja zawiera wszystkie wymagane sekcje, a do tego tabelę pól odpowiedzi i sekcję błędów. Bez opisu błędów ograniczenie „max 100” byłoby niepełne, bo czytelnik nie wiedziałby, co się stanie po jego przekroczeniu.

**Czytelna struktura.** Tabele parametrów i pól odpowiedzi pozwalają szybko odczytać typ, wartość domyślną i ograniczenia. Żądanie pokazano w dwóch formach – jako surowe HTTP i jako polecenie `curl`, które można od razu uruchomić.

**Spójne przykłady.** Przykład odpowiedzi jest wewnętrznie zgodny z żądaniem: `page=2`, `limit=20`, filtr `role=admin` i wszyscy zwróceni użytkownicy mają rolę `admin`, a `totalPages = 3` wynika z `total = 42` przy 20 wynikach na stronę.

**Przypadki brzegowe.** Opisano zachowanie dla strony spoza zakresu (pusta tablica zamiast błędu), czego krótki opis wejściowy w ogóle nie obejmował.

### Słabe strony i ryzyka

**Treść dopowiedziana przez model.** Znaczna część dokumentacji nie wynika z danych wejściowych, tylko z założeń modelu: struktura odpowiedzi (`data` i `pagination`), pola użytkownika (`id`, `name`, `email`, `role`), dozwolone wartości `role`, kody i format błędów oraz decyzja, że `limit > 100` zwraca `400`, a nie jest przycinany do 100. Założenia są rozsądne i typowe dla REST API, ale wyglądają tak samo wiarygodnie jak fakty. Czytelnik nie odróżni ich od rzeczywistego zachowania systemu. W odpowiedzi w czacie model zaznaczył, które elementy są założeniami, ale sam plik `api-docs.md` już tej informacji nie zawiera.

**Brak źródła prawdy.** Dokumentacja nie została wygenerowana z kodu ani specyfikacji OpenAPI, więc nic nie gwarantuje jej zgodności z implementacją. Przy zmianie API łatwo się rozjedzie.

**Pominięte aspekty.** Nie opisano uwierzytelniania ani uprawnień (lista użytkowników z adresami e-mail to dane osobowe, więc endpoint raczej nie powinien być publiczny), limitów zapytań (rate limiting), sortowania wyników ani tego, czy filtr `role` rozróżnia wielkość liter.

**Dane w przykładach.** Przykładowe dane są fikcyjne i użyto domeny `example.com`, co jest dobrą praktyką. W dokumentacji generowanej z prawdziwych logów lub bazy trzeba by pilnować, aby nie trafiły do niej rzeczywiste dane osobowe.

### Ocena ogólna

Jako punkt wyjścia dokumentacja jest dobra: poprawna formalnie, czytelna i bardziej kompletna niż opis wejściowy. Model dobrze radzi sobie ze strukturą i stylem dokumentacji. Wartość merytoryczna zależy jednak od weryfikacji – każde założenie trzeba porównać z rzeczywistym kodem endpointu, zanim dokument trafi do użytkowników API.

## Wnioski i rekomendacje

| Rekomendacja | Uzasadnienie |
|--------------|--------------|
| Podawać modelowi więcej kontekstu (kod kontrolera, schemat bazy, istniejącą specyfikację) | Mniej założeń, mniejsze ryzyko niezgodności z implementacją |
| Prosić model o jawne oznaczanie założeń w samym dokumencie | Recenzent od razu widzi, co wymaga potwierdzenia |
| Generować dokumentację ze specyfikacji OpenAPI lub z kodu (np. adnotacje, Swagger) | Jedno źródło prawdy, automatyczna aktualizacja |
| Traktować dokumentację AI jak kod – przez code review | Wyłapanie błędów merytorycznych przed publikacją |
| Uzupełnić o uwierzytelnianie, rate limiting i sortowanie | To pierwsze pytania integratora API |
