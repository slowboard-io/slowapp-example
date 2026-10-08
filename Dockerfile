# The example slowapp. The base is pinned by tag and digest; Dependabot opens a PR when
# slowapp-base releases (monthly at least, for Debian's security updates).
FROM ghcr.io/mike-anderson/slowapp-python:1.1.0@sha256:d1542bced1c247f49dcfd34ed2b1a5b6cd36b8113cb7f5d2699b251b3124daeb
COPY slowapp.toml /app/slowapp.toml
COPY moon /opt/app/moon
ENV PYTHONPATH=/opt/app:/opt/slowapp
RUN python3 -m compileall -q /opt/app
ENTRYPOINT ["python3", "-m", "moon"]
CMD ["job", "render"]
