#!/bin/bash
set -eo pipefail  # Exit on error and fail on pipe errors

# Ensure version argument is provided
if [[ -z "$1" ]]; then
    echo "Error: Version argument is required"
    exit 1
fi

version="$1"
echo "Preparing release candidate for version: $version"

# Clean up previous release candidate directory
rm -rf release-candidate/*
echo "Removed old release-candidate directory."

# Generate build
ucc-gen build --ta-version "$version" --output release-candidate
if [[ $? -ne 0 ]]; then
    echo "Build generation failed for version $version"
    exit 1
fi
echo "Build generation succeeded."

# Package the app
slim package "release-candidate/Splunk_TA_Dynatrace" --output-dir releases
if [[ $? -ne 0 ]]; then
    echo "Slim packaging failed."
    exit 1
fi
echo "Slim packaging succeeded."

# Inspect the app for precertification
splunk-appinspect inspect "releases/Splunk_TA_Dynatrace-$version.tar.gz" --mode precert --included-tags cloud
if [[ $? -ne 0 ]]; then
    echo "Splunk appinspect failed."
    exit 1
fi
echo "Splunk appinspect succeeded."

echo "Release candidate $version prepared successfully."
