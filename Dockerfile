# The example slowapp. The base is pinned by tag and digest; Dependabot opens one PR when
# slowapp-base releases, bumping this and the workflow ref in .github/workflows/app.yml together.
FROM ghcr.io/mike-anderson/slowapp-python:1.5.0@sha256:ba854f3f6bda285b05ebdfb73115475eeef545c87b1d9c47a1d7434de66777a6
COPY slowapp.toml /app/slowapp.toml
COPY moon /opt/app/moon
ENV PYTHONPATH=/opt/app:/opt/slowapp
RUN python3 -m compileall -q /opt/app
ENTRYPOINT ["python3", "-m", "moon"]
CMD ["job", "render"]
