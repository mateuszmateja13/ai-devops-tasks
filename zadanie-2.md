# Zadanie 2: porównanie odpowiedzi dwóch modeli

Te same dwa pytania zadano dwukrotnie: najpierw modelowi Opus 5.5, a następnie modelowi Haiku 5.5.

## Odpowiedzi modelu Opus 5.5

### Czym jest DevOps? (wyjaśnienie w 3 zdaniach)

DevOps to kultura organizacyjna i zbiór praktyk łączących zespoły wytwarzania oprogramowania (Development) z zespołami utrzymania infrastruktury (Operations), których celem jest skrócenie cyklu dostarczania oprogramowania przy zachowaniu wysokiej jakości i niezawodności. Opiera się na automatyzacji procesów, takich jak ciągła integracja i ciągłe wdrażanie (CI/CD), infrastruktura jako kod oraz stały monitoring działających systemów. W ujęciu zarządczym DevOps przekłada się na szybsze reagowanie na potrzeby biznesu, mniejszą liczbę awarii i lepszą współpracę między działami, co w kontekście Twojej pracy odpowiada choćby utrzymaniu i aktualizowaniu modelu predykcyjnego w środowisku produkcyjnym portu lotniczego (podejście to w odniesieniu do uczenia maszynowego nazywa się MLOps).

### Jakie są 3 najpopularniejsze narzędzia używane w DevOps?

Najczęściej wskazywane są Git (zwykle z platformą GitHub lub GitLab) do kontroli wersji i współpracy nad kodem, Docker do konteneryzacji aplikacji, czyli pakowania ich wraz z zależnościami tak, by działały identycznie w każdym środowisku, oraz Kubernetes do orkiestracji kontenerów, czyli ich automatycznego uruchamiania, skalowania i utrzymywania w środowisku produkcyjnym. Tuż za nimi plasują się narzędzia CI/CD, takie jak Jenkins czy GitHub Actions, a w obszarze infrastruktury jako kodu Terraform. W Twojej pracy praktyczne znaczenie miałyby przede wszystkim Git do wersjonowania kodu ETL i modelu XGBoost oraz Docker do odtwarzalnego uruchamiania całego potoku, co dobrze wpisuje się w wymóg replikowalności badań.

## Odpowiedzi modelu Haiku 5.5

### Czym jest DevOps?

DevOps to kultura organizacyjna i zbiór praktyk łączących zespoły wytwarzania oprogramowania (Development) z zespołami utrzymania infrastruktury (Operations), których celem jest skrócenie cyklu dostarczania oprogramowania przy zachowaniu wysokiej jakości i niezawodności. Opiera się na automatyzacji, czyli ciągłej integracji i ciągłym wdrażaniu (CI/CD), infrastrukturze jako kodzie oraz stałym monitoringu działających systemów. W praktyce oznacza to szybsze reagowanie na potrzeby biznesu, mniej awarii i lepszą współpracę między działami.

### Najpopularniejsze narzędzia

Najczęściej wskazuje się Git, używany z GitHubem lub GitLabem do kontroli wersji i pracy zespołowej nad kodem, Docker, który pakuje aplikację wraz z zależnościami tak, by działała tak samo w każdym środowisku, oraz Kubernetes, który automatycznie uruchamia, skaluje i nadzoruje kontenery w produkcji. Blisko czołówki są narzędzia CI/CD, takie jak Jenkins czy GitHub Actions, oraz Terraform do infrastruktury jako kodu. W Twoim projekcie najbardziej przydatne byłyby Git do wersjonowania kodu ETL i modelu XGBoost oraz Docker do odtwarzalnego uruchamiania całego potoku, co wspiera wymóg replikowalności badań.

## Podsumowanie różnic

Merytorycznie obie odpowiedzi są bardzo zbliżone. Oba modele wskazały te same kluczowe elementy DevOps (CI/CD, infrastruktura jako kod, monitoring), te same trzy narzędzia (Git, Docker, Kubernetes) oraz ten sam wniosek dotyczący replikowalności badań w Twojej pracy. Różnice dotyczą głównie sposobu ujęcia i stopnia kontekstualizacji. Opus 5.5 w pierwszej odpowiedzi połączył DevOps z konkretnym przypadkiem portu lotniczego i wprowadził pojęcie MLOps, czyli bezpośrednie nawiązanie do tematu pracy magisterskiej. Haiku 5.5 zachował bardziej ogólny charakter definicji i ograniczył kontekst do jednego zdania podsumowującego. Haiku jest też nieco bardziej zwięzły, a jego odpowiedzi mają wyraźniejsze nagłówki i pogrubione etykiety. Opus 5.5 w drugiej odpowiedzi nieco szerzej rozwinął opisy narzędzi, wyjaśniając w nawiasach, czym jest konteneryzacja i orkiestracja. Haiku przyjął podobne ujęcie, ale bez tych objaśnień. Oba modele przestrzegały wymogu trzech zdań w pierwszym pytaniu oraz zasady pisania ciągłym tekstem bez list.
