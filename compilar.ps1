# Garante que o script rode na pasta onde ele está localizado
Set-Location -Path $PSScriptRoot

# Verifica privilégios de Administrador e eleva se necessário
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Elevando privilégios para Administrador..." -ForegroundColor Yellow
    # Reinicia o script como admin mantendo o diretório de trabalho correto
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"Set-Location -Path '$PSScriptRoot'; & '$PSCommandPath'`"" -Verb RunAs
    exit
}

Write-Host "--- GeneXus Launcher Build System ---" -ForegroundColor Cyan
Write-Host "Incrementando versão..." -ForegroundColor Cyan

$versionFile = "version.config"
if (Test-Path $versionFile) {
    $v = (Get-Content $versionFile -Raw).Trim()
    # Usa Regex para separar com segurança a versão (ex: 1.01)
    if ($v -match '^(\d+)\.(\d+)$') {
        $major = $matches[1]
        $minor = [int]$matches[2] + 1
        $newVersion = "$major.$($minor.ToString('00'))"
        $newVersion | Out-File $versionFile -Encoding ascii
        Write-Host "Versão atualizada para: $newVersion" -ForegroundColor Green
    } else {
        $newVersion = "1.01"
        $newVersion | Out-File $versionFile -Encoding ascii
        Write-Host "Formato inválido detectado. Resetando para: $newVersion" -ForegroundColor Yellow
    }
} else {
    $newVersion = "1.01"
    $newVersion | Out-File $versionFile -Encoding ascii
    Write-Host "Arquivo de versão criado: $newVersion" -ForegroundColor Green
}

Write-Host "`nEncerrando GeneXusLauncher.exe..." -ForegroundColor Cyan
Stop-Process -Name "GeneXusLauncher" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "`nLimpando pastas de build..." -ForegroundColor Cyan
Remove-Item -Path ".\build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".\dist" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`nCompilando com PyInstaller (isso pode levar alguns instantes)..." -ForegroundColor Cyan
# Rodamos o PyInstaller
& pyinstaller --onefile --windowed --uac-admin --name GeneXusLauncher --icon=images/AppIcon.png --add-data "images;images" --add-data "version.config;." .\start_Genexus.py



if ($LASTEXITCODE -eq 0) {
    Write-Host "`nCopiando executável para a raiz..." -ForegroundColor Cyan
    Copy-Item -Path ".\dist\GeneXusLauncher.exe" -Destination ".\GeneXusLauncher.exe" -Force

    Write-Host "`nProcesso concluído com sucesso!" -ForegroundColor Green

} else {
    Write-Host "`nERRO: Falha durante a compilação do PyInstaller." -ForegroundColor Red
}

Write-Host "`n"
Start-Sleep -Seconds 2
