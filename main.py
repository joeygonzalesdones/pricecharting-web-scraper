from selenium import webdriver
from selenium.webdriver.common.by import By

PRICECHARTING_URL = "https://www.pricecharting.com/console/gamecube"


def main():
    driver = webdriver.Chrome()
    driver.get(PRICECHARTING_URL)
    print(f"Driver title: {driver.title}")
    driver.implicitly_wait(2)

    games_table = driver.find_element(by=By.ID, value="games_table")
    games_table_body = games_table.find_element(by=By.TAG_NAME, value="tbody")
    games_table_rows = games_table_body.find_elements(by=By.TAG_NAME, value="tr")

    for index, row in enumerate(games_table_rows):
        print(f"-------------------- Row {index} --------------------")
        row_data = row.find_elements(by=By.TAG_NAME, value="td")
        for column_index, value in enumerate(row_data):
            print(f"* Column {column_index}: '{value.text}'")

    driver.quit()


if __name__ == "__main__":
    main()
