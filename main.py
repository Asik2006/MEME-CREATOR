import sys
import sqlite3 as sql
import os

from rembg import remove
from PIL import Image, ImageDraw, ImageFont
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QPushButton


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('шаблон.ui', self)
        self.create_btn.clicked.connect(self.open_create_form)
        self.save_btn.clicked.connect(self.save_catalog)

        # Начало БД
        self.con = sql.connect('photo_db.db')
        self.cur = self.con.cursor()

        self.cur.execute('CREATE TABLE IF NOT EXISTS photos(id INT PRIMARY KEY, photo BLOB)')
        id = self.cur.execute('SELECT id FROM photos')
        self.n = id.fetchall()

        self.photos = self.cur.execute('SELECT photo FROM photos')

        k = 1
        for photo in self.photos:
            with open(f'saves\{k}.png', 'wb') as file:
                file.write(photo[0])
                k += 1

        self.con.commit()
        self.cur.close()
        self.con.close()
        # Конец БД



    def open_create_form(self):
        self.create_form = Create()
        self.create_form.show()

    def save_catalog(self):
        self.con = sql.connect('photo_db.db')
        self.cur = self.con.cursor()
        self.photos = self.cur.execute('SELECT photo FROM photos')

        k = 1
        for photo in self.photos:
            with open(f'saves\{k}.png', 'wb') as file:
                file.write(photo[0])
                k += 1

        self.con.commit()
        self.cur.close()
        self.con.close()
        dir_ = QFileDialog.getOpenFileName(self, 'Фото', '\saves\-')[0]
        os.startfile(dir_)


class Create(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('суета.ui', self)
        self.img_open.clicked.connect(self.open)
        self.full_create_btn.clicked.connect(self.doing)

        self.main_w = Main()

        if len(self.main_w.n) == 0:
            self.number = 1
        else:
            self.number = len(self.main_w.n) + 1

    def open(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]

    def readImage(self, filename):
        fin = open(filename, "rb")
        imgg = fin.read()
        fin.close()
        binary = sql.Binary(imgg)
        return binary

    def doing(self):
        input_path = self.fname
        output_path = f'out{self.number}.png'

        input = Image.open(input_path)
        output = remove(input)

        output.save(output_path)

        img = Image.open(output_path)
        x, y = img.size

        font = ImageFont.truetype('Font-123.ttf', size=48)
        text = self.text_meme.text()


        draw_text = ImageDraw.Draw(img)
        draw_text.text((0.1 * x, 0.75 * y), text, (255,255,255), font=font)

        img.save(output_path)

        self.main_w.con = sql.connect('photo_db.db')
        self.main_w.cur = self.main_w.con.cursor()
        bin = self.readImage(output_path)
        data_tuple = (self.number, bin)
        self.main_w.cur.execute('INSERT INTO photos(id, photo) VALUES(?, ?)', data_tuple)
        self.main_w.con.commit()
        self.number += 1
        self.main_w.cur.close()
        self.main_w.con.close()
        os.remove(output_path)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())