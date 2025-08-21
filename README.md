# wyślij.co

Polska platforma wspierania organizacji charytatywnych - katalog organizacji dobroczynnych z możliwością łatwego wspierania ich działalności poprzez zakup potrzebnych produktów.

## 📋 Spis treści

- [O projekcie](#-o-projekcie)
- [Funkcjonalności](#-funkcjonalności)
- [Technologia](#-technologia)
- [Rozwój lokalny](#-rozwój-lokalny)
- [Dodawanie organizacji](#-dodawanie-organizacji)
- [Współpraca](#-współpraca)
- [Licencja](#-licencja)

## 🎯 O projekcie

**wyślij.co** to bezpłatna, otwarta platforma stworzona z myślą o ułatwieniu wspierania polskich organizacji charytatywnych. Naszą misją jest:

- **Transparentność** - pełna otwartość kodu i procesów
- **Dostępność** - bezpłatne korzystanie dla wszystkich organizacji
- **Prostota** - łatwe dodawanie organizacji i znajdowanie sposobów wsparcia
- **Niezależność** - brak zysków z działania platformy

Platforma umożliwia organizacjom charytatywnym prezentację swoich potrzeb w formie "list zakupów", dzięki czemu darczyńcy mogą bezpośrednio kupować konkretne produkty potrzebne organizacjom.

## 🚀 Funkcjonalności

- **Katalog organizacji** - przegląd zweryfikowanych polskich organizacji charytatywnych
- **Listy potrzeb** - każda organizacja może prezentować swoje aktualne potrzeby
- **Weryfikacja KRS** - automatyczne sprawdzanie organizacji w oficjalnym rejestrze
- **Responsywny design** - dostosowany do wszystkich urządzeń
- **Statyczne strony** - szybkie ładowanie i wysoka dostępność
- **SEO-friendly** - zoptymalizowane pod kątem wyszukiwarek

## 🔧 Technologia

### Architektura
- **Backend**: Flask + Frozen-Flask (generowanie stron statycznych)
- **Frontend**: Tailwind CSS + Jinja2 templates
- **Dane**: Pliki YAML z informacjami o organizacjach
- **Hosting**: GitHub Pages (darmowy hosting)
- **CI/CD**: GitHub Actions (automatyczne budowanie i deploy)

### Struktura projektu
```
├── site/                   # Główna aplikacja Flask
│   ├── server.py          # Serwer i generator stron statycznych
│   ├── config.py          # Konfiguracja aplikacji
│   ├── templates/         # Szablony HTML (Jinja2)
│   └── statics/           # Pliki statyczne (CSS, JS, obrazy, ikony)
├── organizations/         # Pliki YAML z danymi organizacji
├── .github/               # GitHub Actions i szablony
├── tailwind.config.js     # Konfiguracja Tailwind CSS
├── package.json           # Zależności Node.js
└── pyproject.toml         # Zależności Python (uv)
```

## 🛠️ Rozwój lokalny

### Wymagania
- **uv** - zarządzanie zależnościami Python
- **Node.js 18+** - do budowania stylów CSS

### Konfiguracja środowiska

```bash
# Klonowanie repozytorium
git clone https://github.com/wyslijco/wyslijco.github.io.git
cd wyslijco.github.io

# Instalacja zależności Python
uv sync

# Instalacja zależności Node.js
npm install
```

### Uruchomienie w trybie deweloperskim

```bash
# Terminal 1: Budowanie stylów CSS (tryb obserwacji)
npm run css

# Terminal 2: Serwer Flask
ORGANIZATIONS_DIR_PATH=organizations ORGANIZATIONS_SLUG_FIELD_NAME=adres uv run python site/server.py
```

Aplikacja będzie dostępna pod adresem: http://localhost:5000

### Budowanie wersji produkcyjnej

```bash
# Budowanie stylów CSS
npm run build

# Generowanie stron statycznych
uv run python site/server.py build
```

## 📝 Dodawanie organizacji

### Format pliku YAML

Każda organizacja powinna mieć plik `.yaml` w katalogu `organizations/`:

```yaml
nazwa: "Przykładowa Fundacja"
adres: "przykladowa-fundacja"
strona: "https://example.org"
krs: "1234567890"
dostawa:
  ulica: "ul. Główna 1"
  kod: "00-001"
  miasto: "Warszawa"
  telefon: "+48 123 456 789"
produkty:
  - nazwa: "Żywność dla schroniska"
    link: "https://example.org/zywnosc"
    opis: "Karma dla psów i kotów"
  - nazwa: "Materiały biurowe"
    link: "https://example.org/biuro"
```

### Sposoby dodawania organizacji

#### Opcja 1: Formularz GitHub Issue (zalecana dla organizacji)

Jeśli nie masz doświadczenia z kodem, skorzystaj z **[formularza zgłoszenia organizacji](https://github.com/wyslijco/wyslijco.github.io/issues/new/choose)**:

1. **Wybierz "Zgłoszenie organizacji"** z dostępnych szablonów Issue
2. **Wypełnij formularz** z danymi organizacji:
   - Nazwa organizacji i strona internetowa
   - Numer KRS (10 cyfr)
   - Propozycja adresu strony (slug)
   - Pełne dane dostawy (adres, telefon, email)
   - Opcjonalny kod paczkomatu
3. **Wyślij zgłoszenie** - automatycznie zostanie utworzony Issue
4. **Poczekaj na weryfikację** - zespół skontaktuje się przez oficjalne kanały organizacji

#### Opcja 2: Pull Request (dla osób technicznych)

1. **Przygotuj dane** - zbierz wszystkie wymagane informacje o organizacji
2. **Stwórz plik YAML** - zgodnie z formatem poniżej
3. **Zweryfikuj dane** - upewnij się, że numer KRS jest prawidłowy
4. **Stwórz Pull Request** - z nowym plikiem organizacji
5. **Przejdź weryfikację** - automatyczne sprawdzenie poprawności danych

### Wymagania dla organizacji

- Posiadanie aktywnego wpisu w rejestrze KRS
- Działalność charytatywna zgodna z misją platformy  
- Aktualne dane kontaktowe i adres dostawy
- Lista produktów z bezpośrednimi linkami zakupowymi

## 🤝 Współpraca

Projekt jest otwarty na współpracę! Możesz pomóc na różne sposoby:

### Dla programistów
- Rozwój funkcjonalności platformy
- Optymalizacja wydajności
- Poprawki błędów
- Testy automatyczne

### Dla organizacji
- Dodawanie nowych organizacji
- Aktualizacja danych istniejących organizacji
- Feedback o funkcjonalności platformy

### Dla użytkowników
- Zgłaszanie błędów i problemów
- Sugestie nowych funkcjonalności
- Rozpowszechnianie informacji o platformie

Szczegółowe informacje znajdziesz w pliku [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 Licencja

Projekt udostępniony na licencji określonej w pliku [LICENSE](LICENSE).

## 🆘 Pomoc i kontakt

- **Issues**: [GitHub Issues](https://github.com/wyslijco/wyslijco.github.io/issues) - zgłaszanie błędów i sugestii
- **Dokumentacja**: [GitHub Wiki](https://github.com/wyslijco/wyslijco.github.io/wiki) - szczegółowa dokumentacja

---

**💝 Wyślij.co! Pomaganie nigdy nie było tak proste.**
