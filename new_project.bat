@echo off

rem Get the project name and module name from the command line
set project_name=%1
set module_name=%2

rem Create the root directory and other necessary directories
mkdir %project_name%
cd %project_name%

mkdir data

rem Create the setup.py file
echo.>setup.py

rem Create the LICENSE file
echo.>LICENSE

rem Create the README file
echo.>README.md

rem Create the requirements.txt file
echo.>requirements.txt

rem Create the Dockerfile file
echo.>Dockerfile

rem Create the src directory
mkdir src

rem move to src directory
cd src

rem Create the run.py file and model directory
echo.>run.py
mkdir model

rem Create the tests package directory
mkdir tests
cd tests 
echo.>__init__.py
cd ..

rem Create the main package directory
mkdir %project_name%
cd %project_name%

rem Create the __init__.py files
echo.>__init__.py
echo.>_version.py

rem Create the module directory
mkdir %module_name%
cd %module_name%
echo.>__init__.py
echo.>%module_name%.py
cd ..
cd ..