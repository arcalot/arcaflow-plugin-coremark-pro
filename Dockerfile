# Package path for this plugin module relative to the repo root
ARG package=arcaflow_plugin_coremark_pro

# STAGE 1 -- Build module dependencies and run tests
# The 'poetry' and 'coverage' modules are installed and verson-controlled in the
# quay.io/arcalot/arcaflow-plugin-baseimage-python-buildbase image to limit drift
FROM quay.io/arcalot/arcaflow-plugin-baseimage-python-buildbase:0.4.0 as build
ARG package

RUN dnf -y install git && \
    git clone https://github.com/eembc/coremark-pro.git && \
    cd coremark-pro && \
    make build

COPY poetry.lock /app/
COPY pyproject.toml /app/

# Convert the dependencies from poetry to a static requirements.txt file
RUN python -m poetry install --without dev --no-root \
 && python -m poetry export -f requirements.txt --output requirements.txt --without-hashes

COPY ${package}/ /app/${package}
COPY tests /app/${package}/tests

ENV PYTHONPATH /app/${package}
WORKDIR /app/${package}

# Run tests and return coverage analysis
RUN python -m coverage run tests/test_${package}.py \
 && python -m coverage html -d /htmlcov --omit=/usr/local/*


# STAGE 2 -- Build final plugin image
FROM quay.io/arcalot/arcaflow-plugin-baseimage-python-osbase:0.4.0
ARG package

RUN dnf -y install perl

COPY --from=build /app/requirements.txt /app/
COPY --from=build /htmlcov /htmlcov/
COPY LICENSE /app/
COPY CoreMark-PRO_LICENSE /app/
COPY README.md /app/
COPY ${package}/ /app/${package}

# Install all plugin dependencies from the generated requirements.txt file
RUN python -m pip install -r requirements.txt

COPY --from=build /app/coremark-pro /root/coremark-pro

WORKDIR /app/${package}

ENTRYPOINT ["python", "coremark_pro_plugin.py"]
CMD []

LABEL org.opencontainers.image.source="https://gitlab.com/redhat/edge/tests/perfscale/arcaflow-plugin-coremark-pro"
LABEL org.opencontainers.image.licenses="Apache-2.0+GPL-2.0+COREMARK®-PRO-ACCEPTABLE-USE-AGREEMENT-only"
LABEL org.opencontainers.image.vendor="Red Hat RHIVOS Perf & Scale"
LABEL org.opencontainers.image.authors="Red Hat RHIVOS Perf & Scale Team"
LABEL org.opencontainers.image.title="Python Plugin coremark_pro"
LABEL io.github.arcalot.arcaflow.plugin.version="1"
