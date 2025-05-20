import time
from dataclasses import dataclass
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

CONSOLE = "gamecube"
PRICECHARTING_URL = f"https://www.pricecharting.com/console/{CONSOLE}?sort=popularity&exclude-hardware=true"


@dataclass
class GameData:
    """Represents a video game item and its estimated prices."""

    title: str
    popularity_rank: Optional[int]
    price_loose: Optional[float]
    price_cib: Optional[float]
    price_new: Optional[float]


def main():
    driver = webdriver.Chrome()
    driver.get(PRICECHARTING_URL)
    driver.implicitly_wait(2)

    item_count = get_item_count(driver)

    games_table = driver.find_element(by=By.ID, value="games_table")
    game_items = load_items(driver, games_table, item_count)

    parsed_game_data = [parse_item(item, popularity_rank) for popularity_rank, item in enumerate(game_items)]

    driver.quit()
    print(f"Parsed {len(parsed_game_data)} / {item_count} items.")
    print(f"First item: {parsed_game_data[0]}")
    print(f"Last item: {parsed_game_data[-1]}")


def get_item_count(driver: WebDriver) -> int:
    console_header = driver.find_element(by=By.ID, value="console-header")
    console_header_elements = console_header.find_elements(by=By.TAG_NAME, value="p")

    item_count = None
    for element in console_header_elements:
        if element.text.startswith("You own:"):
            item_count = element.text.split(" / ")[1].split()[0]

    if item_count is None:
        raise RuntimeError('Item count element ("You own: ### / ### items") not found')
    if not item_count.isdigit():
        raise RuntimeError(f'Item count element "{item_count}" not a valid number')

    return int(item_count)


def load_items(driver: WebDriver, games_table: WebElement, item_count: int) -> List[WebElement]:
    games_table_body = games_table.find_element(by=By.TAG_NAME, value="tbody")
    games_table_rows = games_table_body.find_elements(by=By.TAG_NAME, value="tr")

    items_currently_loaded = len(games_table_rows)
    while items_currently_loaded < item_count:
        ActionChains(driver).send_keys_to_element(games_table, Keys.END).perform()
        time.sleep(1)
        games_table_rows = games_table_body.find_elements(by=By.TAG_NAME, value="tr")
        items_currently_loaded = len(games_table_rows)

    return games_table_rows


def parse_item(game_item: WebElement, popularity_rank: Optional[int] = None) -> GameData:
    elements = game_item.find_elements(by=By.TAG_NAME, value="td")
    title = elements[1].text

    price_loose = None
    if elements[2].text:
        price_loose = _parse_price_string(elements[2].text)

    price_cib = None
    if elements[3].text:
        price_cib = _parse_price_string(elements[3].text)

    price_new = None
    if elements[4].text:
        price_new = _parse_price_string(elements[4].text)

    return GameData(title, popularity_rank, price_loose, price_cib, price_new)


def _parse_price_string(price_string: str) -> Optional[float]:
    value = None
    if price_string:
        value = float(price_string.lstrip("$").replace(",", ""))
    return value


if __name__ == "__main__":
    main()
