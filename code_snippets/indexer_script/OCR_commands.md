Gut. Dann gehen wir den **vernünftigen, technisch sauberen Weg**. Tesseract kann das. Es ist nur ein bisschen beleidigend zu konfigurieren. Windows halt.

Ich erkläre dir **schrittweise**, ohne Mystik, ohne Linux-Gatekeeping.

---

## Ziel

* Dein **eingescanntes PDF** wird **neu mit OCR versehen**
* **Deutsch korrekt** erkannt
* Umlaute (ä ö ü Ä Ö Ü ß) werden **von Anfang an richtig**
* Keine Bastellösung mit kaputtem Textlayer

---

## Überblick: Was wir machen

1. Tesseract installieren
2. Deutsche Sprachdaten aktivieren
3. (Optional, aber sehr empfohlen) OCRmyPDF nutzen
4. PDF neu ocr-en
5. Ergebnis prüfen

---

## 1. Tesseract unter Windows installieren

### Offizieller Installer (empfohlen)

Lade hier:

* [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

Nimm:

* **tesseract-ocr-w64-setup.exe**

Beim Installieren **unbedingt beachten**:

* ✔ Sprache **Deutsch (deu)** anhaken
* ✔ Optional: weitere Sprachen, falls nötig
* ✔ Pfad merken, meist:

  ```
  C:\Program Files\Tesseract-OCR\
  ```

Nach der Installation:

```powershell
tesseract --version
```

Wenn das klappt: gut. Wenn nicht, fehlt der Pfad in der PATH-Variable. Sag Bescheid, dann fixen wir das.

---

## 2. Prüfen, ob Deutsch wirklich aktiv ist

```powershell
tesseract --list-langs
```

Du solltest sehen:

```
deu
eng
```

Wenn **deu fehlt**, dann:

* Sprachdaten manuell nachinstallieren
* Datei heißt:

  ```
  deu.traineddata
  ```
* Zielordner:

  ```
  C:\Program Files\Tesseract-OCR\tessdata\
  ```

---

## 3. Der saubere Weg: OCRmyPDF (stark empfohlen)

Tesseract allein kann OCR, aber **OCRmyPDF**:

* erhält Layout
* ersetzt oder ergänzt bestehenden Textlayer
* ist genau für PDFs gedacht

### Python installieren (falls noch nicht da)

* [https://www.python.org/downloads/](https://www.python.org/downloads/)
* Beim Installieren: ✔ **Add Python to PATH**

### OCRmyPDF installieren

```powershell
pip install ocrmypdf
```

Test:

```powershell
ocrmypdf --version
```

---

## 4. PDF neu ocr-en (mit deutschen Umlauten!)

### Grundbefehl

```powershell
ocrmypdf -l deu input.pdf output.pdf
```


```powershell
ocrmypdf -l deu input.pdf output.pdf
```

Das macht:

* Sprache **Deutsch**
* Neuer OCR-Layer
* Alte kaputte Texterkennung wird ersetzt

### Wenn das PDF schon OCR hat (dein Fall!)
Sehr wichtig. Sonst sagt OCRmyPDF: „Ist doch schon Text drin“ und lässt den Müll stehen.
option `--force-ocr`
option '--sidecar' to export txt file directly

```powershell
ocrmypdf --force-ocr -l deu input.pdf output.pdf
```



```shell
ocrmypdf --force-ocr -l deu --deskew ^
--sidecar "C:\Users\Daniel\Downloads\Texte_Chat_bot_Examen\Texte_Josefa\Funda_Th_correct\Becka_Praxis_der_Gerechtigkeit_OCR.txt" ^
"C:\Users\Daniel\Downloads\Texte_Chat_bot_Examen\Texte_Josefa\Sozialethik\Becka_Praxis_der_Gerechtigkeit_TO_DO_SCHLECHT.pdf"^
 "C:\Users\Daniel\Downloads\Texte_Chat_bot_Examen\Texte_Josefa\Sozialethik\Becka_Praxis_der_Gerechtigkeit_OCR.pdf"
```

```powershell
ocrmypdf --force-ocr -l deu --deskew --sidecar "C:\Users\Daniel\Downloads\Texte_Chat_bot_Examen\Texte_Josefa\Sozialethik\Leniger_Restorative_Justice_OCR.txt"`
 "C:\Users\Daniel\Downloads\Texte_Chat_bot_Examen\Texte_Josefa\Sozialethik\Leniger_Restorative_Justice_TO_DO.pdf"`
 "C:\Users\Daniel\Downloads\Texte_Chat_bot_Examen\Texte_Josefa\Sozialethik\Leniger_Restorative_Justice_OCR.pdf"
```

---

## 5. Qualitäts-Upgrade (empfohlen)

Wenn das Original schlecht gescannt ist:

```powershell
ocrmypdf --force-ocr -l deu input.pdf output.pdf
```


```powershell
ocrmypdf --force-ocr -l deu --deskew --clean input.pdf output.pdf
```


```powershell
ocrmypdf --force-ocr -l deu --deskew --clean ".\Remenyi_Gottes Gegenwart.pdf" ".\Remenyi_Gottes_Gegenwart_CORRECT_OCR2.pdf"
```




Optional:

* `--deskew` → schief eingescannt? fix
* `--clean` → Hintergrundrauschen reduzieren

---

## 6. Ergebnis prüfen

* Text kopieren
* Teste gezielt:

  * ä ö ü Ä Ö Ü ß
  * Wörter wie:

    * „für“
    * „größer“
    * „Möglichkeit“
    * „Übertragung“

Wenn die jetzt stimmen: Mission erfüllt.

---

## 7. Falls trotzdem noch Fehler bleiben

Dann liegt es meist an:

* Frakturschrift
* sehr alten Drucken
* extrem schlechtem Scan

Dann kannst du zusätzlich testen:

```powershell
ocrmypdf -l deu+eng --force-ocr input.pdf output.pdf
```

Manchmal hilft die Kombi. OCR ist leider kein Theologe, sondern ein nervöser Praktikant.

---

## 8. Alternative: Nur Text extrahieren (nicht empfohlen, aber möglich)

```powershell
tesseract input.pdf output -l deu pdf
```

Erzeugt ein neues PDF, aber Layout leidet oft. Für wissenschaftliche Arbeit eher meh.

---

## Meine klare Empfehlung für dich

Da du mit **wissenschaftlichen Texten** arbeitest:

* **OCRmyPDF + Tesseract + deu**
* OCR **neu erzeugen**, nicht reparieren
* Danach erst **Suchen & Ersetzen**, wenn überhaupt nötig

Wenn du willst, sag mir:

* wie viele Seiten
* Antiqua oder Fraktur
* ob du das PDF weiter zitieren willst

Dann stelle ich dir **den optimalen Befehl** zusammen. Ich murrend. Aber präzise.
