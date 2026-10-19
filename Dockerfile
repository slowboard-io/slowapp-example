# The example slowapp. The base is pinned by tag and digest; Dependabot opens one PR when
# slowapp-base releases, bumping this and the workflow ref in .github/workflows/app.yml together.
FROM ghcr.io/mike-anderson/slowapp-python:1.4.1@sha256:eb97f920f1bce8efb7a3eb4827cbafff53672f50102d730ee955ae8f7abcde1b
COPY slowapp.toml /app/slowapp.toml
COPY moon /opt/app/moon
ENV PYTHONPATH=/opt/app:/opt/slowapp
RUN python3 -m compileall -q /opt/app
ENTRYPOINT ["python3", "-m", "moon"]
CMD ["job", "render"]
