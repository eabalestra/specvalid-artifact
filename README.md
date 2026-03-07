# SpecValid — Artifact for ICST 2026

> **LLM-based test generation for specification inference**

This artifact accompanies the paper:

> _"LLM-Based Test Generation for Spec Inference"_ — ICST 2026 Research Track

---

## Purpose

**SpecValid** is a tool that uses Large Language Models (LLMs) to generate JUnit test cases designed to violate postconditions of Java methods. Generated tests are validated through dynamic invariant detection with Daikon, enabling automated specification inference.

This artifact provides:

- The full source code of SpecValid
- All experimental subjects (via GAssert), precomputed specifications (via SpecFuzzer), and Daikon for invariant detection
- A Docker-based reproducible environment to re-run the experiments reported in the paper

### Badges claimed

| Badge                  | Justification                                                                                                                                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Artifact Available** | The artifact is hosted in a publicly accessible archival repository (Zenodo) with a persistent DOI.                                                                                                                 |
| **Artifact Reviewed**  | The artifact is complete (all subjects, tools, and data included), consistent with the paper results, documented with step-by-step instructions, and fully exercisable via Docker without additional configuration. |

---

## Provenance

- **Archival repository (Zenodo DOI):** _(to be added after Zenodo upload)_
- **Source code:** https://github.com/eabalestra/specvalid
- **Paper preprint:** included in this artifact as `llm-based-test-generation-for-spec-inference.pdf`

---

## Data

This artifact includes three bundled datasets required to reproduce the experiments:

| Archive                          | Size    | Contents                                                                       | Source                                                          |
| -------------------------------- | ------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------- |
| `GAssert.tar.gz`                 | ~1.1 GB | Java subjects under analysis (classes + test suites + mutation infrastructure) | [GAssert project](https://github.com/facumolina/evosuite-tests) |
| `daikon-5.8.2.zip`               | ~245 MB | SpecFuzzer's Daikon variant used for dynamic invariant detection               | https://plse.cs.washington.edu/daikon/                          |
| `specfuzzer-subject-results.zip` | ~187 MB | Precomputed SpecFuzzer specifications for all subjects                         | https://github.com/eabalestra/specfuzzer-subject-results        |

All data is open-source or research-use. No proprietary data is included. No human subjects or personal data are involved.

---

## Setup

### Hardware requirements

| Resource | Minimum         | Recommended                       |
| -------- | --------------- | --------------------------------- |
| RAM      | 8 GB            | 16 GB                             |
| Disk     | 10 GB free      | 15 GB free                        |
| CPU      | x86_64, 4 cores | 8+ cores                          |
| GPU      | not required    | NVIDIA GPU (speeds up local LLMs) |

> ⚠️ Running local models via Ollama requires downloading model weights (~25 GB for Llama 3.3 70B Q4, ~43 GB for DeepSeek-R1 70B). Cloud APIs (OpenAI, HuggingFace) require only an API key.

### Software requirements

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) v2.0+ (included in Docker Desktop)

No other dependencies are needed — Java 8, Python 3.12, Daikon, and all Python packages are installed inside the container.

### Build the Docker image

```bash
docker compose build
```

This step takes ~5–10 minutes on first run (downloads ~500 MB of packages and extracts the bundled archives). Subsequent builds use the Docker cache and are faster.

### Pull a local model (optional — only for Ollama-based models)

```bash
# Start the Ollama service
docker compose up -d ollama

# Pull Llama 3.3 70B Q4 (~25 GB)
docker compose exec ollama ollama pull llama3.3:70b-instruct-q4_K_M
```

---

## Usage

### Option A: Run with OpenAI API key (recommended for quick evaluation)

No need to start Ollama. Just export your API key and run:

```bash
export OPENAI_API_KEY=sk-...

docker compose run --rm specvalid \
  ./experiments/run-testgen.sh -m "GPT51" -p "General_V1" -o output/results
```

This runs SpecValid on all 43 subjects using `gpt-5.1` (the primary model used in the paper). Results are written to `./output/results/` on the host. Expected runtime: ~20–40 minutes depending on API latency.

