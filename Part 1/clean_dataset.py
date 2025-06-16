import os
import sys
import re
import json

def extract_href_url(html_content: str):
    """
    Extracts the URL from an HTML anchor tag.

    Args:
        html_content (str): The HTML content containing the anchor tag.

    Returns:
        str: The extracted URL or an empty string if no URL is found.
    """
    pattern = r'<a\s+[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>.*?</a>'

    match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)

    if match:
        return match.group(1)
    return None

def clean_html_tags(text: str) -> str:
    """
    Removes HTML tags from the text.

    Args:
        text (str): The input text containing HTML tags.

    Returns:
        str: The text with HTML tags removed.
    """
    text = re.sub(r'<(?!/?a\b)[^>]*>', '', text)
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<(b|i|em|strong|u)>(.*?)</\1>', r'\2', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', text, flags=re.IGNORECASE | re.DOTALL)

    return text.strip()

def clean_string(text: str) -> str:
    """Cleans the input text by removing unwanted characters and HTML tags.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The cleaned text.
    """
    char_map = {
        '&#39;': "'",
        '&#34;': '"',
        '&#38;': '&',
        '&#60;': '<',
        '&#62;': '>',
        '&#160;': ' ',
        '&#233;': 'é',
        '&#8364;': '€',
        '&#8217;': '’',
        '&#8220;': '“',
        '&#8221;': '”',
        '&#8211;': '–',
        '&#8212;': '—',
        '&#8230;': '…',
        '&#8218;': '‚',
        '&#8222;': '„',
        '&#8482;': '™',
        '&#174;': '®',
        '&#169;': '©',
        '&#8734;': '∞',
        '&#13243;': '㌻',
        '\n\n': ''
    }

    for entity, char in char_map.items():
        text = text.replace(entity, char)

    # Replace anchor tags with their href URLs
    find_all_atag = r'<a\s+[^>]*>.*?</a>'
    matches = re.findall(find_all_atag, text, re.IGNORECASE | re.DOTALL)

    for match in matches:
        url = extract_href_url(match)
        if url:
            text = text.replace(match, url)

    # Remove HTML tags (except anchor tags which are already handled above)
    text = clean_html_tags(text)

    return text.strip()


def clean_json_recursively(obj):
    """Nettoie récursivement les valeurs dans un objet JSON"""
    if isinstance(obj, dict):
        return {k: clean_json_recursively(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json_recursively(item) for item in obj]
    elif isinstance(obj, str):
        return clean_string(obj)
    else:
        return obj

def clean_file(file_name: str) -> None:
    """
    Cleans the input JSON file properly maintaining JSON structure.
    Handles both regular JSON and JSONL (newline-delimited JSON) formats.
    """
    with open(file_name, 'r', encoding='utf-8') as file:
        content = file.read().strip()

    # Checking if the content is JSONL or a single JSON object
    lines = content.split('\n')

    try:
        # Trying to load as a single JSON
        data = json.loads(content)
        is_jsonl = False
    except json.JSONDecodeError:
        # If it fails, try to process as JSONL
        try:
            data = []
            for line_num, line in enumerate(lines, 1):
                if line.strip():  # Ignorer les lignes vides
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Erreur JSON ligne {line_num}: {e}")
                        return
            is_jsonl = True
        except Exception as e:
            print(f"Erreur lors du parsing JSONL: {e}")
            return

    # Recursive cleaning of JSON data
    cleaned_data = clean_json_recursively(data)

    # Create cleaned filename
    base_name = os.path.splitext(file_name)[0]
    extension = os.path.splitext(file_name)[1]
    cleaned_file_name = f"cleaned-{os.path.basename(base_name)}{extension}"

    # Write cleaned JSON to new file
    with open(cleaned_file_name, 'w', encoding='utf-8') as file:
        if is_jsonl:
            # Writing in JSONL format (one object per line)
            for item in cleaned_data:
                json.dump(item, file, ensure_ascii=False, separators=(',', ':'))
                file.write('\n')
        else:
            # Writing in standard JSON format
            json.dump(cleaned_data, file, ensure_ascii=False, indent=2)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python clean_dataset.py <file_name>")
        sys.exit(1)

    file_name = sys.argv[1]
    clean_file(file_name)
    print(f"File '{file_name}' cleaned successfully.")
