# Zadanie 1

## Czym jest DevOps? (wyjaśnienie w 3 zdaniach)

DevOps to kultura organizacyjna i zbiór praktyk łączących zespoły wytwarzania oprogramowania (Development) z zespołami utrzymania infrastruktury (Operations), których celem jest skrócenie cyklu dostarczania oprogramowania przy zachowaniu wysokiej jakości i niezawodności. Opiera się na automatyzacji procesów, takich jak ciągła integracja i ciągłe wdrażanie (CI/CD), infrastruktura jako kod oraz stały monitoring działających systemów. W ujęciu zarządczym DevOps przekłada się na szybsze reagowanie na potrzeby biznesu, mniejszą liczbę awarii i lepszą współpracę między działami, co w kontekście Twojej pracy odpowiada choćby utrzymaniu i aktualizowaniu modelu predykcyjnego w środowisku produkcyjnym portu lotniczego (podejście to w odniesieniu do uczenia maszynowego nazywa się MLOps).

## Jakie są 3 najpopularniejsze narzędzia używane w DevOps?

Najczęściej wskazywane są Git (zwykle z platformą GitHub lub GitLab) do kontroli wersji i współpracy nad kodem, Docker do konteneryzacji aplikacji, czyli pakowania ich wraz z zależnościami tak, by działały identycznie w każdym środowisku, oraz Kubernetes do orkiestracji kontenerów, czyli ich automatycznego uruchamiania, skalowania i utrzymywania w środowisku produkcyjnym. Tuż za nimi plasują się narzędzia CI/CD, takie jak Jenkins czy GitHub Actions, a w obszarze infrastruktury jako kodu Terraform. W Twojej pracy praktyczne znaczenie miałyby przede wszystkim Git do wersjonowania kodu ETL i modelu XGBoost oraz Docker do odtwarzalnego uruchamiania całego potoku, co dobrze wpisuje się w wymóg replikowalności badań.
