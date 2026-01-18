import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

class Zbiornik:
    def __init__(self, x, y, width=100, height=140, pojemnosc=100, nazwa=""):
        # Dane stale
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        self.pojemnosc = pojemnosc

        #Dane zmienne (procesowe)
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0

    # Funkcja dodajaca ciecz do zbiornika
    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    # Funkcja usuwajaca ciecz ze zbiornika
    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto

    # Funkcja do przeliczania poziomu wody
    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    def czy_pusty(self): 
        return self.aktualna_ilosc <= 0.1
    def czy_pelny(self): 
        return self.aktualna_ilosc >= self.pojemnosc - 0.1

    def punkt_gora(self):
        return (self.x + self.width / 2, self.y)
    def punkt_dol(self):
        return (self.x + self.width / 2, self.y + self.height)

    # Funkcja rysujaca zbiornik
    def draw(self, painter):
        if self.poziom >= 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.drawRect(int(self.x + 3), int(y_start), int(self.width - 6), int(h_cieczy - 2))

            pen = QPen(Qt.white, 4)
            pen.setJoinStyle(Qt.MiterJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

            painter.setPen(Qt.white)
            painter.drawText(int(self.x - 20), int(self.y - 10), self.nazwa)

class Rura:
    def __init__(self, punkty, grubosc=12, kolor=Qt.gray):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255)
        self.czy_plynie = False

    # Funkcja ustawiajaca przeplyw 
    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie

    # Funkcja rysujaca rure
    def draw(self, painter):
        if len(self.punkty) < 2:
            return
        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc - 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)

class Zawor:
    def __init__(self, x, y, nazwa=""):
        self.x = x
        self.y = y
        self.nazwa = nazwa
        self.otwarty = False
        self.rozmiar = 15

    # Funkcja rysujaca zawor
    def draw(self, painter):
        kolor = QColor(0, 255, 0) if self.otwarty else QColor(255, 50, 20)
        
        painter.setPen(QPen(Qt.white, 1))
        painter.setBrush(kolor)

        path = QPainterPath()
        path.moveTo(self.x - self.rozmiar, self.y - self.rozmiar)
        path.lineTo(self.x + self.rozmiar, self.y + self.rozmiar)
        path.lineTo(self.x + self.rozmiar, self.y - self.rozmiar)
        path.lineTo(self.x - self.rozmiar, self.y + self.rozmiar)
        path.closeSubpath()
        
        painter.drawPath(path)
        
        painter.setBrush(Qt.white)
        painter.drawEllipse(QPointF(self.x, self.y), 3, 3)

        painter.setPen(Qt.white)
        painter.drawText(int(self.x - 50), int(self.y - 10), self.nazwa)

