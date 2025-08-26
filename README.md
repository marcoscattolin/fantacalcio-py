# Fantacalcio-PY

Fantacalcio-PY è un tool che aiuta gli utenti a prepararsi per l'asta del fantacalcio. Il programma esegue le seguenti operazioni:

1.  **Recupero Dati**: Scarica i dati dei calciatori da due fonti:
    *   **FPEDIA**: per le statistiche della stagione in corso.
    *   **FSTATS**: per le statistiche della stagione precedente.
2.  **Elaborazione**: Pulisce ed elabora i dati provenienti dalle diverse fonti.
3.  **Calcolo Indice di Convenienza**: Calcola un indice di "convenienza" per ogni giocatore. Questo indice mette in rapporto il valore di un giocatore (prezzo base all'asta) con il suo rendimento passato e attuale, aiutando a identificare giocatori sottovalutati.
4.  **Salvataggio Risultati**: I risultati finali, ordinati per indice di convenienza, vengono salvati in un file Excel.


## Prerequisiti

Per utilizzare questo progetto, è necessario avere installato **Python 3.13** o superiore e **uv** per la gestione delle dipendenze.

## Installazione

1.  **Clonare la repository (se non già fatto)**:
    ```bash
    git clone <url_della_repository>
    cd fantacalcio-py-main
    ```

2.  **Installare le dipendenze**:
    
    ```bash
    uv venv
    uv sync
    ```
    Questo comando creerà un ambiente virtuale e installerà tutte le librerie necessarie specificate nel file `pyproject.toml`.

## Configurazione

Il progetto richiede delle credenziali per accedere a `FSTATS`. Queste credenziali vanno inserite in un file `.env` nella root del progetto.

Il file `config.py` contiene altre configurazioni, come gli URL per lo scraping e i percorsi dei file di output. Non dovrebbe essere necessario modificarlo per il funzionamento base.

## Avvio del Progetto

Per avviare l'analisi completa, settare PYTHONPATH

```bash

```

ed eseguire lo script `main.py` utilizzando `uv`.


```bash
uv run ./src/main.py
```

Lo script eseguirà tutti i passaggi (recupero, elaborazione, calcolo e salvataggio).

## Output

Al termine dell'esecuzione, verranno creati dei file Excel nella directory `data/output`. 


