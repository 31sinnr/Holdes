import requests
from bs4 import BeautifulSoup
from requestor import Requestor
import style as s

GITHUB_API_URL = "https://api.github.com/repos/31sinnr/Holdes/releases/latest"
LOCAL_VERSION = "1.2"

def get_latest_release_tag():
    try:
        response = requests.get(GITHUB_API_URL, timeout=5)
        if response.status_code == 200:
            return response.json().get("tag_name", "")
    except requests.RequestException as e:
        return
    return None

def check_version():
    latest = get_latest_release_tag()
    if latest != LOCAL_VERSION:
        print(f"Доступна новая версия: {s.Colors.GREEN}{LOCAL_VERSION}{s.Colors.RESET}")
        print(f"Скачать можно тут: {s.Colors.BLUE}https://github.com/31sinnr/Holdes/releases/latest{s.Colors.RESET}\n")

check_version()

def get_product(url):
    try:
        response = Requestor.make_request(url, True)

        if not response:
            s.error("Ошибка при загрузке страницы.")
            return

        soup = BeautifulSoup(response, 'html.parser')
        params_block = soup.find("div", class_="params-list params-list--in-product")
        
        if not params_block:
            s.warning("Не удалось найти блок с характеристиками.")
            return

        items = params_block.find_all("div", class_="params-list__item")
        with open("product.txt", "w", encoding="utf-8") as f:
            f.write("Характеристики товара:\n\n")

            for item in items:
                name_div = item.find("div", class_="params-list__item-name")
                value_div = item.find("div", class_="params-list__item-value")
                
                if value_div and value_div.find("img"):
                    img_tag = value_div.find("img")
                    src_value = img_tag.get("src", "")

                    if src_value == "/img/pres_ico.png":
                        value_text = "да"
                    else:
                        value_text = "нет"

                    name_text = name_div.get_text(strip=True) if name_div else "—"
                    prefix = "• "

                elif "params-list__item--caption" in item.get("class", []):
                    name_text = item.get_text(strip=True)
                    value_text = "" 
                    prefix = ""
                else:
                    if name_div:
                        for el in name_div.select(".params-list__item-name-widget, .d-none"):
                            el.decompose()
                        name_text = name_div.get_text(" ", strip=False)
                    else:
                        name_text = "—"

                    value_span = value_div.find("span") if value_div else None
                    value_text = value_span.get_text(strip=True) if value_span else "—"

                    name_text = name_text.replace("\n", "").replace("\r", "")
                    name_text = name_text.replace('\xa0', ' ')  

                    value_text = value_text.replace("\n", "").replace("\r", "")
                    value_text = value_text.replace('\xa0', ' ') 

                    if name_text.startswith("       "):
                        prefix = "  • "
                    else:
                        prefix = "• "

                    value_text = value_text.strip()
                    name_text = name_text.strip()

                line = f"{prefix}{name_text}: {value_text}"
                f.write(line + "\n")
            s.success("Характеристики товара добавлены в product.txt")

    except requests.exceptions.RequestException as e:
        s.error(f"Ошибка при загрузке страницы: {e}")

url = input(f"Введите ссылку на товар: {s.Colors.BLUE}")
print(f"{s.Colors.RESET}")
get_product(url)
