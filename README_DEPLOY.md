# Deployment und Start Anleitung

Dieses Repository enthält nun die aufgeteilten BPMN Prozesse und Skripte, um diese in einer Camunda Process Engine zu deployen und auszuführen.

## Änderungen

1.  **Nahrungszyklusprozess.bpmn**: Der Prozess `Process_1d67c0b` wurde in eine eigene Datei extrahiert und als `Nahrungszyklusprozess` (Executable) definiert. Externe Tasks wurden für `requestLLM` und `requestPurchaseRecommendation` konfiguriert.
2.  **DPE_Haustierprozess.bpmn**: Der ursprüngliche Prozess wurde bereinigt. Die Call Activity ruft nun den Prozess mit ID `Nahrungszyklusprozess` auf. Es wurden Variablen-Mappings (Input/Output) hinzugefügt, um `haustierId` (Referenz) und `vorraete` (Value) zu übergeben.

## Voraussetzungen

*   Python 3
*   Laufende Camunda Platform 7 Instanz (REST API erreichbar unter `http://localhost:8080/engine-rest`)
*   Python `requests` Bibliothek (`pip install requests`)

## Ausführung

### 1. Deployment

Führe das Deployment-Skript aus, um beide BPMN-Dateien in die Engine zu laden:

```bash
python3 deploy_and_start.py
```
*(Hinweis: Um auch direkt eine Prozessinstanz zu starten, entkommentiere die Zeile `start_process()` am Ende der Datei oder rufe die Funktion manuell auf.)*

### 2. Worker Starten

Da der Prozess "External Tasks" verwendet (für LLM Anfragen, Kaufempfehlungen und DB-Updates), muss ein Worker laufen, der diese Aufgaben abarbeitet. Starten Sie den Worker in einem separaten Terminal:

```bash
python3 worker.py
```

Der Worker pollt die Topics `requestLLM`, `requestPurchaseRecommendation` und `updateDatabase` und schließt die Aufgaben ab.

## Prozessdetails

### Variablenübergabe (Call Activity)

*   **Input**:
    *   `haustierId` -> `haustierId`: Übergabe der ID (Call by Reference Simulation).
    *   `vorraete` -> `vorraete`: Übergabe des aktuellen Vorrats (Call by Value).
*   **Output**:
    *   `neueVorraete` -> `vorraete`: Rückgabe des neuen Vorratsstandes an den Hauptprozess.

### Topics

*   `requestLLM`: Send Task im Nahrungszyklusprozess.
*   `requestPurchaseRecommendation`: Send Task im Nahrungszyklusprozess.
*   `updateDatabase`: Service Task im Hauptprozess.
