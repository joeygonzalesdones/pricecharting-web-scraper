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

    game_count = get_game_count(driver)
    print(f"Game count: {game_count}")

    element = driver.find_element(by=By.XPATH, value="//*[@id='console-header']/p/b")
    print(f"element.text: '{element.text}'")
    item_count = element.text.split(" / ")[1].split()[0]
    print(f"item_count: '{item_count}'")

    # for _ in range(20):
    #     rows = driver.find_elements(by=By.XPATH, value="//*[@id='games_table']/tbody/tr")
    #     print(f"{len(rows)} rows loaded")
    #     ActionChains(driver).send_keys_to_element(rows[0], Keys.END).perform()
    #     time.sleep(0.5)

    return


def main_old():
    driver = webdriver.Chrome()
    driver.get(PRICECHARTING_URL)
    driver.implicitly_wait(2)

    game_count = get_game_count(driver)

    games_table = driver.find_element(by=By.ID, value="games_table")
    game_items = load_items(driver, games_table, game_count)

    parsed_game_data = [parse_item(item, popularity_rank) for popularity_rank, item in enumerate(game_items)]

    driver.quit()
    print(f"Parsed {len(parsed_game_data)} / {game_count} items.")
    print(f"First item: {parsed_game_data[0]}")
    print(f"Last item: {parsed_game_data[-1]}")


def get_game_count(driver: WebDriver) -> int:
    element = driver.find_element(by=By.XPATH, value="//*[@id='console-header']/p/b")
    game_count = element.text.split(" / ")[1].split()[0]

    if game_count is None:
        raise RuntimeError('Game count ("You own: ### / ### items") not found')
    if not game_count.isdigit():
        raise RuntimeError(f'Game count "{game_count}" not a valid number')

    return int(game_count)


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
