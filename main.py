import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()

def login():
    driver = webdriver.Edge()
    try:
        driver.get("https://php2d.kemdikbud.go.id/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login"))).send_keys(
            os.getenv("USERNAME_PPK"))
        driver.find_element(By.ID, "password").send_keys(os.getenv("PASSWORD_PPK"))
        WebDriverWait(driver, 120).until(EC.url_to_be("https://php2d.kemdikbud.go.id/daftar-subproposal-ketua"))
        print("Login Successful!")
        return driver
    except Exception as e:
        print(f"Gagal Login: {e}")
        driver.quit()
        return None


def crawl_logbook(driver, url):
    logbook_data = []
    page_num = 1

    driver.get(url)
    time.sleep(2)

    while True:
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".table-responsive tbody tr"))
            )
            table_rows = driver.find_elements(By.CSS_SELECTOR, ".table-responsive tbody tr")
        except Exception as e:
            print(f"Gagal menemukan tabel: {e}")
            break

        for i in range(len(table_rows)):
            retry_count = 0
            while retry_count < 3:
                try:
                    row = driver.find_elements(By.CSS_SELECTOR, ".table-responsive tbody tr")[i]
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) != 5:
                        print(f"Baris tidak valid dengan {len(cells)} sel. Melewati...")
                        break

                    row_data = process_main_row(cells)
                    process_modal(driver, cells[4], row_data)
                    process_attachments(driver, cells[4], row_data)

                    logbook_data.append(row_data)
                    break
                except StaleElementReferenceException:
                    print(f"Stale element, retry {retry_count}")
                    retry_count += 1
                    time.sleep(2)
                except Exception as e:
                    print(f"Error processing row: {str(e)}")
                    break

        try:
            next_page = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "li.page-item:not(.disabled) a[aria-label='Next »']"))
            )

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_page)
            time.sleep(0.5)

            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.page-item:not(.disabled) a[aria-label='Next »']"))
            )

            driver.execute_script("arguments[0].click();", next_page)
            page_num += 1

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".table-responsive tbody tr"))
            )
            time.sleep(1)

        except Exception as e:
            print(f"Tidak ada halaman selanjutnya: {str(e)}")
            break

    return logbook_data


def process_main_row(cells):
    row_data = {
        'no': cells[0].text.strip(),
        'waktu': cells[1].text.strip(),
        'validasi_dospem': get_validation_status(cells[2]),
        'validasi_pt': {
            'status': get_validation_status(cells[3]),
            'keterangan': cells[3].find_element(By.CLASS_NAME, "status-pill").get_attribute("data-title")
        },
        'aktivitas_ringkas': cells[4].find_element(By.TAG_NAME, "p").text.strip(),
        'attachments': [],
        'detail_logbook': {},
        'start_date': None
    }

    try:
        date_text = cells[1].text.strip().split('\n')[1]
        start_date_str = date_text[1:-1].split(' s.d ')[0].strip()
        start_date = datetime.strptime(start_date_str, "%d %b %Y")
        row_data['start_date'] = start_date.isoformat()
    except Exception as e:
        print(f"Gagal parsing tanggal: {str(e)}")
        row_data['start_date'] = "0000-00-00"

    return row_data


def get_validation_status(cell):
    pill = cell.find_element(By.CLASS_NAME, "status-pill")
    classes = pill.get_attribute("class").split()
    return classes[1] if len(classes) > 1 else 'unknown'


def process_modal(driver, cell, row_data):
    try:
        lihat_btn = cell.find_element(By.CSS_SELECTOR, "a[data-target='.modal-lihat-kegiatan']")
        driver.execute_script("arguments[0].click();", lihat_btn)

        modal = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "modal-lihat-kegiatan"))
        )

        WebDriverWait(modal, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "popupLihat"))
        )

        popup = modal.find_element(By.CLASS_NAME, "popupLihat")
        row_data['detail_logbook'] = extract_modal_data(popup)

        close_btn = modal.find_element(By.CSS_SELECTOR, ".modal-header button.close")
        driver.execute_script("arguments[0].click();", close_btn)
        WebDriverWait(driver, 10).until(EC.invisibility_of_element(modal))

    except Exception as e:
        print(f"Gagal memproses modal: {str(e)}")