class Symulacja(QWidget):
    # Funkcja napelniajaca zbiornik
    def napelnij_zbiornik(self, zbiornik):
        zbiornik.aktualna_ilosc = zbiornik.pojemnosc
        zbiornik.aktualizuj_poziom()
        self.update()

    # Funkcja oprozniajaca zbiornik
    def oproznij_zbiornik(self, zbiornik):
        zbiornik.aktualna_ilosc = 0.1
        zbiornik.aktualizuj_poziom()
        self.update()

    #Funkcja tworzaca przyciski zaworow
    def stworz_przycisk_zaworu(self, x, y, nazwa):
            btn = QPushButton(nazwa, self)
            btn.setGeometry(x, y, 90, 30)
            btn.setCheckable(True)
            btn.setStyleSheet("""QPushButton {background-color: #444; color: white;} QPushButton:checked {background-color: #f39c12; color: white; font-weight: bold;}""") 
            return btn

    # Funckja wyswietlajaca status zbiornikow
    def status_zbiornikow(self, painter):
        painter.setPen(QColor(243, 156, 18))
        painter.drawText(780, 40, "STATUS ZBIORNIKOW:")

        painter.setPen(Qt.white)
        for i in range(len(self.zbiorniki)):
            z = self.zbiorniki[i]
            procent = z.aktualna_ilosc / z.pojemnosc * 100
    
            y_pozycja = 60 + (i * 20)
            painter.drawText(780, y_pozycja, f"{z.nazwa}: {z.aktualna_ilosc:.1f}L ({procent:.0f}%)")

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("SCADA - Symulacja Pyhton")
        self.setFixedSize(1000, 700)
        self.setStyleSheet("background-color: #1e1e1e")

        self.z1 = Zbiornik(150, 50, 300, 160, 300, nazwa="Zbiornik Glowny")
        self.z1.aktualna_ilosc = 200.0
        self.z1.aktualizuj_poziom()

        self.z2 = Zbiornik(50, 350, nazwa="Zbiornik A")
        self.z3 = Zbiornik(250, 350, nazwa="Zbiornik B")
        self.z4 = Zbiornik(450, 350, nazwa="Zbiornik C")
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]

        p_start1 = self.z1.punkt_dol()
        p_koniec1 = self.z2.punkt_gora()
        p_koniec2 = self.z3.punkt_gora()
        p_koniec3 = self.z4.punkt_gora()
        p_start2 = self.z2.punkt_dol()
        p_start3 = self.z3.punkt_dol()
        p_start4 = self.z4.punkt_dol()
        mid_y = (p_start1[1] + p_koniec1[1]) / 2 - 30
        mid_y2 = 600
        self.rura0 = Rura([p_start1, (p_start1[0], mid_y)])
        self.rura1 = Rura([(p_start1[0], mid_y), (p_koniec1[0], mid_y), p_koniec1])
        self.rura2 = Rura([(p_start1[0], mid_y), p_koniec2])
        self.rura3 = Rura([(p_start1[0], mid_y), (p_koniec3[0], mid_y), p_koniec3])
        self.rura4 = Rura([p_start3, (p_start3[0], mid_y2)])
        self.rura5 = Rura([p_start4, (p_start4[0], mid_y2)])
        self.rura6 = Rura([p_start2, (p_start2[0], mid_y2), (p_start3[0], mid_y2)])
        self.rura7 = Rura([(p_start3[0], mid_y2), (p_start4[0], mid_y2)] )
        self.rura8 = Rura([(p_start4[0], mid_y2), (p_start4[0]+170, mid_y2), (p_start4[0]+170, 70), (450, 70)])
        self.rury = [self.rura1, self.rura2, self.rura3, self.rura0, self.rura4, self.rura5, self.rura6, self.rura7, self.rura8]

        self.vA = Zawor(self.z2.punkt_gora()[0], 300, "V-A1")
        self.vB = Zawor(self.z3.punkt_gora()[0], 300, "V-B1")
        self.vC = Zawor(self.z4.punkt_gora()[0], 300, "V-C1")
        self.vA2 = Zawor(self.z2.punkt_dol()[0], 540, "V-A2")
        self.vB2 = Zawor(self.z3.punkt_dol()[0], 540, "V-B2")
        self.vC2 = Zawor(self.z4.punkt_dol()[0], 540, "V-C2")
        self.zawory = [self.vA, self.vB, self.vC, self.vA2, self.vB2, self.vC2]

        self.running = False
        self.flow_speed = 0.6
        self.kat_pompy = 0.0

        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)

        self.btn_A = self.stworz_przycisk_zaworu(780, 210, "Zawor V-A1")
        self.btn_A2 = self.stworz_przycisk_zaworu(885, 210, "Zawor V-A2")
        self.btn_B = self.stworz_przycisk_zaworu(780, 265, "Zawor V-B1")
        self.btn_B2 = self.stworz_przycisk_zaworu(885, 265, "Zawor V-B2")
        self.btn_C = self.stworz_przycisk_zaworu(780, 320, "Zawor V-C1")
        self.btn_C2 = self.stworz_przycisk_zaworu(885, 320, "Zawor V-C2")

        self.btn_main = QPushButton("WŁĄCZ ZASILANIE", self)
        self.btn_main.setGeometry(800, 145, 160, 40)
        self.btn_main.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")
        self.btn_main.clicked.connect(self.przelacz_zasilanie)

    # Funkcja umozliwiajaca proces symulacji
    def przelacz_zasilanie(self):
        if self.running:
            self.timer.stop()
            self.btn_main.setText("WŁĄCZ ZASILANIE")
            self.btn_main.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")
        else:
            self.timer.start(20)
            self.btn_main.setText("SYSTEM AKTYWNY")
            self.btn_main.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.running = not self.running

    # Funkcja logiki przeplywu
    def logika_przeplywu(self):
        self.vA.otwarty = self.btn_A.isChecked()
        self.vB.otwarty = self.btn_B.isChecked()
        self.vC.otwarty = self.btn_C.isChecked()
        self.vA2.otwarty = self.btn_A2.isChecked()
        self.vB2.otwarty = self.btn_B2.isChecked()
        self.vC2.otwarty = self.btn_C2.isChecked()

        p_A = False
        if self.btn_A.isChecked() and not self.z1.czy_pusty() and not self.z2.czy_pelny():
            ilosc = self.z1.usun_ciecz(self.flow_speed)
            self.z2.dodaj_ciecz(ilosc)
            p_A = True

        p_B = False
        if self.btn_B.isChecked() and not self.z1.czy_pusty() and not self.z3.czy_pelny():
            ilosc = self.z1.usun_ciecz(self.flow_speed)
            self.z3.dodaj_ciecz(ilosc)
            p_B = True

        p_C = False
        if self.btn_C.isChecked() and not self.z1.czy_pusty() and not self.z4.czy_pelny():
            ilosc = self.z1.usun_ciecz(self.flow_speed)
            self.z4.dodaj_ciecz(ilosc)
            p_C = True

        p_A2 = False
        if self.btn_A2.isChecked() and not self.z2.czy_pusty():
            ilosc = self.z2.usun_ciecz(self.flow_speed)
            self.z1.dodaj_ciecz(ilosc)
            p_A2 = True

        p_B2 = False
        if self.btn_B2.isChecked() and not self.z3.czy_pusty():
            ilosc = self.z3.usun_ciecz(self.flow_speed)
            self.z1.dodaj_ciecz(ilosc)
            p_B2 = True

        p_C2 = False
        if self.btn_C2.isChecked() and not self.z4.czy_pusty():
            ilosc = self.z4.usun_ciecz(self.flow_speed)
            self.z1.dodaj_ciecz(ilosc)
            p_C2 = True
        
        self.rura0.ustaw_przeplyw(p_A or p_B or p_C)
        self.rura1.ustaw_przeplyw(p_A)
        self.rura2.ustaw_przeplyw(p_B)
        self.rura3.ustaw_przeplyw(p_C)
        self.rura4.ustaw_przeplyw(p_B2)
        self.rura5.ustaw_przeplyw(p_C2)
        self.rura6.ustaw_przeplyw(p_A2)
        self.rura7.ustaw_przeplyw(p_A2 or p_B2)
        self.rura8.ustaw_przeplyw(p_A2 or p_B2 or p_C2)

        if self.rura8.czy_plynie:
            self.kat_pompy = (self.kat_pompy + 10) % 360

        self.update()

    # Funkcja rysujaca wszystko
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for r in self.rury:
            r.draw(p)
        for z in self.zbiorniki:
            z.draw(p)
        for v in self.zawory:
            v.draw(p)
        self.status_zbiornikow(p)

        # Pompa wody
        px, py = 670, 300

        p.setPen(QPen(Qt.white, 2))
        p.setBrush(QColor(60, 60, 60))
        p.drawEllipse(px - 25, py - 25, 50, 50)

        p.save()
        p.translate(px, py)
        p.rotate(self.kat_pompy)

        p.setPen(QPen(QColor(243, 156, 18), 4))
        p.drawLine(-15, 0, 15, 0)
        p.drawLine(0, -15, 0, 15)

        p.restore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Symulacja()
    window.show()
    sys.exit(app.exec_())