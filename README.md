# PHP2D Logbook Scraper

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg?style=flat-square&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4+-orange.svg?style=flat-square&logo=selenium&logoColor=white)
![dotenv](https://img.shields.io/badge/dotenv-v0.20+-green.svg?style=flat-square)
![JSON](https://img.shields.io/badge/JSON-standard-yellow.svg?style=flat-square)


  A modern Python script to automatically extract logbook data from the PHP2D Kemdikbud website.
</p>

---

## ✨ Overview

This Python script, `main.py`, is designed to streamline the process of collecting logbook data from the **Program Hibah Pembelajaran Daring Diktiristek (PHP2D)** website of Kemdikbud (Kementerian Pendidikan, Kebudayaan, Riset, dan Teknologi Republik Indonesia). It leverages Selenium to automate browser interactions, navigate the website, and meticulously scrape relevant information from logbook entries. The extracted data is then structured and saved into a `logbook_data_sorted.json` file for further analysis or record-keeping.

**Key Features:**

*   **Automated Login:**  Securely logs into the PHP2D website using credentials stored in environment variables, eliminating manual login steps.
*   **Comprehensive Data Extraction:** Scrapes detailed logbook information, including:
    *   Basic logbook entry details (No., Waktu, Aktivitas Ringkas).
    *   Validation statuses (Dosen Pembimbing, Perguruan Tinggi) with descriptions.
    *   In-depth activity details from modal pop-ups, covering:
        *   Activity time.
        *   Visit details (PT, Dosen Pembimbing, Tim, TOKMA, POKSAR, ORMAWA visits).
        *   Descriptive text fields for activities, challenges, outputs, and contributions.
        *   Progress tracking and percentage completion.
    *   Attached files with filenames and downloadable URLs.
*   **Pagination Handling:**  Automatically navigates through multiple pages of logbook entries to ensure complete data retrieval.
*   **Robust Error Handling:** Implements retry mechanisms for stale element exceptions and graceful error handling for network issues or website changes.
*   **Structured JSON Output:**  Saves the scraped data in a well-organized `logbook_data_sorted.json` file, sorted by start date for chronological analysis.
*   **Modern and Efficient:**  Utilizes `selenium.webdriver.Edge` for modern browser compatibility and efficient scraping.

## 🛠️ Tech Stack

*   **Python 3.7+:**  The primary programming language.
*   **Selenium:** For browser automation and web scraping.
*   **python-dotenv:** To manage environment variables securely.
*   **JSON:** For structured data output.
*   **Edge WebDriver:**  Required for Selenium to interact with the Microsoft Edge browser.

## ⚙️ Prerequisites

Before running the script, ensure you have the following installed and configured:

1.  **Python 3.7 or higher:**  Download and install Python from [python.org](https://www.python.org/downloads/).
2.  **Required Python Packages:** Install the necessary libraries using pip:

    ```bash
    pip install selenium python-dotenv
    ```

3.  **Microsoft Edge Browser:**  Ensure you have Microsoft Edge browser installed on your system.
4.  **Edge WebDriver:** Download the appropriate Edge WebDriver for your Edge browser version from [Microsoft Edge WebDriver](https://msedgewebdriver.azureedge.net/index.html).
    *   **Important:** Place the downloaded `msedgedriver` executable in a directory that is included in your system's `PATH` environment variable, or specify the webdriver path directly in the Selenium `webdriver.Edge()` instantiation if needed (though not recommended for portability).
5.  **Environment Variables:** Create a `.env` file in the same directory as `main.py` and define the following environment variables:

    ```dotenv
    USERNAME_PPK=your_username_ppk
    PASSWORD_PPK=your_password_ppk
    ```

    *   Replace `your_username_ppk` and `your_password_ppk` with your actual PHP2D website credentials. **Ensure you handle your credentials securely and do not commit the `.env` file to version control in public repositories.**

## 🚀 Installation & Setup

1.  **Clone the repository (if applicable):**

    ```bash
    git clone https://github.com/IRedDragonICY/ppk-kemdikbud-scraper.git
    cd ppk-kemdikbud-scraper
    ```

2.  **Install Python Packages:**

    ```bash
    pip install -r requirements.txt  # If a requirements.txt file is provided
    # OR
    pip install selenium python-dotenv # If installing manually
    ```

3.  **Configure Environment Variables:** Create a `.env` file in the project root and set your credentials as described in the [Prerequisites](#-prerequisites) section.

4.  **Verify Edge WebDriver Setup:** Ensure `msedgedriver` is correctly installed and accessible in your system's `PATH`.

## 🕹️ Usage

To run the script and scrape logbook data:

1.  **Navigate to the project directory** in your terminal.

2.  **Execute the `main.py` script:**

    ```bash
    python main.py
    ```

3.  **Monitor the Output:** The script will print progress messages to the console, including login success/failure and any errors encountered during scraping.

4.  **Data Output:** Upon successful execution, the scraped logbook data will be saved in a file named `logbook_data_sorted.json` in the same directory as the script.

## 📄 Output - `logbook_data_sorted.json`

The script generates a JSON file named `logbook_data_sorted.json`. This file contains a list of logbook entries, each represented as a JSON object. The data is structured as follows:

```json
[
  {
    "no": "1",
    "waktu": "Periode Pelaksanaan\n(14 Okt 2023 s.d 20 Okt 2023)",
    "validasi_dospem": "valid",
    "validasi_pt": {
      "status": "invalid",
      "keterangan": "Belum Validasi"
    },
    "aktivitas_ringkas": "Persiapan dan koordinasi awal tim",
    "attachments": [
      {
        "filename": "dokumen_persiapan.pdf",
        "url": "https://example.com/download/dokumen_persiapan.pdf"
      },
      {
        "filename": "notulensi_koordinasi.docx",
        "url": "https://example.com/download/notulensi_koordinasi.docx"
      }
    ],
    "detail_logbook": {
      "waktu_kegiatan": "Mingguan",
      "kunjungan": {
        "pt_berkunjung": "2",
        "dospem_berkunjung": "1",
        "konsultasi_dosen": "Ya",
        "tim_berkunjung_jumlah": "5",
        "tim_berkunjung_orang": "3",
        "tokma_berkunjung_jumlah": "0",
        "tokma_berkunjung_orang": "0",
        "poksar_berkunjung_jumlah": "0",
        "poksar_berkunjung_orang": "0",
        "tim_ormawa_jumlah": "0",
        "tim_ormawa_orang": "0"
      },
      "aktivitas": "Melakukan persiapan awal dan koordinasi tim proyek PHP2D.",
      "kendala": "Tidak ada kendala signifikan.",
      "output": "Rencana kerja dan pembagian tugas tim.",
      "kontribusi_pt": "Fasilitasi ruang rapat untuk koordinasi.",
      "kontribusi_dospem": "Memberikan arahan dan masukan pada rencana kerja.",
      "kontribusi_masyarakat": "",
      "kontribusi_poksar": "",
      "kontribusi_ormawa": "",
      "rencana_setelah": "Melanjutkan dengan implementasi tahap awal proyek."
      "persentase_capaian": [
        {
          "capaian": "Penyusunan Rencana Kerja - Selesai",
          "persentase": "100"
        },
        {
          "capaian": "Pembentukan Tim - Selesai",
          "persentase": "100"
        }
      ]
    }
  },
  // ... more logbook entries
]
```
# ⚠️ Disclaimer

This script is intended for personal use to facilitate data extraction from the PHP2D Kemdikbud website for legitimate purposes.

Use this script responsibly and ethically, respecting the website's terms of service and robots.txt.

Be aware that website structures and functionalities can change, potentially breaking the script. Regular maintenance and updates might be required.

The developers are not responsible for any misuse or consequences arising from the use of this script.

# 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](link-to-issues-page if applicable).

# 📜 License

MIT License


# 🧑‍💻 Author

Mohammad Farid Hendianto
Ahmad Dahlan University


