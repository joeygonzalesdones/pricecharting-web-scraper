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
    game_page_url: str
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
    print()

    start_time = time.time()
    game_table_rows = load_games_as_dom_elements(driver, game_count)
    elapsed_time = time.time() - start_time
    total_games_loaded = len(game_table_rows)

    print(f"Loaded {total_games_loaded}/{game_count} games in {elapsed_time:.3f} seconds")
    print(f"({elapsed_time/total_games_loaded} seconds/game)")
    print()
    print(f"First game text: '{game_table_rows[0].text}'")
    print(f"Last game text: '{game_table_rows[-1].text}'")
    print()

    start_time = time.time()
    parsed_game_data = [parse_game_data(element, rank) for rank, element in enumerate(game_table_rows)]
    elapsed_time = time.time() - start_time
    print(f"Parsed games in {elapsed_time:.3f} seconds")
    print()

    first_game = parsed_game_data[0]
    last_game = parsed_game_data[-1]
    print(f"First game: {first_game}")
    print(f"Last game: {last_game}")


def get_game_count(driver: WebDriver) -> int:
    element = driver.find_element(by=By.XPATH, value="//*[@id='console-header']/p/b")
    game_count = element.text.split(" / ")[1].split()[0]

    if game_count is None:
        raise RuntimeError('Game count ("You own: ### / ### items") not found')
    if not game_count.isdigit():
        raise RuntimeError(f'Game count "{game_count}" not a valid number')

    return int(game_count)


def load_games_as_dom_elements(driver: WebDriver, game_count: int) -> List[WebElement]:
    game_elements = driver.find_elements(by=By.XPATH, value="//*[@id='games_table']/tbody/tr")
    while len(game_elements) < game_count:
        print(f"{len(game_elements)} games loaded")
        ActionChains(driver).send_keys_to_element(game_elements[0], Keys.END).perform()
        time.sleep(1)
        game_elements = driver.find_elements(by=By.XPATH, value="//*[@id='games_table']/tbody/tr")
    return game_elements


def parse_game_data(game_element: WebElement, popularity_rank: Optional[int] = None) -> GameData:
    columns = game_element.find_elements(by=By.TAG_NAME, value="td")
    title_element = columns[1]
    title = title_element.text
    game_page_url = title_element.find_element(by=By.TAG_NAME, value="a").get_attribute(name="href")
    price_used = _parse_price_string(columns[2].text)
    price_cib = _parse_price_string(columns[3].text)
    price_new = _parse_price_string(columns[4].text)
    return GameData(title, game_page_url, popularity_rank, price_used, price_cib, price_new)


def _parse_price_string(price_string: str) -> Optional[float]:
    if price_string:
        return float(price_string.lstrip("$").replace(",", ""))
    return None


if __name__ == "__main__":
    main()
