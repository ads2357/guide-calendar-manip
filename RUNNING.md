# This tool runs on Python, which runs on GNU/Linux, Mac and Windows and more.
# Instructions for Linux (and maybe Mac) are below.

# Dependencies: Python 3, Python VirtualEnv. Other dependencies will be installed by setup.py.

# TODO tidy and expand, and provide portable and installable versions


# In a terminal, go to the download directory and run:
rm -rf env # if exists and is out of date
virtualenv -p python3 env
source env/bin/activate
./setup.py develop
mergediary --help
