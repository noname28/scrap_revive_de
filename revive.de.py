from bs4 import BeautifulSoup
import requests
import pandas as pd
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSlot

class Game(QMainWindow):
    def __init__(self):
        super().__init__()

        # Combo box for year selection
        self.combo_1 = QComboBox(self)
        self.combo_1.addItems(["English", "Deutsch"])
        self.combo_1.move(150, 100)

        # Label for year selection
        self.qlabel_year = QLabel("Select Language :", self)
        self.qlabel_year.move(50, 100)

        # Label for description
        self.qlabel_description = QLabel("This Program scrapes the revive.de internet site", self)
        self.qlabel_description.setFixedWidth(500)
        self.qlabel_description.move(50, 50)

        # Download button
        self.button = QPushButton('Download', self)
        self.button.move(100, 250)
        self.button.clicked.connect(self.run)

        # Status label
        self.label = QLabel(self)
        self.label.setGeometry(200, 200, 200, 30)

        # Set main window properties
        self.setGeometry(50, 50, 500, 400)
        self.setWindowTitle("Web Mining Program")
        self.show()

    @pyqtSlot()
    def run(self):
        content_type = self.combo_1.currentText()

        if content_type == "English":
            url = "https://revive.de/en/search?options%5Bprefix%5D=last&options%5Bunavailable_products%5D=hide&q=%2A"
            self.get_url(url)
        elif content_type == "Deutsch":
            url = "https://revive.de/search?options%5Bprefix%5D=last&options%5Bunavailable_products%5D=hide&q=%2A"
            self.get_url(url)

    def format_price(self, price_text):
        # Sadece fiyatı ve para birimini al (örneğin: '2.69900 €' -> '2.699,00 €')
        parts = price_text.split(' ')
        if len(parts) == 2:
            price = parts[0].replace('.', ',')
            currency = parts[1]
            return f"{price} {currency}"
        return price_text
    
    def get_url(self, url):
        try:
            wContent_type = self.combo_1.currentText()
            wCount = 0;
            wSite_Path = "https://revive.de"

            df = pd.DataFrame(columns=['Url', 'Product Title', 'Image Front', 'Product Price', 'List Price', 'Product Vendor', 'Discount'])

            for i in range(1, 3000):
                new_url = f"{url}&page={i}"
                response = requests.get(new_url)

                if response.status_code != 200:
                    print(f"Error: Unable to fetch data from URL. Status code: {response.status_code}")
                    df.to_excel('revice.de.xlsx', index=False)
                    print("Data saved to revice.de.xlsx")
                    break

                soup = BeautifulSoup(response.content, 'html.parser')

                Is_Not_Matched = soup.find('div', class_='index-section')
                if Is_Not_Matched:
                    QMessageBox.about(self, "Title", f"Contionue exception : {e}, \n wCount : {wCount} ");
                    print(f"Error: Unable to fetch data from URL. Status code: {response.status_code}")
                    df.to_excel('revice.de.xlsx', index=False)
                    print("Data saved to revice.de.xlsx")
                    break

                list_div = soup.find('div', class_='new-grid product-grid collection-grid')

                table = list_div.find_all("a", class_="grid-item__link")

                for item in table:
                    try:
                        wCount = wCount + 1;
                        wHref = wSite_Path + item.get('href')
                        wProductTitle = item.find("div", class_='grid-product__title tw-line-clamp-2').text
                        wImageFront = 'https:' + item.find('img').get('src')
                        
                        # İndirimli fiyatı al
                        current_price_tag = item.find('span', class_='grid-product__price--current')
                        if current_price_tag:
                            current_price = current_price_tag.find('span', class_='visually-hidden').get_text()
                        else:
                            current_price = 'N/A'

                        # Orijinal fiyatı al
                        original_price_tag = item.find('span', class_='grid-product__price--original')
                        if original_price_tag:
                            original_price = original_price_tag.find('span', class_='visually-hidden').get_text()
                        else:
                            original_price = 'N/A'

                        formatted_current_price = self.format_price(current_price)
                        formatted_original_price = self.format_price(original_price)

                        wProductVendor = item.find('div', class_='grid-product__vendor').get_text() if item.find('div', class_='grid-product__vendor') else 'N/A'
                        
                        # İndirim bilgisi kontrolü
                        discount_tag = item.find('div', class_='grid-product__tag grid-product__tag--sale')
                        if discount_tag:
                            wDiscount = discount_tag.get_text().replace('\n', '').strip()
                        else:
                            wDiscount = 'N/A'

                        # Append data to DataFrame
                        df = pd.concat([df, pd.DataFrame({
                            'Url': [wHref],
                            'Product Title': [wProductTitle],
                            'Image Front': [wImageFront],
                            'Product Price': [current_price],
                            'List Price': [original_price],
                            'Product Vendor': [wProductVendor],
                            'Discount': [wDiscount]
                        })], ignore_index=True)

                    except Exception as e:
                        df.to_excel('revice.de.xlsx', index=False)
                        print("Data saved to revice.de.xlsx")
                        print(f"An error occurred while processing an item: {e}")
                        QMessageBox.about(self, "Title", f"Contionue exception : {e}, \n wCount : {wCount} ");
                        continue

            df.to_excel('revice.de.xlsx', index=False)
            print("Data saved to revice.de.xlsx")
            QMessageBox.about(self, "Title", "Revice.de.xlsx file written." & str(wCount))

            

        except Exception as e:
            df.to_excel('revice.de.xlsx', index=False)
            print("Data saved to revice.de.xlsx")
            print(f"An error occurred: {e}")
            QMessageBox.about(self, "Title", "Last exception");

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Game()
    sys.exit(app.exec_())
