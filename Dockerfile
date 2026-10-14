# The example slowapp. The base is pinned by tag and digest; Dependabot opens a PR when
# slowapp-base releases (monthly at least, for Debian's security updates).
FROM ghcr.io/mike-anderson/slowapp-python:1.2.0@sha256:5cc196d93d9960643d51eac7a49f46fe4eb9a1c4f68deba0f60579ea9559a532
COPY slowapp.toml /app/slowapp.toml
COPY moon /opt/app/moon
ENV PYTHONPATH=/opt/app:/opt/slowapp
RUN python3 -m compileall -q /opt/app
ENTRYPOINT ["python3", "-m", "moon"]
CMD ["job", "render"]
