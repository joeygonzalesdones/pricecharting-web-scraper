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
    print(f"Total # games: {game_count}")

    start_time = time.time()
    game_table_rows = load_games(driver, game_count)
    elapsed_time = time.time() - start_time
    total_games_loaded = len(game_table_rows)

    print(f"Loaded {total_games_loaded}/{game_count} games in {elapsed_time:.3f} seconds")
    print(f"({elapsed_time/total_games_loaded} seconds/game)")
    print()
    print(f"First game text: '{game_table_rows[0].text}'")
    print(f"Last game text: '{game_table_rows[-1].text}'")


def get_game_count(driver: WebDriver) -> int:
    element = driver.find_element(by=By.XPATH, value="//*[@id='console-header']/p/b")
    game_count = element.text.split(" / ")[1].split()[0]

    if game_count is None:
        raise RuntimeError('Game count ("You own: ### / ### items") not found')
    if not game_count.isdigit():
        raise RuntimeError(f'Game count "{game_count}" not a valid number')

    return int(game_count)


def load_games(driver: WebDriver, game_count: int) -> List[WebElement]:
    game_table_rows = driver.find_elements(by=By.XPATH, value="//*[@id='games_table']/tbody/tr")
    while len(game_table_rows) < game_count:
        print(f"{len(game_table_rows)} games loaded")
        ActionChains(driver).send_keys_to_element(game_table_rows[0], Keys.END).perform()
        time.sleep(1)
        game_table_rows = driver.find_elements(by=By.XPATH, value="//*[@id='games_table']/tbody/tr")
    return game_table_rows


def parse_game_data(game_item: WebElement, popularity_rank: Optional[int] = None) -> GameData:
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
