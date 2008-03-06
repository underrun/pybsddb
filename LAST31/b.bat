@echo off
setlocal


rem  Use non-default python?
iff "%1" == "15" .or. "%1" == "20" then
	set SETUP=c:\tools\python%1%\python.exe -u setup.py
	shift
else
	set SETUP=python -u setup.py
endiff


rem "c" --> clean
iff "%1" == "c" then
	shift
	set CMD=%SETUP% clean
	set OTHERCMD=del bsddb3\*.pyd

rem just remove the *.pyd's
elseiff "%1" == "d" then
	shift
	set CMD=del bsddb3\*.pyd

rem "i" --> install
elseiff "%1" == "i" then
	shift
	set CMD=%SETUP% build install

rem "s" --> source dist
elseiff "%1" == "s" then
	shift
	set CMD=%SETUP sdist

rem "r" --> binary dist
elseiff "%1" == "r" then
	shift
	set CMD=%SETUP bdist_wininst

rem "f" --> FINAL
elseiff "%1" == "f" then
	shift
	set CMD=%SETUP% %FLAGS% build_ext --inplace %1 %2 %3 %4 %5 %6 %7 %8 %9

rem (no command arg) --> normal build for development
else
	set CMD=%SETUP% %FLAGS% build_ext --inplace --debug %1 %2 %3 %4 %5 %6 %7 %8 %9
endiff



echo %CMD%
%CMD%

iff "%OTHERCMD%" != "" then
	echo %OTHERCMD%
	%OTHERCMD%
endiff

