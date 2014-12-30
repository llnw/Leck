#!/bin/sh

curl https://chromium.googlesource.com/chromium/tools/depot_tools.git/+/8a57ce17e317c0213a95f7e504d13132badcdf2f/owners.py?format=TEXT | base64 -d > owners.py
curl https://chromium.googlesource.com/chromium/tools/depot_tools.git/+/8a57ce17e317c0213a95f7e504d13132badcdf2f/owners_finder.py?format=TEXT | base64 -d > owners_finder.py
