import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import time
import os
import shutil

download_dir = "/tmp"
os.makedirs(download_dir, exist_ok=True)

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

def update_packing_google_sheets(csv_file_path):
    try:
        if not os.path.exists(csv_file_path):
            print(f"Arquivo {csv_file_path} não encontrado.")
            return
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("hxh.json", scope)
        client = gspread.authorize(creds)
        sheet1 = client.open_by_url("https://docs.google.com/spreadsheets/d/1nMLHR6Xp5xzQjlhwXufecG1INSQS4KrHn41kqjV9Rmk/edit?gid=0#gid=0")
        worksheet1 = sheet1.worksheet("Base")
        df = pd.read_csv(csv_file_path)
        df = df.fillna("")
        worksheet1.clear()
        worksheet1.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"Arquivo enviado com sucesso para a aba 'Base'.")
        time.sleep(5)
    except Exception as e:
        print(f"Erro durante o processo: {e}")
        
async def login(page):
    await page.goto("https://spx.shopee.com.br/")
    try:
        await page.wait_for_selector('xpath=//*[@placeholder="Ops ID"]', timeout=15000)
        await page.fill('xpath=//*[@placeholder="Ops ID"]', 'Ops89710')
        await page.fill('xpath=//*[@placeholder="Senha"]', '@Shopee123')
        await page.click('xpath=/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/form/div/div/button')
        await page.wait_for_timeout(15000)
        try:
            await page.click('.ssc-dialog-close', timeout=5000)
        except:
            print("Nenhum pop-up foi encontrado.")
            await page.keyboard.press("Escape")
    except Exception as e:
        print(f"Erro no login: {e}")
        raise

async def get_data(page, download_dir):
    try:
        await page.goto("https://spx.shopee.com.br/#/queue-list")
        await page.wait_for_timeout(10000)
        await page.locator('xpath=/html/body/div[1]/div/div[2]/div[2]/div/div/div/div/div/div[2]/div[2]/div[2]/div/div[2]/span[2]/span/button').click()
        await page.wait_for_timeout(10000)
        await page.locator('xpath=//li[1]//span[1]//div[1]//div[1]//span[1]').click()
        await page.wait_for_timeout(10000)

        d3 = (datetime.now() - timedelta(days=7)).strftime("%Y/%m/%d")
        d1 = (datetime.now() + timedelta(days=1)).strftime("%Y/%m/%d")

        # Primeiro campo de data

        """
        date_input = await page.wait_for_selector('xpath=/html/body/div[6]/div[2]/div/div/div[3]/div[2]/div/form/div/div/div/span[2]/div/div[1]/span[1]/span/input', timeout=5000)
        #date_input = await page.wait_for_selector('input[placeholder="Data de início"]', timeout=5000)
        await date_input.click()
        await date_input.fill('')
        await date_input.type(d3)
        await page.wait_for_timeout(5000)
        """
        
        date_input = page.locator('input[placeholder="Data de início"]').nth(0)
        await date_input.wait_for(state="visible", timeout=10000)
        await date_input.click(force=True)
        await date_input.fill(d3)

        """
        # Segundo campo de data
        date_input2 = await page.wait_for_selector('xpath=/html/body/div[6]/div[2]/div/div/div[3]/div[2]/div/form/div/div/div/span[2]/div/div[1]/span[3]/span/input', timeout=5000)
        await date_input2.click()
        await date_input2.fill('')
        await date_input2.type(d1)
        await page.wait_for_timeout(5000)
        """

        date_input = page.locator('input[placeholder="Data final"]').nth(0)
        await date_input.wait_for(state="visible", timeout=10000)
        await date_input.click(force=True)
        await date_input.fill(d3)
        

        await page.locator('xpath=/html/body/div[5]/div[2]/div/div/div[1]/div').click()
        await page.wait_for_timeout(5000)

        await page.locator('xpath=/html/body/div[5]/div[2]/div/div/div[4]/div[2]/button[2]/span').click()
        await page.wait_for_timeout(15000)

        """
        # 👉 Botão de download
        async with page.expect_download() as download_info:
            await page.locator('xpath=/html/body/span/div/div[1]/div/span/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div[2]/button/span').click()
        download = await download_info.value
        download_path = os.path.join(download_dir, download.suggested_filename)
        await download.save_as(download_path)
        time.sleep(2)  # Pequeno delay para garantir o arquivo no sistema
        rename_downloaded_file(download_dir)
        """

        # Use async with para download
        async with page.expect_download() as download_info:
            #await page.wait_for_selector('xpath=/html/body/span/div/div[1]/div/span/div/div[2]/div[2]/div[1]/div/div[1]/div/div[1]/div[2]/button', timeout=30000)
            await page.locator('xpath=/html[1]/body[1]/span[1]/div[1]/div[1]/div[1]/span[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/button[1]/span[1]').click()
        download = await download_info.value
        download_path = os.path.join(DOWNLOAD_DIR, download.suggested_filename)
        await download.save_as(download_path)
        new_file_path = rename_downloaded_file(download_dir)

    except Exception as e:
        print(f"Erro ao coletar dados: {e}")
        raise

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox", "--disable-dev-shm-usage", "--window-size=1920,1080"])
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        try:
            await login(page)
            await get_data(page, download_dir)
            print("Download finalizado com sucesso.")
            await update_packing_google_sheets(csv_file_path)
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
