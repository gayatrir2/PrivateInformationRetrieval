# Private Information Retrieval for Sensitive Medical Records
### A Comparative Study of SealPIR, XPIR, and CPIR on the SUPPORT2 Dataset

---

## What This Project Does

This project evaluates three Private Information Retrieval (PIR) libraries —
**SealPIR**, **XPIR**, and **CPIR** — applied to a realistic sensitive medical
database. We measure each library's encryption overhead, query latency, and
ease of deployment to help database owners and researchers choose the most
appropriate PIR implementation for their use case.

---

## Why PIR Matters for Medical Records

When a user queries a medical database, the server can infer sensitive
information simply from *what* is being looked up — a patient's cancer
diagnosis, a rare condition, or a comorbidity profile — even without reading
the returned record. **Private Information Retrieval (PIR)** is a cryptographic
protocol that guarantees a user can retrieve a specific record from a database
without the server (or any observer) learning which record was requested.

In a healthcare context, this protects:
- **Patients and clinicians** from having sensitive condition lookups tracked
- **Researchers** from exposing which population subgroups they are studying
- **Database owners** from inadvertently leaking access patterns that reveal
  confidential query intent

---

## Libraries Evaluated

### 1. SealPIR
> Single-server computational PIR using BFV somewhat homomorphic encryption (SWHE)

- **Developer:** Microsoft Research (Angel et al., 2018)
- **GitHub:** [github.com/microsoft/SealPIR](https://github.com/microsoft/SealPIR)
- **Base library:** [github.com/microsoft/SEAL](https://github.com/microsoft/SEAL)

SealPIR encrypts a one-hot query vector using the Brakerski-Fan-Vercauteren
(BFV) scheme and applies oblivious expansion so the server performs homomorphic
multiplications across the database without learning the target index. Security
is grounded in the hardness of the Ring Learning With Errors (Ring-LWE) problem.
Key parameters — polynomial degree (`N`), plaintext modulus (`log t`), and
recursion level (`d`) — allow performance to be tuned to database size.

---

### 2. XPIR
> Single-server computational PIR using lattice-based (Ring-LWE) homomorphic encryption

- **Developer:** Aguilar-Melchor et al., French academic collaboration (PoPETs 2016)
- **GitHub:** [github.com/XPIR-team/XPIR](https://github.com/XPIR-team/XPIR)

XPIR implements computational PIR over a configurable recursion tree and
uniquely includes a **built-in optimizer** that benchmarks available
cryptographic schemes (LWE, Paillier, NoCryptography) against the current
database size and network conditions at session startup, automatically selecting
the optimal parameters. This makes XPIR the most accessible library for
practitioners without deep cryptographic expertise.

---

### 3. CPIR
> Verifiable single-server PIR using Linear Map Commitments (LMC) over pairing-based cryptography

- **Developer:** PIR-PIXR team
- **GitHub:** [github.com/PIR-PIXR/CPIR](https://github.com/PIR-PIXR/CPIR)

CPIR wraps a base Chor PIR scheme with a **Linear Map Commitment (LMC)** layer
built on the `blst` pairing library. For every response, the server generates a
cryptographic proof binding the returned record to a public commitment made at
database load time. Clients verify this proof before decrypting, ensuring that
even a malicious server cannot deliver tampered or fabricated records. This is
the only library among the three that protects against a *malicious* server in
addition to an honest-but-curious one.

---

## Dataset

**SUPPORT2 — Study to Understand Prognoses and Preferences for Outcomes and
Risks of Treatment (Phase II)**

- **Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/880/support2)
- **Original archive:** ICPSR (Harrell, 1995), funded by the Robert Wood Johnson Foundation
- **Size:** 9,105 critically ill patients across 5 US medical centers (1989–1994)
- **Sensitive attributes used (26 columns):**
  - *Clinical:* `dzgroup`, `ca`, `diabetes`, `dementia`, `num.co`
  - *Physiological:* `scoma`, `meanbp`, `hrt`, `resp`, `temp`, `pafi`, `alb`,
    `bili`, `crea`, `sod`, `ph`, `glucose`, `bun`, `wblc`, `urine`
  - *Demographic:* `age`, `sex`, `race`, `income`, `edu`
  - *Outcome:* `death`

---

## Data Preprocessing — `generic_dataprocessing.ipynb`

PIR libraries require databases stored as **flat binary files** with
**fixed-size, uniformly padded records**. The notebook transforms the raw
SUPPORT2 dataset into this format through the following steps:

1. **Fetch** the dataset directly from UCI via the `ucimlrepo` API
2. **Filter** the 45-column dataset down to the 26 clinically sensitive columns
   listed above
3. **Impute** missing numeric values using clinically validated fill-in values
   recommended by the HBiostat Repository (e.g., `alb=3.5`, `pafi=333.3`,
   `bun=6.51`)
4. **Encode** categorical string columns (`income`, `race`, `sex`, `ca`,
   `dzgroup`) as ordinal integers, since PIR libraries cannot process raw
   string values
5. **Serialize** each patient record to binary using Python's `struct` module,
   packing all 26 fields as IEEE 754 double-precision floats (8 bytes each) for
   a natural record size of 208 bytes
6. **Pad** each record to a fixed **512-byte boundary** (nearest power-of-two
   block size) as required by PIR library internals
7. **Write** all 9,105 records sequentially to a flat binary file (~4.7 MB
   total) for use as shared database input across all three libraries

> **Note:** A separate 39-record aggregated research database (512 bytes/record)
> was also generated for researcher-level queries over pre-computed group
> statistics. XPIR requires separate server instances for databases with
> different element sizes, so patient and researcher queries run on different
> ports.

---

## Results Summary

### Ease of Use

| Library | Pros | Cons |
|---|---|---|
| **SealPIR** | Easy parameter customization via `N`, `d`, `log t` | Version mismatch between SEAL v4.x and PIR functions required manual library edits and SEAL downgrade to v3.6.6 |
| **XPIR** | Built-in optimizer auto-selects best scheme and parameters | Requires Rosetta 2 on Apple Silicon; depends on legacy Boost/GMP/MPFR libraries |
| **CPIR** | No multi-server coordination needed; single-server design | Manual blst + GMP configuration, minimal documentation, no package manager support |

### Best Use Case Fit

| Use Case | Recommended Library | Reason |
|---|---|---|
| 🧑‍⚕️ Patient / Researcher queries | **XPIR with LWE** | RTT of 351ms (patient) and 12ms (researcher); auto-tunes parameters; no cryptographic expertise required |
| 🏛️ Hospital / Large institution | **SealPIR** | Highest throughput at scale when properly tuned; BFV parameters reward expert configuration on large databases |
| 🔍 Auditor / Regulatory compliance | **CPIR** | LMC proofs cryptographically verify server response integrity; detects single-field tampering in 0.039ms; only option against malicious servers |

---
