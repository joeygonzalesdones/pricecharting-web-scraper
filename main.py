import time
from dataclasses import dataclass
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

CONSOLE = "gamecube"
LOADING_LOOP_SLEEP_DURATION = 1.0
PRICECHARTING_URL = f"https://www.pricecharting.com/console/{CONSOLE}?sort=popularity&exclude-hardware=true"


@dataclass
class GameData:
    """Groups data related to a specific video game. All price values are given
    in United States dollars (USD).

    :param title: The game's title
    :param game_page_url: URL of the game's dedicated page on PriceCharting
    :param popularity_rank: The game's rank when sorted by popularity for its console
    :param price_loose: The game's current market price in loose condition (cartridge/disk only)
        as estimated by PriceCharting
    :param price_cib: The game's current market price in complete-in-box condition
        as estimated by PriceCharting
    :param price_new: The game's current market price in brand-new condition
        as estimated by PriceCharting
    """

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

    start_time = time.time()
    game_table_rows = load_games_as_dom_elements(driver, game_count, LOADING_LOOP_SLEEP_DURATION)
    loading_duration = time.time() - start_time

    start_time = time.time()
    parsed_game_data = [parse_game_data(element, rank) for rank, element in
                        enumerate(game_table_rows)]
    parsing_duration = time.time() - start_time


def get_game_count(driver: WebDriver) -> int:
    """Parses the current game list page to find the total number of games available
    when the page is fully loaded.

    :param driver: The web browser controller
    :raises RuntimeError: If the game count is missing or not a valid number
    :return: The total number of games on the current page
    """

    element = driver.find_element(by=By.XPATH, value="//*[@id='console-header']/p/b")
    game_count = element.text.split(" / ")[1].split()[0]

    if game_count is None:
        raise RuntimeError('Game count ("You own: ___ / <game_count> items") not found')
    if not game_count.isdigit():
        raise RuntimeError(f'Game count "{game_count}" not a valid number')

    return int(game_count)


def load_games_as_dom_elements(
        driver: WebDriver,
        game_count: int,
        sleep_duration: float = 1.0
) -> List[WebElement]:
    """Retrieves the DOM elements on the current page that correspond to the data entries
    for each game.

    Rather than loading all content immediately, the page loads more content once the current
    bottom is reached. This function iteratively loads the available game entries, jumps to
    the end of the page to continue loading, and sleeps so the web server can catch up,
    stopping once the expected number of game entries have been loaded.

    :param driver: The web browser controller
    :param game_count: The number of games to load
    :param sleep_duration: The number of seconds to sleep between attempts to load more content.
    :return: A list of DOM elements, where each element contains data for a single game
    """

    game_elements = driver.find_elements(by=By.XPATH, value="//*[@id='games_table']/tbody/tr")
    while len(game_elements) < game_count:
        ActionChains(driver).send_keys_to_element(game_elements[0], Keys.END).perform()
        time.sleep(sleep_duration)
        game_elements = driver.find_elements(by=By.XPATH, value="//*[@id='games_table']/tbody/tr")
    return game_elements


def parse_game_data(game_element: WebElement, popularity_rank: Optional[int] = None) -> GameData:
    """Parses a specific game's DOM element into an object storing the relevant data.

    :param game_element: A DOM element corresponding to an individual game
    :param popularity_rank: The game's rank when sorted by popularity for its console
    :return: An object storing only the relevant data for the game
    """

    columns = game_element.find_elements(by=By.TAG_NAME, value="td")
    title_element = columns[1]
    title = title_element.text
    game_page_url = title_element.find_element(by=By.TAG_NAME, value="a").get_attribute(name="href")
    price_used = _parse_price_string(columns[2].text)
    price_cib = _parse_price_string(columns[3].text)
    price_new = _parse_price_string(columns[4].text)
    return GameData(title, game_page_url, popularity_rank, price_used, price_cib, price_new)


def _parse_price_string(price_string: str) -> Optional[float]:
    """Parses a string representing a price in USD into the corresponding floating point value.
    For example, `_parse_price_string("$1,234.56")` should return `1234.56`.

    :param price_string: A string representing a price in USD
    :return: The corresponding floating point value, or None if the input string is empty
    """

    if price_string:
        return float(price_string.lstrip("$").replace(",", ""))
    return None


if __name__ == "__main__":
    main()
