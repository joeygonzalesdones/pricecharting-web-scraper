from selenium import webdriver

from scrape_console import scrape_console_page


def main():
    driver = webdriver.Chrome()
    pc_url = "https://www.pricecharting.com/console/gamecube?sort=popularity&exclude-hardware=true"
    driver.get(pc_url)
    driver.implicitly_wait(2)
    console_data = scrape_console_page(driver)
    driver.close()
    print(console_data)


if __name__ == '__main__':
    main()
