<img width="119" alt="image" src="https://github.com/wyslijco/wyslijco.github.io/assets/200957/65435e0b-d446-4a5c-b174-27e37c16e783">

# Pomoc w rozwoju wyślij.co

**wyślij.co** to polska platforma wspierania organizacji charytatywnych, stworzona z myślą o ułatwieniu pomocy potrzebującym. Od początku za najważniejsze założenia przyjęliśmy pełną transparentność, otwartość kodu, użycie rozwiązań darmowych i wykluczenie wszelkich możliwości pozyskiwania jakichkolwiek korzyści za jej tworzenie, prowadzenie i rozwój.

**wyślij.co** jest projektem otwartym, dostępnym na zasadach wolnego oprogramowania. Dzięki temu każdy może uczestniczyć w jego rozwoju i pomagać polskim organizacjom charytatywnym.

Jeżeli chcesz dołączyć do grona kontrybutorów, przede wszystkim przejrzyj naszą sekcję 
[Issues](https://github.com/wyslijco/wyslijco.github.io/issues) repozytorium. Szukaj zgłoszeń 
na nowe funkcjonalności lub błędy, które zostały już przedyskutowane i zatwierdzone przez nasz 
zespół. Najczęściej takie zadania dla nowych osób będą oznaczone specjalną etykietą 
`good first issue` albo `help needed`.

Jeżeli masz pomysł na nowe funkcjonalności lub widzisz błąd - zgłoś je także przez 
[Issues](https://github.com/wyslijco/wyslijco.github.io/issues). To także ważna forma kontrybucji do projektu!

# Założenia techniczne projektu

Od początku zależało nam, żeby **wyślij.co** było usługą jak najtańszą i najłatwiejszą w utrzymaniu. Ze względu 
na prostotę projektu zdecydowaliśmy się hostować platformę w formie strony statycznej 
na [GitHub Pages](https://pages.github.com/). GitHub oferuje cały szereg narzędzi, dzięki którym 
realizacja naszego zadania okazała się możliwa praktycznie bez kosztów finansowych, angażując 
jedynie nasz czas pracy.

Zanim zabierzesz się za pracę nad naszym projektem, zapoznaj się z jego założeniami oraz konstrukcją,
żeby lepiej rozumieć, jak dostarczamy nasze rozwiązanie.

## Jak budowane są strony dla GitHub Pages?

Do budowania strony wykorzystujemy prosty framework backendowy - [Flask](https://flask.palletsprojects.com/en/3.0.x/) - dostępny 
w języku Python. Dzięki dodatkowej bibliotece [Frozen Flask](https://pypi.org/project/Frozen-Flask/), 
możemy automatycznie generować statyczne pliki dla poszczególnych podstron usługi.

W lokalnym środowisku możemy wykorzystać Flaska do kodowania rozwiązań. Budowanie stron odbywa się
w procesie zautomatyzowanym za pomocą [GitHub Actions](https://docs.github.com/en/actions).
Wygenerowane pliki statyczne są ładowane na serwery GitHuba i tam aktualizowana jest nasza strona. 

## Stos technologiczny

### Backend
- **[Flask](https://flask.palletsprojects.com/)** - framework webowy w języku Python
- **[Frozen Flask](https://pypi.org/project/Frozen-Flask/)** - generowanie statycznych stron HTML
- **[Jinja2](https://jinja.palletsprojects.com/)** - system szablonów HTML

### Frontend
- **[Tailwind CSS](https://tailwindcss.com/)** - framework CSS
- **Vanilla JavaScript** - interakcyjność po stronie klienta
- **Responsive design** - dostosowanie do wszystkich urządzeń

### Narzędzia deweloperskie
- **[uv](https://docs.astral.sh/uv/)** - zarządzanie zależnościami Python
- **[npm](https://www.npmjs.com/)** - zarządzanie zależnościami JavaScript
- **[GitHub Actions](https://docs.github.com/en/actions)** - CI/CD i automatyczne deploymenty

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

# Proces rozwoju

## Tworzenie Pull Requestów

Gotowe zmiany należy przedstawić w formie Pull Requestu:

1. **Fork repozytorium** do swojego konta GitHub
2. **Stwórz branch** z opisową nazwą (np. `feature/nowa-organizacja`, `fix/blad-walidacji`)
3. **Implementuj zmiany** zgodnie z konwencjami projektu
4. **Przetestuj lokalnie** - upewnij się, że wszystko działa
5. **Stwórz Pull Request** z jasnym opisem zmian

### Wymagania dla Pull Requestów

- [ ] Opis zmian w języku polskim
- [ ] Odniesienie do powiązanego Issue (jeśli dotyczy)
- [ ] Przetestowane działanie lokalnie
- [ ] Zachowane konwencje nazewnicze

### Przykład opisu Pull Requesta

```markdown
## Opis zmian
Dodanie nowej organizacji "Przykładowa Fundacja" wraz z jej produktami.

## Lista zmian
- Dodany plik `organizations/przykladowa-fundacja.yaml`
- Zweryfikowany numer KRS w rejestrze
- Sprawdzona unikalność adresu organizacji

## Powiązane Issues
Zamyka #123
```

## Walidacja i automatyzacja

Projekt wykorzystuje **GitHub Actions** do automatycznej walidacji:

- **Walidacja YAML** - sprawdzenie poprawności składni plików organizacji
- **Weryfikacja KRS** - automatyczne sprawdzanie numerów w rejestrze
- **Kontrola konfliktów** - wykrywanie duplikatów adresów organizacji
- **Build test** - sprawdzenie poprawności generowania stron statycznych

## Bezpieczeństwo

### Zasady bezpieczeństwa

- **Nie publikuj danych wrażliwych** - unikaj commitowania tokenów, haseł, kluczy API
- **Weryfikuj organizacje** - sprawdzaj wiarygodność dodawanych organizacji
- **Bezpieczne linki** - wszystkie linki do produktów powinny być bezpieczne (HTTPS)
- **Walidacja danych** - każda organizacja musi przejść weryfikację KRS

### Zgłaszanie problemów bezpieczeństwa

W przypadku znalezienia luki bezpieczeństwa, prosimy o kontakt przez [GitHub Security Advisories](../../security/advisories) zamiast publicznych Issues.

# Dodatkowe zasoby

## Dokumentacja

- **[README.md](README.md)** - podstawowe informacje o projekcie
- **[GitHub Wiki](../../wiki)** - szczegółowa dokumentacja
- **[Przykłady organizacji](organizations/)** - wzorce plików YAML

## Społeczność

- **[Issues](../../issues)** - zgłaszanie błędów i propozycji
- **[Discussions](../../discussions)** - ogólne dyskusje o projekcie
- **[Pull Requests](../../pulls)** - przegląd zmian

## Kontakt

W razie wszelkich niejasności najlepszym kanałem komunikacji jest sekcja [Issues](../../issues). Wystarczy założyć nowe zgłoszenie i opisać zagadnienie - zespół postara się odpowiedzieć jak najszybciej.

---

**Dziękujemy za zainteresowanie rozwojem wyślij.co i wspieranie polskich organizacji charytatywnych!** 🎉 