**OpenAI models available:**

| Flag value   | OpenAI model    | Used in paper |
| ------------ | --------------- | ------------- |
| `GPT51`      | `gpt-5.1`       | ✅ Yes        |
| `GPT4o`      | `gpt-4o`        |               |
| `GPT4oMini`  | `gpt-4o-mini`   |               |
| `GPT4Turbo`  | `gpt-4-turbo`   |               |
| `GPT35Turbo` | `gpt-3.5-turbo` |               |

---

### Option B: Run with HuggingFace API key (Llama 3.3 70B / DeepSeek-R1)

```bash
export HUGGINGFACE_API_KEY=hf_...

# Llama 3.3 70B (used in paper)
docker compose run --rm specvalid \
  ./experiments/run-testgen.sh -m "Llama3370Instruct" -p "General_V1" -o output/results

# DeepSeek-R1 (used in paper)
docker compose run --rm specvalid \
  ./experiments/run-testgen.sh -m "DeepSeekR1" -p "General_V1" -o output/results
```

---

### Option C: Run with local models via Ollama (no API key needed)

```bash
# 1. Start Ollama
docker compose up -d ollama

# 2. Pull Llama 3.3 70B Q4 (one-time, ~25 GB)
docker compose exec ollama ollama pull llama3.3:70b-instruct-q4_K_M

# 3. Run experiments
docker compose run --rm specvalid \
  ./experiments/run-testgen.sh -m "L_Llama3370Instruct_Q4" -p "General_V1" -o output/results
```

#### With GPU acceleration (NVIDIA only)

Requires the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) installed on the host. Add `--gpus all` when starting Ollama:

```bash
docker compose stop ollama
docker run -d --gpus all \
  -v specvalid-artifact_ollama_data:/root/.ollama \
  --network specvalid-artifact_default \
  --network-alias ollama \
  --name specvalid-artifact-ollama-1 \
  ollama/ollama

docker compose run --rm specvalid \
  ./experiments/run-testgen.sh -m "L_Llama3370Instruct_Q4" -p "General_V1" -o output/results
```

---

### Replicate paper results

The paper evaluates three LLMs: **GPT-5.1** (OpenAI), **Llama 3.3 70B** (via Ollama), and **DeepSeek-R1** (via Ollama).

```bash
# GPT-5.1 (OpenAI)
export OPENAI_API_KEY=sk-...
docker compose run --rm specvalid \
  ./experiments/run-testgen.sh -m "GPT51" -p "General_V1" -o output/paper-results

# Start Ollama first (required for local models)
docker compose up -d ollama

# Llama 3.3 70B (pull once: ~25 GB)
docker compose exec ollama ollama pull llama3.3:70b-instruct-q4_K_M
docker compose run --rm specvalid \
  ./experiments/run-testgen.sh -m "L_Llama3370Instruct_Q4" -p "General_V1" -o output/paper-results

# DeepSeek-R1 70B (pull once: ~43 GB)
docker compose exec ollama ollama pull deepseek-r1:70b
docker compose run --rm specvalid \
  ./experiments/run-testgen.sh -m "L_DeepSeekR1Llama70_Q4" -p "General_V1" -o output/paper-results
```

Results are written to `./output/paper-results/` on the host. Each subject directory contains the generated tests and the Daikon-inferred invariants.

---

### Quick test: run a single paper subject

Use `-s "<subject_id> <FullyQualifiedClass> <method>"` to run just one subject instead of all 43.
This is the recommended way to quickly verify the tool works.

We recommend `polyupdate_sm` as the showcase subject: it achieved the **largest false-positive reduction** in the paper, with precision jumping from **21% to 75.6%** — the biggest improvement across all 43 evaluated subjects:

```bash
export OPENAI_API_KEY=sk-...
docker compose run --rm specvalid \
  ./experiments/run-testgen.sh \
  -s "polyupdate_sm examples.Polyupdate sm" \
  -m "GPT51" -p "General_V1" -o output/quick
```

