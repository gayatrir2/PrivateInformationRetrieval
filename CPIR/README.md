# CPIR on SUPPORT2: Private and Verifiable Medical Record Retrieval

This project evaluates the **Committed Private Information Retrieval (CPIR)** library on the 
[SUPPORT2 clinical dataset](https://archive.ics.uci.edu/dataset/880/support2), as part of a 
comparative study of PIR libraries for privacy-preserving medical record access. The project 
was completed for **17735/95878 Engineering Privacy in Software** at Carnegie Mellon University.

---

## Project Overview

We implement and benchmark CPIR alongside SealPIR and XPIR to evaluate their suitability for 
protecting sensitive patient data in healthcare databases. CPIR is evaluated specifically for 
its verifiability guarantees: unlike SealPIR and XPIR, which only protect query privacy against 
honest-but-curious servers, CPIR additionally protects result integrity against malicious servers 
using Linear Map Commitments (LMC) over BLS12-381 elliptic curve pairings.

The database used is derived from the SUPPORT2 dataset (9,105 critically ill patients, 26 
clinical features), which serves as a realistic proxy for the type of clinical databases that 
benefit from privacy-preserving retrieval.

---

## What CPIR Provides

- **Query Privacy**: The server learns nothing about which record the client requested
- **Result Integrity**: The client can verify the returned record has not been tampered with
- **Byzantine-Robustness**: If a server returns incorrect data, the client identifies which 
  server misbehaved and recovers the correct data from the remaining honest server
- **k-Verifiability**: Even if all servers are under attacker control, the client will not 
  accept an incorrect record (though privacy may be lost in that scenario)

This is a strictly stronger guarantee than SealPIR and XPIR, which offer query privacy only.

---

## Generating the Database

The binary database is generated from the SUPPORT2 dataset hosted at the UCI Machine Learning 
Repository:

1. Download the dataset from: https://archive.ics.uci.edu/dataset/880/support2
2. Run the preprocessing script to extract 26 clinical features and serialize to binary format
3. The output file `support2_cpir.bin` should be placed in the project root before compiling

The preprocessing selects the following feature categories:
- **Clinical/Diagnostic**: `dzgroup`, `dzclass`, `ca`, `diabetes`, `dementia`
- **Physiological/Vitals**: `scoma`, `meanbp`, `hrt`, `resp`, `temp`, lab results Day 3
- **Demographic**: `age`, `sex`, `race`, `income`, `edu`
- **Outcomes**: `death`, `hospdead`, `num.co`

---

## Dependencies

| Library | Version | Purpose |
|---|---|---|
| GCC | 11.3.0+ | C compiler |
| GMP | 6.2.1 | Large number arithmetic |
| OpenSSL | 2022+ | SHA3-256 hashing |
| blst | v0.3.10 | BLS12-381 elliptic curve pairings |

### Installing Dependencies

**GCC**
```bash
sudo apt update && sudo apt upgrade
sudo apt install build-essential
```

**GMP**
```bash
# Download from https://gmplib.org/ and extract, then:
sudo apt-get install m4
./configure && make && sudo make install && make check
```

**OpenSSL**
```bash
sudo apt install libssl-dev
```

**blst**
```bash
git clone https://github.com/supranational/blst.git
cd blst && ./build.sh
# Copy the generated libblst.a to blst/lib/ in the project root
cp libblst.a /FULL-PATH/CPIR/blst/lib/
```

---

## Compiling and Running

Replace `/FULL-PATH/CPIR` with your actual project path in all commands below.

**LM-CKGS (2-server)**
```bash
gcc -o ComCKGS ComCKGSmain.c database.c LMC.c verifyhash.c CKGS.c \
    -lcrypto -lgmp -L /FULL-PATH/CPIR/blst/lib/ -lblst
./ComCKGS
```

**LM-CKGS (k-server)**
```bash
gcc -o ComGenCKGS ComGenCKGSmain.c database.c LMC.c verifyhash.c GenCKGS.c utils.c \
    -lcrypto -lgmp -L /FULL-PATH/CPIR/blst/lib/ -lblst
./ComGenCKGS
```

**LM-WY**
```bash
gcc -o ComWY ComWYmain.c database.c LMC.c verifyhash.c WY.c utils.c \
    -lcrypto -lgmp -L /FULL-PATH/CPIR/blst/lib/ -lblst
./ComWY
```

**LM-BE**
```bash
gcc -o ComBE ComBEmain.c database.c LMC.c verifyhash.c BE.c utils.c \
    -lcrypto -lgmp -lm -L /FULL-PATH/CPIR/blst/lib/ -lblst
./ComBE
```

---

## Implementation Results (SUPPORT2 Dataset)

Tested on 9,105 patient records × 26 clinical features using the LM-CKGS (2-server) scheme:

| Stage | Time (ms) |
|---|---|
| Query generation (Chor PIR) | 0.164 |
| LMC commitment | 1,430.54 |
| LMC proof generation (per server) | 10,029 |
| LMC verification | 1,057 |
| Query decode | 0.015 |
| Answer generation | 3.68 |

The underlying Chor-based PIR query generation (0.164ms) and answer generation (3.68ms) are 
among the fastest of any PIR library. Over 99% of total query time is attributable to the LMC 
integrity layer, which is the deliberate cost of the stronger security guarantee.

**Tamper detection was verified**: modifying a single field (age from 71 to 50) after 
commitment produced a `FAILED` verdict, confirming the LMC layer correctly detects even 
single-field tampering.

---

## Acknowledgments

Original CPIR library by the PIR-PIXR team. Paper available at 
[arXiv:2302.01733](https://arxiv.org/abs/2302.01733) and 
[ESORICS 2023](https://link.springer.com/chapter/10.1007/978-3-031-50594-2_20).  
Original work supported by the Australian Research Council, Grant DP200100731.

---

## References

- Chor, B., Kushilevitz, E., Goldreich, O., & Sudan, M. (1998). Private information retrieval. *Journal of the ACM*, 45(6), 965–981.
- Lai, R. W., & Malavolta, G. (2019). Subvector commitments with application to succinct arguments. *CRYPTO 2019*.
- Woodruff, D., & Yekhanin, S. (2005). A geometric approach to information-theoretic private information retrieval. *CCC 2005*.
- Bitar, R., & El Rouayheb, S. (2018). Staircase-PIR: Universally robust private information retrieval. *ITW 2018*.
