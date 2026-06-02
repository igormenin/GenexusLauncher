@echo off
set EXE_NAME=GeneXusLauncher.exe
timeout /t 2 /nobreak > nul
taskkill /f /im "%EXE_NAME%" > nul 2>&1
powershell -Command "Expand-Archive -Path 'last_version.zip' -DestinationPath '.' -Force"
if exist "last_version.zip" del "last_version.zip"
powershell -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Atualizacao concluida com sucesso!' + [char]10 + [char]10 + 'Voce ja pode iniciar o aplicativo novamente.', 'GeneXus Launcher')"

del "%~f0"
