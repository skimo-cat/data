#!/bin/bash

cd /home/quim/data && . /home/quim/data/venv/bin/activate && python3 estacions_automatiques.py
cd /home/quim/data && . /home/quim/data/venv/bin/activate && python3 increment_gruix_neu.py
cd /home/quim/data && . /home/quim/data/venv/bin/activate && python3 increment_lauregi.py
cd /home/quim/data && . /home/quim/data/venv/bin/activate && python3 increment_meteofrance.py
# Ask for a BPA far into the future to always get the last one
cd /home/quim/data/insta && wget "https://bpa.icgc.cat/api/apiext/butlletiglobal?id=512&values=2040-12-27;1" -O bpa-sample.json
cd /home/quim/data/insta && . /home/quim/data/venv/bin/activate && python3 create_story.py && python3 create_bpa_story.py
cp /home/quim/data/insta/story.png /home/quim/data/docs/story.png
cp /home/quim/data/insta/avalanche_story.png /home/quim/data/docs/bpa-story.png
cp /home/quim/data/out.mp4 /home/quim/data/docs/wcs.mp4
git config --global user.name 'skimo'
git config --global user.email 'skimoskimo@skimo.com'
git checkout --orphan latest_branch
git add -A
git commit -m "Automated"
git branch -D main
git branch -m main
git push -f origin main
