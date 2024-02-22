#!/bin/bash
set -eo pipefail  # Exit on error and fail on pipe errors

# Ensure version argument is provided
if [[ -z "$1" ]]; then
    echo "Error: Version argument is required"
    exit 1
fi

version="$1"
echo "Preparing release candidate for version: $version"

# Define variables for easy configuration
appName="Splunk_TA_Dynatrace"  # Parameterize the app name
releaseCandidateDir="release-candidate"  # Parameterize the release-candidate directory
releasesDir="releases"  # Parameterize the releases directory

echo "Configuration: App Name: $appName, Release Candidate Directory: $releaseCandidateDir, Releases Directory: $releasesDir"

# Clean up previous release candidate directory
rm -rf "$releaseCandidateDir"/*
echo "Removed old release-candidate directory."

# Generate build
ucc-gen build --ta-version "$version" --output "$releaseCandidateDir"
if [[ $? -ne 0 ]]; then
    echo "Build generation failed for version $version"
    exit 1
fi
echo "Build generation succeeded."

# Package the app
slim package "$releaseCandidateDir/$appName" --output-dir "$releasesDir"
if [[ $? -ne 0 ]]; then
    echo "Slim packaging failed."
    exit 1
fi
echo "Slim packaging succeeded."

# Inspect the app for precertification
splunk-appinspect inspect "$releaseCandidateDir/${appName}-$version.tar.gz" --mode precert --included-tags cloud
if [[ $? -ne 0 ]]; then
    echo "Splunk appinspect failed."
    exit 1
fi
echo "Splunk appinspect succeeded."

echo "Release candidate $version prepared successfully."#!/bin/bash
set -eo pipefail  # Exit on error and fail on pipe errors

# Ensure version argument is provided
if [[ -z "$1" ]]; then
    echo "Error: Version argument is required"
    exit 1
fi

version="$1"
echo "Preparing release candidate for version: $version"

# Define variables for easy configuration
appName="Splunk_TA_Dynatrace"  # Parameterize the app name
releaseCandidateDir="release-candidate"  # Parameterize the release-candidate directory
releasesDir="releases"  # Parameterize the releases directory

echo "Configuration: App Name: $appName, Release Candidate Directory: $releaseCandidateDir, Releases Directory: $releasesDir"

# Clean up previous release candidate directory
rm -rf "$releaseCandidateDir"/*
echo "Removed old release-candidate directory."

# Generate build
ucc-gen build --ta-version "$version" --output "$releaseCandidateDir"
if [[ $? -ne 0 ]]; then
    echo "Build generation failed for version $version"
    exit 1
fi
echo "Build generation succeeded."

# Package the app
slim package "$releaseCandidateDir/$appName" --output-dir "$releasesDir"
if [[ $? -ne 0 ]]; then
    echo "Slim packaging failed."
    exit 1
fi
echo "Slim packaging succeeded."

# Inspect the app for precertification
splunk-appinspect inspect "$releaseCandidateDir/${appName}-$version.tar.gz" --mode precert --included-tags cloud
if [[ $? -ne 0 ]]; then
    echo "Splunk appinspect failed."
    exit 1
fi
echo "Splunk appinspect succeeded."

echo "Release candidate $version prepared successfully."#!/bin/bash
set -eo pipefail  # Exit on error and fail on pipe errors

# Ensure version argument is provided
if [[ -z "$1" ]]; then
    echo "Error: Version argument is required"
    exit 1
fi

version="$1"
echo "Preparing release candidate for version: $version"

# Define variables for easy configuration
appName="Splunk_TA_Dynatrace"  # Parameterize the app name
releaseCandidateDir="release-candidate"  # Parameterize the release-candidate directory
releasesDir="releases"  # Parameterize the releases directory

echo "Configuration: App Name: $appName, Release Candidate Directory: $releaseCandidateDir, Releases Directory: $releasesDir"

# Clean up previous release candidate directory
rm -rf "$releaseCandidateDir"/*
echo "Removed old release-candidate directory."

# Generate build
ucc-gen build --ta-version "$version" --output "$releaseCandidateDir"
if [[ $? -ne 0 ]]; then
    echo "Build generation failed for version $version"
    exit 1
fi
echo "Build generation succeeded."

# Package the app
slim package "$releaseCandidateDir/$appName" --output-dir "$releasesDir"
if [[ $? -ne 0 ]]; then
    echo "Slim packaging failed."
    exit 1
fi
echo "Slim packaging succeeded."

# Inspect the app for precertification
splunk-appinspect inspect "$releaseCandidateDir/${appName}-$version.tar.gz" --mode precert --included-tags cloud
if [[ $? -ne 0 ]]; then
    echo "Splunk appinspect failed."
    exit 1
fi
echo "Splunk appinspect succeeded."

echo "Release candidate $version prepared successfully."#!/bin/bash
set -eo pipefail  # Exit on error and fail on pipe errors

# Ensure version argument is provided
if [[ -z "$1" ]]; then
    echo "Error: Version argument is required"
    exit 1
fi

version="$1"
echo "Preparing release candidate for version: $version"

# Define variables for easy configuration
appName="Splunk_TA_Dynatrace"  # Parameterize the app name
releaseCandidateDir="release-candidate"  # Parameterize the release-candidate directory
releasesDir="releases"  # Parameterize the releases directory

echo "Configuration: App Name: $appName, Release Candidate Directory: $releaseCandidateDir, Releases Directory: $releasesDir"

# Clean up previous release candidate directory
rm -rf "$releaseCandidateDir"/*
echo "Removed old release-candidate directory."

# Generate build
ucc-gen build --ta-version "$version" --output "$releaseCandidateDir"
if [[ $? -ne 0 ]]; then
    echo "Build generation failed for version $version"
    exit 1
fi
echo "Build generation succeeded."

# Package the app
slim package "$releaseCandidateDir/$appName" --output-dir "$releasesDir"
if [[ $? -ne 0 ]]; then
    echo "Slim packaging failed."
    exit 1
fi
echo "Slim packaging succeeded."

# Inspect the app for precertification
splunk-appinspect inspect "$releaseCandidateDir/${appName}-$version.tar.gz" --mode precert --included-tags cloud
if [[ $? -ne 0 ]]; then
    echo "Splunk appinspect failed."
    exit 1
fi
echo "Splunk appinspect succeeded."

echo "Release candidate $version prepared successfully."#!/bin/bash
set -eo pipefail  # Exit on error and fail on pipe errors

# Ensure version argument is provided
if [[ -z "$1" ]]; then
    echo "Error: Version argument is required"
    exit 1
fi

version="$1"
echo "Preparing release candidate for version: $version"

# Define variables for easy configuration
appName="Splunk_TA_Dynatrace"  # Parameterize the app name
releaseCandidateDir="release-candidate"  # Parameterize the release-candidate directory
releasesDir="releases"  # Parameterize the releases directory

echo "Configuration: App Name: $appName, Release Candidate Directory: $releaseCandidateDir, Releases Directory: $releasesDir"

# Clean up previous release candidate directory
rm -rf "$releaseCandidateDir"/*
echo "Removed old release-candidate directory."

# Generate build
ucc-gen build --ta-version "$version" --output "$releaseCandidateDir"
if [[ $? -ne 0 ]]; then
    echo "Build generation failed for version $version"
    exit 1
fi
echo "Build generation succeeded."

# Package the app
slim package "$releaseCandidateDir/$appName" --output-dir "$releasesDir"
if [[ $? -ne 0 ]]; then
    echo "Slim packaging failed."
    exit 1
fi
echo "Slim packaging succeeded."

# Inspect the app for precertification
splunk-appinspect inspect "$releaseCandidateDir/${appName}-$version.tar.gz" --mode precert --included-tags cloud
if [[ $? -ne 0 ]]; then
    echo "Splunk appinspect failed."
    exit 1
fi
echo "Splunk appinspect succeeded."

echo "Release candidate $version prepared successfully."#!/bin/bash
set -eo pipefail  # Exit on error and fail on pipe errors

# Ensure version argument is provided
if [[ -z "$1" ]]; then
    echo "Error: Version argument is required"
    exit 1
fi

version="$1"
echo "Preparing release candidate for version: $version"

# Define variables for easy configuration
appName="Splunk_TA_Dynatrace"  # Parameterize the app name
releaseCandidateDir="release-candidate"  # Parameterize the release-candidate directory
releasesDir="releases"  # Parameterize the releases directory

echo "Configuration: App Name: $appName, Release Candidate Directory: $releaseCandidateDir, Releases Directory: $releasesDir"

# Clean up previous release candidate directory
rm -rf "$releaseCandidateDir"/*
echo "Removed old release-candidate directory."

# Generate build
ucc-gen build --ta-version "$version" --output "$releaseCandidateDir"
if [[ $? -ne 0 ]]; then
    echo "Build generation failed for version $version"
    exit 1
fi
echo "Build generation succeeded."

# Package the app
slim package "$releaseCandidateDir/$appName" --output-dir "$releasesDir"
if [[ $? -ne 0 ]]; then
    echo "Slim packaging failed."
    exit 1
fi
echo "Slim packaging succeeded."

# Inspect the app for precertification
splunk-appinspect inspect "$releaseCandidateDir/${appName}-$version.tar.gz" --mode precert --included-tags cloud
if [[ $? -ne 0 ]]; then
    echo "Splunk appinspect failed."
    exit 1
fi
echo "Splunk appinspect succeeded."

echo "Release candidate $version prepared successfully."#!/bin/bash
set -eo pipefail  # Exit on error and fail on pipe errors

# Ensure version argument is provided
if [[ -z "$1" ]]; then
    echo "Error: Version argument is required"
    exit 1
fi

version="$1"
echo "Preparing release candidate for version: $version"

# Define variables for easy configuration
appName="Splunk_TA_Dynatrace"  # Parameterize the app name
releaseCandidateDir="release-candidate"  # Parameterize the release-candidate directory
releasesDir="releases"  # Parameterize the releases directory

echo "Configuration: App Name: $appName, Release Candidate Directory: $releaseCandidateDir, Releases Directory: $releasesDir"

# Clean up previous release candidate directory
rm -rf "$releaseCandidateDir"/*
echo "Removed old release-candidate directory."

# Generate build
ucc-gen build --ta-version "$version" --output "$releaseCandidateDir"
if [[ $? -ne 0 ]]; then
    echo "Build generation failed for version $version"
    exit 1
fi
echo "Build generation succeeded."

# Package the app
slim package "$releaseCandidateDir/$appName" --output-dir "$releasesDir"
if [[ $? -ne 0 ]]; then
    echo "Slim packaging failed."
    exit 1
fi
echo "Slim packaging succeeded."

# Inspect the app for precertification
splunk-appinspect inspect "$releaseCandidateDir/${appName}-$version.tar.gz" --mode precert --included-tags cloud
if [[ $? -ne 0 ]]; then
    echo "Splunk appinspect failed."
    exit 1
fi
echo "Splunk appinspect succeeded."

echo "Release candidate $version prepared successfully."#!/bin/bash
set -eo pipefail  # Exit on error and fail on pipe errors

# Ensure version argument is provided
if [[ -z "$1" ]]; then
    echo "Error: Version argument is required"
    exit 1
fi

version="$1"
echo "Preparing release candidate for version: $version"

# Define variables for easy configuration
appName="Splunk_TA_Dynatrace"  # Parameterize the app name
releaseCandidateDir="release-candidate"  # Parameterize the release-candidate directory
releasesDir="releases"  # Parameterize the releases directory

echo "Configuration: App Name: $appName, Release Candidate Directory: $releaseCandidateDir, Releases Directory: $releasesDir"

# Clean up previous release candidate directory
rm -rf "$releaseCandidateDir"/*
echo "Removed old release-candidate directory."

# Generate build
ucc-gen build --ta-version "$version" --output "$releaseCandidateDir"
if [[ $? -ne 0 ]]; then
    echo "Build generation failed for version $version"
    exit 1
fi
echo "Build generation succeeded."

# Package the app
slim package "$releaseCandidateDir/$appName" --output-dir "$releasesDir"
if [[ $? -ne 0 ]]; then
    echo "Slim packaging failed."
    exit 1
fi
echo "Slim packaging succeeded."

# Inspect the app for precertification
splunk-appinspect inspect "$releaseCandidateDir/${appName}-$version.tar.gz" --mode precert --included-tags cloud
if [[ $? -ne 0 ]]; then
    echo "Splunk appinspect failed."
    exit 1
fi
echo "Splunk appinspect succeeded."

echo "Release candidate $version prepared successfully."
