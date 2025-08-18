<img width="119" alt="image" src="https://github.com/wyslijco/wyslijco.github.io/assets/200957/65435e0b-d446-4a5c-b174-27e37c16e783">

# Pomoc w rozwoju wyslij.co

Nasza strona powstała z myślą o wspieraniu organizacji charytatywnych w Polsce. 
Od początku za najwazniejsze założenia przyjęliśmy pełną transparentność, otwartość kodu, 
użycie rozwiązań darmowych i wykluczenie wszelkich możliwości pozyskiwania jakichkolwiek 
korzyści za jej tworzenie, prowadzenie i rozwój.

Wyslij.co jest projektem otwartym, dostępnym  na zasadach wolnego oprogramowania. Dzieki temu
każdy może uczestniczyć w jego rozwoju.

Jeżeli chcesz dołączyć do grona kontrybutorów, przede wszystkim przejrzyj naszą sekcję 
[Issues](https://github.com/wyslijco/wyslijco.github.io/issues) repozytorium. Szukaj zgłoszeń 
na nowe funkcjonalności lub błędy, które zostały już przedyskutowane i zatwierdzone przez nasz 
zespół. Najczęściej takie zadania dla nowych osób będą oznaczone specjalną etykietą 
`good first issue` albo `help needed`.

Jeżeli masz pomysł na nowe funkcjonalności lub widzisz błąd - zgłoś je także przez 
[Issues](https://github.com/wyslijco/wyslijco.github.io/issues). To także ważna forma kontrybucji do projektu!

# Wytyczne dotyczące rozwoju usługi

Od początku zależało nam, żeby wyslij.co było usługą jak najtańszą i najłatwiejszą w utrzymaniu.
Ze względu na jej prostotę zdecydowaliśmy się hostować ją w formie strony na [GitHub Pages](https://pages.github.com/).
GitHub oferuje cały szereg narzędzi, dzięki którym realizacja naszego zadania okazała się możliwa
praktycznie bez kosztów finansowych, a jedynie angażując nasz czas pracy.

Zanim zabierzesz się za pracę nad naszym projektem, zapoznaj się z jego założeniami oraz konstrukcją,
żeby lepiej rozumieć, jak dostarczamy nasze rozwiązanie.

## Jak budowane są strony dla GitHub Pages?

Do budowania strony wykorzystujemy prosty framework backendowy - [Flask](https://flask.palletsprojects.com/en/3.0.x/) - dostępny 
w języku Python. Dzięki dodatkowej bibliotece [Frozen Flask](https://pypi.org/project/Frozen-Flask/), 
możemy automatycznie generować statyczne pliki dla poszczególnych podstron usługi.

W lokalnym środowisku możemy wykorzystać Flaska do kodowania rozwiązań. Budowanie stron odbywa się
w procesie zautomatyzowanym za pomocą [GitHub Actions](https://docs.github.com/en/actions).
Wygenerowane pliki statyczne są ładowane na serwery GitHuba i tam aktualizowana jest nasza strona. 

## Jaki jest stos technologiczny projektu?

Silnikiem do budowania stron jest wspomniany wyżej [Flask](https://flask.palletsprojects.com/en/3.0.x/) 
wraz z [Frozen Flask](https://pypi.org/project/Frozen-Flask/). Budują one strony z użyciem
szablonów napisanych z użyciem Jinja2. Rozwiązania te napisane są w języku programowania [Python](https://www.python.org/).

Część frontendowa napisana jest przede wszystkim z wykorzystaniem frameworka tailwind CSS.

# Lokalne uruchomienie projektu

## Wymagania

Aby uruchomić projekt będziesz potrzebować:

1. **uv** - nowoczesne narzędzie do zarządzania Pythonem i zależnościami:
   ```sh
   # Instalacja uv (Linux/macOS)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Instalacja uv (Windows)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
   uv automatycznie zainstaluje odpowiednią wersję Pythona jeśli będzie potrzebna.

2. **Node.js** - do budowania stylów CSS z Tailwind:
   - Wersja 18+ (rekomendowana: najnowsza LTS)
   - Można zainstalować przez [nvm](https://github.com/nvm-sh/nvm) lub pobrać z [nodejs.org](https://nodejs.org/) 

## Instalacja zależności

Z poziomu głównego folderu repozytorium wykonaj:

```sh
# Instalacja zależności Python (automatycznie tworzy virtualenv)
uv sync

# Instalacja zależności Node.js
npm install
```

## Budowanie stylów CSS

Aby zbudować style CSS z Tailwind:

```sh
# Jednorazowe zbudowanie stylów
npm run build

# Tryb obserwacji zmian (zalecany podczas developmentu)
npm run css
```

## Uruchomienie lokalnego serwera

Aby uruchomić deweloperski serwer:

```sh
ORGANIZATIONS_DIR_PATH=organizations ORGANIZATIONS_SLUG_FIELD_NAME=adres uv run python site/server.py
```

## Konwencje nazewnicze

Dla ułatwienia prac nad kodem, przyjmujemy, że w kodzie źródłowym wykorzystujemy angielskie nazwy - zarówno dla zmiennych, jak i funkcji.
Jeżeli gdzieś musimy zastosować polskie nazwy (szczególnie taką konwencję przyjęliśmy w plikach yaml edytowanych przez organizacje), 
staramy się je parametryzować w konfiguracji projektu.

W opisach Pull Requestów oraz w Issues stosujemy język polski, żeby uprościć komunikację z organizacjami i każdym, kto chciałby z nami
współpracować nad rozwojem usługi. 

# Tworzenie Pull Requestów

Gotowe zmiany należy przedstawić w formie Pull Requestu. Każda zmiana wymaga zatwierdzenia przez przynajmniej jedną osobę z naszego zespołu.
W opisie Pull Requesta zamieść informacje o wprowadzonych zmianach oraz odniesienie do Issue, którego dotyczą zmiany.

# Dodatkowe pytania i kontakt

W razie wszelkich niejasności, najlepszym kanałem komunikacji z nami jest sekcja Issues. Wystarczy założyć nowe zgłoszenie i opisać zagadnienie. 
