# XPIR – Private Information Retrieval for Healthcare Data

This repository accompanies the implementation of **XPIR** (eXtended Private Information Retrieval) on Apple M-Chip System applied to the [SUPPORT2 clinical dataset](https://archive.ics.uci.edu/dataset/880/support2) (9,105 patient records). It provides:

- A Colab notebook to construct the **patient** and **researcher** binary databases for XPIR
- Python decoder scripts for interpreting retrieved records on the client side
- A researcher index map for labeling aggregate query results

> **Based on:** Aguilar-Melchor, C., Barrier, J., Fousse, L., & Killijian, M.-O. (2016). XPIR: Private information retrieval for everyone. *PoPETs 2016*. https://doi.org/10.1515/popets-2016-0010  
> **XPIR Source:** https://github.com/XPIR-team/XPIR

---

## Repository Contents

| File | Purpose | Location on your machine |
|---|---|---|
| `XPIR_patient_researcher_DBconstruction.ipynb` | Colab notebook to build both binary databases | Run on Google Colab |
| `decode_pir_record.py` | Decodes a retrieved patient record from `reception/` | `_build/apps/client/` |
| `decode_research_record.py` | Decodes a retrieved researcher aggregate record from `reception/` | `_build/apps/client/` |
| `research_index_map.json` | Maps researcher record index numbers to group labels | `_build/apps/client/` |

> All three Python/JSON files must be placed in the **client folder**: `~/XPIR/_build/apps/client/`

---

## Prerequisites

### 1. Build XPIR on your machine
Follow the official XPIR build instructions for your OS:
- **macOS (Apple Silicon):** All XPIR commands must run inside a Rosetta 2 shell:
  ```bash
  arch -x86_64 zsh
  ```
- **Dependencies:** GMP, MPFR, Boost, CMake, OpenMP
- **Build:**
  ```bash
  git clone https://github.com/XPIR-team/XPIR.git
  cd XPIR
  mkdir _build && cd _build
  cmake ..
  make -j4
  ```

### 2. Construct the Databases
Open `XPIR_DBconstruction.ipynb` in Google Colab and run all cells. This will:

- Download the SUPPORT2 dataset from UCI
- Preprocess and impute missing values
- Serialize each patient record as 26 `float64` values = **208 bytes/record** → `xpir_db.zip` (9,105 files)
- Serialize each researcher aggregate record as 57 `float64` values padded to **512 bytes/record** → `xpir_research_db.zip` (39 files)
- Download both zip files and `research_index_map.json`

After downloading:

```bash
# Patient database
unzip xpir_db.zip -d xpir_db_extracted
mkdir -p ~/XPIR/_build/apps/server/db
cp xpir_db_extracted/* ~/XPIR/_build/apps/server/db/

# Researcher database
unzip xpir_research_db.zip -d xpir_research_db_extracted
mkdir -p ~/XPIR/_build/apps/server/research_db/db
cp xpir_research_db_extracted/* ~/XPIR/_build/apps/server/research_db/db/

# Verify counts
ls ~/XPIR/_build/apps/server/db | wc -l           # should print 9105
ls ~/XPIR/_build/apps/server/research_db/db | wc -l  # should print 39
```

### 3. Place Python Files in the Client Folder
```bash
cp decode_pir_record.py       ~/XPIR/_build/apps/client/
cp decode_research_record.py  ~/XPIR/_build/apps/client/
cp research_index_map.json    ~/XPIR/_build/apps/client/
```

---

## Patient Queries

### Start the Patient Server

Open **Terminal 1** (Rosetta shell on Apple Silicon):

```bash
arch -x86_64 zsh
cd ~/XPIR/_build/apps/server
./pir_server
```

Expected output:
```
DBDirectoryProcessor: 9105 entries processed
DBDirectoryProcessor: The size of the database is 1893840 bytes
PIRServer: Please launch a client to configure the server
```

### Connect the Patient Client

Open **Terminal 2** (Rosetta shell):

```bash
arch -x86_64 zsh
cd ~/XPIR/_build/apps/client
./pir_client          # default port 1234, NoCryptography auto-selected
```

You will see a file list and prompt:
```
# Which file do you want ? #
```
Enter a number from **0 to 9104** to retrieve that patient record (0-indexed).

### Setting Cryptographic Parameters (LWE or Paillier)

To override the default auto-selection and force a specific cryptographic scheme:

```bash
# Force LWE (248-bit security, recommended)
./pir_client --crypto "LWE.*"

# Force Paillier (80-bit security)
./pir_client --crypto "Paillier.*"

# Specific LWE parameters (security:poly_degree:coeff_bits)
./pir_client --crypto "LWE:248:2048:60"

# Specific Paillier parameters (security:plaintext_bits:ciphertext_bits)
./pir_client --crypto "Paillier:80:1024:2048"
```

> ⚠️ On zsh, always wrap the `--crypto` argument in **double quotes** to prevent shell glob expansion of `*`.

### Decode the Retrieved Patient Record

After the client exits, decode the result:

```bash
cd ~/XPIR/_build/apps/client
python3 decode_pir_record.py
```

This script reads the most recently retrieved binary file from the `reception/` folder, unpacks the 26 `float64` values, and displays all clinical and demographic fields in a human-readable table, including vitals (blood pressure, heart rate, temperature), lab values (albumin, glucose, BUN), disease group, comorbidities, and outcome.

To decode a specific file by index:
```bash
python3 decode_pir_record.py <filename>
# e.g., python3 decode_pir_record.py 431
```

---

## Researcher Queries

Researcher queries retrieve **pre-aggregated, PII-free statistics** across 39 clinically meaningful patient groups. No individual patient record is ever returned. PII fields (income, sex, race, education) are excluded at the data layer.

### View the Researcher Query Index

```bash
cd ~/XPIR/_build/apps/client
python3 decode_research_record.py --index
```

This reads `research_index_map.json` and prints the full index of available query groups, organized by category:

| Category | Records | Examples |
|---|---|---|
| Disease group | 8 | ARF/MOSF w/Sepsis, CHF, Cirrhosis, COPD... |
| Disease × Outcome | 16 | CHF \| Survived, CHF \| Deceased... |
| Age bracket | 5 | Age: 18–40, 41–60, 61–70, 71–80, 81+ |
| BP severity | 3 | BP: Normal (<80), Elevated (80–100), Hypertensive (>100) |
| Comorbidity | 4 | Diabetes present/absent, Dementia present/absent |
| Cancer status | 3 | No cancer, Cancer, Metastatic |

### Start the Researcher Server

Open **Terminal 1** (Rosetta shell) — this is a **separate server from the patient server**, running on port 1235:

```bash
arch -x86_64 zsh
cd ~/XPIR/_build/apps/server/research_db
~/XPIR/_build/apps/server/pir_server -p 1235
```

> **Note:** The first time a client connects, the server will spend ~60 seconds generating a performance cache for all cryptographic parameter combinations. This is a one-time process. Subsequent connections use the cached values instantly.

Expected output after cache generation:
```
DBDirectoryProcessor: 39 entries processed
PIROptimizer: Finished generating the absorption and precompute performance cache
PIRServer: Please launch a client to configure the server
```

### Connect the Researcher Client

Open **Terminal 2** (Rosetta shell). You **must** specify port 1235:

```bash
arch -x86_64 zsh
cd ~/XPIR/_build/apps/client
./pir_client -p 1235
```

You will see the 39-file catalog and prompt:
```
# Which file do you want ? #
```

Enter an index number from **0 to 38**. Cross-reference with the index printed by `--index` above.

For example, entering `2` retrieves aggregate statistics for "Disease: Cirrhosis".

### Setting Cryptographic Parameters for Researcher Queries

```bash
# LWE (recommended — 248-bit security, alpha=24, 2 query elements)
./pir_client -p 1235 --crypto "LWE.*"

# Paillier (80-bit security, alpha=1, 39 query elements — slower query generation)
./pir_client -p 1235 --crypto "Paillier.*"
```

### Decode the Retrieved Researcher Record

After the client exits:

```bash
python3 decode_research_record.py
```

This script reads the latest binary file from `reception/`, unpacks 57 `float64` values (19 attributes × mean/std/count), looks up the group label from `research_index_map.json`, and displays a formatted table showing:

- **Mean** and **Standard Deviation** of each clinical variable for the queried group
- **Patient count (N)** in that group
- **Mortality rate** (as a percentage) for the `death` field
- **Comorbidity prevalence** (as a percentage) for `diabetes` and `dementia`

To decode a specific file:
```bash
python3 decode_research_record.py <filename>
# e.g., python3 decode_research_record.py 5
```

---

## Running Both Servers Simultaneously

The patient and researcher servers can run at the same time in separate terminals:

| Server | Port | DB path | Records |
|---|---|---|---|
| Patient | 1234 (default) | `apps/server/db/` | 9,105 |
| Researcher | 1235 | `apps/server/research_db/db/` | 39 |

Connect the client with the appropriate `-p` flag:
```bash
./pir_client            # → patient server (port 1234)
./pir_client -p 1235    # → researcher server (port 1235)
```

---

## Performance Summary

**Patient Queries (9,105 records × 208 bytes)**

| Scheme | Security | Query RTT | Answer Decode |
|---|---|---|---|
| LWE | 248-bit | ~351ms | ~350ms |
| Paillier | 80-bit | ~12,480ms | ~12,468ms |

**Researcher Queries (39 records × 512 bytes)**

| Scheme | Security | Query RTT | Answer Decode |
|---|---|---|---|
| LWE | 248-bit | ~12ms | ~11ms |
| Paillier | 80-bit | ~107ms | ~13ms |

---

## Citation

```
Aguilar-Melchor, C., Barrier, J., Fousse, L., & Killijian, M.-O. (2016).
XPIR: Private information retrieval for everyone.
Proceedings on Privacy Enhancing Technologies, 2016(2), 155–174.
https://doi.org/10.1515/popets-2016-0010
```

---

## License

This repository contains only database construction scripts and decoder utilities written for research and educational purposes. XPIR itself is subject to its own license at https://github.com/XPIR-team/XPIR.
