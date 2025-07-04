from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import os
import shutil

# Diretório de download para GitHub Actions
download_dir = "/tmp"

# Cria o diretório, se não existir
os.makedirs(download_dir, exist_ok=True)

# Configurações do Chrome para ambiente headless do GitHub Actions
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

# Configurações de download
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Inicializa o driver
driver = webdriver.Chrome(options=chrome_options)

def login(driver):
    driver.get("https://spx.shopee.com.br/")
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Ops ID"]')))
        driver.find_element(By.XPATH, '//*[@placeholder="Ops ID"]').send_keys('Ops89710')
        driver.find_element(By.XPATH, '//*[@placeholder="Senha"]').send_keys('@Shopee123')
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/form/div/div/button'))
        ).click()

        time.sleep(15)
        try:
            popup = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ssc-dialog-close"))
            )
            popup.click()
        except:
            print("Nenhum pop-up foi encontrado.")
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
    except Exception as e:
        print(f"Erro no login: {e}")
        driver.quit()
        raise

def get_data(driver):
    try:
        driver.get("https://spx.shopee.com.br/#/queue-list")
        time.sleep(15)
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div/div[2]/span[2]/span/button/span').click()
        time.sleep(15)
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/ul/li[1]/span/div/div/span'))
        ).click()
        time.sleep(15)

        # Datas formatadas
        d3 = (datetime.now() - timedelta(days=3)).strftime("%Y/%m/%d")
        d1 = (datetime.now() + timedelta(days=1)).strftime("%Y/%m/%d")  # Corrigido o nome da variável

        # Primeiro campo de data
        date_input = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div/div/div[3]/div[2]/div/form/div/div/div/span[2]/div/div[1]/span[1]/span/input')
        date_input.click()
        date_input.clear()
        date_input.send_keys(d3)
        time.sleep(5)

        # Segundo campo de data
        date_input2 = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div/div/div[3]/div[2]/div/form/div/div/div/span[2]/div/div[1]/span[3]/span/input')
        date_input2.click()
        date_input2.clear()
        date_input2.send_keys(d1)
        time.sleep(5)

        driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div/div/div[1]/div').click()
        time.sleep(5)

        driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div/div/div[4]/div[2]/button[2]/span').click()
        time.sleep(15)

        #driver.get("https://spx.shopee.com.br/#/taskCenter/exportTaskCenter")
        time.sleep(15)
        driver.finde_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/span/div/div').click
        time.sleep(5)
        driver.finde_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div[2]/div[2]/span/div/div').click

        # 👉 Botão de download
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/span/div/div[1]/div/span/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div[2]/button/span'))
        ).click()
        """
        # 👉 Botão de download
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="fms-container"]/div[2]/div[2]/div/div/div/div[1]/div[8]/div/div[1]/div/div[2]/div[1]/div[1]/div[2]/div/div/div/table/tbody[2]/tr[1]/td[7]/div/div/button'))
        ).click()
        """
        time.sleep(20)  # Aguarda o download
        rename_downloaded_file(download_dir)

    except Exception as e:
        print(f"Erro ao coletar dados: {e}")
        driver.quit()
        raise
        
def rename_downloaded_file(download_dir):
    try:
        files = [f for f in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, f))]
        files = [os.path.join(download_dir, f) for f in files]
        newest_file = max(files, key=os.path.getctime)

        current_hour = datetime.now().strftime("%H")
        new_file_name = f"QUEUE-{current_hour}.csv"
        new_file_path = os.path.join(download_dir, new_file_name)

        if os.path.exists(new_file_path):
            os.remove(new_file_path)

        shutil.move(newest_file, new_file_path)
        print(f"Arquivo salvo como: {new_file_path}")
    except Exception as e:
        print(f"Erro ao renomear o arquivo: {e}")

def main():
    try:
        login(driver)
        get_data(driver)
        print("Download finalizado com sucesso.")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
