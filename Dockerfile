# The example slowapp. The base is pinned by tag and digest; Dependabot opens a PR when
# slowapp-base releases (monthly at least, for Debian's security updates).
FROM ghcr.io/mike-anderson/slowapp-python:1.0.0@sha256:08f0b4211764bcce27195597507e4346bb8e790f5714574e67c08bb59376a8e1
COPY slowapp.toml /app/slowapp.toml
COPY moon /opt/app/moon
ENV PYTHONPATH=/opt/app:/opt/slowapp
RUN python3 -m compileall -q /opt/app
ENTRYPOINT ["python3", "-m", "moon"]
CMD ["job", "render"]