def extract_modal_data(popup):
    detail = {}

    try:
        waktu_element = popup.find_element(By.CSS_SELECTOR, ".select2-selection__rendered")
        detail['waktu_kegiatan'] = waktu_element.get_attribute("title") or waktu_element.text.strip()
    except Exception as e:
        print(f"Error extracting waktu: {str(e)}")
        detail['waktu_kegiatan'] = "N/A"

    kunjungan = {}
    fields = [
        ('pt_berkunjung', 'lihat_pt_berkunjung_ke_lokasi_jumlah_kedatangan'),
        ('dospem_berkunjung', 'lihat_dospem_berkunjung_ke_lokasi_jumlah_kedatangan'),
        ('konsultasi_dosen', 'lihat_konsultasi_dosen'),
        ('tim_berkunjung_jumlah', 'lihat_tim_berkunjung_ke_lokasi_jumlah_kedatangan'),
        ('tim_berkunjung_orang', 'lihat_tim_berkunjung_ke_lokasi_jumlah_orang'),
        ('tokma_berkunjung_jumlah', 'lihat_tokma_berkunjung_ke_lokasi_jumlah_kedatangan'),
        ('tokma_berkunjung_orang', 'lihat_tokma_berkunjung_ke_lokasi_jumlah_orang'),
        ('poksar_berkunjung_jumlah', 'lihat_poksar_berkunjung_ke_lokasi_jumlah_kedatangan'),
        ('poksar_berkunjung_orang', 'lihat_poksar_berkunjung_ke_lokasi_jumlah_orang'),
        ('tim_ormawa_jumlah', 'lihat_tim_ormawa_berkunjung_ke_lokasi_jumlah_kedatangan'),
        ('tim_ormawa_orang', 'lihat_tim_ormawa_berkunjung_ke_lokasi_jumlah_orang')
    ]

    for key, cls in fields:
        try:
            element = popup.find_element(By.CLASS_NAME, cls)
            kunjungan[key] = element.get_attribute("value") or "0"
        except:
            kunjungan[key] = "0"

    detail['kunjungan'] = kunjungan

    sections = {
        'aktivitas': 'lihat_data',
        'kendala': 'lihat_kendala',
        'output': 'lihat_output',
        'kontribusi_pt': 'lihat_kontribusi_pt',
        'kontribusi_dospem': 'lihat_kontribusi_dospem',
        'kontribusi_masyarakat': 'lihat_kontribusi_masyarakat',
        'kontribusi_poksar': 'lihat_kontribusi_poksar',
        'kontribusi_ormawa': 'lihat_kontribusi_pelaksana',
        'rencana_setelah': 'lihat_rencana_setelah_keg_sekarang'
    }

    for key, cls in sections.items():
        try:
            element = popup.find_element(By.CLASS_NAME, cls)
            detail[key] = element.get_attribute("value") or ""
        except:
            detail[key] = ""

    capaian = []
    try:
        table = popup.find_element(By.CLASS_NAME, "table-striped")
        rows = table.find_elements(By.CSS_SELECTOR, "tbody.proposalRencanaLihat tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                capaian.append({
                    'capaian': f"{cells[0].text.strip()} - {cells[1].text.strip()}",
                    'persentase': cells[2].find_element(By.CSS_SELECTOR, "input.persentaseRencana").get_attribute(
                        "value")
                })
    except Exception as e:
        print(f"Gagal mengambil capaian: {str(e)}")

    detail['persentase_capaian'] = capaian

    return detail


def process_attachments(driver, cell, row_data):
    try:
        file_btn = cell.find_element(By.CSS_SELECTOR, "a[data-target='.modal-file-kegiatan']")
        driver.execute_script("arguments[0].click();", file_btn)

        file_modal = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "modal-file-kegiatan"))
        )

        attachments = file_modal.find_elements(By.CLASS_NAME, "attachment")
        for att in attachments:
            row_data['attachments'].append({
                'filename': att.find_element(By.TAG_NAME, "span").text.strip(),
                'url': att.get_attribute("href")
            })

        close_btn = file_modal.find_element(By.CSS_SELECTOR, ".modal-header button.close")
        driver.execute_script("arguments[0].click();", close_btn)
        WebDriverWait(driver, 10).until(EC.invisibility_of_element(file_modal))

    except Exception as e:
        print(f"Gagal mengambil lampiran: {str(e)}")


if __name__ == "__main__":
    driver = login()
    if driver:
        try:
            logbook_url = "https://php2d.kemdikbud.go.id/logbook/9479"
            data = crawl_logbook(driver, logbook_url)

            data.sort(key=lambda x: x['start_date'])

            for item in data:
                item.pop('start_date', None)

            with open('logbook_data_sorted.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print("Data berhasil disimpan ke logbook_data_sorted.json")
        finally:
            driver.quit()
    else:
        print("Gagal login, proses dihentikan.")