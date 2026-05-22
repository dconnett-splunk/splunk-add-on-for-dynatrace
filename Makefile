SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

TA_NAME := Splunk_TA_Dynatrace
PACKAGE_DIR := package
BUILD_DIR := .build
OUTPUT_DIR := release-candidate
RELEASE_DIR := releases

VERSION ?= $(shell python3 -c 'import json; print(json.load(open("globalConfig.json"))["meta"]["version"])')
UCC_VERSION ?= 6.4.0
UCC_PYTHON ?= python3.10
ADDON_PYTHON ?= python3.9
SLIM ?= /Applications/Splunk/bin/slim
SPLUNKTAUCCLIB_VERSION ?= 7.0.0
SOLNLIB_VERSION ?= 7.0.0
REQUESTS_VERSION ?= 2.32.3

UCC_VENV := $(BUILD_DIR)/ucc-$(UCC_VERSION)
UCC_GEN := $(UCC_VENV)/bin/ucc-gen
BUILD_CONFIG := $(BUILD_DIR)/$(TA_NAME)-$(VERSION)-globalConfig.json
BUILT_APP := $(OUTPUT_DIR)/$(TA_NAME)
ARTIFACT := $(RELEASE_DIR)/$(TA_NAME)-$(VERSION).tar.gz
MODINPUT_SCRIPTS := dynatrace_api_v2 dynatrace_entity dynatrace_problem dynatrace_timeseries_metrics dynatrace_timeseries_metrics_v2 dynatrace_timeseries_single_metric
MODINPUT_SCRIPT_PATHS := $(addprefix $(PACKAGE_DIR)/bin/,$(addsuffix .py,$(MODINPUT_SCRIPTS)))
PACKAGED_MODINPUT_SCRIPT_PATHS := $(addprefix $(TA_NAME)/bin/,$(addsuffix .py,$(MODINPUT_SCRIPTS)))

FORBIDDEN_ARTIFACT_PATHS := opentelemetry|grpc|(^|/)local/|\.env|\.slimignore|\.uccignore|secret|password|api[_-]?token|auth[_-]?token

.PHONY: help beta package local-output ucc-build verify-package check-tools check-runtime-pins check-modinput-scripts test clean-build

help:
	@printf '%s\n' \
		'Build targets:' \
		'  make beta VERSION=2.1.8-beta4      Build, package, and verify a beta tarball.' \
		'  make package VERSION=2.1.8          Build, package, and verify a tarball.' \
		'  make local-output VERSION=2.1.8     Rebuild output/ for the local Splunk symlink.' \
		'  make verify-package VERSION=...     Verify an existing tarball in releases/.' \
		'  make test                           Run focused entity-selector tests.' \
		'' \
		'Important knobs:' \
		'  UCC_VERSION=6.4.0                   UCC used in the private build venv.' \
		'  UCC_PYTHON=python3.10               Python used to create the UCC build venv.' \
		'  ADDON_PYTHON=python3.9              Python used by UCC to vendor app deps.' \
		'  SLIM=/Applications/Splunk/bin/slim  Splunk packaging toolkit path.'

beta:
	@if [[ "$(VERSION)" != *beta* ]]; then \
		echo 'ERROR: beta builds must set VERSION to a beta version, e.g. VERSION=2.1.8-beta3'; \
		exit 2; \
	fi
	@$(MAKE) package VERSION="$(VERSION)"

package: check-tools check-runtime-pins ucc-build
	@mkdir -p "$(RELEASE_DIR)"
	"$(SLIM)" package "$(BUILT_APP)" --output-dir "$(RELEASE_DIR)"
	@$(MAKE) verify-package VERSION="$(VERSION)"

local-output:
	@$(MAKE) ucc-build OUTPUT_DIR=output VERSION="$(VERSION)"

ucc-build: check-modinput-scripts $(UCC_GEN) $(BUILD_CONFIG)
	"$(UCC_GEN)" build \
		--source "$(PACKAGE_DIR)" \
		--config "$(BUILD_CONFIG)" \
		--ta-version "$(VERSION)" \
		--output "$(OUTPUT_DIR)" \
		--python-binary-name "$(ADDON_PYTHON)" \
		--overwrite

$(UCC_GEN):
	@mkdir -p "$(BUILD_DIR)"
	"$(UCC_PYTHON)" -m venv "$(UCC_VENV)"
	"$(UCC_VENV)/bin/python" -m pip install --upgrade pip
	"$(UCC_VENV)/bin/python" -m pip install "splunk-add-on-ucc-framework==$(UCC_VERSION)"

$(BUILD_CONFIG): globalConfig.json | $(BUILD_DIR)
	cp "$<" "$@"

$(BUILD_DIR):
	@mkdir -p "$@"

check-tools:
	@command -v rg >/dev/null
	@"$(UCC_PYTHON)" --version
	@"$(ADDON_PYTHON)" --version
	@test -x "$(SLIM)"

check-runtime-pins:
	@rg -n '^splunktaucclib==$(SPLUNKTAUCCLIB_VERSION)$$' "$(PACKAGE_DIR)/lib/requirements.txt" >/dev/null
	@rg -n '^solnlib==$(SOLNLIB_VERSION)$$' "$(PACKAGE_DIR)/lib/requirements.txt" >/dev/null
	@rg -n '^requests==$(REQUESTS_VERSION)$$' "$(PACKAGE_DIR)/lib/requirements.txt" >/dev/null

check-modinput-scripts:
	@for script in $(MODINPUT_SCRIPT_PATHS); do \
		test -x "$$script" || { echo "ERROR: $$script must be executable for Splunk modular input registration"; exit 1; }; \
	done

verify-package:
	@test -f "$(ARTIFACT)"
	@mkdir -p "$(BUILD_DIR)"
	@if tar -tzf "$(ARTIFACT)" | rg -i '$(FORBIDDEN_ARTIFACT_PATHS)'; then \
		echo 'ERROR: forbidden dependency or sensitive/local path found in artifact'; \
		exit 1; \
	fi
	@scan_dir="$$(mktemp -d "$(BUILD_DIR)/scan-$(VERSION)-XXXXXX")"; \
		tar -xzf "$(ARTIFACT)" -C "$$scan_dir"; \
		for script in $(PACKAGED_MODINPUT_SCRIPT_PATHS); do \
			test -x "$$scan_dir/$$script" || { echo "ERROR: $$script is not executable in artifact"; exit 1; }; \
		done; \
		PYTHONPATH="$$scan_dir/$(TA_NAME)/lib:$$scan_dir/$(TA_NAME)/bin" "$(ADDON_PYTHON)" -c 'from importlib import metadata as md; import packaging._manylinux, packaging.tags, packaging.version, requests, solnlib.splunk_rest_client, splunktaucclib, dynatrace_entity_selectors; assert md.version("splunktaucclib") == "$(SPLUNKTAUCCLIB_VERSION)"; assert md.version("solnlib") == "$(SOLNLIB_VERSION)"; assert md.version("requests") == "$(REQUESTS_VERSION)"; assert dynatrace_entity_selectors.select_entity_types("HOST,SERVICE") == ["HOST", "SERVICE"]; print("artifact runtime checks ok")'

test:
	python -m unittest tests.test_dynatrace_entity_selectors -v

clean-build:
	rm -rf "$(BUILD_DIR)"
