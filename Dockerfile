FROM ubuntu:noble-20260210.1

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src
ENV DEBIAN_FRONTEND=noninteractive

ENV DAIKONDIR=/app/experiments/daikon-5.8.2
ENV GASSERT_DIR=/app/experiments/GAssert
ENV SPECS_DIR=/app/experiments/specfuzzer-subject-results
ENV MAJOR_HOME=/app/experiments/major
ENV SPECVALID_DIR=/app

# System packages: Java 8, Python 3.12, build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    openjdk-8-jdk-headless \
    python3.12 python3.12-venv \
    curl unzip make ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# uv (Python package manager)
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/app/.venv/bin:/root/.local/bin/:$PATH"

# Copy project and install Python dependencies
COPY specvalid/ /app/
WORKDIR /app
ENV UV_NO_DEV=1
RUN uv sync --locked

# Extract GAssert (subjects + test infrastructure)
COPY GAssert.tar.gz /tmp/
RUN tar -xzf /tmp/GAssert.tar.gz -C experiments/ \
    && rm /tmp/GAssert.tar.gz

# Extract Daikon 5.8.2 + compile dcomp_rt.jar
COPY daikon-5.8.2.zip /tmp/
RUN unzip -qo /tmp/daikon-5.8.2.zip -d experiments/ \
    && rm /tmp/daikon-5.8.2.zip \
    && make -C "$DAIKONDIR/java" dcomp_rt.jar

# Extract SpecFuzzer results (precomputed specifications)
COPY specfuzzer-subject-results.zip /tmp/
RUN unzip -qo /tmp/specfuzzer-subject-results.zip -d experiments/ \
    && rm /tmp/specfuzzer-subject-results.zip

CMD ["bash"]
