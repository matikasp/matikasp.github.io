import os
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
    target_table = soup.find("table", {"id": "top20"})

    if target_table is None:
        print("Nie znaleziono tabeli TIOBE Index.")
        exit(1)

    rows = target_table.find_all("tr")
    languages = []
    # Pomijamy pierwszy wiersz nagłówkowy
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 6:
            rank = cols[0].get_text(strip=True)
            language = cols[4].get_text(strip=True)
            rating = cols[5].get_text(strip=True)
            change = cols[6].get_text(strip=True)
            languages.append({
                "rank": rank,
                "language": language,
                "rating": rating,
                "change": change
            })
    return languages

def search_additional_info(query):
    """Wyszukuje dodatkowe informacje dla danego zapytania przy użyciu duckduckgo_search."""
    ddgs = ddg()
    results = ddgs.text(query, max_results=1)
    if results:
        return results[0]
    return None

def sanitize_filename(name):
    """Sanitizes the filename by replacing problematic characters."""
    return name.lower().replace(' ', '_').replace('/', '_').replace('\\', '_')

def generate_markdown(languages, output_dir="languages", main_filename="index.md"):
    """Generuje pliki Markdown z tabelą i dodatkowymi informacjami dla każdego języka."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(main_filename, "w", encoding="utf-8") as main_file:
        main_file.write("---\n")
        main_file.write("layout: default\n")
        main_file.write("title: Lista języków programowania (TIOBE Index)\n")
        main_file.write("---\n\n")
        main_file.write("# Lista języków programowania (TIOBE Index)\n\n")
        main_file.write("| Ranking | Język | Rating | Zmiana |\n")
        main_file.write("|---------|-------|--------|--------|\n")
        for lang in languages:
            main_file.write(f"| {lang['rank']} | [{lang['language']}](./{output_dir}/{sanitize_filename(lang['language'])}.html) | {lang['rating']} | {lang['change']} |\n")
        main_file.write("\n\n")

    for lang in languages:
        filename = os.path.join(output_dir, f"{sanitize_filename(lang['language'])}.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"---\n")
            f.write(f"title: {lang['language']}\n")
            f.write(f"layout: default\n")
            f.write(f"---\n\n")
            f.write(f"# {lang['language']}\n\n")
            f.write(f"**Ranking:** {lang['rank']}\n\n")
            f.write(f"**Rating:** {lang['rating']}\n\n")
            f.write(f"**Zmiana:** {lang['change']}\n\n")

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
    print("Pliki markdown zostały wygenerowane.")

if __name__ == "__main__":
    main()