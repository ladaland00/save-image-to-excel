import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException


def closeModal():
    try:
        closeModal = driver.find_element(
            By.XPATH, "//*[contains(@class, 'leadinModal-close')]")
        print("CLICK Modal")
        actions.move_to_element(closeModal).click(closeModal).perform()
    except NoSuchElementException:
        print("no Consent")


def cookiesConsent():
    try:
        Consent = driver.find_element(
            By.XPATH, "//*[contains(@id, 'hs-eu-cookie-confirmation')]")
        try:
            ConsentBTN = Consent.find_element(
                By.XPATH, "//*[contains(@id, 'hs-eu-confirmation-button')]")
            print("CLICK Consent")
            actions.move_to_element(ConsentBTN).click(ConsentBTN).perform()
        except NoSuchElementException:
            print("no Consent")
    except NoSuchElementException:
        print("no Consent")


# define custom options for the Selenium driver
options = Options()

options.add_argument('--disable-blink-features=AutomationControlled')
# Define search parameters
searchPhrase = "laptop"
homeUrl = "https://morrisandco.sandersondesigngroup.com/search/wallpaper/?q=wallpaper&Page=1"
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)
actions = ActionChains(driver)
# Visit your target site
print("Go to Home Page")
print("Loading...")
driver.get(homeUrl)
time.sleep(10)
cookiesConsent()
cardData = []



def scrapData(indexPage):
    listInfo = []
    listAllData = driver.find_elements(
        By.XPATH, "//ul[contains(@class, 'products-grid')]/li")
    for index, listData in enumerate(listAllData):
        try:
            wallpaperClick = listData.find_elements(
                By.XPATH, "./div/div[contains(@class, 'product-swatches-container')]/ul[contains(@class, 'product-swatches')]/li")

            try:
                nameWallPaper = listData.find_element(
                    By.XPATH, "./div/div[contains(@class, 'product-info')]/div[contains(@class, 'product-title')]").text
            except NoSuchElementException:
                print("Not Showing nameWallPaper")
                nameWallPaper = ""
            info = {
                "nameWallPaper": nameWallPaper
            }
            print(len(wallpaperClick))
            if (len(wallpaperClick) > 0):
                for indexColor, listColor in enumerate(wallpaperClick):
                    actions.move_to_element(
                        listColor).click(listColor).perform()
                    try:
                        nameColor = listData.find_element(
                            By.XPATH, "./div/div[contains(@class, 'product-info')]/div[contains(@class, 'description')]").text
                    except NoSuchElementException:
                        print("Not Showing nameColor")
                        nameColor = ""
                    try:
                        imagePath = listData.find_element(
                            By.XPATH, "./div/a/div/img")
                        imgSource = imagePath.get_attribute("src")

                        info["name-color-"+str(indexColor)] = nameColor
                        info["image-"+str(indexColor)] = imgSource

                    except Exception as e:
                        print(f"Error processing image: {e}")
                    print(str(indexColor+1) + "/" +
                              str(len(wallpaperClick)))
                    print(str(index+1) + "/" + str(len(listAllData)))
                    print("Start scrap page -", (int(indexPage)+1))
            else:
                try:
                    nameColor = listData.find_element(
                        By.XPATH, "./div/div[contains(@class, 'product-info')]/div[contains(@class, 'description')]").text
                except NoSuchElementException:
                    print("Not Showing nameColor")
                    nameColor = ""
                try:
                    imagePath = listData.find_element(
                        By.XPATH, "./div/a/div/img")
                    imgSource = imagePath.get_attribute("src")

                    info["name-color-"+str(0)] = nameColor
                    info["image-"+str(0)] = imgSource

                except Exception as e:
                    print(f"Error processing image: {e}")
                print(str(1) + "/" + str(len(wallpaperClick)))
                print(str(index+1) + "/" + str(len(listAllData)))
                print("Start scrap page -", (int(indexPage)+1))

            listInfo.append(info)
        except NoSuchElementException:
            print("one image")

    return listInfo


def scrapePage():
    global cardData
    try:
        wait.until(EC.visibility_of_element_located(
            (By.ID, "main-content")))
        time.sleep(10)
        closeModal()

        try:
            pagination = driver.find_element(By.ID, "pagination")
            indexPage = pagination.get_attribute("current-page")
            pageCardData = scrapData(indexPage)
            cardData = cardData+pageCardData
            print("Find next page")
            try:
                # nextBtn = driver.find_element(By.CLASS_NAME, "nextPage")
                # driver.execute_script("arguments[0].scrollIntoView(true);", nextBtn)
                script = """
            var xPathRes = document.evaluate('//li[@class="nextPage"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            var nextBtn = xPathRes.singleNodeValue;

            if (nextBtn) {
                nextBtn.click();
            } else {
                throw new Error('Element not found');
            }
            """
                driver.execute_script(script)
                time.sleep(2)
                scrapePage()
            except NoSuchElementException:
                print("No Btn next")
            except TimeoutException:
                print("Not Showing next")
            except JavascriptException:
                print("JavaScript error:")
        except TimeoutException:
            print("Not Showing Btn")
    except TimeoutException:
        print("Time out main-content")
    except NoSuchElementException:
        print("Not Showing main-content")


# Start scraping from the initial page
scrapePage()
print("cardData --- ", cardData)

# # Save the scraped data to a file
outputFileName = "scrapedData.json"
with open(outputFileName, "w", encoding='utf-8') as file:
    json.dump({"data": cardData}, file, indent=4, ensure_ascii=False)

# print("Data saved to", outputFileName)
df = pd.DataFrame(cardData)
df.to_csv('scrapedData.csv', index=False)

# Release the resources allocated by Selenium and shut down the browser
print("Close browser")
driver.quit()
