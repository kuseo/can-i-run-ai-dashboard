# can-i-run-ai-dashboard

Streamlit dashboard for the `canirunai` Python SDK.

## Local Development

This project targets Python 3.14 because the upstream `canirunai` package currently declares `requires-python >=3.14`.

```bash
make local-dev-setup
make local-run
```

You can override the local bind address and port if needed.

```bash
make local-run STREAMLIT_HOST=127.0.0.1 STREAMLIT_PORT=8502
```

## Container Image

Build the Docker image:

```bash
make docker-build IMAGE_REPOSITORY=ghcr.io/<org>/can-i-run-ai-dashboard IMAGE_TAG=dev
```

Build and push the Docker image:

```bash
make docker-push IMAGE_REPOSITORY=ghcr.io/<org>/can-i-run-ai-dashboard IMAGE_TAG=v0.1.0
```

## Helm Deploy

Deploy or update the Helm release:

```bash
make helm-deploy \
  IMAGE_REPOSITORY=ghcr.io/<org>/can-i-run-ai-dashboard \
  IMAGE_TAG=v0.1.0 \
  HELM_NAMESPACE=default \
  HELM_VALUES=helm/can-i-run-ai-dashboard/values.yaml
```

You can also override `HELM_RELEASE`, `HELM_CHART`, and `HELM_ARGS` as needed.