The full list of available subjects is in `specvalid/experiments/subjects-to-run`.

Results appear under `./output/quick/` on the host.

---

### Advanced: run on your own Java class

To use SpecValid on a method not in the paper's subject set you need:

1. Specs generated by **SpecFuzzer** (see its artifact for instructions)
2. A compiled test suite targeting that method

The tool expects these six files per subject:

| Argument                   | Description                                  | Example filename                                       |
| -------------------------- | -------------------------------------------- | ------------------------------------------------------ |
| `<java_src>`               | `.java` source of the class under test       | `SimpleMethods.java`                                   |
| `<test_suite>`             | Compiled test suite `.java` (EvoSuite-style) | `SimpleMethods_getMin_ESTest.java`                     |
| `<test_driver>`            | EvoSuite scaffolding `.java`                 | `SimpleMethods_getMin_ESTest_scaffolding.java`         |
| `<buckets_assertions>`     | Clustered specs (`-buckets.assertions`)      | `SimpleMethods-getMin-specfuzzer-1-buckets.assertions` |
| `<method>`                 | Method name                                  | `getMin`                                               |
| `<invariants.gz>` (`-sf`)  | Daikon-inferred invariants (gzip)            | `SimpleMethods-getMin.inv.gz`                          |
| `<all_assertions>` (`-sa`) | Full SpecFuzzer output (`.assertions`)       | `SimpleMethods-getMin-specfuzzer-1.assertions`         |

**`-buckets.assertions` format** (clustered, used for LLM input):

```txt
buckets=9
specs=9
=====================================
:::OBJECT
=====================================
:::POSTCONDITION
FuzzedInvariant ( (Integer_Variable_0 < Integer_Variable_1) or (Integer_Variable_1 <= Integer_Variable_2) ) holds for: <orig(a) , orig(b) , return>
FuzzedInvariant ( Integer_Variable_0 > Integer_Variable_1 - 1 ) holds for: <orig(a), return>
```

**`.assertions` format** (full list, used for verification):

```txt
===========================================================================
examples.SimpleMethods:::OBJECT
===========================================================================
examples.SimpleMethods.getMin(int, int):::EXIT
FuzzedInvariant ( Integer_Variable_0 >= Integer_Variable_1 ) holds for: <orig(a), return>
\result <= \old(a)
\result <= \old(b)
```

Run directly with:

```bash
docker compose run --rm specvalid \
  specvalid testgen \
    path/to/MyClass.java \
    path/to/MyClass_method_ESTest.java \
    path/to/MyClass_method_ESTest_scaffolding.java \
    path/to/MyClass-method-specfuzzer-1-buckets.assertions \
    method \
    -m "GPT51" -p "General_V1" \
    -sf path/to/MyClass-method.inv.gz \
    -sa path/to/MyClass-method-specfuzzer-1.assertions \
    -o output/custom
```

---

## Directory structure

```sh
specvalid-artifact/
├── README.md                              # This file
├── LICENSE                                # MIT License
├── llm-based-test-generation-for-spec-inference.pdf  # Accepted paper
├── Dockerfile                             # Container build definition
├── docker-compose.yml                     # Orchestrates specvalid + ollama services
├── GAssert.tar.gz                         # Java subjects (~1.1 GB)
├── daikon-5.8.2.zip                       # SpecFuzzer's Daikon variant for dynamic invariant detection (~245 MB)
├── specfuzzer-subject-results.zip         # Precomputed specs (~187 MB)
├── output/                                # Experiment results (written at runtime)
└── specvalid/                             # SpecValid source code
    ├── src/                               # Python source (cli, generators, daikon, etc.)
    ├── experiments/
    │   ├── run-testgen.sh                 # Main experiment script
    │   └── subjects/                      # Subject metadata
    ├── libs/                              # Java libraries (Daikon, FuzzSpecs, ANTLR)
    ├── pyproject.toml                     # Python project config
    └── uv.lock                            # Locked Python dependencies
```
