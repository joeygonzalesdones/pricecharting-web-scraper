from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

PRICECHARTING_URL = "https://www.pricecharting.com/console/gamecube"


def main():
    driver = webdriver.Chrome()
    driver.get(PRICECHARTING_URL)
    print(f"Driver title: {driver.title}")
    driver.implicitly_wait(2)

    item_count = get_item_count(driver)

    games_table = driver.find_element(by=By.ID, value="games_table")
    games_table_body = games_table.find_element(by=By.TAG_NAME, value="tbody")
    games_table_rows = games_table_body.find_elements(by=By.TAG_NAME, value="tr")

    for index, row in enumerate(games_table_rows):
        print(f"-------------------- Row {index} --------------------")
        row_data = row.find_elements(by=By.TAG_NAME, value="td")
        for column_index, value in enumerate(row_data):
            print(f"* Column {column_index}: '{value.text}'")

    print()
    print(f"Total count: {item_count} items")

    driver.quit()


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


if __name__ == "__main__":
    main()
