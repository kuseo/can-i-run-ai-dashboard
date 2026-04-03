IMAGE_REPOSITORY ?= ghcr.io/kuseo/can-i-run-ai-dashboard
IMAGE_TAG ?= v0.1.0
IMAGE := $(IMAGE_REPOSITORY):$(IMAGE_TAG)

HELM_RELEASE ?= can-i-run-ai-dashboard
HELM_NAMESPACE ?= rpms
HELM_CHART ?= helm/can-i-run-ai-dashboard
HELM_VALUES ?=
HELM_ARGS ?=
HELM_VALUES_ARG = $(if $(HELM_VALUES),-f $(HELM_VALUES))
HELM_IMAGE_ARGS = --set-string image.repository=$(IMAGE_REPOSITORY) --set-string image.tag=$(IMAGE_TAG)

STREAMLIT_HOST ?= 0.0.0.0
STREAMLIT_PORT ?= 8501

.DEFAULT_GOAL := help

.PHONY: help docker-build docker-push helm-deploy local-dev-setup local-run

help:
	@printf "%s\n" \
		"Available targets:" \
		"  docker-build      Build Docker image ($(IMAGE))" \
		"  docker-push       Build and push Docker image ($(IMAGE))" \
		"  helm-deploy       Deploy/update Helm release ($(HELM_RELEASE))" \
		"  local-dev-setup   Create local Streamlit development environment with uv" \
		"  local-run         Run Streamlit locally with uv"

docker-build:
	docker build -t $(IMAGE) .

docker-push: docker-build
	docker push $(IMAGE)

helm-deploy:
	helm upgrade --install $(HELM_RELEASE) $(HELM_CHART) --namespace $(HELM_NAMESPACE) $(HELM_IMAGE_ARGS) $(HELM_VALUES_ARG) $(HELM_ARGS)

local-dev-setup:
	uv sync --frozen --python 3.14

local-run:
	uv run streamlit run app.py --server.address=$(STREAMLIT_HOST) --server.port=$(STREAMLIT_PORT)
