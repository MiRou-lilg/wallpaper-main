@echo off
set /p msg="Enter commit label/message: "

IF "%msg%"=="" (
    set msg="Auto-update commit"
)

echo Staging changes...
git add .

echo Committing...
git commit -m "%msg%"

echo Pushing changes...
git push

echo Done!
pause