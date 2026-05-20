## Setup of developer env

Note: Must install docker desktop, vscode or pycharm pro optional

Note2: Appinspect requires libmagic verify this has been installed correctly each time a new workstation/vm is used https://dev.splunk.com/enterprise/docs/releaseapps/appinspect/splunkappinspectclitool/installappinspect

```bash
git clone git@github.com:splunk/<repo slug>.git
cd <repo dir>
git submodule update --init --recursive

#setup python venv must be 3.7
/Library/Frameworks/Python.framework/Versions/3.7/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
pip install https://download.splunk.com/misc/appinspect/splunk-appinspect-latest.tar.gz

```


## Package build

Use the Makefile for UCC/Slim packaging instead of invoking `ucc-gen` directly. It pins the UCC build tool, uses Python 3.9 for vendored add-on dependencies, and verifies the tarball for the dependency regression that can break older Splunk Python handler runtimes.

```bash
make beta VERSION=2.1.8-beta3
```

For the local Splunk symlinked app, rebuild `output/Splunk_TA_Dynatrace` with:

```bash
make local-output VERSION=2.1.8
```


## Test

Using docker

```bash
pytest
```

Using external Splunk instance with Eventgen and app pre-installed

```bash
pytest --splunk-type=external --splunk-host=something --splunk-user=foo --splunk-password=something
```
