from PIL import Image as Img
import wave
from time import sleep
import math
from pydub import AudioSegment
from pydub.playback import play
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import os


colorVal = {  # nazwie koloru przypisujemy jego parametry RGBA
        "red": (237, 28, 36, 255),  # hi-hat
        "darkBlue": (63, 72, 204, 255),  # snare
        "yellow": (255, 242, 0, 255),  # kick
        "white": (255, 255, 255, 255)  # silence
}

colorPath = {  # nazwie koloru przypisujemy sciezke do pliku z samplem
        "red": './Pliki_projektu/hat.wav',  # talerz
        "darkBlue": './Pliki_projektu/snare.wav',  # werbel
        "yellow": './Pliki_projektu/kick.wav',  # stopa
        "white": './Pliki_projektu/silence.wav'  # cisza
}

colorSounds = {  # nazwie koloru przypisujemy załadowany sampel
        "red": AudioSegment.from_wav(colorPath["red"]),
        "darkBlue": AudioSegment.from_wav(colorPath["darkBlue"]),
        "yellow": AudioSegment.from_wav(colorPath["yellow"]),
        "white": AudioSegment.from_wav(colorPath["white"])
}


# liczy długość sampla o ścieżce fname w milisekundach
def wav_len(fname):
    file = AudioSegment.from_wav(fname)
    return file.duration_seconds * 1000


sampleLens = {  # nazwie koloru przypisujemy długość jego sampla w milisekundach
        "red": wav_len(colorPath['red']),
        "darkBlue": wav_len(colorPath['darkBlue']),
        "yellow": wav_len(colorPath['yellow']),
        "white": 0
}


# pixel-pixel pobrany z obrazu w postaci (r,g,b,a), a ignorujemy; plx pixel pobranyb z bazy danych;
# zwraca odleglosc pomiedzy dwoma pixelami
def distance(pixel, pxl):
    dist = (pixel[0]-pxl[0])**2 + (pixel[1]-pxl[1])**2 + (pixel[2]-pxl[2])**2
    return math.sqrt(dist)


# pixel dla ktorego szukamy najblizszego sasiedztwa; zwraca etykiete do najblzszego koloru
def find_nearest_neighbor(pixel):
    minn = math.sqrt(255**2+255**2+255**2) + 1  # odgornie ustalona wartosc jesli dwa kolory beda identyczne
    color = 'white'   # zainicjalizowana zmienna
    for x in colorVal:
        dist = distance(pixel, colorVal[x])
        if dist <= minn:
            color = x
            minn = dist
    return color


def cls(n):
    for x in range(0, n):
        print("\n")


def wait(n):
    cls(1)
    for x in range(0, n):
        print(".", end=' ')
        sleep(1)


def greater_than_zero(val):
    return val if val >= 0 else 0


# z podanego obrazka tworzy jeden złączony dźwięk
def create_output(img_size, delay, pixels, bars, number_of_superpixels):
    table = []
    for z in range(0, bars):
        xx = 0
        yy = 0
        x_mask = int(img_size[0] / number_of_superpixels)
        y_mask = int(img_size[1] / number_of_superpixels)
        avg0 = 0
        avg1 = 0
        avg2 = 0
        avg = (0, 0, 0, 0)
        counter_x = 0
        counter_y = 0
        while counter_x < number_of_superpixels:
            counter_y = 0
            while counter_y < number_of_superpixels:
                for x in range(0, x_mask):
                    for y in range(0, y_mask):
                        avg0 += pixels[xx + x, yy + y][0]
                        avg1 += pixels[xx + x, yy + y][1]
                        avg2 += pixels[xx + x, yy + y][2]
                avg = (avg0 / (x_mask * y_mask), avg1 / (x_mask * y_mask), avg2 / (x_mask * y_mask), 0)
                tmp = find_nearest_neighbor(avg)
                if tmp == "white":
                    table.append(colorSounds["white"][:delay])
                else:
                    table.append(colorSounds[tmp] + colorSounds["white"][:greater_than_zero(delay - sampleLens[tmp])])
                xx += x_mask
                avg0 = 0
                avg1 = 0
                avg2 = 0
                counter_y += 1
            counter_x += 1
            xx = 0
            yy += y_mask
                
    output = AudioSegment.from_wav("./Pliki_projektu/silence.wav")[:1]
    for x in table:
        output += x
    output += AudioSegment.from_wav("./Pliki_projektu/silence.wav")[:200]  # zeby sie nie urywalo na koncu
    return output


# eksportuje złączone dźwięki do pliku wav o nazwie podanej przez użytkownika
def export_output(output):
    path = input("Jak chcesz nazwać plik?: ")
    path = ''.join(["./", path])
    if not path.endswith(".wav"):
        path = ''.join([path, '.wav'])
    output.export(path, format='wav')
    cls(20)
    print("Pomyślnie wyeksportowano plik! (" + path + ")\n")
    wait(4)


def show_output_as_img(output):
    output.export("./tmp.wav", format='wav')
    spf = wave.open("./tmp.wav", "r")
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, "Int16")
    fs = spf.getframerate()
    x = np.linspace(0, len(signal) / fs, num=len(signal))
    plt.figure(1)
    plt.title("Gratulacje! Tak wygląda Twoja pętla perkusyjna :)")
    plt.plot(x, signal, label='Sygnał audio', linewidth=0.4)
    plt.xlabel('czas [s]')
    plt.legend(loc='best')
    plt.show()
    os.remove("./tmp.wav")


# *** MAIN FUNCTION ***
def main():
    plt.close('all')
    path = input("Podaj nazwę obrazu. Pamiętaj, aby obraz umieścić w folderze Pliki_projektu: ")
    img = Img.open(''.join(['./Pliki_projektu/', path]))
    tempo = 0
    while tempo < 30 or tempo > 220:
        tempo = int(input("Podaj tempo <30, 220> BPM: "))
    delay = 60000 / tempo
    delay /= 4
    bars = 0
    while bars < 1 or bars > 64:
        bars = int(input("Podaj ilość powtórzeń (max 64): "))
    output = create_output(img.size, delay, img.load(), bars, 8)
    play(output)
    show_output_as_img(output)
    decision = 0
    while decision != 'Y' and decision != 'y' and decision != 'n' and decision != 'N':
        decision = input("Czy chcesz zachować utworzony plik? (y/n): ")
    if decision == 'Y' or decision == 'y':
        export_output(output)
    cls(20)
    print("Dziękujemy za korzystanie z programu!\n",
          "IMAGE DRUM MACHINE 1.0\n",
          "Grupa:\n",
          "Michał Kędzia 222463\n",
          "Adrian Kręcikowski 222482\n",
          "Tomasz Wojtkiewicz 222616", end='')
    wait(4)


# THE PROGRAM STARTS HERE
main()
