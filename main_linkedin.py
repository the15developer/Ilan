from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import re
from main import extract_deadline_from_linkedin
from reminder.email_reminder import send_reminder_email


# def extract_deadline_from_text(text):
#     # 1. Sentences with "son başvuru"
#     sentences = re.findall(r'(?:[!?,\n]\s*)?(son başvuru|kadar başvur)[^!?,\n]*[!?,]', text, flags=re.IGNORECASE)

#     for sentence in sentences:
#         match1 = re.search(r'(\d{1,2}\s(?:Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s\d{4})', sentence, flags=re.IGNORECASE)
#         if match1:
#             return match1.group(1)
#         match2 = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4})', sentence)
#         if match2:
#             return match2.group(1)
#         match3 = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', sentence)
#         if match3:
#             return match3.group(1)
#         match4 = re.search(r'(\d{4}-\d{1,2}-\d{1,2})', sentence)
#         if match4:
#             return match4.group(1)

#     return "Son başvuru tarihi bulunamadı"

# Clean the job URLs
def clean_linkedin_job_url(url):
    match = re.search(r"(https://www\.linkedin\.com/jobs/view/\d+)", url)
    if match:
        return match.group(1)
    return url  # fallback: if it somehow doesn't match, keep original






# --- Config ---
CHROME_DRIVER_PATH = "chromedriver.exe"  # update this!
USER_DATA_DIR = "C:/Users/Danny/AppData/Local/Google/Chrome/User Data"
PROFILE_DIR = "Profile 1"  # or "Profile 1"
JOBS_HOME_URL = "https://www.linkedin.com/jobs/"

# --- Setup ---
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
options.add_argument(f"--profile-directory={PROFILE_DIR}")

driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)
wait = WebDriverWait(driver, 10)

# --- Step 1: Go to jobs homepage ---
driver.get(JOBS_HOME_URL)
time.sleep(5)

# --- Step 2: Click on "Tümünü gör" ---
try:
    see_all_button = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Tümünü gör")))
    see_all_button.click()
    print("Clicked on 'Tümünü gör'")
except:
    print("Couldn't find 'Tümünü gör' button.")
    driver.quit()
    exit()

# --- Step 3: Wait for job listing page to load ---
time.sleep(5)

try:
    #search_box = wait.until(EC.visibility_of_element_located((By.ID, "jobs-search-box-keyword-id-ember468")))
    # Try this if `id` doesn't work
    search_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[aria-label='Ünvan, yetenek veya şirket ile arayın']")))

 # Log whether the element is interactable
    if search_box.is_displayed():
        print("The search box is visible.")
    else:
        print("The search box is not visible.")
    
    # Check if the search box is enabled (interactable)
    if search_box.is_enabled():
        print("The search box is enabled and can be interacted with.")
    else:
        print("The search box is not enabled.")


    search_box.clear()  # clear any existing text
    search_box.send_keys("Intern")  # enter the word "Intern"
    print("Entered 'Intern' into the search box.")

    # Simulate pressing the Enter key to trigger the search
    search_box.send_keys(Keys.RETURN)
    print("Search triggered by pressing Enter.")

except Exception as e:
    print(f"Couldn't find or interact with the search input box: {e}")
    driver.quit()
    exit()

time.sleep(5)

# --- Step 4: Smart scroll inside the specific div ---
# --- Step 4: Real-time Smart Scroll (small steps) inside the specific div and extract info ---

try:
    scrollable_div = driver.find_element(By.CLASS_NAME, "GDWMPYlbLLvJwwJkvOFRdwOcJxcoOxMsCHeyMglQ")

    processed_links = set()
    last_scroll_top = 0
    cleaned_links=[]

    while True:
        # Get all currently visible job links
        job_listings = scrollable_div.find_elements(By.CSS_SELECTOR, "div.artdeco-entity-lockup__title a")

        for job in job_listings:
            url = job.get_attribute("href")
            if url and url not in processed_links:
                clean_url = clean_linkedin_job_url(url)
                cleaned_links.append(clean_url)
                # Mark as processed early to avoid retrying if error
                processed_links.add(url)

                if clean_url:
                    print(f"Processing job: {clean_url}")
                    result = extract_deadline_from_linkedin(clean_url)
                    if result:
                        baslik, aciklama, tarih = result
                        print("Başlık:", baslik)
                        print("Tarih:", tarih)
                        print("Açıklama:", aciklama[:300], "...\n")
                    else:
                        print("No deadline data extracted from:", clean_url)
                else:
                    print("Failed to clean URL:", url)

        # Scroll **down by a little amount** (not full height!)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 300", scrollable_div)
        time.sleep(1.5)  # Shorter wait since it's a small scroll

        current_scroll_top = driver.execute_script("return arguments[0].scrollTop", scrollable_div)
        max_scroll_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

        # Check if scrolling doesn't change anymore -> end of list
        if current_scroll_top == last_scroll_top or current_scroll_top + scrollable_div.size['height'] >= max_scroll_height:
            print("Reached the end of the job list.")
            print("Processed :", len(cleaned_links), "jos listings.")
            break

        last_scroll_top = current_scroll_top

except Exception as e:
    print("Scrolling failed:", e)

