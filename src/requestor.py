import requests, json, os, time, uuid, tldextract, sys
import undetected_chromedriver as uc
from urllib.parse import urlparse
import style as s

class Requestor:

    @staticmethod
    def load_captcha_data(url):
        domain = Requestor.extract_domain(url)
        filename = f"{domain}.STRKR" 
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return json.load(file)
        return None

    @staticmethod
    def save_captcha_data(url, user_agent, cookies):
        domain = Requestor.extract_domain(url)
        filename = f"{domain}.STRKR" 
        data = {"user_agent": user_agent, "cookies": cookies}
        with open(filename, "w") as file:
            json.dump(data, file)

    @staticmethod
    def extract_domain(url, bWithProtocol=False):
        parsed_url = urlparse(url)
        extracted = tldextract.extract(parsed_url.netloc)
        base_domain = f"{extracted.domain}.{extracted.suffix}"
        if bWithProtocol:
            return f"{parsed_url.scheme}://{base_domain}"
        return base_domain

    @staticmethod
    def start_browser(url):
        domain = Requestor.extract_domain(url)
        ShortUrl = Requestor.extract_domain(url, True)
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options, headless=False)
        driver.get(ShortUrl)
        time.sleep(7)

        try:
            user_agent = driver.execute_script("return navigator.userAgent;")
            cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

            if not cookies:
                s.error(f"Не удалось собрать cookies для домена {domain}")
            else:
                s.success(f"Собраны cookies для домена {domain}")
        except Exception as e:
            s.error(f"Ошибка при извлечении данных: {e}")

        if cookies:
            Requestor.save_captcha_data(url, user_agent, cookies)
        else:
            s.error("Ошибка при сохранении cookies, повторите попытку.")

        driver.quit()

    @staticmethod
    def make_request(url, bDoBypass=False, bResetCookie=False):
        if not url.lower().startswith(('http://', 'https://')):
            url = 'https://' + url  

        if bResetCookie:
            Requestor.start_browser(url)
            captcha_data = Requestor.load_captcha_data(url)

        domain = Requestor.extract_domain(url)
        session = requests.Session()
        urlForHeaders = url

        if "coin-stats.com" in url:
            urlForHeaders = "coinstats.com"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 OPR/118.0.0.0 (Edition Yx GX)",
            "Referer": urlForHeaders,
            "Origin": urlForHeaders,
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=1, i",
            "x-language-code": "en",
            "x-app-appearance": "dark",
            "platform": "web",
            "if-none-match": '',
            "Uuid": str(uuid.uuid4())
        }

        if bDoBypass:
            captcha_data = Requestor.load_captcha_data(url)

            if not captcha_data:
                s.warning(f"Cookies для домена {domain} не найдены. Запускаем браузер для их получения...")
                Requestor.start_browser(url)
                captcha_data = Requestor.load_captcha_data(url)

            if captcha_data is None:
                s.error("Ошибка: cookies не загружены. Повторите попытку.")
                return None

            session.cookies.update(captcha_data["cookies"])
            headers["User-Agent"] = captcha_data["user_agent"]

        try:
            response = session.get(url, headers=headers)

            if response.status_code == 403:

                if not bDoBypass: 
                    s.warning(f"Доступ запрещен. Перезапускаем браузер но уже с куками {domain}...")
                    return Requestor.make_request(url, True)
                
                elif bDoBypass and not bResetCookie:
                    s.warning(f"Доступ запрещен. Перезапускаем браузер для обновления cookies для {domain}...")
                    return Requestor.make_request(url, True, True) 

                s.error(f"Ошибка: Доступ по-прежнему запрещен для {domain}.")
                return None

            return response.text

        except requests.exceptions.RequestException as e:
            s.error(f"Ошибка при запросе: {e}")
            return None
