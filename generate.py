import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS as ddg

def fetch_tiobe_page(url):
    """Pobiera zawartość strony TIOBE Index."""
    response = requests.get(url)
    if response.status_code != 200:
        print("Błąd pobierania strony!")
        exit(1)
    return response.text

def parse_table(html):
    """Parsuje stronę HTML i wyciąga dane z tabeli zawierającej listę języków."""
    soup = BeautifulSoup(html, "html.parser")
    target_table = None

    # Szukamy tabeli, która zawiera nagłówek "Programming Language"
    tables = soup.find_all("table")
    for table in tables:
        if table.find("th") and "Programming Language" in table.get_text():
            target_table = table
            break

    if target_table is None:
        print("Nie znaleziono tabeli TIOBE Index.")
        exit(1)

    rows = target_table.find_all("tr")
    languages = []
    # Pomijamy pierwszy wiersz nagłówkowy
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 4:
            rank = cols[0].get_text(strip=True)
            language = cols[1].get_text(strip=True)
            rating = cols[2].get_text(strip=True)
            change = cols[3].get_text(strip=True)
            languages.append({
                "rank": rank,
                "language": language,
                "rating": rating,
                "change": change
            })
    return languages

def search_additional_info(query):
    """Wyszukuje dodatkowe informacje dla danego zapytania przy użyciu duckduckgo_search."""
    results = ddg().text(query)
    if results:
        return results[0]
    return None

def generate_markdown(languages, filename="programming_languages.md"):
    """Generuje plik Markdown z tabelą i dodatkowymi informacjami dla każdego języka."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Lista języków programowania (TIOBE Index)\n\n")
        f.write("| Ranking | Język | Rating | Zmiana |\n")
        f.write("|---------|-------|--------|--------|\n")
        for lang in languages:
            f.write(f"| {lang['rank']} | {lang['language']} | {lang['rating']} | {lang['change']} |\n")
        f.write("\n\n")

        # Dla każdego języka generujemy sekcję z dodatkowymi informacjami
        for lang in languages:
            f.write(f"## {lang['language']}\n\n")
            query = f"{lang['language']} programming language"
            info = search_additional_info(query)
            if info:
                f.write(f"**Tytuł:** {info.get('title', 'N/A')}\n\n")
                f.write(f"**Link:** {info.get('href', 'N/A')}\n\n")
                f.write(f"**Opis:** {info.get('body', 'N/A')}\n\n")
            else:
                f.write("Brak dodatkowych informacji.\n\n")

def main():
    url = "https://www.tiobe.com/tiobe-index/"
    html = fetch_tiobe_page(url)
    languages = parse_table(html)
    generate_markdown(languages)
    print("Plik markdown został wygenerowany jako 'programming_languages.md'.")

if __name__ == "__main__":
    main()
