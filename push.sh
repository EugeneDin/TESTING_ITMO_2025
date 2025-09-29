#!/bin/bash
# Скрипт для упрощенной заливки всего в мастер. Юз виз кер!
DATE=`date +%d-%m-%Y`
# git pull
git add -A
git commit -m $DATE
git push origin main