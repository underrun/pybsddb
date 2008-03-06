@echo off
setlocal

rem Update the local copy of the DB libs and stuff.

set DBDIR=c:\projects\db-3.1.17

mkdir db
mkdir db\include
mkdir db\lib
mkdir db\bin

copy /u %DBDIR%\build_win32\db.h          db\include
copy /u %DBDIR%\build_win32\Debug\*.lib   db\lib
copy /u %DBDIR%\build_win32\Release\*.lib db\lib
copy /u %DBDIR%\build_win32\Release\*.dll db\bin
copy /u %DBDIR%\build_win32\Release\*.exe db\bin

endlocal