@echo off
rem Скрипт для упрощенной заливки всего в мастер. Юз виз кер!
git add -A
git commit -m %date%
git push origin main
pause