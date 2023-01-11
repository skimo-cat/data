#!/bin/bash

cd /home/pi/skimo-data
.  /home/pi/skimo-data/venv/bin/activate && python3 estacions_automatiques.py
.  /home/pi/skimo-data/venv/bin/activate && python3 increment_gruix_neu.py
git config --global user.name 'skimo'
git config --global user.email 'skimoskimo@skimo.com'
git checkout --orphan latest_branch
git add -A
git commit -m "Automated"
git branch -D main
git branch -m main
git push -f origin main
